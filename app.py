import os, json
from pathlib import Path
from datetime import timedelta
from flask import Flask, jsonify, render_template, request, session
from decimal import Decimal, ROUND_HALF_UP  # ⬅ para redondeo 0.5 "half up"

from aforo import CalculadoraTanque
from api import ApiCorreccion
from datos import DataLoader
from validaciones import Validaciones  # Importamos la clase Validaciones

app = Flask(__name__)

# --- Sesión y rutas de archivos ---
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")
app.permanent_session_lifetime = timedelta(days=7)

BASE_DIR = Path(__file__).parent
AIRPORTS_FILE = os.environ.get("AIRPORTS_FILE", str(BASE_DIR / "DB" / "airports.json"))
TANK_MAP_FILE = os.environ.get("TANK_MAP_FILE", str(BASE_DIR / "DB" / "tank_map.json"))

# --- Carga de catálogos ---
def load_airports(file_path: str) -> dict:
    p = Path(file_path)
    if not p.exists():
        app.logger.warning(f"[AIRPORTS] No se encontró {file_path}. Usando diccionario vacío.")
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        # Validación mínima
        for code, meta in data.items():
            if not isinstance(meta, dict):
                raise ValueError(f"Aeropuerto {code} inválido (no es objeto)")
            if "nombre" not in meta or "tanques" not in meta or not isinstance(meta["tanques"], list):
                raise ValueError(f"Estructura inválida para aeropuerto {code}")
        return data
    except Exception as e:
        app.logger.error(f"[AIRPORTS] Error cargando {file_path}: {e}")
        return {}

def load_tank_map(file_path: str) -> dict:
    p = Path(file_path)
    if not p.exists():
        app.logger.warning(f"[TANK_MAP] No se encontró {file_path}. Usando diccionario vacío.")
        return {}
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
        # Claves case-insensitive en memoria
        return {str(k).lower(): str(v) for k, v in raw.items()}
    except Exception as e:
        app.logger.error(f"[TANK_MAP] Error cargando {file_path}: {e}")
        return {}

AIRPORTS = load_airports(AIRPORTS_FILE)
TANK_MAP = load_tank_map(TANK_MAP_FILE)

# --- Utilidades ---
def tank_belongs_to_airport(tank_code: str, airport_code: str) -> bool:
    if not tank_code or not airport_code:
        return False
    return tank_code.upper() in {t.upper() for t in AIRPORTS.get(airport_code, {}).get("tanques", [])}

def get_tank_path(numero: str) -> str:
    """Devuelve el nombre de archivo de aforo para el tanque `numero` usando TANK_MAP (case-insensitive)."""
    if not numero:
        raise ValueError("Código de tanque vacío.")
    path = TANK_MAP.get(numero.lower())
    if not path:
        raise ValueError(f"Tanque '{numero}' no está configurado en {TANK_MAP_FILE}.")
    return path

def redondear_a_05_half_up(valor: float) -> float:
    """
    Redondea al múltiplo de 0.5 más cercano usando 'half up' (25→25, 25.25→25.5, 25.75→26.0).
    Evita el redondeo bancario de round() de Python.
    """
    d = Decimal(str(valor)) * Decimal('2')
    entero = d.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    return float(entero / Decimal('2'))

# --- Ruta principal: POST devuelve JSON (para fetch), GET renderiza index.html ---
@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        airport = (request.form.get('airport') or "").upper().strip()
        tanque = request.form.get('tanque')
        altura_inicial = request.form.get('altura_inicial')
        altura_final = request.form.get('altura_final')
        volumen = request.form.get('volumen')
        api = request.form.get('api')
        temperatura = request.form.get('temperatura')
        drenaje = request.form.get("galonesDrenados")

        # Validaciones rápidas (JSON)
        if not airport or airport not in AIRPORTS:
            return jsonify({"error": "Selecciona un aeropuerto válido."}), 400
        if not tanque:
            return jsonify({"error": "Selecciona un tanque."}), 400
        if not tank_belongs_to_airport(tanque, airport):
            return jsonify({"error": "El tanque no pertenece al aeropuerto seleccionado."}), 400

        try:
            # Validaciones de negocio base
            numero = Validaciones.validate_tank_number(tanque)
            altura_1 = Validaciones.validate_float(altura_inicial, "Altura inicial")
            altura_final = Validaciones.validate_float(altura_final, "Altura final")
            volumen = Validaciones.validate_float(volumen, "Volumen neto CarroTk")
            drenaje = Validaciones.validate_float(drenaje, "galonesDrenados")

            # API: aceptar decimales y redondear a múltiplo de 0.5 más cercano
            api_input = Validaciones.validate_float(api, "API")
            api_observado = redondear_a_05_half_up(api_input)

            # Temperatura: usa tu validación actual (no cambiamos reglas aquí)
            temp = Validaciones.validate_temperature(temperatura)

            # Cálculo
            vol_1, vol_2, result = calculate_volume(
                numero, altura_1, altura_final, api_observado, temp, volumen, drenaje
            )

            # Guarda el aeropuerto elegido por conveniencia futura
            session["airport"] = airport

            return jsonify({
                'altura_inicial': altura_1,
                'altura_final': altura_final,
                'vol_1': vol_1,
                'vol_2': vol_2,
                **result  # 'api' en result ya va con el api_observado redondeado
            })

        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    # GET: pasamos el catálogo completo; sin preselección (placeholder en el HTML)
    return render_template('index.html', airports=AIRPORTS)

# --- Cálculo de volumen ---
def calculate_volume(numero, altura_inicial, altura_final, api_observado, temp, volumen, drenaje):
    tks = DataLoader("DB/tablas_aforo")
    obAforo = CalculadoraTanque(altura_inicial, volumen, numero)

    # Archivo de aforo (desde DB/tank_map.json)
    datos_path = get_tank_path(numero)
    aforo_tks = tks.load_file(datos_path)

    # Método según prefijo (normalizado)
    num_l = (numero or "").lower()
    if "ctg" in num_l or "baq" in num_l:
        vol_1 = obAforo.get_volumen_ctg(aforo_tks, altura_inicial)
        vol_2 = obAforo.get_volumen_ctg(aforo_tks, altura_final)
    else:
        # SMR por defecto
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
        'api': api_observado,          # API redondeado
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
