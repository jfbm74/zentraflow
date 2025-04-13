"""
Script para crear las tablas necesarias para el módulo de ingesta de correo
"""

from app import create_app
from database import db
from modules.ingesta_correo.models import CorreoIngestado, ReglaFiltrado

app = create_app('development')

with app.app_context():
    # Crear las tablas
    print("Creando tablas para el módulo de ingesta de correo...")
    db.create_all()
    
    print("Tablas creadas exitosamente!")
    
    # Verificar que las tablas se hayan creado correctamente
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    
    if 'correos_ingestados' in inspector.get_table_names():
        print("✅ Tabla correos_ingestados creada correctamente")
    else:
        print("❌ Error: No se pudo crear la tabla correos_ingestados")
        
    if 'reglas_filtrado' in inspector.get_table_names():
        print("✅ Tabla reglas_filtrado creada correctamente")
    else:
        print("❌ Error: No se pudo crear la tabla reglas_filtrado")