// admin.js

function volver() {
    window.history.back();
}

document.addEventListener("DOMContentLoaded", function () {
    // Selecciona los elementos clickeables que actúan como toggles (.menu-header)
    document.querySelectorAll(".sidebar .menu-item > .menu-header").forEach((header, index) => {
        const submenu = header.nextElementSibling; // El submenu es el siguiente hermano del header
        const arrowIcon = header.querySelector('.caret-icon'); // Encuentra el icono de flecha dentro del header

        // Asegúrate de que realmente hay un submenu y una flecha para este header
        if (submenu && submenu.classList.contains('submenu') && arrowIcon) {

             // Recuperar estado del localStorage
             const isInitiallyOpen = localStorage.getItem(`menu_open_${index}`) === "true";

             // Aplica el estado inicial
             submenu.style.display = isInitiallyOpen ? "block" : "none";
             // Aplica la clase 'open' al header si el submenu está abierto
             if (isInitiallyOpen) {
                 header.classList.add("open");
                  // Rota la flecha si el menú está abierto
                 arrowIcon.style.transform = "rotate(180deg)";
             } else {
                 // Asegura que la flecha esté en la posición inicial si el menú está cerrado
                 arrowIcon.style.transform = "rotate(0deg)";
             }


            // Añade el evento click al header
            header.addEventListener("click", function () {
                const currentlyOpen = submenu.style.display === "block";

                // Alterna la visibilidad del submenu
                submenu.style.display = currentlyOpen ? "none" : "block";

                // Alterna la clase 'open' en el header
                this.classList.toggle("open"); // toggle sin segundo argumento alterna basado en la existencia

                // Rota el icono de flecha
                 arrowIcon.style.transform = currentlyOpen ? "rotate(0deg)" : "rotate(180deg)";

                // Guarda el estado en localStorage
                localStorage.setItem(`menu_open_${index}`, !currentlyOpen);
            });
        } else {
             // Si no hay submenu o flecha (ej: link directo como Configuracion, Logout, Empresas),
             // no hagas el header clickeable o quita la flecha si no la ocultaste con CSS
             if (header) { // Asegurarse de que header existe antes de modificarlo
                 header.style.cursor = 'default'; // Opcional: cambiar cursor
                 if(arrowIcon) {
                      arrowIcon.style.display = 'none'; // Ocultar flecha si no hay submenu
                 }
             }
        }
    });

    // --- Lógica para los botones Claro/Oscuro (Opcional, requiere vista para guardar) ---
    // Si quieres que estos botones guarden la preferencia de tema persistentemente,
    // DEBES añadir la lógica de manejo de peticiones POST con JSON a tu vista `configuracion_admin_view`
    // como se mencionó anteriormente. Este JS asume que enviarás un POST a la URL de configuración.

    document.querySelectorAll('.theme-toggle-button').forEach(button => {
        button.addEventListener('click', function() {
            const themeType = this.getAttribute('data-theme'); // 'light' or 'dark'
            let backgroundThemeClass, sidebarThemeClass;

            // Define las clases CSS a aplicar/guardar para cada tipo de tema
            if (themeType === 'light') {
                 backgroundThemeClass = 'bg-light'; // Nombre de la clase CSS para tema claro de fondo
                 sidebarThemeClass = 'bar-clean-white'; // Nombre de la clase CSS para tema claro de sidebar
                 // Puedes ajustar estos nombres de clase si tienes temas claros/oscuros específicos
            } else { // dark
                 backgroundThemeClass = 'bg-dark'; // Nombre de la clase CSS para tema oscuro de fondo
                 sidebarThemeClass = 'bar-midnight'; // Nombre de la clase CSS para tema oscuro de sidebar
            }

            // Aplicar las clases CSS al body inmediatamente en el cliente para feedback visual
            // Esto es temporal hasta que la página se recargue con las clases persistidas por Django
            document.body.classList.remove('bg-light', 'bg-dark', 'bg-sky-light', 'bg-sunset-soft', 'bg-forest-deep', 'bg-sandstone-warm', 'bg-cool-grey', 'bg-teal-fresh',
                                          'bar-darkblue', 'bar-midnight', 'bar-lightgrey', 'bar-lila-elegant', 'bar-gold-warm', 'bar-cyan-vibrant', 'bar-clean-white', 'bar-maroon-bold', 'bar-mint-pastel'); // Remueve todas las posibles clases de tema
            document.body.classList.add(backgroundThemeClass, sidebarThemeClass); // Añade las nuevas clases


            // Opcional: Enviar la preferencia de tema al servidor para persistirla
            // Esto requiere modificar la vista `configuracion_admin_view` para manejar peticiones AJAX/JSON
            const csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value; // Obtén el token CSRF

             fetch("{% url 'configuracion_admin' %}", { // Asegúrate que esta URL es correcta
                 method: 'POST',
                 headers: {
                     'Content-Type': 'application/json',
                     'X-CSRFToken': csrftoken,
                      'X-Requested-With': 'XMLHttpRequest' // Indica que es una petición AJAX
                 },
                 body: JSON.stringify({
                     background_theme: backgroundThemeClass,
                     sidebar_theme: sidebarThemeClass,
                     // Puedes añadir un flag si la vista necesita saber que es un "toggle rápido"
                     is_quick_toggle: true
                 })
             })
             .then(response => response.json())
             .then(data => {
                 if (data.success) {
                     console.log('Preferencia de tema guardada en el servidor.');
                     // La recarga de página no es estrictamente necesaria aquí si aplicas las clases cliente-side,
                     // pero garantiza que Django renderiza con el tema persistido.
                     // window.location.reload(); // Opcional: recargar para confirmar
                 } else {
                     console.error('Error al guardar la preferencia de tema:', data.error);
                     // Manejar error en la UI si es necesario
                 }
             })
             .catch(error => {
                 console.error('Error en la petición AJAX para guardar tema:', error);
                 // Manejar error de red/servidor
             });

        });
    });

    // Si quieres que la selección de los SWATCHES en la página de configuración
    // también cambie los inputs ocultos/radios y aplique la clase 'selected',
    // el script para swatches en configuracion.html (dentro de block extra_js)
    // debe seguir siendo necesario.
});