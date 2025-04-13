"""
Módulo de ingesta de correo
"""

from flask import Blueprint

# Crear el blueprint para el módulo de ingesta de correo
ingesta_correo_bp = Blueprint('ingesta_correo', __name__, url_prefix='/ingesta-correo')

# Importar rutas después de crear el blueprint
from . import routes