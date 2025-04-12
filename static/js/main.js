// Funcionalidades para ZentraFlow - Zentratek

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Inicializar dropdowns de Bootstrap
    var dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'));
    var dropdownList = dropdownElementList.map(function (dropdownToggleEl) {
        return new bootstrap.Dropdown(dropdownToggleEl);
    });

    // Función para mostrar alertas con Toast en lugar de alert()
    window.showToast = function(message, type = 'success') {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            // Crear el contenedor de toasts si no existe
            const container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(container);
        }
        
        // Crear el elemento toast
        const toastEl = document.createElement('div');
        toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');
        
        // Contenido del toast
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        // Añadir al contenedor
        document.getElementById('toast-container').appendChild(toastEl);
        
        // Inicializar y mostrar
        const toast = new bootstrap.Toast(toastEl, {
            autohide: true,
            delay: 3000
        });
        toast.show();
        
        // Eliminar el elemento cuando se oculte
        toastEl.addEventListener('hidden.bs.toast', function() {
            toastEl.remove();
        });
    };

    // Función para simular alertas en botones del detalle de glosa
    window.showAlert = function(message) {
        showToast(message);
    };

    // Manejar el cambio en los filtros de la bandeja de glosas
    const estadoSelect = document.getElementById('estado');
    const aseguradoraSelect = document.getElementById('aseguradora');
    
    if (estadoSelect && aseguradoraSelect) {
        estadoSelect.addEventListener('change', function() {
            console.log('Filtro de estado cambiado:', this.value);
            // Aquí iría la lógica para filtrar por estado (en un backend real)
            showToast(`Filtro aplicado: Estado = ${this.value || 'Todos'}`, 'info');
        });
        
        aseguradoraSelect.addEventListener('change', function() {
            console.log('Filtro de aseguradora cambiado:', this.value);
            // Aquí iría la lógica para filtrar por aseguradora (en un backend real)
            showToast(`Filtro aplicado: Aseguradora = ${this.value || 'Todas'}`, 'info');
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
            showToast('Filtros limpiados', 'info');
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

    // Validación para los campos de decisión y justificación
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

    // Simulación de actividad en los módulos (solo para demo)
    const simulateModuleActivity = function() {
        const progressBars = document.querySelectorAll('.progress-bar');
        if (progressBars.length > 0) {
            progressBars.forEach(bar => {
                const currentWidth = parseInt(bar.style.width);
                // Simular fluctuación aleatoria
                const fluctuation = Math.floor(Math.random() * 5) - 2; // Entre -2% y +2%
                let newWidth = currentWidth + fluctuation;
                if (newWidth < 10) newWidth = 10;
                if (newWidth > 100) newWidth = 100;
                bar.style.width = newWidth + '%';
                bar.parentElement.previousElementSibling.textContent = newWidth + '%';
            });
        }
    };
    
    // Actualizar simulación cada 30 segundos
    setInterval(simulateModuleActivity, 30000);
    
    // Crear toast container al inicio
    const toastContainer = document.createElement('div');
    toastContainer.id = 'toast-container';
    toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
    document.body.appendChild(toastContainer);
});