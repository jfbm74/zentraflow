"""
Rutas para el módulo de flujo de trabajo
"""

from flask import render_template, g, session
from ..flujo_trabajo import flujo_trabajo_bp
from utils.auth import login_required

@flujo_trabajo_bp.route('/')
@login_required
def flujo_trabajo():
    """
    Ruta principal para el módulo de flujo de trabajo
    """
    # Obtener información del usuario en sesión
    user_name = session.get('user_name', 'Usuario')
    user_email = session.get('user_email', '')
    
    # Datos de ejemplo para la vista
    flujos = [
        {
            'id': 1,
            'nombre': 'Proceso de Glosas',
            'estado': 'Activo',
            'ultima_ejecucion': '2024-04-13 10:30',
            'proxima_ejecucion': '2024-04-13 15:00',
            'tareas': 5
        },
        {
            'id': 2,
            'nombre': 'Proceso de Facturas',
            'estado': 'Pausado',
            'ultima_ejecucion': '2024-04-13 09:15',
            'proxima_ejecucion': '-',
            'tareas': 3
        },
        {
            'id': 3,
            'nombre': 'Proceso de Reportes',
            'estado': 'Activo',
            'ultima_ejecucion': '2024-04-13 11:45',
            'proxima_ejecucion': '2024-04-13 16:00',
            'tareas': 4
        }
    ]
    
    return render_template('flujo_trabajo.html',
                         flujos=flujos,
                         user_name=user_name,
                         user_email=user_email) 