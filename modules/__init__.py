"""
Asegurar que el módulo de ingesta_correo esté correctamente importado en init_app
"""

# En modules/__init__.py actualiza la función init_app para incluir correctamente
# el blueprint de ingesta_correo si aún no está importado

def init_app(app):
    """Registra todos los blueprints de los módulos en la aplicación Flask"""
    
    # Importar blueprints de los módulos
    from modules.clientes import clientes_bp
    from modules.usuarios import usuarios_bp
    from modules.glosas import glosas_bp
    from dashboard import dashboard_bp
    from auth.routes import auth_bp
    from modules.ingesta_correo import ingesta_correo_bp  # Asegúrate de que esta línea esté presente
    from modules.extraccion_datos import extraccion_datos_bp
    from modules.flujo_trabajo import flujo_trabajo_bp
    from modules.generacion_pdf import generacion_pdf_bp
    from modules.reportes import reportes_bp
    from modules.configuracion import configuracion_bp
    
    # Registrar blueprints
    app.register_blueprint(clientes_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(glosas_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(ingesta_correo_bp)  # Asegúrate de que esta línea esté presente
    app.register_blueprint(extraccion_datos_bp)
    app.register_blueprint(flujo_trabajo_bp)
    app.register_blueprint(generacion_pdf_bp)
    app.register_blueprint(reportes_bp)
    app.register_blueprint(configuracion_bp)