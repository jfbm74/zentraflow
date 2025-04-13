from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Length, Optional

class ReglaFiltradoForm(FlaskForm):
    """Formulario para crear/editar reglas de filtrado"""
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=3, max=100)])
    
    condicion_tipo = SelectField('Tipo de Condición', 
                               choices=[
                                   ('remitente', 'Remitente'),
                                   ('asunto', 'Asunto')
                               ],
                               validators=[DataRequired()])
    
    condicion_operador = SelectField('Operador', 
                                   choices=[
                                       ('contiene', 'Contiene'),
                                       ('no_contiene', 'No Contiene'),
                                       ('igual_a', 'Igual a')
                                   ],
                                   validators=[DataRequired()])
    
    condicion_valor = StringField('Valor', validators=[DataRequired(), Length(min=1, max=255)])
    
    accion = SelectField('Acción', 
                        choices=[
                            ('procesar', 'Procesar'),
                            ('ignorar', 'Ignorar')
                        ],
                        validators=[DataRequired()])
    
    prioridad = IntegerField('Prioridad', validators=[Optional()])
    
    estado = BooleanField('Activa', default=True)