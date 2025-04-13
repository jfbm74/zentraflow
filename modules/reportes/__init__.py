"""
Módulo de reportes para ZentraFlow
"""

from flask import Blueprint

reportes_bp = Blueprint('reportes', __name__, url_prefix='/reportes')

from . import routes 