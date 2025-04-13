## Reglas para uso de Cursor AI

- Lenguaje: Python 3.11+
- Framework: Flask con SQLAlchemy
- Estructura de carpetas:
  - modules/
    - ingestion/
    - parsing/
    - workflows/
    - pdf_generation/
- Convenciones:
  - Modelos en `models.py` dentro de cada módulo.
  - Uso de `Blueprints` para organizar vistas.
  - Estándar PEP8 para estilo de código.