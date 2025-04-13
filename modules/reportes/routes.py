"""
Rutas para el módulo de reportes
"""

from flask import render_template, g, session
from ..reportes import reportes_bp
from utils.auth import login_required

@reportes_bp.route('/')
@login_required
def reportes():
    """
    Ruta principal para el módulo de reportes
    """
    # Obtener información del usuario en sesión
    user_name = session.get('user_name', 'Usuario')
    user_email = session.get('user_email', '')
    
    # Datos de ejemplo para la vista
    reportes = [
        {
            'id': 1,
            'nombre': 'Reporte de Glosas Mensual',
            'tipo': 'Mensual',
            'fecha': '2024-04-13',
            'estado': 'Generado',
            'tamanio': '1.2 MB'
        },
        {
            'id': 2,
            'nombre': 'Análisis de Tendencias',
            'tipo': 'Trimestral',
            'fecha': '2024-04-13',
            'estado': 'En Proceso',
            'tamanio': '-'
        },
        {
            'id': 3,
            'nombre': 'Reporte de Eficiencia',
            'tipo': 'Semanal',
            'fecha': '2024-04-13',
            'estado': 'Pendiente',
            'tamanio': '-'
        }
    ]
    
    return render_template('reportes.html',
                         reportes=reportes,
                         user_name=user_name,
                         user_email=user_email) 