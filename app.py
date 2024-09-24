import os
from flask import Flask, jsonify, render_template, request, flash
from aforo import CalculadoraTanque
from api import ApiCorreccion
from datos import DataLoader

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        tanque = request.form.get('tanque')
        altura_inicial = request.form.get('altura_inicial')
        altura_final = request.form.get('altura_final')
        volumen = request.form.get('volumen')
        api = request.form.get('api')
        temperatura = request.form.get('temperatura')
        drenaje=request.form.get("galonesDrenados")
        centro=request.form.get("centro_trabajo")

        try:
            numero = validate_number(tanque, "Número del tanque")
            altura_1 = validate_float(altura_inicial, "Altura inicial")
            altura_final = validate_float(altura_final, "Altura final")
            volumen = validate_float(volumen, "Volumen neto CarroTk")
            api_observado = validate_float(api, "API")
            temp = validate_float(temperatura, "Temperatura")
            drenaje = validate_float(drenaje, "galonesDrenados")

            check_height_limits(numero, altura_1)

            tks = DataLoader("DB")

            datos_path = "aforo_tk_08.json" if numero == 8 else "aforo_tk_09.json" 
            aforo_tks = tks.load_file(datos_path)

            obAforo = CalculadoraTanque(altura_inicial, volumen, tanque)

            vol_1 = obAforo.mostrar_volumen(aforo_tks, altura_inicial)
            if vol_1 is None:
                return jsonify({'error': 'La altura inicial está fuera de rango.'})

            vol_2 = obAforo.mostrar_volumen(aforo_tks, altura_final)
            if vol_2 is None:
                return jsonify({'error': 'La altura final está fuera de rango.'})

            ap = ApiCorreccion(api_observado, temp)
            api_corregido, fac_cor = ap.corregir_correccion()
            vol_br_rec = round((vol_2 - vol_1), 2)
            vol_neto_rec = round((vol_br_rec * fac_cor), 2)
            
            diferencia = round((vol_neto_rec - volumen), 2)+drenaje
            tolerancia = volumen * 0.002

            mensaje, mensaje_class = prepare_result_message(diferencia, tolerancia)

            return jsonify({
                'altura_inicial': altura_1,
                'altura_final': altura_final,
                'vol_1': vol_1,
                'vol_2': vol_2,
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
                
                
            })

        except ValueError as e:
            flash(str(e), 'error')

    return render_template('index.html')

def validate_number(value, field_name):
    if not value.isdigit():
        raise ValueError(f"{field_name} debe ser un número entero.")
    return int(value)

def validate_float(value, field_name):
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"{field_name} debe ser un número decimal.")

def check_height_limits(numero, altura):
    if (numero == 8 and altura > 9728) or (numero == 9 and altura > 9799):
        raise ValueError(f"La altura máxima permitida para el tanque {numero} es {'9728 mm' if numero == 8 else '9799 mm'}.")
def prepare_result_message(diferencia, tolerancia):
    if diferencia < -tolerancia:
        return f"Faltante de: {round(diferencia, 2)} gls (Tolerancia: {round(tolerancia, 2)} gls)", "display-4 text-danger"
    else:
        return f"Conforme, tolerancia: {round(tolerancia, 2)} gls.", "display-4 text-success"


""" 
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Usa el puerto de Heroku
    app.run(host='0.0.0.0', port=port)  # Asegúrate de enlazar a todas las interfaces

"""

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Obtén el puerto asignado por Heroku
    app.run(debug=True)  # Vincula a 0.0.0.0 y usa el puerto