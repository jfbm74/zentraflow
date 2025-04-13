"""
Módulo de autenticación OAuth para ZentraFlow
"""

from flask import Blueprint

oauth_bp = Blueprint('oauth', __name__, url_prefix='/oauth')

from . import routes 