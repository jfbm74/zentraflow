/**
 * Funcionalidad para probar la conexión OAuth en ZentraFlow
 */

// Función para mostrar toast en caso de que la función global no esté disponible
function fallbackToast(message, type) {
    console.log('Mensaje de respuesta:', message, '(Tipo:', type, ')');
    
    // Crear un elemento div para el toast
    const toast = document.createElement('div');
    toast.className = `position-fixed bottom-0 end-0 p-3 m-3 alert alert-${type}`;
    toast.style.zIndex = '5000';
    toast.innerHTML = message;
    document.body.appendChild(toast);
    
    // Eliminar después de 3 segundos
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Función para probar la conexión OAuth
function probarConexionOAuth() {
    console.log('Iniciando prueba de conexión OAuth...');
    
    // Mostrar indicador de carga
    const botonProbar = document.getElementById('btn-probar-conexion');
    const textoOriginal = botonProbar.innerHTML;
    botonProbar.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Probando...';
    botonProbar.disabled = true;
    
    // Obtener el token CSRF si se está utilizando
    let csrfToken = '';
    const csrfElement = document.querySelector('input[name="csrf_token"]');
    if (csrfElement) {
        csrfToken = csrfElement.value;
    }
    
    // Realizar solicitud AJAX
    fetch('/configuracion/probar-conexion-correo', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({}),
        credentials: 'same-origin'
    })
    .then(response => {
        console.log('Respuesta recibida:', response.status);
        if (!response.ok) {
            throw new Error('Error en la solicitud: ' + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        console.log('Datos recibidos:', data);
        
        // Restaurar el botón a su estado original
        botonProbar.innerHTML = textoOriginal;
        botonProbar.disabled = false;
        
        // Mostrar mensaje usando showToast si está disponible, de lo contrario usar fallback
        if (data.success) {
            if (typeof showToast === 'function') {
                showToast(data.message, 'success');
            } else {
                fallbackToast(data.message, 'success');
            }
        } else {
            if (typeof showToast === 'function') {
                showToast(data.message, 'danger');
            } else {
                fallbackToast(data.message, 'danger');
            }
        }
    })
    .catch(error => {
        console.error('Error en la solicitud:', error);
        
        // Restaurar el botón y mostrar error
        botonProbar.innerHTML = textoOriginal;
        botonProbar.disabled = false;
        
        // Mostrar mensaje de error
        if (typeof showToast === 'function') {
            showToast('Error al probar la conexión: ' + error.message, 'danger');
        } else {
            fallbackToast('Error al probar la conexión: ' + error.message, 'danger');
        }
    });
}

// Agregar event listener cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM cargado, buscando botón de prueba de conexión...');
    const botonProbar = document.getElementById('btn-probar-conexion');
    if (botonProbar) {
        console.log('Botón encontrado, agregando event listener...');
        botonProbar.addEventListener('click', probarConexionOAuth);
    } else {
        console.warn('Botón de prueba de conexión no encontrado en la página');
    }
});