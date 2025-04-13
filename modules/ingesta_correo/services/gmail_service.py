"""
Servicio de conexión a Gmail API para ingesta de correos
"""

import os
import base64
import json
import logging
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from flask import g, current_app

# Configurar logger
logger = logging.getLogger(__name__)

# Alcances requeridos para Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
if os.environ.get('GMAIL_MARK_READ', 'False').lower() == 'true':
    SCOPES.append('https://www.googleapis.com/auth/gmail.modify')

class GmailService:
    """Clase para gestionar la conexión y operaciones con Gmail API"""
    
    def __init__(self, cliente_config=None):
        """
        Inicializa el servicio de Gmail
        
        Args:
            cliente_config (dict): Configuración del cliente 
                                  (client_id, client_secret, refresh_token, etc.)
        """
        self.cliente_config = cliente_config
        self.service = None
        self.credentials = None
    
    def inicializar_credenciales(self):
        """Inicializa las credenciales para Gmail API basado en la configuración del cliente"""
        if not self.cliente_config:
            raise ValueError("No se ha proporcionado configuración de cliente")
        
        # Obtener datos de config_correo
        config_correo = self.cliente_config.get('correo', {})
        
        # Verificar que la configuración esté completa
        if not config_correo.get('email'):
            raise ValueError("No se ha configurado el correo a monitorear")
        
        # Determinar método de autenticación
        metodo_auth = config_correo.get('metodo_auth', 'oauth2')
        
        if metodo_auth == 'oauth2':
            # Configuración OAuth2
            client_id = config_correo.get('client_id')
            client_secret = config_correo.get('client_secret')
            refresh_token = config_correo.get('refresh_token')
            
            if not (client_id and client_secret):
                raise ValueError("Faltan credenciales OAuth2 (client_id y/o client_secret)")
            
            if refresh_token:
                # Usar refresh token existente
                self.credentials = Credentials(
                    None,
                    refresh_token=refresh_token,
                    token_uri='https://oauth2.googleapis.com/token',
                    client_id=client_id,
                    client_secret=client_secret
                )
                
                # Refrescar token si es necesario
                if self.credentials.expired:
                    self.credentials.refresh(Request())
            else:
                # No hay refresh token almacenado, se necesita autorización
                raise ValueError("No hay refresh token almacenado. Se requiere autorización manual.")
                
        elif metodo_auth == 'service_account':
            # Configuración de cuenta de servicio
            service_account_path = config_correo.get('service_account_path')
            
            if not service_account_path:
                raise ValueError("No se ha proporcionado ruta de archivo de cuenta de servicio")
            
            if not os.path.exists(service_account_path):
                raise FileNotFoundError(f"No se encontró el archivo de cuenta de servicio: {service_account_path}")
            
            # Cargar credenciales de cuenta de servicio
            from google.oauth2 import service_account
            
            self.credentials = service_account.Credentials.from_service_account_file(
                service_account_path, 
                scopes=SCOPES,
                subject=config_correo.get('email')  # Impersonar el correo configurado
            )
        else:
            raise ValueError(f"Método de autenticación no soportado: {metodo_auth}")
        
        # Construir el servicio de Gmail
        self.service = build('gmail', 'v1', credentials=self.credentials)
        
        return self.service
    
    def verificar_nuevos_correos(self):
        """
        Verifica nuevos correos en la bandeja configurada y devuelve lista de IDs
        
        Returns:
            list: Lista de IDs de mensajes nuevos
        """
        if not self.service:
            self.inicializar_credenciales()
        
        # Obtener la carpeta a monitorear
        carpeta = self.cliente_config.get('correo', {}).get('carpeta', 'INBOX')
        
        # Construir consulta
        query = f"in:{carpeta} is:unread"
        
        # Si hay una última verificación almacenada, filtrar por fecha
        if 'ultima_verificacion' in self.cliente_config.get('correo', {}):
            try:
                ultima_fecha = self.cliente_config.get('correo', {}).get('ultima_verificacion')
                if isinstance(ultima_fecha, str):
                    # Convertir a objeto datetime
                    ultima_verificacion = datetime.fromisoformat(ultima_fecha)
                    # Convertir a formato RFC 3339 (usado por Gmail API)
                    fecha_rfc3339 = ultima_verificacion.strftime('%Y/%m/%d')
                    query += f" after:{fecha_rfc3339}"
            except Exception as e:
                logger.warning(f"Error al procesar última verificación: {str(e)}")
        
        try:
            # Ejecutar búsqueda
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=50  # Limitar a 50 correos por búsqueda
            ).execute()
            
            messages = results.get('messages', [])
            return messages
        except HttpError as error:
            logger.error(f"Error al verificar correos: {str(error)}")
            raise
    
    def obtener_detalles_correo(self, message_id):
        """
        Obtiene los detalles de un correo específico
        
        Args:
            message_id (str): ID del mensaje de Gmail
            
        Returns:
            dict: Detalles del correo (remitente, asunto, fecha, tiene_adjuntos)
        """
        if not self.service:
            self.inicializar_credenciales()
        
        try:
            # Obtener el mensaje completo
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extraer headers
            headers = message.get('payload', {}).get('headers', [])
            
            # Función para obtener valor de un header
            def get_header_value(header_name):
                for header in headers:
                    if header.get('name', '').lower() == header_name.lower():
                        return header.get('value', '')
                return ''
            
            # Obtener datos
            remitente = get_header_value('From')
            asunto = get_header_value('Subject')
            
            # Verificar si tiene adjuntos
            tiene_adjuntos = False
            adj_count = 0
            
            # Buscar partes con adjuntos
            if 'parts' in message.get('payload', {}):
                for part in message['payload']['parts']:
                    if part.get('filename') and part.get('body', {}).get('attachmentId'):
                        tiene_adjuntos = True
                        adj_count += 1
            
            # Fecha interna de Gmail
            fecha_recepcion = datetime.fromtimestamp(int(message['internalDate']) / 1000)
            
            return {
                'remitente': remitente,
                'asunto': asunto,
                'fecha_recepcion': fecha_recepcion,
                'tiene_adjuntos': tiene_adjuntos,
                'adjuntos_count': adj_count,
                'message_id': message_id
            }
            
        except HttpError as error:
            logger.error(f"Error al obtener detalles del correo {message_id}: {str(error)}")
            raise
    
    def marcar_como_leido(self, message_id):
        """
        Marca un correo como leído
        
        Args:
            message_id (str): ID del mensaje de Gmail
            
        Returns:
            bool: True si se marcó correctamente, False en caso contrario
        """
        if not self.service:
            self.inicializar_credenciales()
        
        # Verificar si la configuración permite marcar como leídos
        marcar_leidos = self.cliente_config.get('correo', {}).get('marcar_leidos', False)
        if not marcar_leidos:
            logger.info(f"No se marcará como leído el correo {message_id} (deshabilitado en config)")
            return False
        
        try:
            # Modificar etiquetas para quitar 'UNREAD'
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            return True
        except HttpError as error:
            logger.error(f"Error al marcar como leído el correo {message_id}: {str(error)}")
            return False
    
    def descargar_adjuntos(self, message_id):
        """
        Descarga los adjuntos de un correo
        
        Args:
            message_id (str): ID del mensaje de Gmail
            
        Returns:
            list: Lista de diccionarios con información de los adjuntos descargados
        """
        if not self.service:
            self.inicializar_credenciales()
        
        try:
            # Obtener el mensaje completo
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            adjuntos = []
            
            # Si no hay partes, no hay adjuntos
            if 'parts' not in message.get('payload', {}):
                return adjuntos
            
            # Carpeta temporal para guardar adjuntos
            temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Buscar partes con adjuntos
            for part in message['payload']['parts']:
                if part.get('filename') and part.get('body', {}).get('attachmentId'):
                    filename = part['filename']
                    attachment_id = part['body']['attachmentId']
                    
                    # Obtener el adjunto
                    attachment = self.service.users().messages().attachments().get(
                        userId='me',
                        messageId=message_id,
                        id=attachment_id
                    ).execute()
                    
                    # Decodificar datos
                    file_data = base64.urlsafe_b64decode(attachment['data'])
                    
                    # Guardar en archivo temporal
                    file_path = os.path.join(temp_dir, filename)
                    with open(file_path, 'wb') as f:
                        f.write(file_data)
                    
                    # Añadir a la lista de adjuntos
                    adjuntos.append({
                        'nombre': filename,
                        'ruta': file_path,
                        'tamanio': len(file_data),
                        'tipo': part.get('mimeType', 'application/octet-stream')
                    })
            
            return adjuntos
            
        except HttpError as error:
            logger.error(f"Error al descargar adjuntos del correo {message_id}: {str(error)}")
            raise

def get_gmail_service():
    """
    Obtiene una instancia del servicio Gmail API usando las credenciales del cliente actual
    """
    try:
        if not g.cliente or not g.cliente.config or 'correo' not in g.cliente.config:
            current_app.logger.error("Configuración de correo no encontrada")
            return None

        config_correo = g.cliente.config['correo']
        
        if not config_correo.get('client_id') or not config_correo.get('client_secret'):
            current_app.logger.error("Credenciales de OAuth no configuradas")
            return None

        if not config_correo.get('refresh_token'):
            current_app.logger.error("No se encontró refresh token")
            return None

        # Crear credenciales usando el refresh token
        credentials = Credentials(
            None,  # No access token needed as we'll use refresh token
            refresh_token=config_correo['refresh_token'],
            token_uri="https://oauth2.googleapis.com/token",
            client_id=config_correo['client_id'],
            client_secret=config_correo['client_secret'],
            scopes=['https://www.googleapis.com/auth/gmail.readonly', 
                   'https://www.googleapis.com/auth/gmail.modify']
        )

        # Construir el servicio de Gmail
        service = build('gmail', 'v1', credentials=credentials)
        return service

    except Exception as e:
        current_app.logger.error(f"Error al obtener servicio Gmail: {str(e)}")
        return None

        