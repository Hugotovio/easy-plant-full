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
        drenaje = request.form.get("galonesDrenados")
       
        try:
            numero = validate_tank_number(tanque)
            altura_1 = validate_float(altura_inicial, "Altura inicial")
            altura_final = validate_float(altura_final, "Altura final")
            volumen = validate_float(volumen, "Volumen neto CarroTk")
            api_observado = validate_float(api, "API")
            temp = validate_float(temperatura, "Temperatura")
            drenaje = validate_float(drenaje, "galonesDrenados")

            check_height_limits(numero, altura_1)
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
            flash(str(e), 'error')

    return render_template('index.html')

def calculate_volume(numero, altura_inicial, altura_final, api_observado, temp, volumen, drenaje):
    tks = DataLoader("DB")
    obAforo = CalculadoraTanque(altura_inicial, volumen, numero)

    # Mapeo del número del tanque al nombre del archivo
    datos_path = {
        "smr-Tk-101": "smr-tk-101.json",
        "smr-Tk-102": "smr-tk-102.json",
        "smr-Tk-103": "smr-tk-103.json",
        "smr-recuperador": "smr-recuperador.json",
        "ctg-tk-08": "aforo_tk_08.json",
        "ctg-tk-09": "aforo_tk_09.json"
    }.get(numero)

    aforo_tks = tks.load_file(datos_path)

    # Usa get_volumen_ctg para tanques CTG
    if "ctg" in numero:
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


def validate_tank_number(value):
    valid_tanks = ["smr-Tk-101", "smr-Tk-102", "smr-Tk-103","smr-recuperador", "ctg-tk-08", "ctg-tk-09"]
    if value not in valid_tanks:
        raise ValueError("Número del tanque no válido.")
    return value

def validate_float(value, field_name):
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"{field_name} debe ser un número decimal.")

def check_height_limits(numero, altura):
    # Agregar lógica para los límites de altura si aplica
    pass

def prepare_result_message(diferencia, tolerancia):
    if diferencia < -tolerancia:
        return f"Faltante de: {round(diferencia, 2)} gls (Tolerancia: {round(tolerancia, 2)} gls)", "display-5 text-danger"
    else:
        return f"Conforme, tolerancia: {round(tolerancia, 2)} gls.", "display-5 text-success"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Use the port from Heroku
    app.run(debug=True)  # Ensure you bind to all interfaces


