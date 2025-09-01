// static/js/main.js

function filterTanksByAirport() {
  const airportSel = document.getElementById('airport');
  const sel = document.getElementById('tanque');
  if (!airportSel || !sel) return;

  const AIRPORT = (airportSel.value || '').toUpperCase();

  if (!AIRPORT) {
    // Sin aeropuerto: deshabilita y oculta opciones de tanques
    sel.disabled = true;
    sel.selectedIndex = 0; // placeholder
    for (let i = 1; i < sel.options.length; i++) {
      sel.options[i].hidden = true;
      sel.options[i].disabled = true;
    }
    return;
  }

  // Con aeropuerto: habilita y filtra opciones
  sel.disabled = false;
  for (let i = 1; i < sel.options.length; i++) {
    const opt = sel.options[i];
    const val = (opt.value || '').toUpperCase().trim();
    const txt = (opt.text  || '').toUpperCase().trim();
    const matches = val.startsWith(AIRPORT + '-') || txt.startsWith(AIRPORT + '-');
    opt.hidden   = !matches;
    opt.disabled = !matches;
  }

  // Si lo seleccionado no corresponde, vuelve al placeholder
  if (sel.selectedIndex > 0) {
    const cur = (sel.value || sel.options[sel.selectedIndex].text || '').toUpperCase();
    if (!cur.startsWith(AIRPORT + '-')) sel.selectedIndex = 0;
  }
}

document.addEventListener('DOMContentLoaded', function () {
  // ---- Forzar placeholder en aeropuerto al cargar (evita autocompletado del navegador) ----
  const airportSel = document.getElementById('airport');
  if (airportSel) {
    const hasPlaceholder = !!airportSel.querySelector('option[value=""]');
    if (hasPlaceholder) {
      airportSel.value = ''; // muestra "Selecciona aeropuerto"
    }
  }

  // ---- Filtrado por aeropuerto ----
  if (airportSel) {
    filterTanksByAirport();               // estado inicial
    airportSel.addEventListener('change', filterTanksByAirport);
  }

  // ---- Normalización del campo "volumen" ----
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

  // ---- Unidad (cm/mm) según tanque ----
  let unidadAltura = 'mm';
  const tanqueSel = document.getElementById('tanque');
  if (tanqueSel) {
    tanqueSel.addEventListener('change', function () {
      if ((this.value || '').toLowerCase().startsWith('smr')) {
        unidadAltura = 'cm';
      } else {
        unidadAltura = 'mm';
      }
    });
    // Estado inicial
    tanqueSel.dispatchEvent(new Event('change'));
  }

  // ---- Envío del formulario por fetch ----
  const form = document.getElementById('data-form');
  if (form) {
    form.onsubmit = async function (event) {
      event.preventDefault();

      const formData = new FormData(this);
      try {
        const response = await fetch(this.action, {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          // Intentamos leer JSON de error
          let msg = "Error desconocido";
          try {
            const err = await response.json();
            msg = err.error || msg;
          } catch (_) {}
          alert(msg);
          return;
        }

        const data = await response.json();

        // Pintar resultados
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
