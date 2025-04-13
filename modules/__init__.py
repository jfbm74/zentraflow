"""
Inicializador de módulos de la aplicación
"""

def init_app(app):
    """Registra todos los blueprints de los módulos en la aplicación Flask"""
    
    # Importar blueprints de los módulos
    from modules.clientes import clientes_bp
    from modules.usuarios import usuarios_bp
    from dashboard import dashboard_bp
    from auth.routes import auth_bp
    
    # Registrar blueprints
    app.register_blueprint(clientes_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(auth_bp, url_prefix='/auth')