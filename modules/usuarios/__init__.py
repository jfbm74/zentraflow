"""
Módulo de gestión de usuarios del sistema
"""

from flask import Blueprint

# Crear el blueprint para el módulo de usuarios
usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

# Elimina esta línea que causa el problema circular
# from modules.usuarios import routes