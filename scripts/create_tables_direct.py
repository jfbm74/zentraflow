"""
Script para crear las tablas necesarias para el módulo de ingesta de correo

Este script debe ejecutarse desde la raíz del proyecto.
"""

# Agregar el directorio actual al path de Python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from sqlalchemy import text
from modules.ingesta_correo.models import CorreoIngestado, ReglaFiltrado

print("Creando tablas para el módulo de ingesta de correo...")

with app.app_context():
    # Crear las tablas
    try:
        # Intentar crear la tabla correos_ingestados
        db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS correos_ingestados (
            id SERIAL PRIMARY KEY,
            cliente_id INTEGER NOT NULL REFERENCES clientes(id),
            message_id_google VARCHAR(255) UNIQUE,
            remitente VARCHAR(255) NOT NULL,
            asunto VARCHAR(500) NOT NULL,
            fecha_recepcion TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            fecha_procesamiento TIMESTAMP WITHOUT TIME ZONE,
            estado VARCHAR(50) DEFAULT 'pendiente',
            adjuntos_detectados INTEGER DEFAULT 0,
            regla_aplicada_id INTEGER,
            detalles_error TEXT
        )
        """))
        
        # Intentar crear la tabla reglas_filtrado
        db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS reglas_filtrado (
            id SERIAL PRIMARY KEY,
            cliente_id INTEGER NOT NULL REFERENCES clientes(id),
            nombre VARCHAR(100) NOT NULL,
            condicion_tipo VARCHAR(50) NOT NULL,
            condicion_operador VARCHAR(50) NOT NULL,
            condicion_valor VARCHAR(255) NOT NULL,
            accion VARCHAR(50) NOT NULL,
            prioridad INTEGER DEFAULT 0,
            estado VARCHAR(20) DEFAULT 'activa'
        )
        """))
        
        db.session.commit()
        print("✅ Tablas creadas exitosamente!")
        
        # Verificar que las tablas se hayan creado
        result = db.session.execute(text("SELECT to_regclass('correos_ingestados')"))
        table_exists = result.scalar() is not None
        print(f"Tabla correos_ingestados existe: {table_exists}")
        
        result = db.session.execute(text("SELECT to_regclass('reglas_filtrado')"))
        table_exists = result.scalar() is not None
        print(f"Tabla reglas_filtrado existe: {table_exists}")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al crear las tablas: {str(e)}")