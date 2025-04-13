"""
Rutas de autenticación para la aplicación
"""

from flask import Blueprint, render_template, redirect, url_for, request, session, flash, g
from modules.usuarios.models import Usuario, SesionUsuario
from database import db
from datetime import datetime

# Crear el blueprint para autenticación
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Si ya está logueado, redirigir al dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = Usuario.query.filter_by(email=email).first()
        
        if user and user.check_password(password) and user.activo:
            # Actualizar último acceso
            user.ultimo_acceso = datetime.utcnow()
            
            # Registrar la sesión
            sesion = SesionUsuario(
                usuario_id=user.id,
                ip=request.remote_addr,
                user_agent=request.user_agent.string,
                fecha_inicio=datetime.utcnow()
            )
            
            db.session.add(sesion)
            db.session.commit()
            
            # Almacenar información en la sesión
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_name'] = user.nombre_completo
            session['user_role'] = user.rol.value
            session['cliente_id'] = user.cliente_id
            session['cliente_name'] = user.cliente.nombre
            session['sesion_id'] = sesion.id
            
            # Redirigir a la página solicitada originalmente o al dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard.index'))
        else:
            if user and not user.activo:
                error = 'Usuario inactivo. Contacte al administrador.'
            else:
                error = 'Credenciales inválidas. Por favor intente nuevamente.'
    
    return render_template('auth/login.html', error=error)

@auth_bp.route('/logout')
def logout():
    # Registrar fin de sesión
    if 'sesion_id' in session:
        sesion = SesionUsuario.query.get(session['sesion_id'])
        if sesion:
            sesion.fecha_fin = datetime.utcnow()
            db.session.commit()
    
    # Limpiar sesión
    session.clear()
    flash('Ha cerrado sesión correctamente.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = Usuario.query.filter_by(email=email).first()
        
        if user:
            # Aquí iría la lógica para enviar correo de restablecimiento
            # Por ahora, solo mostramos un mensaje
            flash('Se ha enviado un correo con las instrucciones para restablecer su contraseña.', 'info')
        else:
            flash('No se encontró ninguna cuenta con ese correo electrónico.', 'warning')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Esta ruta sería para el restablecimiento de contraseña usando un token
    # Por ahora es un placeholder
    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'danger')
            return render_template('auth/reset_password.html', token=token)
        
        # Aquí iría la lógica para verificar el token y cambiar la contraseña
        flash('Su contraseña ha sido restablecida correctamente. Ahora puede iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
    
    # Verificar que el token sea válido
    # Aquí iría la lógica para validar el token
    
    return render_template('auth/reset_password.html', token=token)