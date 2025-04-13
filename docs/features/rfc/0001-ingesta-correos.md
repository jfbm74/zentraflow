# RFC-0001: Ingesta de Correos desde Cuenta de Glosas

## Objetivo
Detectar y filtrar automáticamente los correos relevantes a glosas enviados a `intranet@bonsanaips.com`.

## Diseño Técnico
- Monitoreo IMAP cada 1 min usando `imapclient`.
- Filtro por:
  - Asunto que contenga “glosa”
  - Archivos adjuntos de tipo PDF, XLSX

## Endpoints / Funciones
- `check_inbox()` – conexión con servidor
- `filter_glosa_emails()` – aplicar patrones

## Modelos involucrados
- `Correo` (fecha, remitente, asunto, adjunto, estado_procesamiento)

## Seguridad
- Uso de credenciales en variables de entorno
- Validación de remitente autorizado

## Dependencias
- IMAPClient
- dotenv
# RFC-0001: Ingesta de Correos desde Cuenta de Glosas

## Objetivo
Implementar un módulo que monitoree periódicamente una cuenta de correo electrónico para detectar, filtrar y procesar automáticamente mensajes relacionados con glosas médicas, enviando los adjuntos relevantes al módulo de extracción de datos.

## Alcance
Este RFC cubre:
- Configuración del servicio de ingesta
- Conexión con la cuenta de correo mediante Microsoft Graph API
- Reglas de filtrado configurables
- Registro de actividad (log de eventos)
- Interfaz de administración del módulo

## Diseño Técnico

### Tecnologías y Librerías
- **Protocolo de correo**: Microsoft Graph API
- **Lenguaje**: Python
- **Framework sugerido**: Flask + celery/apscheduler (para tareas recurrentes)
- **Librerías sugeridas**: `msal`, `requests`, `python-dotenv`, `pandas` (para pre-procesamiento ligero si aplica)

### Funcionalidades

#### 1. Autenticación y Conexión a la cuenta de correo
- Uso de Microsoft Graph API con OAuth 2.0 (App Registration)
- Token de acceso renovable automáticamente

#### 2. Verificación periódica (cada 5 minutos)
- Verificar nuevos correos en la carpeta principal
- Recuperar solo correos no leídos con fecha posterior al último chequeo

#### 3. Reglas de Filtrado Configurables
Cada correo se evalúa contra un conjunto de reglas definidas por el usuario:
- Condiciones por:
  - **Remitente** (contiene)
  - **Asunto** (contiene, coincide, regex opcional)
- Acciones:
  - **Procesar** (se envía a módulo de extracción)
  - **Ignorar** (se marca como leído y se omite)
- Estado de la regla: Activa / Inactiva

#### 4. Registro de Actividad
- Guardar eventos en tabla/log:
  - Correo recibido: remitente, asunto, timestamp
  - Resultado del filtrado: aceptado, ignorado
  - Resultado de envío de adjunto: éxito / fallo (ej. error de OCR)

#### 5. Interfaz Administrativa Web
- Visualizar configuración actual
- Botón de "Verificar ahora"
- Tabla con historial de actividad (últimos eventos)
- Editor de reglas de filtrado (crear, editar, activar/desactivar)

## Endpoints / Rutas Propuestas
- `GET /ingesta-correo` → Panel principal
- `POST /ingesta-correo/verificar` → Ejecutar ingesta manual
- `GET /ingesta-correo/logs` → Consultar logs recientes
- `GET/POST /ingesta-correo/reglas` → Gestión de reglas de filtrado

## Modelos de Datos
### CorreoIngestado
- `id`: UUID
- `remitente`: string
- `asunto`: string
- `fecha_recepcion`: datetime
- `estado`: ['procesado', 'pendiente', 'ignorado', 'error']
- `adjuntos_detectados`: int
- `regla_aplicada`: string (opcional)

### ReglaFiltrado
- `id`: UUID
- `nombre`: string
- `condicion_tipo`: ['remitente', 'asunto']
- `condicion_valor`: string
- `accion`: ['procesar', 'ignorar']
- `estado`: ['activa', 'inactiva']

## Seguridad
- Tokens y credenciales protegidos con variables de entorno
- Validación contra spam/malware (a futuro)

## Dependencias
- Módulo de Extracción de Datos (RFC-0002)
- Configuración previa del acceso a Microsoft Graph API

## Historial y Auditoría
- Todos los eventos deben registrarse con timestamp, ID de correo, estado
- Log descargable desde el frontend

## Estado Esperado del MVP
✅ Lectura de correo y autenticación vía Graph API
✅ Aplicación de reglas simples
✅ Registro de eventos
✅ Panel web funcional
❌ Filtros avanzados por regex (etapa futura)
❌ Antivirus/Malware scanning (etapa futura)

