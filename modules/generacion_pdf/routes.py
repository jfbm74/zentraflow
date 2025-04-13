"""
Rutas para el módulo de generación de PDF
"""

from flask import render_template, g, session
from ..generacion_pdf import generacion_pdf_bp
from utils.auth import login_required

@generacion_pdf_bp.route('/')
@login_required
def generacion_pdf():
    """
    Ruta principal para el módulo de generación de PDF
    """
    # Obtener información del usuario en sesión
    user_name = session.get('user_name', 'Usuario')
    user_email = session.get('user_email', '')
    
    # Datos de ejemplo para la vista
    documentos = [
        {
            'id': 1,
            'nombre': 'Respuesta Glosa #123',
            'tipo': 'Respuesta de Glosa',
            'fecha': '2024-04-13',
            'estado': 'Generado',
            'tamanio': '1.2 MB'
        },
        {
            'id': 2,
            'nombre': 'Reporte Mensual',
            'tipo': 'Reporte',
            'fecha': '2024-04-13',
            'estado': 'En Proceso',
            'tamanio': '-'
        },
        {
            'id': 3,
            'nombre': 'Carta de Presentación',
            'tipo': 'Carta',
            'fecha': '2024-04-13',
            'estado': 'Pendiente',
            'tamanio': '-'
        }
    ]
    
    return render_template('generacion_pdf.html',
                         documentos=documentos,
                         user_name=user_name,
                         user_email=user_email) 