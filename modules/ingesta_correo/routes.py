"""
Rutas para el módulo de ingesta de correo
"""

import json
import io
import csv
from datetime import datetime, timedelta
from flask import render_template, g, session, jsonify, request, flash, redirect, url_for, send_file
from sqlalchemy.orm.attributes import flag_modified
from utils.auth import login_required, role_required
from . import ingesta_correo_bp
from .models import CorreoIngestado, ReglaFiltrado
from database import db
from modules.usuarios.models import RolUsuario
import logging
from .forms import ReglaFiltradoForm
from .services.ingesta_service import IngestaService
from googleapiclient.discovery import build
from dateutil import parser
from .services.gmail_service import get_gmail_service

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
    
    # Obtener parámetros de paginación
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Obtener correos recientes para el historial de actividad con paginación
    historial = []
    pagination = None
    if g.cliente:
        try:
            # Consultar con paginación
            query = CorreoIngestado.query.filter(
                CorreoIngestado.cliente_id == g.cliente.id
            ).order_by(CorreoIngestado.fecha_recepcion.desc())
            
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            
            # Formatear para el historial
            for correo in pagination.items:
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
                     pagination=pagination,
                     fecha_actual=fecha_actual,  
                     cliente=g.cliente,
                     usuario=g.usuario,
                     user_name=user_name,
                     user_email=user_email)

@ingesta_correo_bp.route('/verificar', methods=['POST'])
@login_required
def verificar():
    """Verifica los correos nuevos según las reglas configuradas"""
    try:
        # Obtener el servicio de Gmail
        gmail_service = get_gmail_service()
        if not gmail_service:
            return jsonify({'status': 'error', 'message': 'No se pudo conectar con Gmail'})

        # Obtener reglas del cliente actual
        reglas = ReglaFiltrado.query.filter_by(
            cliente_id=g.cliente.id,
            estado='activa'
        ).order_by(ReglaFiltrado.prioridad.desc()).all()
        
        if not reglas:
            return jsonify({'status': 'error', 'message': 'No hay reglas configuradas'})

        correos_procesados = []
        errores = []

        for regla in reglas:
            try:
                # Construir la consulta de búsqueda según el tipo de condición
                if regla.condicion_tipo == 'remitente':
                    query = f"from:{regla.condicion_valor}"
                elif regla.condicion_tipo == 'asunto':
                    query = f"subject:{regla.condicion_valor}"
                else:
                    continue  # Saltar reglas con tipos no soportados
                
                results = gmail_service.users().messages().list(userId='me', q=query).execute()
                messages = results.get('messages', [])

                for message in messages:
                    try:
                        # Verificar si el correo ya fue procesado
                        correo_existente = CorreoIngestado.query.filter_by(
                            message_id_google=message['id']
                        ).first()

                        if correo_existente:
                            continue  # Saltar este correo si ya existe

                        # Obtener detalles del mensaje
                        msg = gmail_service.users().messages().get(
                            userId='me', 
                            id=message['id']
                        ).execute()

                        # Extraer información del correo
                        headers = msg['payload']['headers']
                        subject = next(h['value'] for h in headers if h['name'].lower() == 'subject')
                        from_header = next(h['value'] for h in headers if h['name'].lower() == 'from')
                        date_header = next(h['value'] for h in headers if h['name'].lower() == 'date')
                        
                        # Convertir fecha de string a datetime
                        fecha_recepcion = parser.parse(date_header)

                        # Verificar adjuntos
                        tiene_adjuntos = 0
                        if 'parts' in msg['payload']:
                            tiene_adjuntos = 1 if any(
                                part.get('filename', '') != '' 
                                for part in msg['payload']['parts']
                            ) else 0

                        # Crear registro de correo ingestado
                        correo = CorreoIngestado(
                            cliente_id=g.cliente.id,
                            message_id_google=message['id'],
                            remitente=from_header,
                            asunto=subject,
                            fecha_recepcion=fecha_recepcion,
                            fecha_procesamiento=datetime.now(),
                            estado='procesado',
                            adjuntos_detectados=tiene_adjuntos,
                            regla_aplicada_id=regla.id
                        )
                        
                        try:
                            db.session.add(correo)
                            db.session.commit()
                            correos_procesados.append(message['id'])
                        except Exception as e:
                            db.session.rollback()
                            errores.append(f"Error al guardar correo en BD: {str(e)}")
                            continue

                        # Marcar como leído
                        try:
                            gmail_service.users().messages().modify(
                                userId='me',
                                id=message['id'],
                                body={'removeLabelIds': ['UNREAD']}
                            ).execute()
                        except Exception as e:
                            errores.append(f"Error al marcar como leído: {str(e)}")

                    except Exception as e:
                        errores.append(f"Error procesando mensaje {message['id']}: {str(e)}")
                        continue

            except Exception as e:
                errores.append(f"Error procesando regla {regla.id}: {str(e)}")
                continue

        # Preparar respuesta
        response = {
            'status': 'success' if not errores else 'warning',
            'correos_procesados': len(correos_procesados),
            'message': 'Verificación completada'
        }
        
        if errores:
            response['errores'] = errores

        return jsonify(response)

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error en verificación: {str(e)}'
        })

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
def crear_regla_legacy():
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
    

# Ruta para obtener todas las reglas del cliente actual
@ingesta_correo_bp.route('/api/reglas', methods=['GET'])
@login_required
@role_required(['admin', 'super_admin', 'gestor'])
def obtener_reglas():
    """Obtiene las reglas de filtrado del cliente actual"""
    try:
        # Obtener reglas ordenadas por prioridad
        reglas = ReglaFiltrado.query.filter_by(cliente_id=g.cliente.id).order_by(ReglaFiltrado.prioridad).all()
        
        # Convertir a formato JSON
        reglas_json = []
        for regla in reglas:
            reglas_json.append({
                'id': regla.id,
                'nombre': regla.nombre,
                'condicion_tipo': regla.condicion_tipo,
                'condicion_operador': regla.condicion_operador,
                'condicion_valor': regla.condicion_valor,
                'accion': regla.accion,
                'prioridad': regla.prioridad,
                'estado': regla.estado
            })
        
        return jsonify({'success': True, 'reglas': reglas_json})
    
    except Exception as e:
        logger.error(f"Error al obtener reglas: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

# Ruta para crear una nueva regla
@ingesta_correo_bp.route('/api/reglas', methods=['POST'])
@login_required
@role_required(['admin', 'super_admin'])
def crear_regla():
    """Crea una nueva regla de filtrado"""
    try:
        # Obtener datos del JSON
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No se recibieron datos'})
        
        # Crear formulario y validar
        form = ReglaFiltradoForm(data=data, meta={'csrf': False})
        
        if not form.validate():
            errores = {}
            for field, field_errors in form.errors.items():
                errores[field] = field_errors
            return jsonify({'success': False, 'errors': errores})
        
        # Determinar prioridad si no se proporcionó
        if not form.prioridad.data:
            # Obtener la prioridad máxima actual y sumar 1
            max_prioridad = db.session.query(db.func.max(ReglaFiltrado.prioridad)).\
                filter(ReglaFiltrado.cliente_id == g.cliente.id).scalar() or 0
            prioridad = max_prioridad + 10  # Dejamos espacio entre prioridades
        else:
            prioridad = form.prioridad.data
        
        # Crear nueva regla
        regla = ReglaFiltrado(
            cliente_id=g.cliente.id,
            nombre=form.nombre.data,
            condicion_tipo=form.condicion_tipo.data,
            condicion_operador=form.condicion_operador.data,
            condicion_valor=form.condicion_valor.data,
            accion=form.accion.data,
            prioridad=prioridad,
            estado='activa' if form.estado.data else 'inactiva'
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
                'prioridad': regla.prioridad,
                'estado': regla.estado
            }
        })
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al crear regla: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

# Ruta para actualizar una regla existente
@ingesta_correo_bp.route('/api/reglas/<int:id_regla>', methods=['PUT'])
@login_required
@role_required(['admin', 'super_admin'])
def actualizar_regla(id_regla):
    """Actualiza una regla de filtrado existente"""
    try:
        # Buscar regla y verificar que pertenezca al cliente actual
        regla = ReglaFiltrado.query.filter_by(id=id_regla, cliente_id=g.cliente.id).first_or_404()
        
        # Obtener datos del JSON
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No se recibieron datos'})
        
        # Crear formulario y validar
        form = ReglaFiltradoForm(data=data, meta={'csrf': False})
        
        if not form.validate():
            errores = {}
            for field, field_errors in form.errors.items():
                errores[field] = field_errors
            return jsonify({'success': False, 'errors': errores})
        
        # Actualizar regla
        regla.nombre = form.nombre.data
        regla.condicion_tipo = form.condicion_tipo.data
        regla.condicion_operador = form.condicion_operador.data
        regla.condicion_valor = form.condicion_valor.data
        regla.accion = form.accion.data
        
        if form.prioridad.data:
            regla.prioridad = form.prioridad.data
        
        regla.estado = 'activa' if form.estado.data else 'inactiva'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Regla actualizada correctamente',
            'regla': {
                'id': regla.id,
                'nombre': regla.nombre,
                'condicion_tipo': regla.condicion_tipo,
                'condicion_operador': regla.condicion_operador,
                'condicion_valor': regla.condicion_valor,
                'accion': regla.accion,
                'prioridad': regla.prioridad,
                'estado': regla.estado
            }
        })
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al actualizar regla: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

# Ruta para eliminar una regla
@ingesta_correo_bp.route('/api/reglas/<int:id_regla>', methods=['DELETE'])
@login_required
@role_required(['admin', 'super_admin'])
def eliminar_regla(id_regla):
    """Elimina una regla de filtrado"""
    try:
        # Buscar regla y verificar que pertenezca al cliente actual
        regla = ReglaFiltrado.query.filter_by(id=id_regla, cliente_id=g.cliente.id).first_or_404()
        
        # Eliminar regla
        db.session.delete(regla)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Regla eliminada correctamente'
        })
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al eliminar regla: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

# Ruta para activar/desactivar una regla
@ingesta_correo_bp.route('/api/reglas/<int:id_regla>/toggle', methods=['PATCH'])
@login_required
@role_required(['admin', 'super_admin'])
def toggle_regla(id_regla):
    """Activa o desactiva una regla de filtrado"""
    try:
        # Buscar regla y verificar que pertenezca al cliente actual
        regla = ReglaFiltrado.query.filter_by(id=id_regla, cliente_id=g.cliente.id).first_or_404()
        
        # Invertir estado
        nuevo_estado = 'inactiva' if regla.estado == 'activa' else 'activa'
        regla.estado = nuevo_estado
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Regla {nuevo_estado} correctamente',
            'nuevo_estado': nuevo_estado
        })
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error al cambiar estado de regla: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

# NUEVOS ENDPOINTS PARA EL RFC-0001-03

@ingesta_correo_bp.route('/api/logs')
@login_required
@role_required(['admin', 'super_admin', 'gestor', 'auditor'])
def api_logs():
    """API para obtener logs paginados del historial de actividad"""
    try:
        # Obtener parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Limitar per_page a un máximo razonable
        if per_page > 100:
            per_page = 100
        
        # Consultar logs paginados
        pagination = CorreoIngestado.query.filter_by(cliente_id=g.cliente.id)\
                                   .order_by(CorreoIngestado.fecha_recepcion.desc())\
                                   .paginate(page=page, per_page=per_page, error_out=False)
        
        # Preparar respuesta JSON
        logs_json = []
        for correo in pagination.items:
            logs_json.append({
                'id': correo.id,
                'fecha': correo.fecha_recepcion.strftime('%Y-%m-%d %H:%M:%S'),
                'evento': 'Correo recibido',
                'detalles': f'De: {correo.remitente}, Asunto: {correo.asunto}',
                'estado': correo.estado
            })
            
            # Si fue procesado, agregar entrada para los adjuntos
            if correo.estado == 'procesado' and correo.adjuntos_detectados > 0:
                logs_json.append({
                    'id': f"{correo.id}-adj",
                    'fecha': (correo.fecha_procesamiento or correo.fecha_recepcion).strftime('%Y-%m-%d %H:%M:%S'),
                    'evento': 'Adjunto extraído',
                    'detalles': f'{correo.adjuntos_detectados} archivo(s) procesado(s)',
                    'estado': 'éxito'
                })
        
        return jsonify({
            'success': True,
            'logs': logs_json,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev,
                'next_num': pagination.next_num,
                'prev_num': pagination.prev_num
            }
        })
    
    except Exception as e:
        logger.error(f"Error al obtener logs API: {str(e)}")
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@ingesta_correo_bp.route('/descargar-log')
@login_required
@role_required(['admin', 'super_admin', 'gestor', 'auditor'])
def descargar_log():
    """Descarga los logs de actividad en formato CSV"""
    try:
        # Obtener parámetro opcional de límite
        limit = request.args.get('limit', 100, type=int)
        if limit > 1000:  # Establecer un límite máximo razonable
            limit = 1000
            
        # Obtener logs ordenados por fecha
        logs = CorreoIngestado.query.filter_by(cliente_id=g.cliente.id)\
                             .order_by(CorreoIngestado.fecha_recepcion.desc())\
                             .limit(limit).all()
        
        # Crear archivo CSV en memoria
        si = io.StringIO()
        cw = csv.writer(si)
        
        # Escribir encabezados
        cw.writerow(['Fecha Recepción', 'Remitente', 'Asunto', 'Estado', 'Adjuntos', 'Detalles Error'])
        
        # Escribir datos
        for log in logs:
            cw.writerow([
                log.fecha_recepcion.strftime('%Y-%m-%d %H:%M:%S'),
                log.remitente,
                log.asunto,
                log.estado,
                log.adjuntos_detectados,
                log.detalles_error or ''
            ])
        
        # Crear bytes para enviar
        output = io.BytesIO(si.getvalue().encode('utf-8'))
        output.seek(0)
        
        # Generar nombre de archivo con timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"historial_ingesta_{g.cliente.id}_{timestamp}.csv"
        
        # Enviar archivo
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Error al descargar logs: {str(e)}")
        flash(f"Error al descargar el historial: {str(e)}", "danger")
        return redirect(url_for('ingesta_correo.ingesta_correo'))