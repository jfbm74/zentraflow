# Gestor de Glosas ZentraFlow - MVP Frontend

Este repositorio contiene el MVP (Producto Mínimo Viable) del Frontend para una aplicación web de gestión de glosas médicas, desarrollado con Flask, HTML y Bootstrap 5.

## Descripción

La aplicación está destinada a clínicas médicas para gestionar las respuestas a glosas (objeciones a facturas) enviadas por aseguradoras. Este MVP es sólo el frontend, por lo que toda la información se muestra con datos de ejemplo (dummy data).

## Características

- Sistema de autenticación (login/logout) con usuarios de demostración
- Panel principal (Dashboard) con indicadores clave
- Bandeja de glosas con filtros y tabla de datos
- Vista detallada de glosas individuales con opciones de respuesta
- Diseño responsivo con Bootstrap 5
- Estructura SaaS que permite personalización por cliente

## Estructura del Proyecto

```
gestor-glosas-pro/
│
├── app.py                  # Aplicación principal Flask con rutas y datos dummy
│
├── templates/              # Plantillas HTML
│   ├── auth/               # Plantillas relacionadas con autenticación
│   │   ├── login.html      # Página de inicio de sesión
│   │   ├── layout_login.html # Plantilla para páginas de login
│   │   └── 404.html        # Página de error 404
│   ├── layout.html         # Plantilla base con header y sidebar
│   ├── dashboard.html      # Panel principal
│   ├── bandeja_glosas.html # Lista de glosas
│   ├── detalle_glosa.html  # Detalle de una glosa específica
│   └── reportes.html       # Placeholder para sección de reportes
│
└── static/                 # Archivos estáticos
    ├── css/
    │   └── style.css       # Estilos personalizados
    └── js/
        └── main.js         # JavaScript para funcionalidades básicas
```

## Requisitos

- Python 3.7 o superior
- Flask y dependencias (ver requirements.txt)

## Instalación

1. Clona este repositorio:
   ```
   git clone https://github.com/tu-usuario/gestor-glosas-pro.git
   cd gestor-glosas-pro
   ```

2. Crea y activa un entorno virtual (opcional pero recomendado):
   ```
   python -m venv venv
   
   # En Windows
   venv\Scripts\activate
   
   # En macOS/Linux
   source venv/bin/activate
   ```

3. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

4. Ejecuta la aplicación:
   ```
   python app.py
   ```

5. Abre tu navegador y visita:
   ```
   http://127.0.0.1:5000/
   ```

## Credenciales de Demostración

Para acceder al sistema, utiliza alguna de las siguientes credenciales:

- **Administrador**:
  - Email: email@clinica.com
  - Contraseña: password123

- **Usuario Regular**:
  - Email: usuario@clinica.com
  - Contraseña: 123456

## Flujo de Uso

1. Inicia sesión con las credenciales proporcionadas.
2. Inicia en el Dashboard para ver estadísticas generales.
3. Navega a "Bandeja de Glosas" para ver la lista de todas las glosas.
4. Haz clic en el botón "Ver" de cualquier glosa para acceder a su detalle.
5. En la vista de detalle, puedes ver la información general, los ítems específicos, y las opciones de respuesta (aceptar/no aceptar + justificación).
6. Para salir, selecciona "Cerrar Sesión" desde el menú de usuario en la barra de navegación.

## Notas de Desarrollo

- Este es un MVP frontend, por lo que no incluye conexión a base de datos o lógica de backend compleja.
- Los datos son simulados en el archivo app.py.
- La aplicación utiliza principalmente Bootstrap 5 para el diseño, complementado con CSS personalizado.
- Se ha implementado una estructura que sugiere la naturaleza SaaS de la aplicación.
- La autenticación es simple y usa datos en memoria para propósitos de demostración.
- Las plantillas de autenticación se mantienen en un directorio separado para mejor organización.

## Próximos Pasos

- Integración con backend y base de datos.
- Implementación completa de autenticación con JWT y roles de usuario.
- Desarrollo completo del módulo de reportes.
- Personalización por cliente.
- Funcionalidad de exportación a PDF.
- Gestión de usuarios y permisos.

## Capturas de Pantalla

(Incluir capturas de pantalla cuando estén disponibles)

## Autor

Tu nombre o el nombre de tu empresa

## Licencia

[Especificar la licencia]