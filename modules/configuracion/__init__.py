"""
Módulo de configuración del sistema
"""

from flask import Blueprint

configuracion_bp = Blueprint('configuracion', __name__, url_prefix='/configuracion')

from . import routes 