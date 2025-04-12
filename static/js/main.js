// Funcionalidades básicas para Gestor de Glosas Pro

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

// Función para simular alertas en botones del detalle de glosa
function showAlert(message) {
    alert(message);
    // En una aplicación real, aquí iría código para mostrar un toast o una notificación más elegante
}

    // Inicializar dropdowns de Bootstrap
    var dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'))
    var dropdownList = dropdownElementList.map(function (dropdownToggleEl) {
        return new bootstrap.Dropdown(dropdownToggleEl)
    });

    // Manejar el cambio en los filtros de la bandeja de glosas
    const estadoSelect = document.getElementById('estado');
    const aseguradoraSelect = document.getElementById('aseguradora');
    
    if (estadoSelect && aseguradoraSelect) {
        estadoSelect.addEventListener('change', function() {
            console.log('Filtro de estado cambiado:', this.value);
            // Aquí iría la lógica para filtrar por estado (en un backend real)
        });
        
        aseguradoraSelect.addEventListener('change', function() {
            console.log('Filtro de aseguradora cambiado:', this.value);
            // Aquí iría la lógica para filtrar por aseguradora (en un backend real)
        });
    }

    // Funcionalidad para el botón de limpiar filtros
    const limpiarBtn = document.querySelector('button.btn-outline-secondary');
    if (limpiarBtn) {
        limpiarBtn.addEventListener('click', function() {
            // Resetear todos los filtros
            const formControls = document.querySelectorAll('.form-select, .form-control');
            formControls.forEach(control => {
                if (control.tagName === 'SELECT') {
                    control.selectedIndex = 0;
                } else {
                    control.value = '';
                }
            });
            console.log('Filtros limpiados');
        });
    }

    // Animación para las tarjetas del dashboard
    const dashboardCards = document.querySelectorAll('.card');
    if (dashboardCards.length > 0) {
        dashboardCards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-5px)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
            });
        });
    }

    // Validación simple para los campos de decisión y justificación
    const decisionRadios = document.querySelectorAll('input[type="radio"][name^="decision_"]');
    const justificacionTextareas = document.querySelectorAll('textarea[id^="justificacion_"]');
    
    if (decisionRadios.length > 0 && justificacionTextareas.length > 0) {
        decisionRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                const itemId = this.name.split('_')[1];
                const justificacionTextarea = document.getElementById('justificacion_' + itemId);
                
                // Si se selecciona "No Acepta", la justificación es obligatoria
                if (this.value === 'No Acepta') {
                    justificacionTextarea.setAttribute('required', 'required');
                    justificacionTextarea.classList.add('border-warning');
                    // Placeholder más explícito
                    justificacionTextarea.placeholder = 'Justificación obligatoria para No Aceptar...';
                } else {
                    justificacionTextarea.removeAttribute('required');
                    justificacionTextarea.classList.remove('border-warning');
                    justificacionTextarea.placeholder = 'Escriba su justificación aquí...';
                }
            });
        });
    }
    
    // Funcionalidad para recordar usuario (login)
    const rememberCheckbox = document.getElementById('inputRememberPassword');
    const emailInput = document.getElementById('inputEmail');
    
    if (rememberCheckbox && emailInput) {
        // Cargar email guardado si existe
        const savedEmail = localStorage.getItem('rememberedEmail');
        if (savedEmail) {
            emailInput.value = savedEmail;
            rememberCheckbox.checked = true;
        }
        
        // Guardar email al enviar formulario si checkbox está marcado
        const loginForm = document.querySelector('form[action*="login"]');
        if (loginForm) {
            loginForm.addEventListener('submit', function() {
                if (rememberCheckbox.checked) {
                    localStorage.setItem('rememberedEmail', emailInput.value);
                } else {
                    localStorage.removeItem('rememberedEmail');
                }
            });
        }
    }
});