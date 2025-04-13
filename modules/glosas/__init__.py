"""
Módulo de gestión de glosas
"""

from flask import Blueprint

# Crear el blueprint para el módulo de glosas
glosas_bp = Blueprint('glosas', __name__, url_prefix='/glosas')

# Importar rutas después de crear el blueprint
from . import routes 