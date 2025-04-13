"""
Módulo del dashboard principal
"""

from flask import Blueprint

# Crear el blueprint para el dashboard
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

# Importar rutas después de crear el blueprint
from . import routes