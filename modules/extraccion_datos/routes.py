"""
Rutas para el módulo de extracción de datos
"""

from flask import render_template, g, session
from ..extraccion_datos import extraccion_datos_bp
from utils.auth import login_required

@extraccion_datos_bp.route('/')
@login_required
def extraccion_datos():
    """
    Ruta principal para el módulo de extracción de datos
    """
    # Obtener información del usuario en sesión
    user_name = session.get('user_name', 'Usuario')
    user_email = session.get('user_email', '')
    
    # Datos de ejemplo para la vista
    extracciones = [
        {
            'id': 1,
            'nombre': 'Extracción de Facturas',
            'estado': 'Completado',
            'fecha': '2024-04-13',
            'archivos': 5
        },
        {
            'id': 2,
            'nombre': 'Extracción de Órdenes',
            'estado': 'En Proceso',
            'fecha': '2024-04-13',
            'archivos': 3
        },
        {
            'id': 3,
            'nombre': 'Extracción de Glosas',
            'estado': 'Pendiente',
            'fecha': '2024-04-13',
            'archivos': 0
        }
    ]
    
    return render_template('extraccion_datos.html',
                         extracciones=extracciones,
                         user_name=user_name,
                         user_email=user_email) 