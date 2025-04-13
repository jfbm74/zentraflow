"""
Módulo de gestión de clientes (tenants) del sistema
"""

from flask import Blueprint

# Crear el blueprint para el módulo de clientes
clientes_bp = Blueprint('clientes', __name__, url_prefix='/clientes')

# Elimina esta línea que causa el problema circular
# from modules.clientes import routes