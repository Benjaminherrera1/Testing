// admin.js

function volver() {
    window.history.back();
}

document.addEventListener("DOMContentLoaded", function () {
    // Selecciona los elementos clickeables que actúan como toggles
    document.querySelectorAll(".sidebar .menu-header").forEach((header, index) => {
        const submenu = header.nextElementSibling; // El submenu es el siguiente hermano

        // Asegúrate de que realmente hay un submenu
        if (submenu && submenu.classList.contains('submenu')) {
             const arrowIcon = header.querySelector('.caret-icon'); // Encuentra el icono de flecha dentro del header

             // Recuperar estado del localStorage
             const isInitiallyOpen = localStorage.getItem(`menu_open_${index}`) === "true";

            // Aplica el estado inicial
            submenu.style.display = isInitiallyOpen ? "block" : "none";
            // Aplica la clase 'open' al header si el submenu está abierto
            if (isInitiallyOpen) {
                header.classList.add("open");
                 // Actualiza la flecha si el menú está abierto (rota 180deg)
                if (arrowIcon) {
                    arrowIcon.style.transform = "rotate(180deg)";
                }
            }


            // Añade el evento click al header
            header.addEventListener("click", function () {
                const currentlyOpen = submenu.style.display === "block";

                // Alterna la visibilidad del submenu
                submenu.style.display = currentlyOpen ? "none" : "block";

                // Alterna la clase 'open' en el header
                this.classList.toggle("open", !currentlyOpen); // Añade 'open' si NO estaba abierto, quita si SÍ estaba abierto

                // Rota el icono de flecha si existe
                if (arrowIcon) {
                    arrowIcon.style.transform = currentlyOpen ? "rotate(0deg)" : "rotate(180deg)";
                }

                // Guarda el estado en localStorage
                localStorage.setItem(`menu_open_${index}`, !currentlyOpen);
            });
        } else {
             // Si no hay submenu, no hagas el header clickeable o quita la flecha
             header.style.cursor = 'default';
             const arrowIcon = header.querySelector('.caret-icon');
             if(arrowIcon) arrowIcon.style.display = 'none';
        }
    });


    // --- Lógica para los botones Claro/Oscuro ---
    // Opcion 1: Solo cambian clases CSS en el cliente (no persistente sin guardar)
    // Opcion 2: Envían una solicitud para guardar la preferencia de tema (persistente)
    // Optemos por la opción 2 (persistente) usando Fetch API

    document.querySelectorAll('.theme-toggle-button').forEach(button => {
        button.addEventListener('click', function() {
            const themeType = this.getAttribute('data-theme'); // 'light' or 'dark'
            let backgroundTheme, sidebarTheme;

            if (themeType === 'light') {
                 backgroundTheme = 'bg-light'; // O el nombre de tu tema claro de fondo
                 sidebarTheme = 'bar-clean-white'; // O el nombre de tu tema claro de sidebar
            } else { // dark
                 backgroundTheme = 'bg-dark'; // O el nombre de tu tema oscuro de fondo
                 sidebarTheme = 'bar-midnight'; // O el nombre de tu tema oscuro de sidebar
            }

            // Obtener token CSRF
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value; // Asegúrate de tener {% csrf_token %} en tu base.html o form

            fetch('/admin/configuracion/', { // Envía a la vista de configuración
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                     'X-Requested-With': 'XMLHttpRequest' // Para que la vista sepa que es AJAX
                },
                body: JSON.stringify({
                    // Puedes enviar solo los nombres de los temas
                    // O puedes enviar un flag indicando que es un toggle rápido
                    quick_theme_toggle: true,
                    background_theme: backgroundTheme,
                    sidebar_theme: sidebarTheme
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Aplica las clases CSS al body inmediatamente en el cliente
                    // Opcional: podrías recargar la página para que Django aplique las clases
                    // window.location.reload();
                    document.body.className = ''; // Limpia clases existentes
                    document.body.classList.add(backgroundTheme, sidebarTheme);
                    console.log('Tema actualizado y guardado');
                    // Opcional: Mostrar un pequeño mensaje de éxito en la UI
                } else {
                    console.error('Error al guardar el tema:', data.error);
                    // Opcional: Mostrar un mensaje de error
                }
            })
            .catch(error => {
                console.error('Error en la solicitud de tema:', error);
                // Opcional: Mostrar un mensaje de error de conexión/servidor
            });
        });
    });
     // NOTA: Para que la lógica de los botones Claro/Oscuro funcione enviando JSON,
     // DEBES modificar la vista `configuracion_admin_view` para aceptar y procesar
     // peticiones POST con Content-Type 'application/json' además de 'multipart/form-data'.
     // O crear una vista separada solo para el toggle rápido de tema.
     // La forma más simple es que estos botones *sólo* cambien las clases CSS cliente-side
     // y la persistencia se haga *solo* desde la página de configuración principal.
     // Si quieres que sean persistentes, modifica la vista.
});