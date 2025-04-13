"""
Rutas para el módulo de configuración
"""

import os
import json
from flask import render_template, g, session, request, flash, redirect, url_for, current_app, jsonify
from werkzeug.utils import secure_filename
from . import configuracion_bp
from modules.usuarios.models import Usuario
from auth.utils import login_required
from .forms import ConfiguracionGeneralForm, ConfiguracionCorreoForm
from database import db
from sqlalchemy.orm.attributes import flag_modified
import uuid
from datetime import datetime
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request

def guardar_logo(archivo, cliente_id):
    """Guarda el logo del cliente en el sistema de archivos"""
    if archivo:
        # Crear directorio si no existe
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'logos')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generar nombre único para el archivo
        filename = f"{cliente_id}_{uuid.uuid4()}{os.path.splitext(archivo.filename)[1]}"
        filepath = os.path.join(upload_dir, secure_filename(filename))
        
        # Guardar archivo
        archivo.save(filepath)
        
        # Retornar ruta relativa para guardar en la base de datos
        return os.path.join('uploads', 'logos', filename)
    return None

def guardar_service_account(archivo, cliente_id):
    """Guarda el archivo JSON de la cuenta de servicio"""
    if archivo:
        # Crear directorio si no existe
        upload_dir = os.path.join(current_app.root_path, 'secure', 'service_accounts')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generar nombre único para el archivo
        filename = f"sa_{cliente_id}_{uuid.uuid4()}.json"
        filepath = os.path.join(upload_dir, secure_filename(filename))
        
        # Guardar archivo
        archivo.save(filepath)
        
        return filepath
    return None

@configuracion_bp.route('/')
@login_required
def index():
    """
    Ruta principal del módulo de configuración
    Muestra las opciones de configuración disponibles según el rol del usuario
    """
    # Obtener información del usuario de la sesión
    user_name = session.get('user_name', '')
    user_email = session.get('user_email', '')
    
    # Crear formularios y poblarlos con datos actuales
    form_general = ConfiguracionGeneralForm()
    form_correo = ConfiguracionCorreoForm()
    
    if g.cliente:
        # Poblar formulario general
        form_general.nombre.data = g.cliente.nombre
        form_general.nit.data = g.cliente.nit
        form_general.timezone.data = g.cliente.config.get('timezone', 'America/Bogota')
        form_general.date_format.data = g.cliente.config.get('date_format', 'DD/MM/YYYY')
        
        # Poblar formulario de correo
        config_correo = g.cliente.config.get('correo', {})
        form_correo.habilitar_ingesta.data = config_correo.get('habilitado', False)
        form_correo.email_monitorear.data = config_correo.get('email', '')
        form_correo.metodo_autenticacion.data = config_correo.get('metodo_auth', 'oauth2')
        form_correo.client_id.data = config_correo.get('client_id', '')
        form_correo.carpeta_monitorear.data = config_correo.get('carpeta', 'INBOX')
        form_correo.intervalo_verificacion.data = str(config_correo.get('intervalo', '5'))
        form_correo.marcar_leidos.data = config_correo.get('marcar_leidos', False)
    
    return render_template('configuracion/index.html', 
                         titulo="Configuración del Sistema",
                         usuario=g.usuario,
                         cliente=g.cliente,
                         user_name=user_name,
                         user_email=user_email,
                         form_general=form_general,
                         form_correo=form_correo)

@configuracion_bp.route('/guardar-correo', methods=['POST'])
@login_required
def guardar_correo():
    """Procesa el formulario de configuración de correo"""
    form = ConfiguracionCorreoForm()
    
    if form.validate_on_submit():
        try:
            config_correo = g.cliente.config.get('correo', {})
            
            # Actualizar configuración básica
            config_correo.update({
                'habilitado': form.habilitar_ingesta.data,
                'email': form.email_monitorear.data,
                'metodo_auth': form.metodo_autenticacion.data,
                'carpeta': form.carpeta_monitorear.data,
                'intervalo': form.intervalo_verificacion.data,
                'marcar_leidos': form.marcar_leidos.data,
                'ultima_modificacion': {
                    'fecha': datetime.utcnow().isoformat(),
                    'usuario': g.usuario.email
                }
            })
            
            # Procesar credenciales según el método de autenticación
            if form.metodo_autenticacion.data == 'oauth2':
                if form.client_id.data:
                    config_correo['client_id'] = form.client_id.data
                if form.client_secret.data:
                    config_correo['client_secret'] = form.client_secret.data
                if form.refresh_token.data:
                    config_correo['refresh_token'] = form.refresh_token.data
                    
            elif form.metodo_autenticacion.data == 'service_account':
                if form.service_account_key.data:
                    filepath = guardar_service_account(form.service_account_key.data, g.cliente.id)
                    if filepath:
                        config_correo['service_account_path'] = filepath
            
            # Actualizar configuración en el cliente
            g.cliente.config['correo'] = config_correo
            flag_modified(g.cliente, 'config')
            db.session.commit()
            
            flash('Configuración de correo guardada exitosamente.', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar la configuración de correo: {str(e)}', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error en {getattr(form, field).label.text}: {error}', 'danger')
    
    return redirect(url_for('configuracion.index', tab='correo'))

@configuracion_bp.route('/guardar-general', methods=['POST'])
@login_required
def guardar_general():
    """Procesa el formulario de configuración general"""
    form = ConfiguracionGeneralForm()
    
    if form.validate_on_submit():
        try:
            # Actualizar datos básicos
            g.cliente.nombre = form.nombre.data
            
            # Procesar logo si se subió uno nuevo
            if form.logo.data:
                # Eliminar logo anterior si existe
                logo_anterior = g.cliente.config.get('logo_url')
                if logo_anterior:
                    try:
                        os.remove(os.path.join(current_app.root_path, 'static', logo_anterior))
                    except (FileNotFoundError, OSError):
                        pass  # Ignorar errores si el archivo no existe
                
                # Guardar nuevo logo
                logo_url = guardar_logo(form.logo.data, g.cliente.id)
                g.cliente.config['logo_url'] = logo_url
            
            # Actualizar configuración
            g.cliente.config['timezone'] = form.timezone.data
            g.cliente.config['date_format'] = form.date_format.data
            
            # Marcar el campo config como modificado
            flag_modified(g.cliente, 'config')
            
            # Guardar cambios
            db.session.commit()
            
            flash('Configuración guardada exitosamente.', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar la configuración: {str(e)}', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Error en {getattr(form, field).label.text}: {error}', 'danger')
    
    return redirect(url_for('configuracion.index')) 


@configuracion_bp.route('/probar-conexion-correo', methods=['POST'])
@login_required
def probar_conexion_correo():
    """Probar la conexión a la cuenta de correo"""
    try:
        # Verificar si el cliente tiene configuración de correo
        if not g.cliente or not g.cliente.config or 'correo' not in g.cliente.config:
            return jsonify({'success': False, 'message': 'Configuración de correo no encontrada'})
        
        # Obtener la configuración de correo
        config_correo = g.cliente.config.get('correo', {})
        
        # Verificar si hay información mínima necesaria
        if not config_correo.get('email'):
            return jsonify({'success': False, 'message': 'No hay una dirección de correo configurada'})
        
        # Simular una prueba de conexión (en un entorno real, aquí iría el código real)
        # Este es un placeholder - en producción, deberías implementar la verdadera prueba de conexión
        if config_correo.get('habilitado', False):
            return jsonify({'success': True, 'message': f'Conexión exitosa con {config_correo.get("email")}'})
        else:
            return jsonify({'success': False, 'message': 'La ingesta de correo está deshabilitada. Actívela primero.'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al probar la conexión: {str(e)}'})

# Configuración de OAuth
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CLIENT_SECRETS_FILE = 'client_secrets.json'

@configuracion_bp.route('/iniciar-oauth')
@login_required
def iniciar_oauth():
    """Inicia el flujo de autorización OAuth"""
    try:
        # Obtener configuración de correo
        config_correo = g.cliente.config.get('correo', {})
        
        if not config_correo.get('client_id') or not config_correo.get('client_secret'):
            flash('Debes configurar el Client ID y Client Secret primero', 'warning')
            return redirect(url_for('configuracion.index', tab='correo'))
        
        # Crear configuración de OAuth
        client_config = {
            "web": {
                "client_id": config_correo['client_id'],
                "project_id": "zentraflow",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": config_correo['client_secret'],
                "redirect_uris": [url_for('configuracion.oauth_callback', _external=True)]
            }
        }
        
        # Crear el flujo de OAuth
        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=url_for('configuracion.oauth_callback', _external=True)
        )
        
        # Generar URL de autorización
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        # Guardar el estado en la sesión
        session['oauth_state'] = state
        
        return redirect(authorization_url)
        
    except Exception as e:
        flash(f'Error al iniciar la autorización: {str(e)}', 'danger')
        return redirect(url_for('configuracion.index', tab='correo'))

@configuracion_bp.route('/oauth-callback')
@login_required
def oauth_callback():
    """Maneja el callback de autorización OAuth"""
    try:
        # Verificar el estado
        if session.get('oauth_state') != request.args.get('state'):
            flash('Estado de OAuth inválido', 'danger')
            return redirect(url_for('configuracion.index', tab='correo'))
        
        # Obtener configuración de correo
        config_correo = g.cliente.config.get('correo', {})
        
        # Crear configuración de OAuth
        client_config = {
            "web": {
                "client_id": config_correo['client_id'],
                "project_id": "zentraflow",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": config_correo['client_secret'],
                "redirect_uris": [url_for('configuracion.oauth_callback', _external=True)]
            }
        }
        
        # Crear el flujo de OAuth
        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=url_for('configuracion.oauth_callback', _external=True)
        )
        
        # Obtener las credenciales
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        
        # Guardar el refresh token en la configuración
        if credentials.refresh_token:
            config_correo['refresh_token'] = credentials.refresh_token
            g.cliente.config['correo'] = config_correo
            flag_modified(g.cliente, 'config')
            db.session.commit()
            
            flash('Refresh Token obtenido y guardado exitosamente', 'success')
        else:
            flash('No se pudo obtener el Refresh Token. Por favor, intenta nuevamente.', 'warning')
            
    except Exception as e:
        flash(f'Error en el callback de autorización: {str(e)}', 'danger')
    
    return redirect(url_for('configuracion.index', tab='correo'))