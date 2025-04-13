# RFC-0003: Módulo de Flujo de Trabajo para Glosas

## Objetivo
Diseñar e implementar un módulo de flujo de trabajo que orqueste las etapas clave del proceso de gestión de glosas, integrando reglas de negocio, asignaciones automáticas, notificaciones y automatizaciones para optimizar el tiempo de respuesta y garantizar trazabilidad.

## Alcance
Este RFC cubre:
- Definición de estados de glosas
- Transición entre etapas
- Aplicación de reglas de negocio y automatizaciones
- SLA y seguimiento
- Interfaz para revisión y decisión manual

## Etapas del Flujo de Trabajo
| Etapa           | Descripción                                              | Responsable | SLA         |
|-----------------|----------------------------------------------------------|-------------|-------------|
| 1. Recepción    | Ingesta de correos y extracción de adjuntos              | Sistema     | 15 minutos  |
| 2. Procesamiento| Extracción de datos estructurados                        | Sistema     | 30 minutos  |
| 3. Revisión     | Validación manual y toma de decisiones                  | Usuario     | 48 horas    |
| 4. Respuesta    | Generación de PDF y envío (opcional)                    | Usuario     | 24 horas    |
| 5. Seguimiento  | Espera y monitoreo de respuesta de aseguradora          | Usuario     | 5 días      |

## Reglas de Negocio
Definidas por condición + acción:
- **Decisión Automática CX**: Valor < $50,000 → Aceptar automáticamente
- **Alerta Valor Alto**: Valor > $5,000,000 → Notificar a supervisor
- **Asignación Automática**: Aseguradora = MediSeguro → Asignar a Equipo A
- **Escalado por Tiempo**: Sin respuesta > 24h → Escalar a Gerencia

## Automatizaciones Soportadas
| Nombre                           | Descripción                                                                 |
|----------------------------------|-----------------------------------------------------------------------------|
| Notificación de Nuevas Glosas   | Enviar correo a usuarios asignados al recibir una nueva glosa              |
| Alerta de Vencimiento           | Notificación 24h antes de SLA para glosas no procesadas                    |
| Respuesta Automática (en prueba)| Genera respuesta automática para glosas de bajo valor (< $100,000)        |
| Informe Semanal                 | Envío automático de reporte los lunes a las 7:00 AM                        |

## Transición de Estados de Glosa
| Estado             | Descripción                                |
|--------------------|--------------------------------------------|
| nuevo              | Ingresado al sistema                       |
| en_procesamiento   | Extracción en curso                        |
| en_revision        | Lista para revisión manual                 |
| respondida         | Decisión tomada y PDF generado            |
| seguimiento        | En espera de respuesta de aseguradora     |
| error_extraccion   | Fallo al procesar archivo                  |

## Endpoints / Rutas Propuestas
- `GET /flujo-trabajo` → Vista general del estado del sistema
- `POST /flujo-trabajo/actualizar-estado` → Cambiar etapa de una glosa
- `POST /flujo-trabajo/evaluar-reglas` → Ejecutar reglas de negocio sobre una glosa
- `GET /flujo-trabajo/logs` → Consultar historial de decisiones, reglas, y transiciones

## Modelos de Datos
### Glosa
- `id`: UUID
- `estado`: string (ver tabla anterior)
- `valor_total`: decimal
- `aseguradora`: string
- `equipo_asignado`: string
- `fecha_ingreso`: datetime
- `fecha_ultimo_estado`: datetime

### ReglaNegocio
- `id`: UUID
- `nombre`: string
- `condicion`: JSON
- `accion`: JSON
- `activa`: bool

### EventoAutomatizacion
- `id`: UUID
- `nombre_evento`: string
- `tipo_trigger`: ['creacion', 'diario', 'por_tiempo']
- `condicion_opcional`: JSON
- `accion`: JSON
- `estado`: ['activo', 'inactivo', 'en_prueba']

## Seguridad
- Validación de cambios de estado por rol (ej. solo supervisores pueden escalar)
- Logs de auditoría por cambio de estado, ejecución de regla y automatización

## Dependencias
- RFC-0001 (correo)
- RFC-0002 (extracción de datos)
- RFC-0004 (generación de PDF)

## Historial y Auditoría
- Todas las transiciones de estado, automatizaciones y ejecuciones de reglas deben quedar registradas con:
  - Timestamp
  - ID de usuario
  - Acción tomada / regla aplicada

## Estado Esperado del MVP
✅ Transiciones manuales entre estados
✅ Registro de eventos y cambios de estado
✅ Notificación básica por correo
✅ Aplicación de reglas simples (por valor o aseguradora)
❌ Automatizaciones complejas o condicionales avanzadas (fase posterior)
❌ Seguimiento de respuesta de aseguradora (etapa futura)

