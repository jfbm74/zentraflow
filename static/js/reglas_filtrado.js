/**
 * JavaScript para gestionar las reglas de filtrado
 */

document.addEventListener('DOMContentLoaded', function() {
    // Referencias a elementos del DOM
    const btnNuevaRegla = document.getElementById('btn-nueva-regla');
    const btnGuardarRegla = document.getElementById('btn-guardar-regla');
    const formNuevaRegla = document.getElementById('form-nueva-regla');
    const modalTitulo = document.getElementById('nuevaReglaModalLabel');
    const nuevaReglaModal = document.getElementById('nuevaReglaModal') ? new bootstrap.Modal(document.getElementById('nuevaReglaModal')) : null;
    
    // Botones de edición
    const botonesEditar = document.querySelectorAll('.btn-editar-regla');
    
    // Botones de eliminación
    const botonesEliminar = document.querySelectorAll('.btn-eliminar-regla');
    
    // Switches de estado
    const switchesEstado = document.querySelectorAll('.switch-estado-regla');
    
    // Variables de estado
    let modoEdicion = false;
    let reglaActualId = null;
    
    // Modal de confirmación para eliminar
    const confirmarEliminarModal = document.getElementById('confirmarEliminarModal');
    const modalConfirmEliminar = confirmarEliminarModal ? new bootstrap.Modal(confirmarEliminarModal) : null;
    const btnConfirmarEliminar = document.getElementById('btn-confirmar-eliminar');
    
    // Event Listeners
    
    // Nueva Regla
    if (btnNuevaRegla) {
        btnNuevaRegla.addEventListener('click', function() {
            resetearFormulario();
            modalTitulo.textContent = 'Crear Nueva Regla';
            modoEdicion = false;
            reglaActualId = null;
        });
    }
    
    // Guardar Regla
    if (btnGuardarRegla) {
        btnGuardarRegla.addEventListener('click', function() {
            if (modoEdicion) {
                actualizarRegla();
            } else {
                crearRegla();
            }
        });
    }
    
    // Botones de edición
    botonesEditar.forEach(function(btn) {
        btn.addEventListener('click', function() {
            const reglaId = this.getAttribute('data-regla-id');
            cargarReglaParaEditar(reglaId);
        });
    });
    
    // Botones de eliminación
    botonesEliminar.forEach(function(btn) {
        btn.addEventListener('click', function() {
            const reglaId = this.getAttribute('data-regla-id');
            const nombreRegla = this.getAttribute('data-regla-nombre');
            mostrarConfirmacionEliminar(reglaId, nombreRegla);
        });
    });
    
    // Confirmar eliminación
    if (btnConfirmarEliminar) {
        btnConfirmarEliminar.addEventListener('click', function() {
            eliminarRegla(reglaActualId);
        });
    }
    
    // Switches de estado
    switchesEstado.forEach(function(switchEl) {
        switchEl.addEventListener('change', function() {
            const reglaId = this.getAttribute('data-regla-id');
            cambiarEstadoRegla(reglaId);
        });
    });
    
    // Funciones
    
    // Resetear formulario
    function resetearFormulario() {
        if (formNuevaRegla) {
            formNuevaRegla.reset();
            
            // Restablecer clases de validación si existen
            const camposInvalidos = formNuevaRegla.querySelectorAll('.is-invalid');
            camposInvalidos.forEach(function(campo) {
                campo.classList.remove('is-invalid');
            });
        }
    }
    
    // Cargar regla para editar
    function cargarReglaParaEditar(reglaId) {
        // Mostrar spinner o indicador de carga
        formNuevaRegla.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <p class="mt-3">Cargando datos de la regla...</p>
            </div>
        `;
        
        fetch(`/ingesta-correo/api/reglas/${reglaId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Actualizar variables de estado
                modoEdicion = true;
                reglaActualId = reglaId;
                modalTitulo.textContent = 'Editar Regla de Filtrado';
                
                // Restaurar formulario
                formNuevaRegla.innerHTML = `
                    <div class="mb-3">
                        <label for="nombreRegla" class="form-label">Nombre de la Regla</label>
                        <input type="text" class="form-control" id="nombreRegla" placeholder="Ej. Aseguradora XYZ" required>
                        <div class="invalid-feedback">Este campo es obligatorio</div>
                    </div>
                    <div class="mb-3">
                        <label for="condicionRegla" class="form-label">Condición</label>
                        <select class="form-select" id="condicionRegla" required>
                            <option value="remitente">Remitente contiene</option>
                            <option value="asunto">Asunto contiene</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="valorRegla" class="form-label">Valor</label>
                        <input type="text" class="form-control" id="valorRegla" placeholder="Ej. @empresa.com, glosa, factura" required>
                        <div class="invalid-feedback">Este campo es obligatorio</div>
                    </div>
                    <div class="mb-3">
                        <label for="accionRegla" class="form-label">Acción</label>
                        <select class="form-select" id="accionRegla" required>
                            <option value="procesar">Procesar</option>
                            <option value="ignorar">Ignorar</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="prioridadRegla" class="form-label">Prioridad (opcional)</label>
                        <input type="number" class="form-control" id="prioridadRegla" placeholder="Ej. 10">
                        <div class="form-text">Un número más alto indica mayor prioridad. Déjelo en blanco para asignar automáticamente.</div>
                    </div>
                    <div class="mb-3 form-check">
                        <input type="checkbox" class="form-check-input" id="estadoRegla" checked>
                        <label class="form-check-label" for="estadoRegla">Regla activa</label>
                    </div>
                `;
                
                // Poblar el formulario con los datos de la regla
                document.getElementById('nombreRegla').value = data.regla.nombre;
                document.getElementById('condicionRegla').value = data.regla.condicion_tipo;
                document.getElementById('valorRegla').value = data.regla.condicion_valor;
                document.getElementById('accionRegla').value = data.regla.accion;
                
                if (data.regla.prioridad) {
                    document.getElementById('prioridadRegla').value = data.regla.prioridad;
                }
                
                document.getElementById('estadoRegla').checked = data.regla.estado === 'activa';
                
                // Mostramos el modal (ya debería estar visible por el botón, pero por si acaso)
                nuevaReglaModal.show();
            } else {
                // Mostrar error
                showToast('Error al cargar la regla: ' + data.message, 'danger');
                nuevaReglaModal.hide();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error al cargar datos de la regla', 'danger');
            nuevaReglaModal.hide();
        });
    }
    
    // Crear nueva regla
    function crearRegla() {
        // Obtener datos del formulario
        const nombre = document.getElementById('nombreRegla').value;
        const condicionTipo = document.getElementById('condicionRegla').value;
        const valor = document.getElementById('valorRegla').value;
        const accion = document.getElementById('accionRegla').value;
        const prioridad = document.getElementById('prioridadRegla') ? document.getElementById('prioridadRegla').value : null;
        const estado = document.getElementById('estadoRegla').checked;
        
        // Validar datos básicos
        if (!nombre || !valor) {
            showToast('Por favor complete los campos obligatorios', 'warning');
            
            if (!nombre) {
                document.getElementById('nombreRegla').classList.add('is-invalid');
            }
            
            if (!valor) {
                document.getElementById('valorRegla').classList.add('is-invalid');
            }
            
            return;
        }
        
        // Preparar datos
        const data = {
            nombre: nombre,
            condicion_tipo: condicionTipo,
            condicion_operador: 'contiene', // Por defecto usamos 'contiene'
            condicion_valor: valor,
            accion: accion,
            prioridad: prioridad || null,
            estado: estado
        };
        
        // Mostrar indicador de carga
        btnGuardarRegla.disabled = true;
        btnGuardarRegla.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Guardando...';
        
        // Enviar petición
        fetch('/ingesta-correo/api/reglas', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            // Restaurar botón
            btnGuardarRegla.disabled = false;
            btnGuardarRegla.innerHTML = 'Guardar Regla';
            
            if (data.success) {
                // Cerrar modal
                nuevaReglaModal.hide();
                
                // Mostrar mensaje de éxito
                showToast('Regla creada correctamente', 'success');
                
                // Recargar la página para mostrar la nueva regla
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                // Mostrar errores
                showToast('Error al crear la regla: ' + (data.message || 'Error desconocido'), 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            btnGuardarRegla.disabled = false;
            btnGuardarRegla.innerHTML = 'Guardar Regla';
            showToast('Error al crear la regla', 'danger');
        });
    }
    
    // Actualizar regla existente
    function actualizarRegla() {
        if (!reglaActualId) {
            showToast('Error: No se pudo identificar la regla a actualizar', 'danger');
            return;
        }
        
        // Obtener datos del formulario
        const nombre = document.getElementById('nombreRegla').value;
        const condicionTipo = document.getElementById('condicionRegla').value;
        const valor = document.getElementById('valorRegla').value;
        const accion = document.getElementById('accionRegla').value;
        const prioridad = document.getElementById('prioridadRegla') ? document.getElementById('prioridadRegla').value : null;
        const estado = document.getElementById('estadoRegla').checked;
        
        // Validar datos básicos
        if (!nombre || !valor) {
            showToast('Por favor complete los campos obligatorios', 'warning');
            
            if (!nombre) {
                document.getElementById('nombreRegla').classList.add('is-invalid');
            }
            
            if (!valor) {
                document.getElementById('valorRegla').classList.add('is-invalid');
            }
            
            return;
        }
        
        // Preparar datos
        const data = {
            nombre: nombre,
            condicion_tipo: condicionTipo,
            condicion_operador: 'contiene', // Por defecto usamos 'contiene'
            condicion_valor: valor,
            accion: accion,
            prioridad: prioridad || null,
            estado: estado
        };
        
        // Mostrar indicador de carga
        btnGuardarRegla.disabled = true;
        btnGuardarRegla.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Actualizando...';
        
        // Enviar petición
        fetch(`/ingesta-correo/api/reglas/${reglaActualId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            // Restaurar botón
            btnGuardarRegla.disabled = false;
            btnGuardarRegla.innerHTML = 'Guardar Regla';
            
            if (data.success) {
                // Cerrar modal
                nuevaReglaModal.hide();
                
                // Mostrar mensaje de éxito
                showToast('Regla actualizada correctamente', 'success');
                
                // Recargar la página para mostrar los cambios
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                // Mostrar errores
                showToast('Error al actualizar la regla: ' + (data.message || 'Error desconocido'), 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            btnGuardarRegla.disabled = false;
            btnGuardarRegla.innerHTML = 'Guardar Regla';
            showToast('Error al actualizar la regla', 'danger');
        });
    }
    
    // Mostrar confirmación de eliminación
    function mostrarConfirmacionEliminar(reglaId, nombreRegla) {
        reglaActualId = reglaId;
        
        // Actualizar el mensaje de confirmación si hay un elemento para ello
        const mensajeConfirmacion = document.getElementById('confirmarEliminarMensaje');
        if (mensajeConfirmacion) {
            mensajeConfirmacion.textContent = `¿Está seguro que desea eliminar la regla "${nombreRegla || 'seleccionada'}"?`;
        }
        
        // Mostrar modal de confirmación
        modalConfirmEliminar.show();
    }
    
    // Eliminar regla
    function eliminarRegla(reglaId) {
        if (!reglaId) {
            showToast('Error: No se pudo identificar la regla a eliminar', 'danger');
            return;
        }
        
        // Mostrar indicador de carga en el botón de confirmar
        btnConfirmarEliminar.disabled = true;
        btnConfirmarEliminar.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Eliminando...';
        
        fetch(`/ingesta-correo/api/reglas/${reglaId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            // Restaurar botón
            btnConfirmarEliminar.disabled = false;
            btnConfirmarEliminar.innerHTML = 'Eliminar';
            
            // Cerrar modal de confirmación
            modalConfirmEliminar.hide();
            
            if (data.success) {
                // Mostrar mensaje de éxito
                showToast('Regla eliminada correctamente', 'success');
                
                // Recargar la página para actualizar la lista
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                // Mostrar error
                showToast('Error al eliminar la regla: ' + (data.message || 'Error desconocido'), 'danger');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            btnConfirmarEliminar.disabled = false;
            btnConfirmarEliminar.innerHTML = 'Eliminar';
            modalConfirmEliminar.hide();
            showToast('Error al eliminar la regla', 'danger');
        });
    }
    
    // Cambiar estado de una regla (activar/desactivar)
    function cambiarEstadoRegla(reglaId) {
        if (!reglaId) {
            return;
        }
        
        fetch(`/ingesta-correo/api/reglas/${reglaId}/toggle`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Mostrar mensaje de éxito
                showToast('Estado de la regla cambiado correctamente', 'success');
                
                // Actualizar la interfaz sin recargar la página
                const switchElement = document.querySelector(`.switch-estado-regla[data-regla-id="${reglaId}"]`);
                if (switchElement) {
                    const labelElement = switchElement.nextElementSibling;
                    if (labelElement) {
                        const badgeElement = labelElement.querySelector('.badge');
                        if (badgeElement) {
                            if (data.nuevo_estado === 'activa') {
                                badgeElement.classList.remove('bg-secondary');
                                badgeElement.classList.add('bg-success');
                                badgeElement.textContent = 'Activa';
                            } else {
                                badgeElement.classList.remove('bg-success');
                                badgeElement.classList.add('bg-secondary');
                                badgeElement.textContent = 'Inactiva';
                            }
                        } else {
                            labelElement.innerHTML = `<span class="badge ${data.nuevo_estado === 'activa' ? 'bg-success' : 'bg-secondary'}">${data.nuevo_estado === 'activa' ? 'Activa' : 'Inactiva'}</span>`;
                        }
                    }
                }
            } else {
                // Mostrar error y restaurar el switch a su estado anterior
                showToast('Error al cambiar el estado de la regla: ' + (data.message || 'Error desconocido'), 'danger');
                
                const switchElement = document.querySelector(`.switch-estado-regla[data-regla-id="${reglaId}"]`);
                if (switchElement) {
                    // Invertir el estado del switch sin disparar el evento
                    switchElement.checked = !switchElement.checked;
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showToast('Error al cambiar el estado de la regla', 'danger');
            
            // Restaurar el switch a su estado anterior
            const switchElement = document.querySelector(`.switch-estado-regla[data-regla-id="${reglaId}"]`);
            if (switchElement) {
                // Invertir el estado del switch sin disparar el evento
                switchElement.checked = !switchElement.checked;
            }
        });
    }
    
    // Función auxiliar para mostrar mensajes toast si no están disponibles globalmente
    if (typeof showToast !== 'function') {
        window.showToast = function(message, type = 'success') {
            // Verificar si existe un contenedor de toasts
            let toastContainer = document.getElementById('toast-container');
            if (!toastContainer) {
                toastContainer = document.createElement('div');
                toastContainer.id = 'toast-container';
                toastContainer.className = 'position-fixed bottom-0 end-0 p-3';
                toastContainer.style.zIndex = '5000';
                document.body.appendChild(toastContainer);
            }
            
            // Crear el toast
            const toast = document.createElement('div');
            toast.className = `toast bg-${type} text-white`;
            toast.role = 'alert';
            toast.ariaLive = 'assertive';
            toast.ariaAtomic = 'true';
            
            // Contenido del toast
            toast.innerHTML = `
                <div class="toast-header bg-${type} text-white">
                    <strong class="me-auto">Notificación</strong>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Cerrar"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            `;
            
            // Agregar al contenedor
            toastContainer.appendChild(toast);
            
            // Mostrar usando Bootstrap Toast
            const bsToast = new bootstrap.Toast(toast, {
                autohide: true,
                delay: 5000
            });
            bsToast.show();
            
            // Eliminar después de ocultarse
            toast.addEventListener('hidden.bs.toast', function() {
                toast.remove();
            });
        };
    }
});