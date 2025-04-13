# RFC-0002: Extracción de Datos desde Adjuntos de Glosas

## Objetivo
Desarrollar un módulo capaz de procesar archivos adjuntos recibidos (Excel, PDF, escaneados), extraer las tablas de datos correspondientes a las glosas y convertir esta información en registros estructurados para ser almacenados y gestionados por el sistema.

## Alcance
- Detección del tipo de archivo (Excel, PDF, escaneado)
- Aplicación de plantilla de extracción según aseguradora y tipo de documento
- Proceso OCR en caso de documentos escaneados
- Validación básica de los datos extraídos
- Envío de resultados al módulo de flujo de trabajo

## Diseño Técnico

### Tipos de Entrada Soportados
- Excel: `.xlsx`, `.xls`, `.csv`
- PDF: texto digital y escaneado (requiere OCR)
- Imagen: `.jpg`, `.png`, `.tiff` (OCR obligatorio)

### Componentes

#### 1. **Detectores de Formato y Ruteo**
- Identifica el tipo de archivo recibido
- Asigna el extractor adecuado: ExcelParser, PDFParser, OCRProcessor

#### 2. **Plantillas de Extracción**
- Cada aseguradora puede tener una o más plantillas activas
- Las plantillas definen:
  - Rango de celdas/tablas
  - Columnas relevantes (Código, Descripción, Valor Glosado, Causal)
  - Mapeo entre cabecera y campo interno del sistema

#### 3. **Módulo de OCR (si aplica)**
- Motor OCR para procesar PDFs escaneados o imágenes
- Puede usar Tesseract OCR o servicios como AWS Textract, Azure Form Recognizer
- OCR solo se activa si el tipo de archivo lo requiere o si se fuerza manualmente

#### 4. **Validación de Datos Extraídos**
- Validaciones básicas:
  - Campos obligatorios presentes
  - Valores numéricos válidos
  - Columnas esperadas detectadas correctamente
- Los errores se notifican en la interfaz y se registran en log

#### 5. **Gestión Manual Opcional**
- El usuario puede subir archivos manualmente y seleccionar la plantilla deseada
- Botón para forzar OCR en caso de ser necesario

## Endpoints / Rutas Propuestas
- `GET /extraccion-datos` → Panel de control del módulo
- `POST /extraccion-datos/procesar` → Procesamiento manual de archivo subido
- `GET /extraccion-datos/logs` → Visualización de estadísticas y errores
- `GET/POST /extraccion-datos/plantillas` → Gestión de plantillas de extracción

## Modelos de Datos
### DocumentoProcesado
- `id`: UUID
- `tipo_archivo`: ['excel', 'pdf', 'imagen']
- `nombre_archivo`: string
- `estado`: ['completado', 'error', 'ocr_requerido', 'pendiente']
- `aseguradora_detectada`: string (opcional)
- `plantilla_usada`: string
- `fecha_procesamiento`: datetime
- `log_errores`: texto (opcional)

### PlantillaExtraccion
- `id`: UUID
- `aseguradora`: string
- `tipo_documento`: string
- `formato`: ['excel', 'pdf', 'ocr']
- `estado`: ['activa', 'en_prueba', 'inactiva']
- `definicion`: JSON (estructura de mapeo de columnas)

## Seguridad
- Verificación del tipo de archivo y tamaño
- Aislamiento del proceso de extracción para evitar errores que impacten todo el sistema
- OCR sandboxed para evitar fugas de datos

## Dependencias
- RFC-0001 (los adjuntos provienen del módulo de ingesta)
- Módulo de flujo de trabajo para registrar ítems glosados extraídos

## Historial y Auditoría
- Registro por documento procesado con:
  - Resultado del análisis
  - Plantilla usada
  - Errores detectados
- Panel con estadísticas (documentos procesados, tasa de éxito, pendientes, errores)

## Estado Esperado del MVP
✅ Extracción de archivos Excel con plantilla predefinida
✅ Gestión básica de plantillas
✅ Registro de logs y errores
✅ Interfaz para extracción manual
❌ Extracción PDF avanzada con OCR automático (fase posterior)
❌ Validación cruzada con estructura de factura (etapa futura)

