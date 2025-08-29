import os
from flask import Flask, jsonify, render_template, request, flash
from aforo import CalculadoraTanque
from api import ApiCorreccion
from datos import DataLoader
from validaciones import Validaciones  # Importamos la clase Validaciones

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        tanque = request.form.get('tanque')
        altura_inicial = request.form.get('altura_inicial')
        print(altura_inicial)
        altura_final = request.form.get('altura_final')
        volumen = request.form.get('volumen')
        api = request.form.get('api')
        temperatura = request.form.get('temperatura')
        drenaje = request.form.get("galonesDrenados")
       
        try:
            # Usamos la clase Validaciones para hacer las validaciones
            numero = Validaciones.validate_tank_number(tanque)
            altura_1 = Validaciones.validate_float(altura_inicial, "Altura inicial")
            altura_final = Validaciones.validate_float(altura_final, "Altura final")
            volumen = Validaciones.validate_float(volumen, "Volumen neto CarroTk")
            
            # Validaciones específicas para API y Temperatura
            api_observado = Validaciones.validate_api(api)
            temp = Validaciones.validate_temperature(temperatura)
            drenaje = Validaciones.validate_float(drenaje, "galonesDrenados")

            # Lógica del cálculo de volumen
            vol_1, vol_2, result = calculate_volume(numero, altura_1, altura_final, api_observado, temp, volumen, drenaje)
        
            if result:
                return jsonify({
                    'altura_inicial': altura_1,
                    'altura_final': altura_final,
                    'vol_1': vol_1,
                    'vol_2': vol_2,
                    **result
                })

        except ValueError as e:
            flash(str(e), 'error')  # Muestra el mensaje de error al usuario

    return render_template('index.html')

def calculate_volume(numero, altura_inicial, altura_final, api_observado, temp, volumen, drenaje):
    tks = DataLoader("DB/tablas_aforo")
    obAforo = CalculadoraTanque(altura_inicial, volumen, numero)

    # Mapeo del número del tanque al nombre del archivo
    datos_path = {
        "smr-Tk-101": "smr-tk-101.json",
        "smr-Tk-102": "smr-tk-102.json",
        "smr-Tk-103": "smr-tk-103.json",
        "smr-Tk-104": "smr-tk-104.json",
        "ctg-tk-08": "aforo_tk_08.json",
        "ctg-tk-09": "aforo_tk_09.json",
        "ctg-tk-102": "aforo_tk_10.json",
        "baq-tk-504": "baq-tk-504.json",
        "baq-tk-503": "baq-tk-503.json",
        "baq-tk-505": "baq-tk-505.json"
    }.get(numero)

    aforo_tks = tks.load_file(datos_path)

    #prueba 
    if "ctg" in numero:
        vol_1 = obAforo.get_volumen_ctg(aforo_tks,altura_inicial)
        print("volumen inicial CTG:", vol_1)
        vol_2 = obAforo.get_volumen_ctg(aforo_tks,altura_final)
    elif "baq" in numero:
        vol_1 = obAforo.get_volumen_ctg(aforo_tks, altura_inicial)
        vol_2 = obAforo.get_volumen_ctg(aforo_tks, altura_final)    
    else:
        vol_1 = obAforo.get_volumen_smr(aforo_tks, altura_inicial)
        vol_2 = obAforo.get_volumen_smr(aforo_tks, altura_final)

    ap = ApiCorreccion(api_observado, temp)
    api_corregido, fac_cor = ap.corregir_correccion()
    vol_br_rec = round((vol_2 - vol_1), 2)
    vol_neto_rec = round((vol_br_rec * fac_cor), 2)

    diferencia = round((vol_neto_rec - volumen), 2) + drenaje
    tolerancia = volumen * 0.002
    mensaje, mensaje_class = prepare_result_message(diferencia, tolerancia)

    return vol_1, vol_2, {
        'vol_br_rec': vol_br_rec,
        'api': api_observado,
        'api_corregido': api_corregido,
        'temperatura': temp,
        'fac_cor': fac_cor,
        'vol_neto_rec': vol_neto_rec,
        'volumen': volumen,
        'diferencia': diferencia,
        'mensaje': mensaje,
        'mensaje_class': mensaje_class
    }

def prepare_result_message(diferencia, tolerancia):
    if diferencia < -tolerancia:
        return f"Faltante de: {round(diferencia, 2)} gls (Tolerancia: {round(tolerancia, 2)} gls)", "display-5 text-danger"
    else:
        return f"Conforme, tolerancia: {round(tolerancia, 2)} gls.", "display-5 text-success"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Usa el puerto de Heroku o 5000 por defecto
    app.run(host="0.0.0.0", port=port, debug=True)  # Asegúrate de enlazar a todas las interfaces
