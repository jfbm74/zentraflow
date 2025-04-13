from app import app
from database import db
from modules.clientes.models import Cliente
from modules.usuarios.models import Usuario, RolUsuario

with app.app_context():
    # Verificar si ya existe el cliente
    cliente = Cliente.query.filter_by(nit="123456789").first()
    if not cliente:
        cliente = Cliente(nombre="Clínica Demo", nit="123456789")
        db.session.add(cliente)
        db.session.commit()
        print("✅ Cliente demo creado.")
    else:
        print("ℹ️ Cliente demo ya existía.")

    # Verificar si ya existe el usuario
    usuario = Usuario.query.filter_by(email="email@clinica.com").first()
    if not usuario:
        usuario = Usuario(
            email="email@clinica.com",
            nombre="Usuario Demo",
            apellido="Zentratek",
            rol=RolUsuario.ADMIN,
            cliente_id=cliente.id,
            activo=True
        )
        usuario.password = "password123"  # Esto invoca el setter que hace el hash
        db.session.add(usuario)
        db.session.commit()
        print("✅ Usuario demo creado.")
    else:
        print("ℹ️ Usuario demo ya existía.")
