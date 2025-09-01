// static/js/main.js

let ALL_TANK_OPTIONS = [];

function cacheTankOptions() {
  const sel = document.getElementById('tanque');
  if (!sel) return;
  ALL_TANK_OPTIONS = [];
  // Guardamos TODAS las opciones originales (excepto el placeholder en índice 0)
  for (let i = 1; i < sel.options.length; i++) {
    const opt = sel.options[i];
    ALL_TANK_OPTIONS.push({ value: opt.value, text: opt.text });
  }
}

function rebuildTanksForAirport(airportCode) {
  const sel = document.getElementById('tanque');
  if (!sel) return;

  const code = (airportCode || '').toUpperCase().trim();
  // Guardar el placeholder actual (índice 0)
  const placeholder = sel.options[0]?.cloneNode(true) || new Option('Selecciona un tanque', '');

  // Limpiar el select y volver a poner el placeholder
  sel.innerHTML = '';
  sel.add(placeholder);
  sel.selectedIndex = 0;

  if (!code) {
    sel.disabled = true;
    return;
  }

  const prefix = code + '-';

  // Agregar SOLO las opciones que coincidan con el aeropuerto
  ALL_TANK_OPTIONS.forEach(o => {
    const v = (o.value || '').toUpperCase();
    const t = (o.text  || '').toUpperCase();
    if (v.startsWith(prefix) || t.startsWith(prefix)) {
      const option = document.createElement('option');
      option.value = o.value;
      option.text  = o.text;
      sel.add(option);
    }
  });

  // Habilitar si hay al menos una opción más el placeholder
  sel.disabled = sel.options.length <= 1;
}

// 🔹 NUEVO: actualizar placeholders de altura según aeropuerto
function updateAlturaPlaceholdersByAirport(airportCode) {
  const ai = document.getElementById('altura_inicial');
  const af = document.getElementById('altura_final');
  if (!ai || !af) return;

  const baseIni = 'Altura Inicial';
  const baseFin = 'Altura Final';

  if ((airportCode || '').toUpperCase() === 'SMR') {
    ai.placeholder = baseIni + ' (Centímetros)';
    af.placeholder = baseFin + ' (Centímetros)';
  } else {
    // Sin unidad (o pon ' (Milímetros)' si lo prefieres)
    ai.placeholder = baseIni;
    af.placeholder = baseFin;
  }
}

document.addEventListener('DOMContentLoaded', function () {
  // Forzar placeholder en aeropuerto al cargar (evita autocompletar del navegador)
  const airportSel = document.getElementById('airport');
  if (airportSel) {
    const hasPlaceholder = !!airportSel.querySelector('option[value=""]');
    if (hasPlaceholder) airportSel.value = '';
  }

  // Cachear opciones originales de tanques (una sola vez)
  cacheTankOptions();

  // Estado inicial
  rebuildTanksForAirport('');
  updateAlturaPlaceholdersByAirport(''); // 🔹 set inicial de placeholders

  // Filtrado por aeropuerto + actualización de placeholders
  if (airportSel) {
    airportSel.addEventListener('change', function () {
      rebuildTanksForAirport(airportSel.value);
      updateAlturaPlaceholdersByAirport(airportSel.value); // 🔹 actualizar placeholders
      // Opcional: reset de unidad cuando cambie aeropuerto
      const tanqueSel = document.getElementById('tanque');
      if (tanqueSel) tanqueSel.dispatchEvent(new Event('change'));
    });
  }

  // Normalización del campo "volumen" (comas → puntos, 3 decimales máx.)
  const volumenInput = document.getElementById('volumen');
  if (volumenInput) {
    volumenInput.addEventListener('input', function () {
      this.value = this.value.replace(',', '.');
      const parts = this.value.split('.');
      if (parts.length > 1 && parts[1].length > 3) {
        this.value = parts[0] + '.' + parts[1].substring(0, 3);
      }
    });
  }

  // Unidad (cm/mm) según tanque
  let unidadAltura = 'mm';
  const tanqueSel = document.getElementById('tanque');
  if (tanqueSel) {
    tanqueSel.addEventListener('change', function () {
      if ((this.value || '').toLowerCase().startsWith('smr')) unidadAltura = 'cm';
      else unidadAltura = 'mm';
    });
    // Estado inicial
    tanqueSel.dispatchEvent(new Event('change'));
  }

  // Envío del formulario por fetch
  const form = document.getElementById('data-form');
  if (form) {
    form.onsubmit = async function (event) {
      event.preventDefault();

      const formData = new FormData(this);
      try {
        const response = await fetch(this.action, { method: 'POST', body: formData });
        if (!response.ok) {
          let msg = "Error desconocido";
          try { msg = (await response.json()).error || msg; } catch {}
          alert(msg);
          return;
        }

        const data = await response.json();

        const set = (id, val) => { const el = document.getElementById(id); if (el) el.innerText = val; };
        set('altura_inicial_result', data.altura_inicial + ' ' + unidadAltura);
        set('vol_1_result',          data.vol_1 + '.Gls');
        set('altura_final_result',   data.altura_final + ' ' + unidadAltura);
        set('vol_2_result',          data.vol_2 + '.Gls');
        set('vol_br_rec_result',     data.vol_br_rec + '.Gls');
        set('temperatura_result',    data.temperatura + '°F');
        set('api_result',            data.api);
        set('api_corregido_result',  data.api_corregido);
        set('fac_cor_result',        data.fac_cor);
        set('vol_neto_rec_result',   data.vol_neto_rec + '.Gls');
        set('volumen_result',        data.volumen + '.Gls');
        set('diferencia_result',     data.diferencia + '.Gls');

        const msgEl = document.getElementById('mensaje_result');
        if (msgEl) {
          msgEl.innerText = data.mensaje;
          msgEl.className = data.mensaje_class || '';
        }

        const results = document.getElementById('results');
        if (results) results.classList.remove('d-none');

      } catch (e) {
        alert('No se pudo enviar la solicitud. Revisa tu conexión.');
      }
    };
  }
});
