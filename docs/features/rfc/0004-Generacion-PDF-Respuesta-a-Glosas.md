# RFC-0004: Generación de PDF de Respuesta a Glosas

## Objetivo
Diseñar un módulo que permita generar documentos PDF estructurados como respuesta oficial a las glosas, usando plantillas configurables y datos provenientes del flujo de trabajo.

## Alcance
Este RFC cubre:
- Selección y aplicación de plantillas PDF
- Generación automática desde el flujo de trabajo
- Generación manual desde interfaz
- Registro de historial y control de errores

## Requisitos Funcionales
- Soporte para múltiples plantillas (por aseguradora o formato)
- Vista previa antes de generar
- Incluir firma digital (opcional)
- Adjuntar documentos adicionales (opcional)
- Historial de generación accesible

## Diseño Técnico

### Motor de Generación
- Tecnología sugerida: `WeasyPrint`, `wkhtmltopdf`, o `reportlab` (Python)
- Conversión de HTML/CSS a PDF basada en plantilla seleccionada
- Plantillas almacenadas como archivos HTML parametrizables

### Proceso Automático
- Se dispara al finalizar la etapa de revisión en el flujo de trabajo
- La plantilla por defecto se selecciona según aseguradora o configuración general
- El documento generado se guarda en el sistema con metadatos

### Proceso Manual
- Usuario puede seleccionar manualmente:
  - La glosa a procesar
  - La plantilla a utilizar
  - Opción de incluir anexos o firma digital
- Botón de “Generar PDF” muestra vista previa antes de confirmar

## Componentes del Documento PDF
- Encabezado con logo de la clínica y datos de contacto
- Datos generales de la glosa: número, factura, aseguradora, fecha
- Tabla detallada por ítem glosado:
  - Código, descripción, valor glosado, decisión, valor aceptado, valor no aceptado, justificación
- Resumen de totales
- Observaciones o argumentos generales (si aplica)
- Pie de página con sello/nota de generación automática

## Endpoints / Rutas Propuestas
- `GET /generacion-pdf` → Panel principal del módulo
- `POST /generacion-pdf/manual` → Generar desde selección manual
- `POST /generacion-pdf/auto` → Trigger desde flujo de trabajo
- `GET /generacion-pdf/historial` → Ver historial y estado de documentos generados

## Modelos de Datos
### DocumentoPDF
- `id`: UUID
- `id_glosa`: UUID
- `plantilla`: string
- `fecha_generacion`: datetime
- `estado`: ['completado', 'error']
- `tamaño_kb`: int
- `usuario_generador`: string
- `firma_incluida`: bool

### PlantillaPDF
- `id`: UUID
- `nombre`: string
- `descripcion`: string
- `formato_html`: archivo o string
- `estado`: ['activa', 'en_prueba', 'inactiva']
- `tipo`: ['estándar', 'minimalista', 'personalizada']

## Seguridad
- Sanitización de datos antes de renderizado
- Validación de firma digital y autenticación del usuario

## Dependencias
- RFC-0003: Flujo de Trabajo (para trigger automático)
- Base de datos central de glosas y decisiones

## Historial y Auditoría
- Cada generación de PDF queda registrada con:
  - Usuario que generó
  - Plantilla usada
  - Estado del proceso (éxito / error)
  - Fecha y hora

## Estado Esperado del MVP
✅ Generación de PDF con plantilla estándar
✅ Historial básico de documentos generados
✅ Selector manual de plantilla y glosa
❌ Vista previa y firma digital (fase siguiente)
❌ Plantillas avanzadas por aseguradora (fase posterior)

