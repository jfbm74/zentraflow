**RFC-0001-01: Panel de Estado y Control de Ingesta de Correo**

*   **RFC Previo:** RFC-0001 (Ingesta General), RFC-0003 (Configuración General Cliente)
    
*   **Objetivo:** Implementar la interfaz principal del módulo "Ingesta de Correo" que muestra el estado actual del servicio de monitoreo, estadísticas clave, la configuración relevante y permite al usuario iniciar una verificación manual o pausar/reanudar el servicio.
    
*   **Alcance:**
    
    *   Renderizado de la vista principal (ingesta\_correo.html).
        
    *   Visualización de datos de configuración leídos desde Cliente.config\_correo (solo lectura en esta vista).
        
    *   Visualización de estadísticas agregadas (contadores de correos procesados, glosas extraídas, pendientes, errores - derivados de CorreoIngestado).
        
    *   Mostrar el estado general del servicio de ingesta para ese cliente (Activo/Pausado).
        
    *   Botón "Verificar ahora" para disparar una tarea de ingesta bajo demanda.
        
    *   Botón "Pausar/Reanudar servicio" para controlar la ejecución periódica de la tarea.
        
*   **Diseño Técnico:**
    
    *   **Ruta Principal (GET /ingesta-correo):**
        
        *   Protegida por @login\_required y @role\_required.
            
        *   Obtiene el Cliente actual (g.cliente).
            
        *   Lee la configuración de cliente.config\_correo.
            
        *   Consulta la tabla CorreoIngestado para calcular estadísticas recientes (ej. últimas 24h o desde la última verificación).
            
        *   Obtiene el estado actual del servicio de ingesta para ese cliente (podría almacenarse en Cliente.config\_correo o en una tabla de estado separada).
            
        *   Renderiza ingesta\_correo.html pasando los datos necesarios.
            
    *   **Ruta de Verificación Manual (POST /ingesta-correo/verificar):**
        
        *   Protegida por @login\_required y @role\_required.
            
        *   Obtiene el Cliente actual.
            
        *   Dispara la tarea Celery/APScheduler responsable de la verificación del buzón _para ese cliente específico_.
            
        *   Devuelve una respuesta (ej. JSON) indicando que la tarea fue iniciada o redirige con un flash.
            
    *   **Ruta de Pausa/Reanudación (POST /ingesta-correo/toggle-servicio):**
        
        *   Protegida por @login\_required y @role\_required.
            
        *   Obtiene el Cliente actual.
            
        *   Actualiza el estado del servicio en la BD (ej. un flag ingesta\_activa en Cliente.config\_correo).
            
        *   Si se usa un planificador como APScheduler, podría necesitar interactuar con él para pausar/reanudar el job específico de ese cliente. Con Celery, la tarea periódica simplemente no lanzaría la verificación si el flag está desactivado.
            
        *   Devuelve una respuesta o redirige con un flash.
            
*   **Modelos Involucrados:**
    
    *   Cliente (para leer config\_correo y guardar/leer estado del servicio).
        
    *   CorreoIngestado (para calcular estadísticas).
        
*   **Seguridad:** Control de acceso por roles. Asegurar que un admin solo pueda controlar el servicio de su propio cliente.
    
*   **Dependencias:** RFC-0001 (define la tarea de fondo), RFC-0003 (define dónde se configura), Celery/APScheduler.
    
*   **MVP Scope:**✅ Visualización de configuración básica y estado (Activo/Inactivo).✅ Visualización de contadores simples (sin filtros de fecha complejos).✅ Botón "Verificar ahora" que dispara la tarea.✅ Botón "Pausar/Reanudar" que actualiza un flag en la BD.