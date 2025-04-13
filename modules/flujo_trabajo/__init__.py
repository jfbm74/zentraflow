"""
Módulo de flujo de trabajo
"""

from flask import Blueprint

flujo_trabajo_bp = Blueprint('flujo_trabajo', __name__)

from . import routes 