"""
Modelos para el módulo de ingesta de correo
"""

from database import db
from datetime import datetime, timedelta
from sqlalchemy import func

class CorreoIngestado(db.Model):
    """Modelo para registrar los correos procesados por el sistema de ingesta"""
    __tablename__ = 'correos_ingestados'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    message_id_google = db.Column(db.String(255), unique=True)
    remitente = db.Column(db.String(255), nullable=False)
    asunto = db.Column(db.String(500), nullable=False)
    fecha_recepcion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_procesamiento = db.Column(db.DateTime)
    
    estado = db.Column(db.String(50), default='pendiente')  # pendiente, procesado, ignorado, error_filtrado, error_descarga, error_handoff
    adjuntos_detectados = db.Column(db.Integer, default=0)
    regla_aplicada_id = db.Column(db.Integer, nullable=True)
    detalles_error = db.Column(db.Text, nullable=True)
    
    # Relación con Cliente
    cliente = db.relationship('Cliente', backref='correos_ingestados')
    
    def __repr__(self):
        return f"<CorreoIngestado {self.id} - {self.asunto}>"
    
    @classmethod
    def obtener_estadisticas(cls, cliente_id, horas=24):
        """
        Obtiene estadísticas de correos procesados para un cliente específico
        en las últimas n horas
        """
        fecha_desde = datetime.utcnow() - timedelta(hours=horas)
        
        # Contar correos por estado
        estadisticas = {}
        
        # Total de correos
        total = cls.query.filter(
            cls.cliente_id == cliente_id,
            cls.fecha_recepcion >= fecha_desde
        ).count()
        
        # Correos por estado
        estados = ['pendiente', 'procesado', 'ignorado', 'error_filtrado', 'error_descarga', 'error_handoff']
        for estado in estados:
            count = cls.query.filter(
                cls.cliente_id == cliente_id,
                cls.estado == estado,
                cls.fecha_recepcion >= fecha_desde
            ).count()
            estadisticas[estado] = count
        
        # Agregar total
        estadisticas['total'] = total
        
        # Contar glosas extraídas (simulado para MVP)
        # En producción, esto se vincularía con el módulo de extracción de datos
        estadisticas['glosas_extraidas'] = cls.query.filter(
            cls.cliente_id == cliente_id,
            cls.estado == 'procesado',
            cls.fecha_recepcion >= fecha_desde
        ).count() * 0.7  # Simular que aprox. 70% de los correos generan glosas
        
        # Último correo procesado
        ultimo_correo = cls.query.filter(
            cls.cliente_id == cliente_id,
            cls.estado.in_(['procesado', 'ignorado'])
        ).order_by(cls.fecha_procesamiento.desc()).first()
        
        if ultimo_correo:
            estadisticas['ultimo_procesado'] = ultimo_correo.fecha_procesamiento
        else:
            estadisticas['ultimo_procesado'] = None
        
        return estadisticas


class ReglaFiltrado(db.Model):
    """Modelo para reglas de filtrado de correos"""
    __tablename__ = 'reglas_filtrado'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    condicion_tipo = db.Column(db.String(50), nullable=False)  # remitente, asunto, cuerpo, adjunto
    condicion_operador = db.Column(db.String(50), nullable=False)  # contiene, no_contiene, igual_a
    condicion_valor = db.Column(db.String(255), nullable=False)
    accion = db.Column(db.String(50), nullable=False)  # procesar, ignorar, marcar
    prioridad = db.Column(db.Integer, default=0)
    estado = db.Column(db.String(20), default='activa')  # activa, inactiva
    
    # Relación con Cliente
    cliente = db.relationship('Cliente', backref='reglas_filtrado')
    
    def __repr__(self):
        return f"<ReglaFiltrado {self.id} - {self.nombre}>"
    
    @classmethod
    def obtener_reglas_activas(cls, cliente_id):
        """Obtiene todas las reglas activas para un cliente"""
        return cls.query.filter(
            cls.cliente_id == cliente_id,
            cls.estado == 'activa'
        ).order_by(cls.prioridad).all()