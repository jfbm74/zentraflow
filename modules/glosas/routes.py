"""
Rutas para el módulo de glosas
"""

from flask import render_template, g, session, request
from ..glosas import glosas_bp
from utils.auth import login_required

@glosas_bp.route('/')
@login_required
def bandeja_glosas():
    """
    Ruta principal para la bandeja de glosas
    """
    # Obtener información del usuario en sesión
    user_name = session.get('user_name', 'Usuario')
    user_email = session.get('user_email', '')
    
    # Datos de ejemplo para la vista
    glosas = [
        {
            'id': 1,
            'numero': 'G-2024-001',
            'aseguradora': 'Seguros Salud S.A.',
            'fecha': '2024-04-13',
            'estado': 'Pendiente',
            'valor': '$ 1,250,000'
        },
        {
            'id': 2,
            'numero': 'G-2024-002',
            'aseguradora': 'MediSeguro',
            'fecha': '2024-04-13',
            'estado': 'En Proceso',
            'valor': '$ 850,000'
        },
        {
            'id': 3,
            'numero': 'G-2024-003',
            'aseguradora': 'Protección Total',
            'fecha': '2024-04-13',
            'estado': 'Respondida',
            'valor': '$ 2,100,000'
        }
    ]
    
    return render_template('bandeja_glosas.html',
                         glosas=glosas,
                         user_name=user_name,
                         user_email=user_email)

@glosas_bp.route('/detalle/<int:id_glosa>')
@login_required
def detalle_glosa(id_glosa):
    """
    Ruta para ver el detalle de una glosa específica
    """
    # Obtener información del usuario en sesión
    user_name = session.get('user_name', 'Usuario')
    user_email = session.get('user_email', '')
    
    # Datos de ejemplo para la vista
    info = {
        'id': id_glosa,
        'numero': f'G-2024-{id_glosa:03d}',
        'aseguradora': 'Seguros Salud S.A.',
        'fecha_recepcion': '2024-04-13',
        'fecha_respuesta': '2024-04-20',
        'estado': 'Pendiente',
        'valor_total': '$ 1,250,000',
        'valor_glosado': '$ 450,000',
        'descripcion': 'Glosa por servicios no cubiertos en el plan'
    }
    
    # Datos de ejemplo para los ítems de la glosa
    items = [
        {
            'id': 1,
            'servicio': 'Consulta Especializada',
            'fecha': '2024-04-10',
            'valor': '$ 250,000',
            'valor_glosado': '$ 150,000',
            'motivo': 'Servicio no autorizado'
        },
        {
            'id': 2,
            'servicio': 'Medicamentos',
            'fecha': '2024-04-10',
            'valor': '$ 500,000',
            'valor_glosado': '$ 200,000',
            'motivo': 'Medicamento no POS'
        },
        {
            'id': 3,
            'servicio': 'Procedimiento',
            'fecha': '2024-04-10',
            'valor': '$ 500,000',
            'valor_glosado': '$ 100,000',
            'motivo': 'Falta soporte'
        }
    ]
    
    # Documentos adjuntos de ejemplo
    documentos = [
        {
            'id': 1,
            'nombre': 'Factura F-2024-001',
            'tipo': 'PDF',
            'tamanio': '1.2 MB',
            'fecha': '2024-04-13'
        },
        {
            'id': 2,
            'nombre': 'Historia Clínica',
            'tipo': 'PDF',
            'tamanio': '2.5 MB',
            'fecha': '2024-04-13'
        }
    ]
    
    return render_template('detalle_glosa.html',
                         info=info,
                         items=items,
                         documentos=documentos,
                         user_name=user_name,
                         user_email=user_email) 