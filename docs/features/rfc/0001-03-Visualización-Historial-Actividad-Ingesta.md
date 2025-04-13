# RFC-0001-03: Visualización del Historial de Actividad de Ingesta

**RFC Previos:** RFC-0001 (Ingesta General Google Workspace), RFC-0004 (Panel Principal Ingesta)

**Fecha:** 2025-04-13 (Reemplazar con fecha actual)

**Autor:** Juan Felipe Bustamante

**Estado:** Propuesto

## 1. Objetivo

Proporcionar a los usuarios administradores (`ADMIN`, `SUPER_ADMIN`) una vista detallada y paginada del historial de correos electrónicos que han sido recibidos y evaluados por el módulo de Ingesta de Correo para su cliente (tenant). Esta vista facilitará la auditoría del proceso, el seguimiento de correos específicos y el diagnóstico de posibles problemas o errores durante la ingesta.

## 2. Alcance

*   Implementación de la sección "Historial de Actividad" dentro de la interfaz del módulo de Ingesta de Correo (`/ingesta-correo`).
*   Visualización de registros de la tabla `CorreoIngestado` pertenecientes al cliente actual, presentados en una tabla HTML.
*   **Columnas Clave en la Tabla:**
    *   Fecha/Hora (de recepción del correo original).
    *   Detalles: Incluirá información relevante como Remitente y Asunto. Potencialmente, si el estado es 'error', mostrar un resumen del error aquí o mediante un tooltip/icono.
    *   Estado: Mostrar el estado final del procesamiento de ese correo por el módulo de ingesta (ej. 'Procesado' (significa que pasó a extracción), 'Ignorado', 'Error Filtrado', 'Error Descarga', 'Error Handoff', 'Pendiente' (si aún no se completa el ciclo)). Usar badges de colores para legibilidad.
*   Implementación de paginación del lado del servidor para manejar eficientemente un gran número de registros históricos.
*   Inclusión de un botón "Descargar Log" que permita exportar los datos del historial visible (o un conjunto básico) a un formato simple como CSV o TXT.

**Fuera de Alcance (Inicial):**

*   Filtros interactivos avanzados en la tabla del historial (ej. filtrar por rango de fechas, por estado específico, por remitente/asunto).
*   Capacidad de búsqueda dentro del historial.
*   Exportación de logs con opciones avanzadas (selección de columnas, rangos de fecha personalizados extensos, diferentes formatos).
*   Visualización detallada del contenido del error directamente en la tabla (se puede añadir más tarde).

## 3. Diseño Técnico

### 3.1. Interfaz de Usuario (Frontend)

*   **Sección "Historial de Actividad":** Ubicada en `templates/ingesta_correo.html`, debajo de las reglas de filtrado.
*   **Tabla de Historial:** Tabla HTML (Bootstrap) con las columnas definidas en el alcance.
*   **Paginación:** Controles de paginación estándar (Bootstrap Pagination) que interactuarán con el backend (ya sea mediante recarga de página con parámetros GET o vía JavaScript/AJAX).
*   **Botón "Descargar Log":** Un botón que, al hacer clic, iniciará la descarga del archivo generado por el backend.
*   **(Opcional) Carga Dinámica:** Se puede usar JavaScript (Fetch API/AJAX) para llamar al endpoint `/api/ingesta-correo/logs` y actualizar la tabla y la paginación sin recargar toda la página.

### 3.2. Lógica del Servidor (Backend - Flask)

*   **Consultar Logs (`GET /api/ingesta-correo/logs` o integrado en `GET /ingesta-correo`):**
    *   Endpoint (o parte de la lógica de la ruta principal) protegido (`@login_required`, `@role_required`).
    *   Recibe parámetros de paginación (ej. `?page=2&per_page=20`).
    *   Consulta la tabla `CorreoIngestado` usando `Flask-SQLAlchemy.paginate`:
        ```python
        pagination = CorreoIngestado.query.filter_by(cliente_id=g.cliente.id)\
                                        .order_by(CorreoIngestado.fecha_recepcion.desc())\
                                        .paginate(page=page_num, per_page=per_page_count, error_out=False)
        logs = pagination.items
        ```
    *   Devuelve los `logs` y la información de `pagination` (total de páginas, página actual, etc.) al frontend, ya sea en el contexto de la plantilla o como JSON si se usa carga dinámica.

*   **Descargar Log (`GET /ingesta-correo/descargar-log`):**
    *   Ruta protegida.
    *   Puede aceptar parámetros básicos (ej. `?limit=100` para descargar los últimos 100).
    *   Consulta `CorreoIngestado` para `g.cliente.id`, ordenado por fecha descendente, aplicando el límite.
    *   Formatea los datos recuperados en una cadena CSV o TXT simple. Se puede usar el módulo `csv` de Python y `io.StringIO`.
    *   Utiliza `send_file` de Flask para devolver el archivo generado como una descarga, estableciendo las cabeceras `Content-Disposition` y `Content-Type` apropiadas.
        ```python
        # Ejemplo básico CSV con io.StringIO
        import io
        import csv
        from flask import send_file
        # ... (obtener logs) ...
        si = io.StringIO()
        cw = csv.writer(si)
        cw.writerow(['Fecha Recepción', 'Remitente', 'Asunto', 'Estado', 'Detalles Error']) # Encabezados
        for log in logs:
             cw.writerow([log.fecha_recepcion, log.remitente, log.asunto, log.estado, log.detalles_error or ''])
        output = io.BytesIO(si.getvalue().encode('utf-8'))
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'historial_ingesta_{g.cliente.id}.csv'
        )
        ```

## 4. Modelos de Datos Involucrados

*   **`CorreoIngestado`**: Modelo principal para la lectura de datos históricos. Se usarán los campos: `fecha_recepcion`, `remitente`, `asunto`, `estado`, `detalles_error`.
*   **`Cliente`**: Necesario para filtrar los logs y asegurar que solo se muestren los del cliente actual (`cliente_id`).

## 5. Seguridad

*   **Autenticación y Autorización:** Todas las rutas/endpoints deben estar protegidos con `@login_required` y `@role_required(['admin', 'super_admin'])`.
*   **Pertenencia al Tenant:** La consulta principal a `CorreoIngestado` **debe** filtrar siempre por `cliente_id=g.cliente.id` para evitar la exposición de datos entre clientes.
*   **Descarga de Datos:** Aunque son logs, la ruta de descarga debe estar igualmente protegida para evitar acceso no autorizado a historiales.

## 6. Dependencias

*   **RFC-0001:** Define el modelo `CorreoIngestado` y el proceso que lo puebla con datos.
*   **RFC-0004:** Proporciona la página principal (`ingesta_correo.html`) donde se integrará esta sección.
*   **Módulo de Autenticación:** Para obtener `g.cliente`.
*   **Base de Datos y ORM:** Para consultar los logs.
*   **Flask-SQLAlchemy:** Específicamente su funcionalidad `paginate`.
*   **(Opcional) Módulo `csv` de Python:** Para la generación del archivo de descarga.

## 7. MVP Scope

*   ✅ **Visualización:** Mostrar la tabla en `ingesta_correo.html` con los registros más recientes (primera página) del historial del cliente.
*   ✅ **Paginación:** Implementar controles de paginación funcionales que permitan navegar entre las páginas del historial.
*   ✅ **Descarga Básica:** Botón "Descargar Log" funcional que exporta un archivo CSV/TXT con un conjunto limitado de registros (ej. los últimos 100 o los de la página actual).
*   ❌ **Filtros Avanzados:** No se implementarán filtros interactivos en la tabla (fecha, estado, etc.) en el MVP.
*   ❌ **Exportación Avanzada:** La descarga no tendrá opciones de personalización (rango de fechas, selección de columnas) en el MVP.
Use code with caution.
