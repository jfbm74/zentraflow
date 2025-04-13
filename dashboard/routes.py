"""
Rutas para el dashboard principal
"""

from flask import Blueprint, render_template, g, jsonify
from utils.auth import login_required

# Crear el blueprint para el dashboard
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    """Ruta principal del dashboard"""
    # Datos de ejemplo para el dashboard
    data = {
        "nuevas": 12,
        "pendientes": 28,
        "valor_total": "$ 15,450,000"
    }
    
    return render_template('dashboard/index.html', 
                         data=data, 
                         cliente=g.cliente,
                         usuario=g.usuario)

@dashboard_bp.route('/api/stats')
@login_required
def api_stats():
    """API para obtener estadísticas del dashboard"""
    # Datos de ejemplo para la API
    return jsonify({
        'chart_data': {
            'labels': ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun'],
            'data': [12, 19, 15, 22, 18, 24]
        },
        'kpis': {
            'nuevas': 12,
            'pendientes': 28,
            'valor_total': "$ 15,450,000",
            'procesadas': 15,
            'tiempo_promedio': '32 horas'
        }
    })