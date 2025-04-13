**Product Requirements Document (PRD) – Sistema de Glosas**

*   **Tecnologías Sugeridas:** Flask + PostgreSQL+ on-premise.
    
*   **Stakeholders:** Personal de glosas, TI Bonsana, desarrollador.
    
*   **Requerimientos Funcionales y No Funcionales:**
    
*   **RF-01: Ingesta de Notificaciones de Glosa por Correo Electrónico.**
    

*   Descripción: El sistema debe **monitorear** una bandeja de entrada específica (intranet@gonzanaips.com) para detectar nuevos correos electrónicos relacionados con glosas.
    
    
*   Prioridad: **Alta** (Es el punto de partida de todo el proceso automatizado).
    
*   **RF-02: Filtrado de Correos Relevantes.**
    
    *   Descripción: El sistema debe ser capaz de **identificar y procesar únicamente** los correos que contienen información de glosas, ignorando otros correos que lleguen a la misma bandeja. Debe basarse en patrones definidos (ej. asunto, remitente, contenido).
        
        
    *   Prioridad: **Alta** (Evita procesar información irrelevante y previene errores).
        
*   **RF-03: Extracción Estructurada de Datos de Glosas.**
    
    *   Descripción: El sistema debe **extraer automáticamente la información detallada** de cada ítem de glosa desde los archivos adjuntos (probablemente Excel o tablas dentro del correo/PDF). Cada detalle de glosa debe generar un registro o fila separada en el sistema.
        
        
    *   Prioridad: **Alta** (Fundamental para la automatización y el análisis posterior).
        
*   **RF-04: Generación de Borrador de Respuesta.**
    
    *   Descripción: Basado en los datos extraídos, el sistema debe **generar automáticamente un borrador** de la respuesta a la glosa.
   
    *   Prioridad: **Alta** (Núcleo de la automatización buscada para agilizar el proceso).
        
*   **RF-05: Aplicación de Regla de Negocio Inicial (No Aceptación por Defecto).**
    
    *   Descripción: Al generar el borrador, el sistema debe, por defecto, marcar la glosa como "**No Aceptada**" y replicar el valor glosado en el campo "Valor No Aceptado". (Esta regla puede necesitar configuración o validación posterior).
              
    *   Prioridad: **Media** (Es una regla de negocio específica que agiliza, pero podría ajustarse manualmente si falla).
        
*   **RF-06: Interfaz de Revisión y Decisión Manual.**
    
    *   Descripción: El sistema debe proveer una interfaz donde el personal de glosas pueda **revisar el borrador** de respuesta, analizar la glosa y **registrar la decisión final** (Acepta / No Acepta - Defiende) y la argumentación correspondiente.
     
    *   Prioridad: **Alta** (La decisión final sigue siendo humana y crítica para el proceso).
        
*   **RF-07: Almacenamiento Estructurado de Datos.**
    
    *   Descripción: El sistema debe **almacenar toda la información** relevante de la glosa: datos extraídos, estado (recibida, en análisis, respondida), decisión (aceptada/no aceptada), valores, fechas, aseguradora, argumentación, etc., en una base de datos centralizada.
        
   
    *   Prioridad: **Alta** (Necesario para la gestión, seguimiento y reportería).
        
*   **RF-08: Generación de Documento de Respuesta en PDF.**
    
    *   Descripción: Una vez tomada la decisión final, el sistema debe **generar un archivo PDF** formateado con la respuesta oficial de la glosa, incluyendo la información requerida por la entidad externa y la decisión (Acepta/No Acepta). Debe seguir una plantilla similar a la existente.
            
    *   Prioridad: **Alta** (Es el entregable final del proceso de respuesta).
        
*   **RF-09: Soporte para Múltiples Aseguradoras.**
    
    *   Descripción: El sistema debe poder manejar y diferenciar la información de glosas provenientes de **diferentes aseguradoras**, permitiendo la gestión y reporte tanto individual como consolidado.
        
     
    *   Prioridad: **Media** (Importante para la operativa real, pero el core podría funcionar inicialmente con una si fuera necesario simplificar).
        
*   **RF-10: Capacidades de Reportería y Consulta.**
    
    *   Descripción: El sistema debe permitir **generar informes** sobre el estado de las glosas (ej. cuántas radicadas, respondidas, pendientes, valores aceptados/no aceptados por aseguradora, tiempos de respuesta). Debe permitir consultas y filtros (por fecha, aseguradora, estado, etc.). Potencialmente, debe poder **exportar datos** para herramientas como Power BI o tener dashboards nativos.
            
    *   Prioridad: **Media** (Aporta gran valor de gestión, pero el procesamiento básico de glosas es prioritario).
        
*   **2\. Requerimientos No Funcionales (RNF)**
    
*   Describen las cualidades del sistema y restricciones sobre cómo debe operar.
    
*   **RNF-01: Usabilidad.**
    

*   Descripción: La interfaz de usuario (especialmente para la revisión y decisión) debe ser **intuitiva y fácil de usar** para el personal de glosas, minimizando la curva de aprendizaje y errores.
    
*   Prioridad: **Alta** (Impacta directamente la adopción y eficiencia del usuario).
    
*   **RNF-02: Integridad y Consistencia de Datos.**
    
    *   Descripción: El sistema debe asegurar la **calidad e integridad de los datos** almacenados, evitando inconsistencias o dificultades para actualizar la información (como el problema descrito con Power BI y los archivos fuente de Excel). Las actualizaciones deben reflejarse consistentemente.
            
    *   Prioridad: **Alta** (Fundamental para la confiabilidad de los datos y reportes).
        
*   **RNF-03: Confiabilidad.**
    
    *   Descripción: El sistema debe ser **confiable** en la detección de correos, extracción de datos y ejecución de los flujos de trabajo sin fallos frecuentes. Debe manejar errores de forma controlada (ej. si un archivo no se puede procesar).
  
    *   Prioridad: **Alta** (El proceso depende de esta automatización).
        
*   **RNF-04: Mantenibilidad.**
    
    *   Descripción: Debe ser relativamente **sencillo actualizar** las reglas de filtrado de correos, los patrones de extracción de datos (si cambian los formatos de las aseguradoras), y las plantillas de PDF.
        
     
    *   Prioridad: **Media** (Facilita la adaptación a largo plazo).
        
*   **RNF-05: Seguridad.**
    
    *   Descripción: Dado que se maneja información financiera y potencialmente relacionada con pacientes (aunque no se menciona explícitamente), el sistema debe contar con medidas de **seguridad** adecuadas, incluyendo control de acceso (autenticación y autorización) y protección de los datos almacenados y en tránsito.
           
    *   Prioridad: **Alta** (Requerimiento normativo y de buenas prácticas).
        
*   **RNF-06: Rendimiento.**
    
    *   Descripción: La extracción de datos y generación de borradores/PDFs debe realizarse en **tiempos razonables** para no convertirse en un cuello de botella. (Se necesita definir qué es "razonable").
              
    *   Prioridad: **Media** (Importante para la eficiencia, pero los volúmenes iniciales pueden ser manejables).
        
*   **Métricas de Éxito:** Tiempos de respuesta, reducción de errores, cantidad de glosas gestionadas.