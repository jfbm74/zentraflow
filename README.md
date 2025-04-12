# Gestor de Glosas Pro - MVP Frontend

Este repositorio contiene el MVP (Producto Mínimo Viable) del Frontend para una aplicación web de gestión de glosas médicas, desarrollado con Flask, HTML y Bootstrap 5.

## Descripción

La aplicación está destinada a clínicas médicas para gestionar las respuestas a glosas (objeciones a facturas) enviadas por aseguradoras. Este MVP es sólo el frontend, por lo que toda la información se muestra con datos de ejemplo (dummy data).

## Características

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
- Flask

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
   pip install flask
   ```

4. Ejecuta la aplicación:
   ```
   python app.py
   ```

5. Abre tu navegador y visita:
   ```
   http://127.0.0.1:5000/
   ```

## Flujo de Uso

1. Inicia en el Dashboard para ver estadísticas generales.
2. Navega a "Bandeja de Glosas" para ver la lista de todas las glosas.
3. Haz clic en el botón "Ver" de cualquier glosa para acceder a su detalle.
4. En la vista de detalle, puedes ver la información general, los ítems específicos, y las opciones de respuesta (aceptar/no aceptar + justificación).

## Notas de Desarrollo

- Este es un MVP frontend, por lo que no incluye conexión a base de datos o lógica de backend compleja.
- Los datos son simulados en el archivo app.py.
- La aplicación utiliza principalmente Bootstrap 5 para el diseño, complementado con CSS personalizado.
- Se ha implementado una estructura que sugiere la naturaleza SaaS de la aplicación.

## Próximos Pasos

- Integración con backend y base de datos.
- Implementación de autenticación y autorización.
- Desarrollo completo del módulo de reportes.
- Personalización por cliente.
- Funcionalidad de exportación a PDF.

## Capturas de Pantalla

(Incluir capturas de pantalla cuando estén disponibles)

## Autor

Tu nombre o el nombre de tu empresa

## Licencia

[Especificar la licencia]
