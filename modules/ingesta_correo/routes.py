"""
Rutas para el módulo de ingesta de correo
"""

from flask import render_template, g, session
from utils.auth import login_required
from . import ingesta_correo_bp

@ingesta_correo_bp.route('/')
@login_required
def ingesta_correo():
    """Ruta principal de ingesta de correo"""
    # Variables para el layout
    user_name = session.get('user_name', 'Usuario')
    user_email = session.get('user_email', '')
    
    # Datos de ejemplo para la ingesta de correo
    correos = [
        {
            'id': 1,
            'remitente': 'glosas@aseguradora.com',
            'asunto': 'Glosa Factura F-2023-1180',
            'fecha': '2023-04-10 10:30',
            'estado': 'Procesado',
            'adjuntos': 2
        },
        {
            'id': 2,
            'remitente': 'notificaciones@mediseguro.com',
            'asunto': 'Nueva Glosa - Factura F-2023-1145',
            'fecha': '2023-04-08 15:45',
            'estado': 'Pendiente',
            'adjuntos': 1
        }
    ]
    
    return render_template('ingesta_correo.html',
                         correos=correos,
                         cliente=g.cliente,
                         usuario=g.usuario,
                         user_name=user_name,
                         user_email=user_email) 