"""
Rutas para la autenticación OAuth
"""

from flask import redirect, url_for, session, request, flash, g
from google_auth_oauthlib.flow import Flow
from sqlalchemy.orm.attributes import flag_modified
import os
from database import db
from . import oauth_bp
from auth.utils import login_required

# Permitir OAuth inseguro en desarrollo local
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'  # Agregar permiso para modificar correos
]
REDIRECT_URI = "http://localhost:5000/oauth/callback"

@oauth_bp.route('/callback')
@login_required
def callback():
    """Maneja el callback de autorización OAuth"""
    try:
        state = request.args.get('state')
        stored_state = session.get('oauth_state')
        
        # Verificación más detallada del estado
        if not state or not stored_state:
            flash('No se encontró el estado de OAuth en la sesión', 'danger')
            return redirect(url_for('configuracion.index', tab='correo'))
            
        if state != stored_state:
            flash(f'Estado de OAuth no coincide. Recibido: {state}, Almacenado: {stored_state}', 'danger')
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
                "redirect_uris": [REDIRECT_URI]
            }
        }
        
        # Crear el flujo de OAuth
        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI,
            state=state
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
    
    # Limpiar el estado de la sesión
    session.pop('oauth_state', None)
    return redirect(url_for('configuracion.index', tab='correo'))

@oauth_bp.route('/iniciar')
@login_required
def iniciar():
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
                "redirect_uris": [REDIRECT_URI]
            }
        }
        
        # Crear el flujo de OAuth
        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        
        # Generar URL de autorización
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        # Guardar el estado en la sesión y asegurarse de que se guarde
        session['oauth_state'] = state
        session.modified = True
        
        return redirect(authorization_url)
        
    except Exception as e:
        flash(f'Error al iniciar la autorización: {str(e)}', 'danger')
        return redirect(url_for('configuracion.index', tab='correo')) 