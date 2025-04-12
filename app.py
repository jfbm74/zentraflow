from flask import Flask, render_template, redirect, url_for, request, session, flash
import os
from functools import wraps

app = Flask(__name__)
# Clave secreta para sesiones - en producción debería ser una clave segura y gestionada por variables de entorno
app.secret_key = os.environ.get('SECRET_KEY', 'un_secreto_muy_seguro_para_desarrollo')

# Usuarios dummy para demostración
users = {
    "email@clinica.com": {
        "password": "password123",
        "name": "Administrador",
        "role": "admin",
        "cliente": "Clínica Ejemplo SAS"
    },
    "usuario@clinica.com": {
        "password": "123456",
        "name": "Usuario Regular",
        "role": "user",
        "cliente": "Clínica Ejemplo SAS"
    }
}

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

# Decorador para requerir login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Ruta de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Si ya está logueado, redirigir al dashboard
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if email in users and users[email]['password'] == password:
            # Autenticación exitosa
            session['logged_in'] = True
            session['user_email'] = email
            session['user_name'] = users[email]['name']
            session['user_role'] = users[email]['role']
            session['cliente'] = users[email]['cliente']
            
            # Redirigir a la página solicitada originalmente o al dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        else:
            error = 'Credenciales inválidas. Por favor intente nuevamente.'
    
    return render_template('auth/login.html', error=error)

# Ruta de logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Rutas protegidas de la aplicación
@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html', 
                           data=dashboard_data, 
                           cliente=session.get('cliente'),
                           user_name=session.get('user_name'),
                           user_email=session.get('user_email'))

@app.route('/glosas')
@login_required
def bandeja_glosas():
    return render_template('bandeja_glosas.html', 
                           glosas=glosas_list, 
                           cliente=session.get('cliente'),
                           user_name=session.get('user_name'),
                           user_email=session.get('user_email'))

@app.route('/glosas/<int:id_glosa>')
@login_required
def detalle_glosa(id_glosa):
    # Intentar obtener la glosa por ID, si no existe, redirigir a la bandeja
    if id_glosa in glosas_detalle:
        glosa = glosas_detalle[id_glosa]
        return render_template('detalle_glosa.html', 
                               info=glosa["info"], 
                               items=glosa["items"], 
                               cliente=session.get('cliente'),
                               user_name=session.get('user_name'),
                               user_email=session.get('user_email'))
    return redirect(url_for('bandeja_glosas'))

@app.route('/reportes')
@login_required
def reportes():
    # Esta página será un placeholder por ahora
    return render_template('reportes.html', 
                           cliente=session.get('cliente'),
                           user_name=session.get('user_name'),
                           user_email=session.get('user_email'))

# Manejador de error 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('auth/404.html'), 404

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)