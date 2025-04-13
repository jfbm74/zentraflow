"""
Configuración de la aplicación Glosas Pro SaaS
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración base para todas las configuraciones"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-replace-in-production')
    
    # Configuración de la base de datos
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        'postgresql://postgres:password@localhost:5432/zentraflow'
    )

class DevelopmentConfig(Config):
    """Configuración para entorno de desarrollo"""
    DEBUG = True

class TestingConfig(Config):
    """Configuración para entorno de pruebas"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TEST_DATABASE_URL', 
        'postgresql://postgres:password@localhost:5432/zentraflow_test'
    )

class ProductionConfig(Config):
    """Configuración para entorno de producción"""
    DEBUG = False
    # En producción, asegúrate de tener configurada adecuadamente la SECRET_KEY
    
    # Opciones adicionales para producción
    # SESSION_COOKIE_SECURE = True  # Para usar solo con HTTPS
    # REMEMBER_COOKIE_SECURE = True
    # REMEMBER_COOKIE_HTTPONLY = True

# Diccionario para seleccionar la configuración según el entorno
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}