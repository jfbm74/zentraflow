# RFC-0003: Configuración General del Cliente (Tenant)

## Objetivo
Proporcionar una interfaz dentro del Módulo de Configuración del Cliente (RFC-0002) donde los administradores puedan gestionar la información básica, la marca visual y las preferencias regionales de su organización (tenant) en la aplicación Glosas Pro SaaS.

## Alcance
Este RFC cubre:
- La pestaña/sección "General" dentro de la interfaz de configuración del cliente.
- Visualización y edición de información básica del cliente (Nombre, NIT).
- Funcionalidad para cargar y gestionar el logo del cliente (para usar en reportes, etc.).
- Configuración de preferencias regionales (Zona Horaria, Formato de Fecha, Formato de Moneda).

**Fuera de Alcance (Inicial):**
- Opciones de personalización de colores de la interfaz.
- Gestión de múltiples direcciones o contactos.
- Integración avanzada con sistemas de identidad del cliente.

## Diseño Técnico

### Tecnologías y Librerías
- **Lenguaje**: Python
- **Framework**: Flask
- **Frontend**: HTML, CSS (Bootstrap/Zentratek), JavaScript
- **Formularios**: Flask-WTF
- **Persistencia**: Modelo `Cliente` (campos `nombre`, `nit`, y el campo JSON `config`).
- **Almacenamiento de Archivos (Logo):** Sistema de archivos local (para desarrollo/MVP simple) o almacenamiento en la nube (S3, Azure Blob, Google Cloud Storage - recomendado para producción SaaS). Se necesitará una librería como `boto3` (AWS), `azure-storage-blob` (Azure), o `google-cloud-storage` (GCP).

### Funcionalidades

#### 1. Acceso y Visualización
- La sección "General" será la primera pestaña o área visible dentro de la ruta `/configuracion/`.
- Muestra los datos actuales leídos del modelo `Cliente` (`g.cliente`).
    - Nombre del Cliente
    - NIT (probablemente solo lectura para `ADMIN`, editable por `SUPER_ADMIN`)
    - Logo actual (si existe, mostrar una miniatura).
    - Zona Horaria seleccionada.
    - Formato de Fecha seleccionado.
    - Formato de Moneda seleccionado.

#### 2. Edición de Información Básica
- Un formulario permitirá editar el Nombre del Cliente.
- La edición del NIT estará restringida (posiblemente solo `SUPER_ADMIN`).
- Validación para asegurar que el nombre no esté vacío.

#### 3. Gestión del Logo
- Un campo de subida de archivo (`FileField` en Flask-WTF) permitirá cargar una nueva imagen para el logo (validar tipos: JPG, PNG, SVG y tamaño máximo).
- Al cargar un nuevo logo:
    - El archivo anterior (si existe) debe ser eliminado del almacenamiento.
    - El nuevo archivo se guarda en la ubicación designada (local o nube).
    - La ruta o identificador del archivo se guarda en `Cliente.config['logo_url']` (o un campo similar).
    - Se muestra una vista previa del nuevo logo cargado.
- Opción para eliminar el logo actual (restablecer a ninguno).

#### 4. Configuración de Preferencias Regionales
- **Zona Horaria:** Un campo `SelectField` poblado con una lista de zonas horarias estándar (ej. usando la librería `pytz`). El valor seleccionado se guarda en `Cliente.config['timezone']`.
- **Formato de Fecha:** Un `SelectField` con opciones comunes (ej. "DD/MM/AAAA", "MM/DD/AAAA", "AAAA-MM-DD"). El valor seleccionado se guarda en `Cliente.config['date_format']`.
- **Formato de Moneda:** Un `SelectField` con opciones comunes (ej. "$1,234.56", "1.234,56 €", "£1,234.56"). Se puede guardar el símbolo y el formato de separadores en `Cliente.config['currency_format']`.

#### 5. Persistencia
- Al guardar el formulario general:
    - Actualizar `Cliente.nombre`.
    - Actualizar `Cliente.nit` (si es editable por el rol).
    - Actualizar el diccionario `Cliente.config` con los valores de `logo_url`, `timezone`, `date_format`, `currency_format`.
    - Usar `flag_modified(g.cliente, 'config')` si es necesario para que SQLAlchemy detecte el cambio en el JSON.
    - `db.session.commit()`.

## Endpoints / Rutas (Dentro del Blueprint `configuracion`)
- `GET /` (o `GET /general` si se usan sub-rutas por sección): Muestra el formulario con los datos actuales.
- `POST /guardar-general`: Ruta específica para procesar el formulario de la sección general.

## Modelos de Datos
- **`Cliente`**: Campos `nombre`, `nit` y `config: JSON` (para `logo_url`, `timezone`, `date_format`, `currency_format`).

## Seguridad
- **Control de Acceso:** La ruta principal ya está protegida por `@login_required` y `@role_required(['admin', 'super_admin'])`. La edición de ciertos campos (como NIT) puede necesitar una verificación adicional del rol dentro de la lógica de la ruta.
- **Subida de Archivos:**
    - **Validación del Lado del Servidor:** Validar estrictamente el tipo MIME y la extensión del archivo subido.
    * **Sanitización del Nombre:** Nunca confiar en el nombre de archivo proporcionado por el cliente. Generar un nombre de archivo seguro y único (ej. usando UUID).
    * **Límites de Tamaño:** Implementar límites de tamaño de archivo tanto en el cliente (JavaScript) como en el servidor (configuración de Flask `MAX_CONTENT_LENGTH` y verificación adicional).
    * **Almacenamiento Seguro:** Si se usa almacenamiento local, asegurarse de que la carpeta de subida no sea accesible directamente desde la web y tenga los permisos correctos. Preferir almacenamiento en la nube configurado de forma privada.

## Dependencias
- Módulo de Configuración base (RFC-0002).
- Librería `pytz` (para zonas horarias).
- Librería de almacenamiento en la nube (si aplica: `boto3`, `azure-storage-blob`, `google-cloud-storage`).
- Librería para manipulación de imágenes (opcional, para generar miniaturas: `Pillow`).

## MVP Scope
✅ Visualización de Nombre y NIT.
✅ Edición del Nombre del Cliente.
✅ Funcionalidad básica de subida/eliminación de logo (guardando en sistema de archivos local simple o placeholder en config JSON).
✅ Selección y guardado de Zona Horaria (usando `pytz`).
✅ Selección y guardado de Formato de Fecha (opciones básicas).
❌ Selección y guardado de Formato de Moneda.
❌ Validación avanzada de subida de archivos (tamaño, tipo MIME complejo).
❌ Almacenamiento en la nube para el logo.