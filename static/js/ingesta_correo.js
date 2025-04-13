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
            verificarCorreos();
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
    
    // Manejadores para la paginación dinámica
    const paginationLinks = document.querySelectorAll('#historial-pagination .page-link');
    if (paginationLinks.length > 0) {
        paginationLinks.forEach(function(link) {
            if (!link.parentElement.classList.contains('disabled') && link.getAttribute('href') !== '#') {
                link.addEventListener('click', function(e) {
                    if (this.getAttribute('href') !== '#') {
                        // Si se implementa la carga dinámica, descomentar esto:
                        /*
                        e.preventDefault();
                        const url = new URL(this.href);
                        const page = url.searchParams.get('page') || 1;
                        const perPage = url.searchParams.get('per_page') || 10;
                        cargarHistorialPaginado(page, perPage);
                        */
                    }
                });
            }
        });
    }
    
    /**
     * Ejecuta una verificación manual del buzón de correo
     */
    function verificarCorreos() {
        // Mostrar indicador de carga
        Swal.fire({
            title: 'Verificando correos...',
            text: 'Por favor espere',
            allowOutsideClick: false,
            allowEscapeKey: false,
            showConfirmButton: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });

        // Realizar la petición usando fetch
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
        .then(response => {
            if (response.status === 'success') {
                // Éxito total
                Swal.fire({
                    icon: 'success',
                    title: '¡Verificación completada!',
                    text: `Se procesaron ${response.correos_procesados} correos nuevos.`,
                    confirmButtonText: 'Aceptar'
                }).then(() => {
                    // Recargar la página para mostrar los nuevos correos
                    window.location.reload();
                });
            } else if (response.status === 'warning') {
                // Éxito parcial (con algunos errores)
                let mensaje = `Se procesaron ${response.correos_procesados} correos nuevos.`;
                if (response.errores && response.errores.length > 0) {
                    mensaje += '\n\nAdvertencias:\n' + response.errores.join('\n');
                }
                
                Swal.fire({
                    icon: 'warning',
                    title: 'Verificación completada con advertencias',
                    text: mensaje,
                    confirmButtonText: 'Aceptar'
                }).then(() => {
                    window.location.reload();
                });
            } else {
                // Error
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: response.message || 'Error al verificar correos',
                    confirmButtonText: 'Aceptar'
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Error al conectar con el servidor: ' + error.message,
                confirmButtonText: 'Aceptar'
            });
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
     * Función para cargar historial de forma dinámica
     * @param {number} page - Número de página a cargar
     * @param {number} perPage - Elementos por página
     */
    function cargarHistorialPaginado(page = 1, perPage = 10) {
        // Mostrar indicador de carga
        const tableBody = document.querySelector('#historial-tabla-body');
        if (tableBody) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center">
                        <div class="spinner-border spinner-border-sm text-primary" role="status">
                            <span class="visually-hidden">Cargando...</span>
                        </div>
                        <span class="ms-2">Cargando registros...</span>
                    </td>
                </tr>
            `;
        }
        
        // Actualizar URL sin recargar la página
        const url = new URL(window.location);
        url.searchParams.set('page', page);
        url.searchParams.set('per_page', perPage);
        window.history.pushState({}, '', url);
        
        // Realizar solicitud AJAX
        fetch(`/ingesta-correo/api/logs?page=${page}&per_page=${perPage}`, {
            method: 'GET',
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
            if (data.success) {
                // Actualizar tabla con los logs
                actualizarTablaHistorial(data.logs);
                
                // Actualizar paginación
                actualizarPaginacion(data.pagination);
            } else {
                showToast(data.message || 'Error al cargar historial', 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error al cargar historial: ' + error.message, 'danger');
            
            // Mostrar mensaje de error en la tabla
            if (tableBody) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="4" class="text-center text-danger">
                            <i class="bi bi-exclamation-triangle-fill me-2"></i>
                            Error al cargar los registros. Por favor, intente nuevamente.
                        </td>
                    </tr>
                `;
            }
        });
    }
    
    /**
     * Actualiza la tabla de historial con los datos recibidos
     * @param {Array} logs - Array de registros de actividad
     */
    function actualizarTablaHistorial(logs) {
        const tableBody = document.querySelector('#historial-tabla-body');
        if (!tableBody) return;
        
        if (logs.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center">No hay registros de actividad disponibles.</td>
                </tr>
            `;
            return;
        }
        
        let htmlContent = '';
        
        logs.forEach(log => {
            let estadoBadge = '';
            if (log.estado === 'procesado' || log.estado === 'éxito') {
                estadoBadge = '<span class="badge bg-success">Procesado</span>';
            } else if (log.estado === 'pendiente') {
                estadoBadge = '<span class="badge bg-warning">Pendiente</span>';
            } else if (log.estado === 'ignorado') {
                estadoBadge = '<span class="badge bg-secondary">Ignorado</span>';
            } else if (log.estado === 'informativo') {
                estadoBadge = '<span class="badge bg-info">Informativo</span>';
            } else {
                estadoBadge = '<span class="badge bg-danger">Error</span>';
            }
            
            htmlContent += `
                <tr>
                    <td>${log.fecha}</td>
                    <td>${log.evento}</td>
                    <td>${log.detalles}</td>
                    <td>${estadoBadge}</td>
                </tr>
            `;
        });
        
        tableBody.innerHTML = htmlContent;
    }
    
    /**
     * Actualiza la paginación con los datos recibidos
     * @param {Object} pagination - Objeto con la información de paginación
     */
    function actualizarPaginacion(pagination) {
        const paginationContainer = document.querySelector('#historial-pagination');
        if (!paginationContainer) return;
        
        if (pagination.pages <= 1) {
            paginationContainer.innerHTML = '';
            return;
        }
        
        let htmlContent = `
            <ul class="pagination justify-content-center">
                <li class="page-item ${!pagination.has_prev ? 'disabled' : ''}">
                    <a class="page-link" href="javascript:void(0)" onclick="${pagination.has_prev ? `cargarHistorialPaginado(${pagination.prev_num})` : ''}">Anterior</a>
                </li>
        `;
        
        // Lógica para mostrar páginas (similar a Jinja2's pagination.iter_pages)
        const leftEdge = 1;
        const rightEdge = 1;
        const leftCurrent = 1;
        const rightCurrent = 2;
        
        let lastPage = null;
        
        for (let i = 1; i <= pagination.pages; i++) {
            if (i <= leftEdge || 
                i > pagination.pages - rightEdge || 
                (i >= pagination.page - leftCurrent && i <= pagination.page + rightCurrent)) {
                if (lastPage && i > lastPage + 1) {
                    htmlContent += `
                        <li class="page-item disabled">
                            <span class="page-link">...</span>
                        </li>
                    `;
                }
                
                htmlContent += `
                    <li class="page-item ${i === pagination.page ? 'active' : ''}">
                        <a class="page-link" href="javascript:void(0)" onclick="cargarHistorialPaginado(${i})">${i}</a>
                    </li>
                `;
                
                lastPage = i;
            }
        }
        
        htmlContent += `
                <li class="page-item ${!pagination.has_next ? 'disabled' : ''}">
                    <a class="page-link" href="javascript:void(0)" onclick="${pagination.has_next ? `cargarHistorialPaginado(${pagination.next_num})` : ''}">Siguiente</a>
                </li>
            </ul>
        `;
        
        paginationContainer.innerHTML = htmlContent;
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
    if (typeof $.fn !== 'undefined' && typeof $.fn.DataTable !== 'undefined') {
        $('.table-datatable').DataTable({
            language: {
                url: '//cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json'
            },
            pageLength: 10,
            responsive: true
        });
    }
    
    // Inicializar paginación dinámica si existe el contenedor
    // Descomentar para habilitar carga dinámica
    /*
    const historialContainer = document.querySelector('#historial-tabla-body');
    if (historialContainer) {
        // Extraer parámetros de URL actuales (si existen)
        const urlParams = new URLSearchParams(window.location.search);
        const currentPage = parseInt(urlParams.get('page') || '1');
        const perPage = parseInt(urlParams.get('per_page') || '10');
        
        // Hacer disponible la función globalmente
        window.cargarHistorialPaginado = cargarHistorialPaginado;
        
        // Opcionalmente cargar primera página con AJAX
        // cargarHistorialPaginado(currentPage, perPage);
    }
    */
    
    // Escuchar clic en el botón de descarga de log
    const btnDescargarLog = document.querySelector('a[href*="descargar-log"]');
    if (btnDescargarLog) {
        btnDescargarLog.addEventListener('click', function(e) {
            // Mostrar mensaje informativo
            showToast('Preparando descarga del historial...', 'info');
        });
    }
});