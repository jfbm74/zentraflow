"""
Rutas para el módulo de ingesta de correo
"""

import json
from datetime import datetime, timedelta
from flask import render_template, g, session, jsonify, request, flash, redirect, url_for
from sqlalchemy.orm.attributes import flag_modified
from utils.auth import login_required, role_required
from . import ingesta_correo_bp
from .models import CorreoIngestado, ReglaFiltrado
from database import db
from modules.usuarios.models import RolUsuario
import logging
from datetime import datetime

# Configurar logger
logger = logging.getLogger(__name__)

@ingesta_correo_bp.route('/')
@login_required
@role_required(['admin', 'gestor', 'auditor'])
def ingesta_correo():
    """Ruta principal de ingesta de correo"""
    # Variables para el layout
    user_name = session.get('user_name', 'Usuario')
    user_email = session.get('user_email', '')
    
    # Obtener configuración de correo del cliente
    config_correo = {}
    estado_servicio = False
    if g.cliente and g.cliente.config and 'correo' in g.cliente.config:
        config_correo = g.cliente.config.get('correo', {})
        estado_servicio = config_correo.get('habilitado', False)
    
    # Obtener estadísticas de correos
    estadisticas = {}
    if g.cliente:
        try:
            estadisticas = CorreoIngestado.obtener_estadisticas(g.cliente.id)
        except Exception as e:
            logger.error(f"Error al obtener estadísticas: {str(e)}")
            flash(f"Error al obtener estadísticas: {str(e)}", "danger")
    
    # Obtener última verificación
    ultima_verificacion = None
    if g.cliente and g.cliente.config and 'correo' in g.cliente.config:
        if 'ultima_verificacion' in g.cliente.config['correo']:
            try:
                ultima_fecha = g.cliente.config['correo']['ultima_verificacion']
                if isinstance(ultima_fecha, str):
                    ultima_verificacion = datetime.fromisoformat(ultima_fecha)
                    # Calcular tiempo transcurrido
                    ahora = datetime.utcnow()
                    delta = ahora - ultima_verificacion
                    if delta.days > 0:
                        ultima_verificacion = f"Hace {delta.days} días"
                    elif delta.seconds >= 3600:
                        ultima_verificacion = f"Hace {delta.seconds // 3600} horas"
                    elif delta.seconds >= 60:
                        ultima_verificacion = f"Hace {delta.seconds // 60} minutos"
                    else:
                        ultima_verificacion = f"Hace {delta.seconds} segundos"
            except (ValueError, TypeError, KeyError) as e:
                logger.error(f"Error al procesar fecha de última verificación: {str(e)}")
                ultima_verificacion = "No disponible"
    
    # Obtener reglas de filtrado
    reglas = []
    if g.cliente:
        try:
            reglas = ReglaFiltrado.query.filter_by(cliente_id=g.cliente.id).all()
        except Exception as e:
            logger.error(f"Error al obtener reglas de filtrado: {str(e)}")
            flash(f"Error al obtener reglas de filtrado: {str(e)}", "danger")
    
    # Obtener correos recientes para el historial de actividad
    historial = []
    if g.cliente:
        try:
            # Obtener correos de los últimos 7 días
            fecha_desde = datetime.utcnow() - timedelta(days=7)
            correos = CorreoIngestado.query.filter(
                CorreoIngestado.cliente_id == g.cliente.id,
                CorreoIngestado.fecha_recepcion >= fecha_desde
            ).order_by(CorreoIngestado.fecha_recepcion.desc()).limit(100).all()
            
            # Formatear para el historial
            for correo in correos:
                historial.append({
                    'fecha': correo.fecha_recepcion.strftime('%Y-%m-%d %H:%M:%S'),
                    'evento': 'Correo recibido',
                    'detalles': f'De: {correo.remitente}, Asunto: {correo.asunto}',
                    'estado': correo.estado
                })
                
                # Si fue procesado, agregar entrada para los adjuntos
                if correo.estado == 'procesado' and correo.adjuntos_detectados > 0:
                    historial.append({
                        'fecha': (correo.fecha_procesamiento or correo.fecha_recepcion).strftime('%Y-%m-%d %H:%M:%S'),
                        'evento': 'Adjunto extraído',
                        'detalles': f'{correo.adjuntos_detectados} archivo(s) procesado(s)',
                        'estado': 'éxito'
                    })
                
        except Exception as e:
            logger.error(f"Error al obtener historial de actividad: {str(e)}")
            flash(f"Error al obtener historial de actividad: {str(e)}", "danger")

    fecha_actual = datetime.utcnow()
    
    return render_template('ingesta_correo.html',
                     config_correo=config_correo,
                     estado_servicio=estado_servicio,
                     estadisticas=estadisticas,
                     ultima_verificacion=ultima_verificacion,
                     reglas=reglas,
                     historial=historial,
                     fecha_actual=fecha_actual,  
                     cliente=g.cliente,
                     usuario=g.usuario,
                     user_name=user_name,
                     user_email=user_email)

@ingesta_correo_bp.route('/verificar', methods=['POST'])
@login_required
@role_required(['admin', 'gestor'])
def verificar_ahora():
    """Ejecuta una verificación manual del buzón de correo"""
    if not g.cliente:
        return jsonify({'success': False, 'message': 'Cliente no encontrado'})
    
    try:
        # Verificar que la ingesta esté configurada y habilitada
        if not g.cliente.config or 'correo' not in g.cliente.config:
            return jsonify({'success': False, 'message': 'La ingesta de correo no está configurada'})
        
        config_correo = g.cliente.config['correo']
        if not config_correo.get('habilitado', False):
            return jsonify({'success': False, 'message': 'La ingesta de correo está deshabilitada'})
        
        # Aquí iría la lógica para ejecutar la tarea de verificación
        # Por ahora, es un placeholder que simula una verificación
        
        # Para la demo, vamos a simular que encontramos algunos correos
        # En un entorno real, esto se conectaría con un worker de Celery o APScheduler
        
        # Actualizar la última verificación
        config_correo['ultima_verificacion'] = datetime.utcnow().isoformat()
        g.cliente.config['correo'] = config_correo
        
        # Crear registros de ejemplo para demostración
        from random import randint, choice
        
        num_correos = randint(1, 3)  # Simular entre 1 y 3 correos nuevos
        remitentes = [
            'notificaciones@segurossalud.com', 
            'glosas@mediseguro.com', 
            'facturacion@proteccionsalud.com'
        ]
        
        asuntos = [
            'GLOSA Factura F-2023-{}'.format(randint(1000, 9999)),
            'Notificación de Glosa #{}'.format(randint(100, 999)),
            'Factura glosada #{}'.format(randint(100, 999))
        ]
        
        for i in range(num_correos):
            nuevo_correo = CorreoIngestado(
                cliente_id=g.cliente.id,
                message_id_google=f"msg_{datetime.utcnow().timestamp()}_{i}",
                remitente=choice(remitentes),
                asunto=choice(asuntos),
                fecha_recepcion=datetime.utcnow(),
                estado='pendiente',
                adjuntos_detectados=randint(0, 2)
            )
            db.session.add(nuevo_correo)
        
        # Guardar cambios
        flag_modified(g.cliente, 'config')
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Verificación realizada correctamente. Se encontraron {num_correos} correos nuevos.'
        })
        
    except Exception as e:
        logger.error(f"Error al realizar verificación manual: {str(e)}")
        return jsonify({'success': False, 'message': f'Error al verificar: {str(e)}'})

@ingesta_correo_bp.route('/toggle-servicio', methods=['POST'])
@login_required
@role_required(['admin'])
def toggle_servicio():
    """Activa o desactiva el servicio de ingesta de correo"""
    if not g.cliente:
        return jsonify({'success': False, 'message': 'Cliente no encontrado'})
    
    try:
        # Obtener el estado deseado del cuerpo de la solicitud
        data = request.get_json()
        nuevo_estado = data.get('active', False) if data else False
        
        # Verificar que exista la configuración
        if not g.cliente.config:
            g.cliente.config = {}
        
        if 'correo' not in g.cliente.config:
            g.cliente.config['correo'] = {}
        
        # Actualizar el estado
        g.cliente.config['correo']['habilitado'] = nuevo_estado
        
        # Actualizar el log de cambios
        accion = "activado" if nuevo_estado else "desactivado"
        g.cliente.config['correo']['ultima_modificacion'] = {
            'fecha': datetime.utcnow().isoformat(),
            'usuario_id': g.usuario.id,
            'accion': f"Servicio {accion}"
        }
        
        # Guardar cambios
        flag_modified(g.cliente, 'config')
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Servicio de ingesta {accion} correctamente',
            'estado': nuevo_estado
        })
        
    except Exception as e:
        logger.error(f"Error al cambiar estado del servicio: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@ingesta_correo_bp.route('/reglas', methods=['POST'])
@login_required
@role_required(['admin', 'gestor'])
def crear_regla():
    """Crea una nueva regla de filtrado"""
    if not g.cliente:
        return jsonify({'success': False, 'message': 'Cliente no encontrado'})
    
    try:
        # Obtener datos del formulario
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No se recibieron datos'})
        
        # Validar datos
        if not data.get('nombre') or not data.get('condicion_valor'):
            return jsonify({'success': False, 'message': 'Faltan campos obligatorios'})
        
        # Crear nueva regla
        regla = ReglaFiltrado(
            cliente_id=g.cliente.id,
            nombre=data.get('nombre'),
            condicion_tipo=data.get('condicion_tipo', 'remitente'),
            condicion_operador=data.get('condicion_operador', 'contiene'),
            condicion_valor=data.get('condicion_valor'),
            accion=data.get('accion', 'procesar'),
            estado='activa' if data.get('estado', True) else 'inactiva'
        )
        
        db.session.add(regla)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Regla creada correctamente',
            'regla': {
                'id': regla.id,
                'nombre': regla.nombre,
                'condicion_tipo': regla.condicion_tipo,
                'condicion_operador': regla.condicion_operador,
                'condicion_valor': regla.condicion_valor,
                'accion': regla.accion,
                'estado': regla.estado
            }
        })
        
    except Exception as e:
        logger.error(f"Error al crear regla: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})