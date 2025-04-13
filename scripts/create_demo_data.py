# scripts/create_demo_data.py

from app import create_app
from database import db
from modules.clientes.models import Cliente
from modules.usuarios.models import Usuario, RolUsuario

app = create_app('development')

with app.app_context():
    # 1. Buscar si existe el cliente con ese nit
    cliente = Cliente.query.filter_by(nit="123456789").first()
    if not cliente:
        # Si no existe, crearlo
        cliente = Cliente(nombre="Clínica Demo", nit="123456789")
        db.session.add(cliente)
        db.session.commit()
        print("Cliente 'Clínica Demo' creado.")
    else:
        print("El cliente con NIT=123456789 ya existe.")

    # 2. Crear usuario solo si no existe
    user = Usuario.query.filter_by(email="demo@clinica.com").first()
    if not user:
        user = Usuario(
            email="demo@clinica.com",
            nombre="Usuario",
            apellido="Demo",
            rol=RolUsuario.ADMIN,
            cliente_id=cliente.id,
            activo=True
        )
        user.password = "password123"
        db.session.add(user)
        db.session.commit()
        print("Usuario demo@clinica.com creado.")
    else:
        print("El usuario demo@clinica.com ya existe.")
