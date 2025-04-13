"""
Punto de entrada principal para la aplicación Glosas Pro SaaS
"""

from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify, g
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importar configuraciones
from config import config
from database import db, init_db
from modules.usuarios.models import Usuario

def create_app(config_name='default'):
    """Factory pattern para crear la aplicación Flask con toda la configuración"""
    app = Flask(__name__)
    
    # Cargar configuración según el entorno
    app.config.from_object(config[config_name])
    
    # Inicializar base de datos
    init_db(app)
    
    # Registrar blueprints
    from modules import init_app as init_modules
    init_modules(app)
    
    # Manejadores de error
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
    
    # Middleware para verificar el cliente (tenant) basado en el usuario en sesión
    @app.before_request
    def set_cliente_from_session():
        if 'user_id' in session and request.endpoint not in ['auth.login', 'auth.logout', 'static']:
            user_id = session.get('user_id')
            user = Usuario.query.get(user_id)
            if user:
                # Establecer variables globales para la plantilla
                g.cliente = user.cliente
                g.usuario = user
            else:
                session.clear()
                flash('Sesión inválida. Por favor inicie sesión nuevamente.', 'danger')
                return redirect(url_for('auth.login'))
    
    # Funciones de contexto global para templates
    @app.context_processor
    def utility_processor():
        def format_currency(amount):
            if amount is None:
                return "$ 0"
            return f"$ {amount:,.2f}"
        
        return dict(format_currency=format_currency)
    
    return app

# Crear la aplicación usando el entorno configurado o 'default' si no existe
env = os.environ.get('FLASK_ENV', 'default')
app = create_app(env)

# Para ejecutar la aplicación directamente con python app.py
if __name__ == '__main__':
    app.run(debug=True)