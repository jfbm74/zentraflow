"""
Modelos relacionados con usuarios y autenticación
"""

from database import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import enum
from sqlalchemy.ext.hybrid import hybrid_property

class RolUsuario(enum.Enum):
    """Definición de roles de usuario en el sistema"""
    ADMIN = "admin"              # Administrador del sistema a nivel cliente
    SUPER_ADMIN = "super_admin"  # Administrador global (personal de Zentratek)
    GESTOR = "gestor"            # Gestor de glosas
    AUDITOR = "auditor"          # Auditor médico o financiero
    VISUALIZADOR = "visualizador"  # Solo lectura

class Usuario(db.Model):
    """Modelo para los usuarios del sistema"""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    _password = db.Column('password', db.String(256), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100))
    rol = db.Column(db.Enum(RolUsuario), nullable=False, default=RolUsuario.VISUALIZADOR)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acceso = db.Column(db.DateTime)
    
    # Relación con Cliente (tenant)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    
    @property
    def password(self):
        """Previene el acceso directo a la contraseña"""
        raise AttributeError('La contraseña no es un atributo legible')
    
    @password.setter
    def password(self, password):
        """Establece la contraseña hasheada"""
        self._password = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica la contraseña"""
        return check_password_hash(self._password, password)
    
    @hybrid_property
    def nombre_completo(self):
        """Retorna el nombre completo del usuario"""
        if self.apellido:
            return f"{self.nombre} {self.apellido}"
        return self.nombre
    
    def __repr__(self):
        return f'<Usuario {self.email}>'
    
    @classmethod
    def obtener_por_email(cls, email):
        """Busca un usuario por su email"""
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def listar_por_cliente(cls, cliente_id):
        """Lista todos los usuarios de un cliente específico"""
        return cls.query.filter_by(cliente_id=cliente_id).all()
    
    def tiene_permiso(self, permisos_requeridos):
        """
        Verifica si el usuario tiene los permisos requeridos
        
        Args:
            permisos_requeridos: Lista de roles que tienen permiso
            
        Returns:
            bool: True si el usuario tiene el permiso, False en caso contrario
        """
        # Convertir a lista si es un solo rol
        if isinstance(permisos_requeridos, str):
            permisos_requeridos = [permisos_requeridos]
            
        # El Super Admin siempre tiene acceso a todo
        if self.rol == RolUsuario.SUPER_ADMIN:
            return True
        
        # Verificar si el rol del usuario está en la lista de permisos
        return self.rol.value in permisos_requeridos


class Permiso(db.Model):
    """Modelo para gestionar permisos específicos por recurso"""
    __tablename__ = 'permisos'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Permiso {self.codigo}>'


class PermisoRol(db.Model):
    """Tabla intermedia para relacionar roles con permisos específicos"""
    __tablename__ = 'permisos_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    rol = db.Column(db.Enum(RolUsuario), nullable=False)
    permiso_id = db.Column(db.Integer, db.ForeignKey('permisos.id'), nullable=False)
    
    # Relación con Permiso
    permiso = db.relationship('Permiso', backref='roles')
    
    # Índice único para evitar duplicados
    __table_args__ = (db.UniqueConstraint('rol', 'permiso_id', name='uq_rol_permiso'),)
    
    def __repr__(self):
        return f'<PermisoRol {self.rol.value} - {self.permiso_id}>'


class SesionUsuario(db.Model):
    """Modelo para registrar las sesiones de los usuarios"""
    __tablename__ = 'sesiones_usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    ip = db.Column(db.String(45))  # IPv6 puede ser hasta 45 caracteres
    user_agent = db.Column(db.String(255))
    fecha_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_fin = db.Column(db.DateTime)
    token = db.Column(db.String(255))
    
    # Relación con Usuario
    usuario = db.relationship('Usuario', backref='sesiones')
    
    def __repr__(self):
        return f'<SesionUsuario {self.usuario_id} - {self.fecha_inicio}>'