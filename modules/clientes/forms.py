"""
Formularios para la gestión de clientes
"""

from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError, Optional
from modules.clientes.models import Cliente
import json

class ClienteForm(FlaskForm):
    """Formulario para crear/editar un cliente"""
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=3, max=100)])
    nit = StringField('NIT', validators=[DataRequired(), Length(min=3, max=20)])
    activo = BooleanField('Activo')
    config = TextAreaField('Configuración (JSON)', validators=[Optional()])
    config_correo = TextAreaField('Configuración de Correo (JSON)', validators=[Optional()])
    submit = SubmitField('Guardar')
    
    def __init__(self, *args, **kwargs):
        self.cliente_id = kwargs.pop('cliente_id', None)
        super(ClienteForm, self).__init__(*args, **kwargs)
    
    def validate_nit(self, field):
        """Validar que el NIT no esté duplicado"""
        cliente = Cliente.query.filter_by(nit=field.data).first()
        if cliente and (not self.cliente_id or cliente.id != self.cliente_id):
            raise ValidationError('Ya existe un cliente con este NIT.')
    
    def validate_config(self, field):
        """Validar que la configuración sea un JSON válido"""
        if field.data:
            try:
                json.loads(field.data)
            except json.JSONDecodeError:
                raise ValidationError('La configuración debe ser un JSON válido.')
    
    def validate_config_correo(self, field):
        """Validar que la configuración de correo sea un JSON válido"""
        if field.data:
            try:
                json.loads(field.data)
            except json.JSONDecodeError:
                raise ValidationError('La configuración de correo debe ser un JSON válido.')