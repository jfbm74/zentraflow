"""
Gestor de migraciones para la base de datos.
Este archivo se usa específicamente para gestionar migraciones
separado de la aplicación principal para evitar problemas de importación.
"""

from flask import Flask
from flask_migrate import Migrate
from database import db
from config import config

# Importar modelos para que Flask-Migrate los detecte
from modules.clientes.models import Cliente
from modules.usuarios.models import Usuario, RolUsuario, Permiso, PermisoRol, SesionUsuario

def create_app(config_name='default'):
    """Crear una aplicación Flask para migraciones"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializar base de datos
    db.init_app(app)
    migrate = Migrate(app, db)
    
    return app

if __name__ == '__main__':
    # Crear la aplicación usando el entorno configurado o 'default' si no existe
    app = create_app()
    print("Aplicación de migraciones configurada correctamente.")