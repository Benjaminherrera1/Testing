// Función para actualizar el stepper basado en el paso actual
function actualizarStepper(pasoActual) {
    // Seleccionar todos los elementos del stepper
    const steps = document.querySelectorAll('.step-h');
    const lines = document.querySelectorAll('.line-h');
    
    // Iterar sobre cada paso y actualizar su estado
    steps.forEach((step, index) => {
        // El índice es 0-based, pero nuestros pasos son 1-based
        const stepNumber = index + 1;
        
        if (stepNumber < pasoActual) {
            // Pasos anteriores: completados (naranja)
            step.classList.add('active-h');
            
            // Si hay una línea después de este paso, también la marcamos como completada
            if (index < lines.length) {
                lines[index].style.backgroundColor = '#FF7900';
            }
        } else if (stepNumber === pasoActual) {
            // Paso actual: activo (naranja)
            step.classList.add('active-h');
            
            // La línea después del paso actual no está completada
            if (index < lines.length) {
                lines[index].style.backgroundColor = '#FFFFFF';
            }
        } else {
            // Pasos futuros: inactivos (blanco)
            step.classList.remove('active-h');
            
            // La línea después de pasos futuros tampoco está completada
            if (index < lines.length) {
                lines[index].style.backgroundColor = '#FFFFFF';
            }
        }
    });
}

// Ejecutar cuando el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    // Obtener el paso actual de la plantilla
    const pasoElement = document.querySelector('body');
    const pasoActual = pasoElement && pasoElement.getAttribute('data-paso-actual');
    
    // Si no hay atributo data-paso-actual, intentamos obtenerlo de otro modo
    if (!pasoActual) {
        // Buscar el paso actual en los elementos con clase 'step-h'
        const currentForm = document.location.pathname;
        let currentStep = 1;
        
        if (currentForm.includes('contacto_i')) {
            currentStep = 2;
        } else if (currentForm.includes('iniciativa_i') && !currentForm.includes('parte2')) {
            currentStep = 3;
        } else if (currentForm.includes('parte2')) {
            currentStep = 4;
        }
        
        // Actualizar el stepper con el paso detectado
        actualizarStepper(currentStep);
    } else {
        // Si encontramos un valor en data-paso-actual, lo usamos
        actualizarStepper(parseInt(pasoActual));
    }
    
    // Añadir validación para el captcha en el formulario de la parte 2
    const formularioIniciativaParte2 = document.getElementById('formularioIniciativaParte2');
    if (formularioIniciativaParte2) {
        formularioIniciativaParte2.addEventListener('submit', function(event) {
            // Verificar si el captcha ha sido completado
            const recaptchaResponse = grecaptcha.getResponse();
            
            if (recaptchaResponse.length === 0) {
                // El captcha no ha sido completado
                event.preventDefault();
                document.getElementById('captcha-error').style.display = 'block';
            } else {
                // El captcha ha sido completado correctamente
                document.getElementById('captcha-error').style.display = 'none';
            }
            
            // Validar que al menos un checkbox esté seleccionado
            const checkboxes = document.querySelectorAll('input[type="checkbox"][name="origen"]:checked');
            if (checkboxes.length === 0) {
                event.preventDefault();
                alert('Por favor, selecciona cómo te enteraste de NODO Centro de Innovación OMCPL');
            }
        });
    }
});