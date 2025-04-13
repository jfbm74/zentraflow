"""
Módulo de generación de PDF para ZentraFlow
"""

from flask import Blueprint

generacion_pdf_bp = Blueprint('generacion_pdf', __name__, url_prefix='/generacion-pdf')

from . import routes 