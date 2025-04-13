"""
Rutas para la gestión de clientes (tenants)
"""

from flask import render_template, redirect, url_for, request, flash, jsonify
from modules.clientes import clientes_bp
from modules.clientes.models import Cliente
from database import db
from utils.auth import login_required, role_required
from modules.usuarios.models import RolUsuario
import json

# Listar todos los clientes (solo para SUPER_ADMIN)
@clientes_bp.route('/')
@login_required
@role_required(['super_admin'])
def listar_clientes():
    clientes = Cliente.query.all()
    return render_template('clientes/listar.html', clientes=clientes)

# Ver detalle de un cliente
@clientes_bp.route('/<int:cliente_id>')
@login_required
@role_required(['super_admin', 'admin'])
def ver_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    return render_template('clientes/detalle.html', cliente=cliente)

# Formulario para crear un nuevo cliente
@clientes_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@role_required(['super_admin'])
def nuevo_cliente():
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.form['nombre']
        nit = request.form['nit']
        
        # Validar que no exista un cliente con el mismo NIT
        if Cliente.query.filter_by(nit=nit).first():
            flash('Ya existe un cliente con este NIT.', 'danger')
            return redirect(url_for('clientes.nuevo_cliente'))
        
        # Crear nuevo cliente
        nuevo_cliente = Cliente(
            nombre=nombre,
            nit=nit,
            config={},
            config_correo={}
        )
        
        try:
            db.session.add(nuevo_cliente)
            db.session.commit()
            flash('Cliente creado exitosamente.', 'success')
            return redirect(url_for('clientes.listar_clientes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear cliente: {str(e)}', 'danger')
    
    return render_template('clientes/nuevo.html')

# Editar un cliente existente
@clientes_bp.route('/<int:cliente_id>/editar', methods=['GET', 'POST'])
@login_required
@role_required(['super_admin'])
def editar_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    
    if request.method == 'POST':
        # Obtener datos del formulario
        cliente.nombre = request.form['nombre']
        cliente.nit = request.form['nit']
        cliente.activo = 'activo' in request.form
        
        # Actualizar configuraciones si se proporcionan
        if 'config' in request.form and request.form['config']:
            try:
                cliente.config = json.loads(request.form['config'])
            except json.JSONDecodeError:
                flash('Error en el formato JSON de la configuración.', 'danger')
                return render_template('clientes/editar.html', cliente=cliente)
        
        if 'config_correo' in request.form and request.form['config_correo']:
            try:
                cliente.config_correo = json.loads(request.form['config_correo'])
            except json.JSONDecodeError:
                flash('Error en el formato JSON de la configuración de correo.', 'danger')
                return render_template('clientes/editar.html', cliente=cliente)
        
        try:
            db.session.commit()
            flash('Cliente actualizado exitosamente.', 'success')
            return redirect(url_for('clientes.ver_cliente', cliente_id=cliente.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar cliente: {str(e)}', 'danger')
    
    return render_template('clientes/editar.html', cliente=cliente)

# Activar/Desactivar un cliente
@clientes_bp.route('/<int:cliente_id>/toggle', methods=['POST'])
@login_required
@role_required(['super_admin'])
def toggle_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    cliente.activo = not cliente.activo
    
    try:
        db.session.commit()
        estado = "activado" if cliente.activo else "desactivado"
        flash(f'Cliente {estado} exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al cambiar estado del cliente: {str(e)}', 'danger')
    
    return redirect(url_for('clientes.listar_clientes'))

# API para obtener información de un cliente
@clientes_bp.route('/api/<int:cliente_id>')
@login_required
@role_required(['super_admin', 'admin'])
def api_cliente(cliente_id):
    cliente = Cliente.query.get_or_404(cliente_id)
    return jsonify({
        'id': cliente.id,
        'nombre': cliente.nombre,
        'nit': cliente.nit,
        'activo': cliente.activo,
        'fecha_creacion': cliente.fecha_creacion.isoformat() if cliente.fecha_creacion else None,
        'usuarios_activos': cliente.usuarios.filter_by(activo=True).count()
    })