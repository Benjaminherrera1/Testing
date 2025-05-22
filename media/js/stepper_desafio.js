document.addEventListener('DOMContentLoaded', () => {
  // Leer paso actual desde el atributo en body
  let pasoActual = parseInt(document.body.getAttribute('data-paso-actual')) || 1;

  const steps = document.querySelectorAll('.step-h');
  const lines = document.querySelectorAll('.line-h');

  const maxPaso = steps.length;

  // Limitar paso actual dentro del rango válido
  pasoActual = Math.min(Math.max(pasoActual, 1), maxPaso);

  function actualizarStepper(paso) {
    steps.forEach((step, idx) => {
      if (idx < paso) {
        step.classList.add('active-h');
      } else {
        step.classList.remove('active-h');
      }
    });

    lines.forEach((line, idx) => {
      if (idx < paso - 1) {
        line.classList.add('active-h');
      } else {
        line.classList.remove('active-h');
      }
    });
  }

  actualizarStepper(pasoActual);

  // Opcional: si tienes botones para cambiar pasos, actualizar comportamiento
  const btnAnterior = document.querySelector('.btn-anterior');
  const btnSiguiente = document.querySelector('.btn-siguiente');

  if (btnAnterior && btnSiguiente) {
    btnAnterior.addEventListener('click', () => {
      if (pasoActual > 1) {
        pasoActual--;
        actualizarStepper(pasoActual);
        actualizarFormulario(pasoActual);
      }
    });

    btnSiguiente.addEventListener('click', () => {
      if (pasoActual < maxPaso) {
        pasoActual++;
        actualizarStepper(pasoActual);
        actualizarFormulario(pasoActual);
      }
    });
  }

  // Mostrar sólo el formulario del paso actual
  function actualizarFormulario(paso) {
    const formularios = document.querySelectorAll('.formulario-paso');
    formularios.forEach((form, idx) => {
      form.style.display = (idx === paso - 1) ? 'block' : 'none';
    });
  }

  actualizarFormulario(pasoActual);

  console.log('Stepper JS cargado y ejecutándose');

});
