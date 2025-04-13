"""
Utilidades de autenticación para la aplicación
"""

from functools import wraps
from flask import session, redirect, url_for, request, flash
from modules.usuarios.models import Usuario, RolUsuario

def login_required(f):
    """
    Decorador para requerir inicio de sesión en rutas protegidas
    
    Si el usuario no está autenticado, redirige a la página de login
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    """
    Decorador para requerir roles específicos en rutas protegidas
    
    Args:
        roles: String con un rol o lista de roles permitidos
        
    Si el usuario no tiene el rol requerido, redirige al dashboard con un mensaje
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('auth.login', next=request.url))
            
            # Convertir a lista si se pasa un solo rol como string
            if isinstance(roles, str):
                required_roles = [roles]
            else:
                required_roles = roles
            
            # Verificar si el usuario tiene alguno de los roles requeridos
            user = Usuario.query.get(session['user_id'])
            if not user:
                session.clear()
                flash('Sesión inválida. Por favor inicie sesión nuevamente.', 'danger')
                return redirect(url_for('auth.login'))
            
            # Super Admin siempre tiene acceso
            if user.rol == RolUsuario.SUPER_ADMIN:
                return f(*args, **kwargs)
                
            # Verificar si el rol del usuario está en la lista
            if user.rol.value not in required_roles:
                flash('No tiene permisos para acceder a esta página.', 'danger')
                return redirect(url_for('dashboard.index'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def tenant_access_required(f):
    """
    Decorador para validar acceso a recursos específicos de un tenant
    
    Verifica que el usuario tenga acceso al tenant (cliente) especificado en la URL
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login', next=request.url))
        
        # Verificar si hay un cliente_id en los parámetros
        cliente_id = kwargs.get('cliente_id')
        if cliente_id:
            user = Usuario.query.get(session['user_id'])
            
            # Super Admin o Admin del sistema tiene acceso a todos los clientes
            if user.rol == RolUsuario.SUPER_ADMIN:
                return f(*args, **kwargs)
                
            # Verificar que el usuario pertenezca al cliente solicitado
            if user.cliente_id != int(cliente_id):
                flash('No tiene acceso a los recursos de este cliente.', 'danger')
                return redirect(url_for('dashboard.index'))
        
        return f(*args, **kwargs)
    return decorated_function