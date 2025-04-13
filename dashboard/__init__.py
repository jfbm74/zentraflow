"""
Módulo del dashboard principal
"""

from flask import Blueprint

# Crear el blueprint para el dashboard
dashboard_bp = Blueprint('dashboard', __name__)

# Importar rutas
from dashboard import routes