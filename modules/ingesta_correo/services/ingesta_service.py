"""
Servicio de ingesta de correos
"""

import logging
import os
from datetime import datetime
from sqlalchemy.orm.attributes import flag_modified
from database import db
from modules.ingesta_correo.models import CorreoIngestado, ReglaFiltrado
from .gmail_service import GmailService

# Configurar logger
logger = logging.getLogger(__name__)

class IngestaService:
    """Clase para gestionar la ingesta de correos"""
    
    def __init__(self, cliente=None, usuario=None):
        """
        Inicializa el servicio de ingesta
        
        Args:
            cliente (Cliente): Objeto cliente al que pertenece la ingesta
            usuario (Usuario): Usuario que inicia la verificación (para logs)
        """
        self.cliente = cliente
        self.usuario = usuario
        self.gmail_service = None
    
    def inicializar(self):
        """
        Inicializa el servicio de Gmail y valida configuración
        
        Returns:
            bool: True si se inicializó correctamente, False en caso contrario
        """
        if not self.cliente:
            logger.error("No se ha proporcionado cliente para la ingesta")
            return False
        
        if not self.cliente.config or 'correo' not in self.cliente.config:
            logger.error(f"Cliente {self.cliente.id} sin configuración de correo")
            return False
        
        # Verificar que la ingesta esté habilitada
        config_correo = self.cliente.config.get('correo', {})
        if not config_correo.get('habilitado', False):
            logger.info(f"Ingesta deshabilitada para cliente {self.cliente.id}")
            return False
        
        # Inicializar servicio de Gmail
        try:
            self.gmail_service = GmailService(self.cliente.config)
            self.gmail_service.inicializar_credenciales()
            return True
        except Exception as e:
            logger.error(f"Error al inicializar servicio de Gmail: {str(e)}")
            return False
    
    def ejecutar_verificacion(self):
        """
        Ejecuta una verificación completa del buzón y procesa los correos encontrados
        
        Returns:
            dict: Resultado de la verificación con estadísticas
        """
        resultado = {
            'success': False,
            'correos_procesados': 0,
            'correos_ignorados': 0,
            'correos_error': 0,
            'mensaje': '',
            'detalles': []
        }
        
        # Inicializar el servicio si no se ha hecho
        if not self.gmail_service:
            if not self.inicializar():
                resultado['mensaje'] = 'Error al inicializar el servicio de ingesta'
                return resultado
        
        try:
            # Verificar nuevos correos
            mensajes = self.gmail_service.verificar_nuevos_correos()
            
            if not mensajes:
                resultado['success'] = True
                resultado['mensaje'] = 'No se encontraron correos nuevos'
                return resultado
            
            # Cargar reglas de filtrado activas
            reglas = ReglaFiltrado.query.filter_by(
                cliente_id=self.cliente.id,
                estado='activa'
            ).order_by(ReglaFiltrado.prioridad.desc()).all()
            
            # Procesar cada mensaje
            for mensaje in mensajes:
                message_id = mensaje['id']
                try:
                    # Obtener detalles del correo
                    detalles = self.gmail_service.obtener_detalles_correo(message_id)
                    
                    # Crear registro en BD
                    correo_ingestado = CorreoIngestado(
                        cliente_id=self.cliente.id,
                        message_id_google=message_id,
                        remitente=detalles['remitente'],
                        asunto=detalles['asunto'],
                        fecha_recepcion=detalles['fecha_recepcion'],
                        fecha_procesamiento=datetime.utcnow(),
                        adjuntos_detectados=detalles['adjuntos_count'],
                        estado='pendiente'  # Estado inicial
                    )
                    
                    # Evaluar reglas de filtrado
                    regla_aplicada, accion = self._aplicar_reglas(correo_ingestado, reglas)
                    
                    # Actualizar con la regla aplicada
                    if regla_aplicada:
                        correo_ingestado.regla_aplicada_id = regla_aplicada.id
                    
                    # Aplicar acción según resultado del filtrado
                    if accion == 'procesar':
                        # Procesar el correo (descargar adjuntos, etc.)
                        correo_ingestado.estado = 'procesado'
                        resultado['correos_procesados'] += 1
                        
                        # Opcionalmente descargar adjuntos aquí
                        if detalles['tiene_adjuntos']:
                            try:
                                adjuntos = self.gmail_service.descargar_adjuntos(message_id)
                                # Aquí se podría llamar a extracción de datos
                                # self._procesar_adjuntos(adjuntos, correo_ingestado)
                            except Exception as e:
                                logger.error(f"Error al descargar adjuntos: {str(e)}")
                                correo_ingestado.estado = 'error_descarga'
                                correo_ingestado.detalles_error = f"Error al descargar adjuntos: {str(e)}"
                                resultado['correos_error'] += 1
                        
                    elif accion == 'ignorar':
                        correo_ingestado.estado = 'ignorado'
                        resultado['correos_ignorados'] += 1
                    else:
                        # Acción desconocida
                        correo_ingestado.estado = 'error_filtrado'
                        correo_ingestado.detalles_error = f"Acción desconocida: {accion}"
                        resultado['correos_error'] += 1
                    
                    # Guardar en BD
                    db.session.add(correo_ingestado)
                    
                    # Marcar como leído si corresponde
                    if correo_ingestado.estado in ['procesado', 'ignorado']:
                        self.gmail_service.marcar_como_leido(message_id)
                    
                    # Agregar detalles al resultado
                    resultado['detalles'].append({
                        'message_id': message_id,
                        'asunto': detalles['asunto'],
                        'remitente': detalles['remitente'],
                        'estado': correo_ingestado.estado
                    })
                    
                except Exception as e:
                    logger.error(f"Error al procesar mensaje {message_id}: {str(e)}")
                    
                    # Crear registro de error
                    correo_error = CorreoIngestado(
                        cliente_id=self.cliente.id,
                        message_id_google=message_id,
                        remitente="No disponible",
                        asunto="No disponible",
                        fecha_recepcion=datetime.utcnow(),
                        fecha_procesamiento=datetime.utcnow(),
                        estado='error_procesamiento',
                        detalles_error=str(e)
                    )
                    
                    db.session.add(correo_error)
                    resultado['correos_error'] += 1
            
            # Commit de cambios a la BD
            db.session.commit()
            
            # Actualizar última verificación en configuración del cliente
            self.cliente.config['correo']['ultima_verificacion'] = datetime.utcnow().isoformat()
            flag_modified(self.cliente, 'config')
            db.session.commit()
            
            # Actualizar resultado
            resultado['success'] = True
            total_correos = len(mensajes)
            resultado['mensaje'] = f'Verificación completada: {total_correos} correos encontrados, {resultado["correos_procesados"]} procesados, {resultado["correos_ignorados"]} ignorados, {resultado["correos_error"]} con errores'
            
        except Exception as e:
            logger.error(f"Error en verificación de correo: {str(e)}")
            db.session.rollback()
            resultado['mensaje'] = f'Error en verificación: {str(e)}'
            
        return resultado
    
    def _aplicar_reglas(self, correo, reglas):
        """
        Aplica las reglas de filtrado a un correo
        
        Args:
            correo (CorreoIngestado): Objeto de correo ingestado
            reglas (list): Lista de reglas de filtrado a aplicar
            
        Returns:
            tuple: (regla_aplicada, accion) - Regla que se aplicó y acción a realizar
        """
        # Si no hay reglas, procesar por defecto
        if not reglas:
            return None, 'procesar'
        
        # Evaluar cada regla en orden de prioridad
        for regla in reglas:
            # Verificar condición
            if regla.condicion_tipo == 'remitente':
                valor_a_evaluar = correo.remitente
            elif regla.condicion_tipo == 'asunto':
                valor_a_evaluar = correo.asunto
            else:
                # Tipo de condición no soportado
                continue
            
            # Aplicar operador
            if regla.condicion_operador == 'contiene':
                if regla.condicion_valor.lower() in valor_a_evaluar.lower():
                    return regla, regla.accion
            elif regla.condicion_operador == 'no_contiene':
                if regla.condicion_valor.lower() not in valor_a_evaluar.lower():
                    return regla, regla.accion
            elif regla.condicion_operador == 'igual_a':
                if regla.condicion_valor.lower() == valor_a_evaluar.lower():
                    return regla, regla.accion
        
        # Si ninguna regla coincide, procesar por defecto
        return None, 'procesar'