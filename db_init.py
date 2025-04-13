"""
Script simple para inicializar la base de datos sin importaciones circulares
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Crear app Flask
app = Flask(__name__)

# Configuración de BD
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 
    'postgresql://juan.bustamante@localhost:5432/zentraflow'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar DB
db = SQLAlchemy(app)

# Definir modelos aquí directamente, sin importar de los módulos
# Definir Cliente
class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    nit = db.Column(db.String(20), unique=True)
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())
    activo = db.Column(db.Boolean, default=True)
    config = db.Column(db.JSON, default={})
    config_correo = db.Column(db.JSON, default={})

# Enum para roles
import enum
class RolUsuario(enum.Enum):
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"
    GESTOR = "gestor"
    AUDITOR = "auditor"
    VISUALIZADOR = "visualizador"

# Definir Usuario
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    _password = db.Column('password', db.String(256), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100))
    rol = db.Column(db.Enum(RolUsuario), nullable=False, default=RolUsuario.VISUALIZADOR)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())
    ultimo_acceso = db.Column(db.DateTime)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)

# Definir otros modelos necesarios
class Permiso(db.Model):
    __tablename__ = 'permisos'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)

class PermisoRol(db.Model):
    __tablename__ = 'permisos_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    rol = db.Column(db.Enum(RolUsuario), nullable=False)
    permiso_id = db.Column(db.Integer, db.ForeignKey('permisos.id'), nullable=False)
    
    # Índice único
    __table_args__ = (db.UniqueConstraint('rol', 'permiso_id', name='uq_rol_permiso'),)

class SesionUsuario(db.Model):
    __tablename__ = 'sesiones_usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    ip = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    fecha_inicio = db.Column(db.DateTime, default=db.func.current_timestamp())
    fecha_fin = db.Column(db.DateTime)
    token = db.Column(db.String(255))

# Inicializar migraciones
migrate = Migrate(app, db)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Tablas creadas exitosamente!")