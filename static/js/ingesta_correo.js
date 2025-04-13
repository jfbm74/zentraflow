/**
 * JavaScript para el módulo de Ingesta de Correo
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Botón "Verificar ahora"
    const btnVerificarAhora = document.getElementById('btn-verificar-ahora');
    if (btnVerificarAhora) {
        btnVerificarAhora.addEventListener('click', function() {
            verificarAhora();
        });
    }
    
    // Botón "Toggle servicio" (Pausar/Reanudar)
    const btnToggleServicio = document.getElementById('btn-toggle-servicio');
    if (btnToggleServicio) {
        btnToggleServicio.addEventListener('click', function() {
            toggleServicio();
        });
    }
    
    // Botón "Nueva Regla"
    const btnNuevaRegla = document.querySelector('button[data-bs-target="#nuevaReglaModal"]');
    if (btnNuevaRegla) {
        const btnGuardarRegla = document.querySelector('#nuevaReglaModal button.btn-primary');
        if (btnGuardarRegla) {
            btnGuardarRegla.addEventListener('click', function() {
                guardarRegla();
            });
        }
    }
    
    /**
     * Ejecuta una verificación manual del buzón de correo
     */
    function verificarAhora() {
        // Desactivar botón y mostrar spinner
        btnVerificarAhora.disabled = true;
        const textoOriginal = btnVerificarAhora.innerHTML;
        btnVerificarAhora.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Verificando...';
        
        // Modal para mostrar resultados
        let verificacionModal = new bootstrap.Modal(document.getElementById('verificacionModal'));
        if (verificacionModal) {
            verificacionModal.show();
            document.getElementById('verificacionModalBody').innerHTML = `
                <div class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Cargando...</span>
                    </div>
                    <p class="mt-2">Verificando buzón de correo...</p>
                </div>
            `;
        }
        
        // Enviar solicitud POST
        fetch('/ingesta-correo/verificar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la solicitud: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            // Restaurar botón
            btnVerificarAhora.disabled = false;
            btnVerificarAhora.innerHTML = textoOriginal;
            
            // Mostrar resultado en modal
            if (verificacionModal) {
                if (data.success) {
                    document.getElementById('verificacionModalBody').innerHTML = `
                        <div class="text-center">
                            <i class="bi bi-check-circle-fill text-success display-1"></i>
                            <h4 class="mt-3">Verificación Completada</h4>
                            <p class="lead">${data.message}</p>
                            <div class="alert alert-info mt-3">
                                La página se recargará en unos segundos para mostrar los resultados...
                            </div>
                        </div>
                    `;
                    // Recargar la página después de 3 segundos
                    setTimeout(() => {
                        window.location.reload();
                    }, 3000);
                } else {
                    document.getElementById('verificacionModalBody').innerHTML = `
                        <div class="text-center">
                            <i class="bi bi-exclamation-triangle-fill text-danger display-1"></i>
                            <h4 class="mt-3">Error</h4>
                            <p class="lead">${data.message}</p>
                        </div>
                    `;
                }
            } else {
                // Mostrar mensaje en caso de que no exista el modal
                if (data.success) {
                    showToast(data.message, 'success');
                    setTimeout(() => window.location.reload(), 2000);
                } else {
                    showToast(data.message, 'danger');
                }
            }
        })
        .catch(error => {
            // Restaurar botón
            btnVerificarAhora.disabled = false;
            btnVerificarAhora.innerHTML = textoOriginal;
            
            // Mostrar error
            console.error('Error:', error);
            showToast('Error al realizar la verificación: ' + error.message, 'danger');
            
            // Actualizar modal si existe
            if (verificacionModal) {
                document.getElementById('verificacionModalBody').innerHTML = `
                    <div class="text-center">
                        <i class="bi bi-exclamation-triangle-fill text-danger display-1"></i>
                        <h4 class="mt-3">Error</h4>
                        <p class="lead">No se pudo realizar la verificación: ${error.message}</p>
                    </div>
                `;
            }
        });
    }
    
    /**
     * Activa o desactiva el servicio de ingesta de correo
     */
    function toggleServicio() {
        // Determinar el estado actual
        const isActive = btnToggleServicio.classList.contains('btn-danger');
        const newState = !isActive;
        
        // Desactivar botón y mostrar spinner
        btnToggleServicio.disabled = true;
        const textoOriginal = btnToggleServicio.innerHTML;
        btnToggleServicio.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Actualizando...';
        
        // Enviar solicitud POST
        fetch('/ingesta-correo/toggle-servicio', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ active: newState }),
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la solicitud: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Mostrar mensaje y recargar página
                const mensaje = data.estado ? 'Servicio activado correctamente' : 'Servicio pausado correctamente';
                showToast(mensaje, 'success');
                setTimeout(() => window.location.reload(), 1500);
            } else {
                // Restaurar botón
                btnToggleServicio.disabled = false;
                btnToggleServicio.innerHTML = textoOriginal;
                
                // Mostrar error
                showToast(data.message, 'danger');
            }
        })
        .catch(error => {
            // Restaurar botón
            btnToggleServicio.disabled = false;
            btnToggleServicio.innerHTML = textoOriginal;
            
            // Mostrar error
            console.error('Error:', error);
            showToast('Error al cambiar el estado del servicio: ' + error.message, 'danger');
        });
    }
    
    /**
     * Guarda una nueva regla de filtrado
     */
    function guardarRegla() {
        // Obtener datos del formulario
        const nombreRegla = document.getElementById('nombreRegla').value;
        const condicionRegla = document.getElementById('condicionRegla').value;
        const valorRegla = document.getElementById('valorRegla').value;
        const accionRegla = document.getElementById('accionRegla').value;
        const estadoRegla = document.getElementById('estadoRegla').checked;
        
        // Validar datos
        if (!nombreRegla || !valorRegla) {
            showToast('Por favor complete los campos obligatorios', 'warning');
            return;
        }
        
        // Desactivar botón y mostrar spinner
        const btnGuardarRegla = document.querySelector('#nuevaReglaModal button.btn-primary');
        btnGuardarRegla.disabled = true;
        const textoOriginal = btnGuardarRegla.innerHTML;
        btnGuardarRegla.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Guardando...';
        
        // Construir objeto de datos
        const data = {
            nombre: nombreRegla,
            condicion_tipo: condicionRegla,
            condicion_operador: 'contiene', // Por ahora solo "contiene" como operador
            condicion_valor: valorRegla,
            accion: accionRegla,
            estado: estadoRegla
        };
        
        // Enviar solicitud POST
        fetch('/ingesta-correo/reglas', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(data),
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la solicitud: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            // Restaurar botón
            btnGuardarRegla.disabled = false;
            btnGuardarRegla.innerHTML = textoOriginal;
            
            if (data.success) {
                // Cerrar modal
                const modalElement = document.getElementById('nuevaReglaModal');
                const modal = bootstrap.Modal.getInstance(modalElement);
                modal.hide();
                
                // Mostrar mensaje
                showToast('Regla creada correctamente', 'success');
                
                // Recargar página para mostrar la nueva regla
                setTimeout(() => window.location.reload(), 1500);
            } else {
                // Mostrar error
                showToast(data.message, 'danger');
            }
        })
        .catch(error => {
            // Restaurar botón
            btnGuardarRegla.disabled = false;
            btnGuardarRegla.innerHTML = textoOriginal;
            
            // Mostrar error
            console.error('Error:', error);
            showToast('Error al guardar la regla: ' + error.message, 'danger');
        });
    }
    
    /**
     * Función para mostrar mensajes toast si no está definida globalmente
     */
    if (typeof showToast !== 'function') {
        window.showToast = function(message, type = 'success') {
            // Verificar si existe el contenedor de toasts
            let toastContainer = document.getElementById('toast-container');
            if (!toastContainer) {
                toastContainer = document.createElement('div');
                toastContainer.id = 'toast-container';
                toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
                toastContainer.style.zIndex = '11';
                document.body.appendChild(toastContainer);
            }
            
            // Crear elemento toast
            const toastId = 'toast-' + Date.now();
            const toast = document.createElement('div');
            toast.id = toastId;
            toast.className = `toast align-items-center text-white bg-${type} border-0`;
            toast.role = 'alert';
            toast.setAttribute('aria-live', 'assertive');
            toast.setAttribute('aria-atomic', 'true');
            
            // Contenido del toast
            toast.innerHTML = `
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            `;
            
            // Agregar al contenedor
            toastContainer.appendChild(toast);
            
            // Crear instancia y mostrar
            const toastInstance = new bootstrap.Toast(toast, {
                autohide: true,
                delay: 3000
            });
            toastInstance.show();
            
            // Eliminar del DOM al ocultarse
            toast.addEventListener('hidden.bs.toast', function() {
                this.remove();
            });
        };
    }
    
    // Inicializar DataTable para las tablas si existe la biblioteca
    if (typeof $.fn.DataTable !== 'undefined') {
        $('.table-datatable').DataTable({
            language: {
                url: '//cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json'
            },
            pageLength: 10,
            responsive: true
        });
    }
});