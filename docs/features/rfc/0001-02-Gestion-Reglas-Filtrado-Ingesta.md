# RFC-0001-02: Gestión de Reglas de Filtrado de Ingesta

**RFC Previos:** RFC-0001 (Ingesta General Google Workspace), RFC-0004 (Panel Principal Ingesta)

**Fecha:** 2024-07-27 (Reemplazar con fecha actual)

**Autor:** [Tu Nombre/Equipo]

**Estado:** Propuesto

## 1. Objetivo

Permitir a los usuarios con roles de administrador (`ADMIN` o `SUPER_ADMIN`) crear, visualizar, editar, activar/desactivar y eliminar las reglas de filtrado que determinan cómo el sistema procesa (o ignora) los correos electrónicos entrantes para la cuenta configurada de su cliente (tenant) específico.

## 2. Alcance

*   Implementación de la sección "Reglas de Filtrado" dentro de la interfaz del módulo de Ingesta de Correo (`/ingesta-correo`).
*   Visualización de las reglas existentes para el cliente actual en una tabla HTML. La tabla mostrará: Nombre, Condición (Tipo, Operador, Valor), Acción, Prioridad (si aplica), Estado (Activa/Inactiva) y Acciones disponibles.
*   Funcionalidad CRUD (Crear, Leer, Actualizar, Eliminar) para las reglas de filtrado (`ReglaFiltrado`) a través de la interfaz web. Se recomienda el uso de modales (Bootstrap) para las operaciones de Crear y Editar para mantener al usuario en la misma página.
*   Inclusión de botones de acción en cada fila de la tabla para: Editar, Eliminar y un control (ej. switch o botón) para Activar/Desactivar la regla.
*   Un botón principal "Nueva Regla" para iniciar el proceso de creación.

**Fuera de Alcance (Inicial):**

*   Interfaz para reordenar visualmente la prioridad de las reglas (arrastrar y soltar).
*   Validación de expresiones regulares complejas en las condiciones.
*   Lógica de combinación de reglas avanzada (AND/OR entre múltiples reglas).
*   Historial de cambios por regla.

## 3. Diseño Técnico

### 3.1. Interfaz de Usuario (Frontend)

*   **Sección "Reglas de Filtrado":** Ubicada en `templates/ingesta_correo.html`.
*   **Tabla de Reglas:** Utilizar una tabla HTML estándar (ej. con clases de Bootstrap).
*   **Modal Crear/Editar:** Un único modal (Bootstrap) con un formulario (Flask-WTF) que se adapte para creación o edición. Los campos incluirán:
    *   `nombre` (Texto)
    *   `condicion_tipo` (Select: Remitente, Asunto)
    *   `condicion_operador` (Select: contiene, no\_contiene, igual\_a)
    *   `condicion_valor` (Texto)
    *   `accion` (Select: procesar, ignorar)
    *   `prioridad` (Number - Opcional MVP)
    *   `estado` (Checkbox/Switch: Activa/Inactiva)
*   **Interacción:** Usar JavaScript (posiblemente con Fetch API o AJAX) para:
    *   Abrir el modal de Crear/Editar (poblando datos si es edición).
    *   Enviar los datos del formulario a las API del backend (POST/PUT).
    *   Manejar las solicitudes de Eliminar (DELETE) y Activar/Desactivar (PATCH).
    *   Actualizar dinámicamente la tabla de reglas después de operaciones exitosas sin recargar toda la página (o recargar si es más simple para el MVP).
    *   Mostrar mensajes de éxito/error (usando Toasts, por ejemplo).

### 3.2. Lógica del Servidor (Backend - Flask)

*   **Listar Reglas (Integrado en `GET /ingesta-correo` o API dedicada `GET /api/ingesta-correo/reglas`):**
    *   Asegurar que el usuario esté autenticado y tenga rol `admin` o `super_admin`.
    *   Consultar `ReglaFiltrado.query.filter_by(cliente_id=g.cliente.id).order_by(ReglaFiltrado.prioridad).all()`.
    *   Pasar la lista de reglas al contexto de la plantilla o devolverla como JSON.

*   **Crear Regla (`POST /api/ingesta-correo/reglas`):**
    *   Endpoint de API protegido (`@login_required`, `@role_required`).
    *   Recibir datos JSON del frontend.
    *   Validar los datos (se puede usar un formulario Flask-WTF internamente para la validación).
    *   Crear una nueva instancia `ReglaFiltrado` con `cliente_id=g.cliente.id`.
    *   Asignar valores recibidos y validados.
    *   Guardar en la BD: `db.session.add(nueva_regla)`, `db.session.commit()`.
    *   Manejar excepciones (ej. `IntegrityError` si hay violación de constraints).
    *   Devolver respuesta JSON: `{'success': True, 'regla': regla_serializada}` o `{'success': False, 'errors': lista_errores}`.

*   **Actualizar Regla (`PUT /api/ingesta-correo/reglas/<int:id_regla>`):**
    *   Endpoint de API protegido.
    *   Buscar `regla = ReglaFiltrado.query.filter_by(id=id_regla, cliente_id=g.cliente.id).first_or_404()`.
    *   Recibir datos JSON.
    *   Validar los datos.
    *   Actualizar los atributos de la `regla` encontrada.
    *   Guardar cambios: `db.session.commit()`.
    *   Manejar excepciones.
    *   Devolver respuesta JSON de éxito o error.

*   **Eliminar Regla (`DELETE /api/ingesta-correo/reglas/<int:id_regla>`):**
    *   Endpoint de API protegido.
    *   Buscar `regla = ReglaFiltrado.query.filter_by(id=id_regla, cliente_id=g.cliente.id).first_or_404()`.
    *   Eliminar de la BD: `db.session.delete(regla)`, `db.session.commit()`.
    *   Manejar excepciones.
    *   Devolver respuesta JSON de éxito (`{'success': True}`) o error.

*   **Activar/Desactivar Regla (`PATCH /api/ingesta-correo/reglas/<int:id_regla>/toggle`):**
    *   Endpoint de API protegido.
    *   Buscar `regla = ReglaFiltrado.query.filter_by(id=id_regla, cliente_id=g.cliente.id).first_or_404()`.
    *   Invertir el valor del campo `estado` (o el booleano correspondiente).
    *   Guardar cambios: `db.session.commit()`.
    *   Manejar excepciones.
    *   Devolver respuesta JSON con el nuevo estado: `{'success': True, 'nuevo_estado': regla.estado}`.

*   **Formulario (Flask-WTF):** Crear una clase `ReglaFiltradoForm(FlaskForm)` en `modules/ingesta_correo/forms.py` con los campos y validadores necesarios (DataRequired, Length, etc.).

## 4. Modelos de Datos Involucrados

*   **`ReglaFiltrado`**: Modelo principal para las operaciones CRUD. Se utilizarán todos sus campos.
*   **`Cliente`**: Necesario para filtrar las reglas y asegurar que un usuario solo opera sobre las reglas de su propio cliente (`cliente_id`).

## 5. Seguridad

*   **Autenticación y Autorización:** Todas las rutas y endpoints API deben estar protegidos con `@login_required` y `@role_required(['admin', 'super_admin'])`.
*   **Pertenencia al Tenant:** En todas las operaciones (Leer, Crear, Actualizar, Eliminar), se debe verificar explícitamente que la regla consultada o modificada pertenece al `cliente_id` asociado al usuario en sesión (`g.cliente.id`). Esto previene que un administrador de un cliente modifique reglas de otro.
*   **Validación de Entrada:** Validar rigurosamente todos los datos provenientes del frontend en el backend antes de interactuar con la base de datos para prevenir inyecciones o datos malformados.
*   **Protección CSRF:** Asegurar que las solicitudes POST, PUT, DELETE, PATCH estén protegidas contra CSRF (Flask-WTF ayuda con esto si se usa correctamente con los formularios).

## 6. Dependencias

*   **RFC-0001:** Define el modelo `ReglaFiltrado` y el contexto general del módulo de ingesta.
*   **RFC-0004:** Proporciona la página principal (`ingesta_correo.html`) donde se integrará esta funcionalidad.
*   **Módulo de Autenticación:** Para obtener `g.cliente` y verificar roles.
*   **Base de Datos y ORM:** Para persistir los cambios.
*   **Flask-WTF:** Para la definición y validación de formularios.

## 7. MVP Scope

*   ✅ **Visualización:** Mostrar la tabla con las reglas existentes del cliente.
*   ✅ **Creación:** Funcionalidad completa para añadir nuevas reglas mediante un modal o página separada, incluyendo validaciones básicas.
*   ✅ **Edición:** Funcionalidad para modificar los campos básicos de una regla existente.
*   ✅ **Eliminación:** Botón funcional para eliminar reglas.
*   ✅ **Activar/Desactivar:** Funcionalidad para cambiar el estado de una regla.
*   ❌ **Gestión de Prioridad/Orden:** La tabla puede mostrar el campo, pero no habrá funcionalidad para reordenar en el MVP. Se insertarán con una prioridad por defecto o incremental simple.
*   ❌ **Validación Avanzada:** No se incluirán validaciones complejas como expresiones regulares en las condiciones.