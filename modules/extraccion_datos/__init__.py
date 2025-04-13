"""
Módulo de extracción de datos
"""

from flask import Blueprint

extraccion_datos_bp = Blueprint('extraccion_datos', __name__)

from . import routes 