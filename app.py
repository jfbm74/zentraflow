from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

# Datos dummy para el dashboard
dashboard_data = {
    "nuevas": 12,
    "pendientes": 28,
    "valor_total": "$ 15,450,000"
}

# Datos dummy para la bandeja de glosas
glosas_list = [
    {"id": 1, "aseguradora": "Seguros Salud S.A.", "factura": "F-2023-1089", "fecha": "2023-10-15", "estado": "Nuevo", "valor": "$ 1,250,000"},
    {"id": 2, "aseguradora": "MediSeguro", "factura": "F-2023-1102", "fecha": "2023-10-18", "estado": "En Análisis", "valor": "$ 3,540,000"},
    {"id": 3, "aseguradora": "Protección Total", "factura": "F-2023-1145", "fecha": "2023-10-22", "estado": "Respondida", "valor": "$ 750,000"},
    {"id": 4, "aseguradora": "Asistencia Médica", "factura": "F-2023-1156", "fecha": "2023-10-25", "estado": "Nuevo", "valor": "$ 2,876,000"},
    {"id": 5, "aseguradora": "Seguros Salud S.A.", "factura": "F-2023-1180", "fecha": "2023-10-29", "estado": "En Análisis", "valor": "$ 5,850,000"}
]

# Datos dummy para el detalle de glosas
glosas_detalle = {
    1: {
        "info": {"id": 1, "aseguradora": "Seguros Salud S.A.", "factura": "F-2023-1089", "fecha": "2023-10-15", "estado": "Nuevo", "valor_total": "$ 1,250,000"},
        "items": [
            {"codigo": "PRO-001", "descripcion": "Consulta especialista", "valor": "$ 450,000"},
            {"codigo": "PRO-002", "descripcion": "Exámenes de laboratorio", "valor": "$ 800,000"}
        ]
    },
    2: {
        "info": {"id": 2, "aseguradora": "MediSeguro", "factura": "F-2023-1102", "fecha": "2023-10-18", "estado": "En Análisis", "valor_total": "$ 3,540,000"},
        "items": [
            {"codigo": "PRO-003", "descripcion": "Procedimiento quirúrgico", "valor": "$ 2,300,000"},
            {"codigo": "PRO-004", "descripcion": "Hospitalización", "valor": "$ 1,240,000"}
        ]
    },
    3: {
        "info": {"id": 3, "aseguradora": "Protección Total", "factura": "F-2023-1145", "fecha": "2023-10-22", "estado": "Respondida", "valor_total": "$ 750,000"},
        "items": [
            {"codigo": "PRO-005", "descripcion": "Medicamentos", "valor": "$ 350,000"},
            {"codigo": "PRO-006", "descripcion": "Terapia física", "valor": "$ 400,000"}
        ]
    },
    4: {
        "info": {"id": 4, "aseguradora": "Asistencia Médica", "factura": "F-2023-1156", "fecha": "2023-10-25", "estado": "Nuevo", "valor_total": "$ 2,876,000"},
        "items": [
            {"codigo": "PRO-007", "descripcion": "Cirugía ambulatoria", "valor": "$ 1,750,000"},
            {"codigo": "PRO-008", "descripcion": "Anestesia", "valor": "$ 650,000"},
            {"codigo": "PRO-009", "descripcion": "Insumos médicos", "valor": "$ 476,000"}
        ]
    },
    5: {
        "info": {"id": 5, "aseguradora": "Seguros Salud S.A.", "factura": "F-2023-1180", "fecha": "2023-10-29", "estado": "En Análisis", "valor_total": "$ 5,850,000"},
        "items": [
            {"codigo": "PRO-010", "descripcion": "Procedimiento especializado", "valor": "$ 3,250,000"},
            {"codigo": "PRO-011", "descripcion": "UCI (3 días)", "valor": "$ 2,600,000"}
        ]
    }
}

# Rutas de la aplicación
@app.route('/')
def dashboard():
    return render_template('dashboard.html', data=dashboard_data, cliente="Clínica Ejemplo SAS")

@app.route('/glosas')
def bandeja_glosas():
    return render_template('bandeja_glosas.html', glosas=glosas_list, cliente="Clínica Ejemplo SAS")

@app.route('/glosas/<int:id_glosa>')
def detalle_glosa(id_glosa):
    # Intentar obtener la glosa por ID, si no existe, redirigir a la bandeja
    if id_glosa in glosas_detalle:
        glosa = glosas_detalle[id_glosa]
        return render_template('detalle_glosa.html', info=glosa["info"], items=glosa["items"], cliente="Clínica Ejemplo SAS")
    return redirect(url_for('bandeja_glosas'))

@app.route('/reportes')
def reportes():
    # Esta página será un placeholder por ahora
    return render_template('reportes.html', cliente="Clínica Ejemplo SAS")

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)