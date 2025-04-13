"""
Modelos relacionados con los clientes (tenants) del sistema SaaS
"""

from database import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class Cliente(db.Model):
    """Modelo para representar a cada cliente (tenant) en el sistema SaaS"""
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    nit = db.Column(db.String(20), unique=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    
    # Configuración específica del cliente
    config = db.Column(JSON, default={})
    
    # Configuración de correo para monitoreo
    config_correo = db.Column(JSON, default={})
    
    # Relaciones
    usuarios = db.relationship('Usuario', backref='cliente', lazy='dynamic', 
                              cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Cliente {self.nombre}>'
    
    @classmethod
    def obtener_por_nombre(cls, nombre):
        """Busca un cliente por su nombre"""
        return cls.query.filter_by(nombre=nombre).first()
    
    @classmethod
    def obtener_por_nit(cls, nit):
        """Busca un cliente por su NIT"""
        return cls.query.filter_by(nit=nit).first()
    
    @classmethod
    def listar_activos(cls):
        """Retorna todos los clientes activos"""
        return cls.query.filter_by(activo=True).all()