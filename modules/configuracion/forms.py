"""
Formularios para el módulo de configuración
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SelectField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length, Email, Optional
import pytz

class ConfiguracionGeneralForm(FlaskForm):
    """Formulario para la configuración general del cliente"""
    nombre = StringField('Nombre del Cliente', 
                        validators=[DataRequired(), Length(min=3, max=100)])
    
    nit = StringField('NIT', render_kw={'readonly': True})
    
    logo = FileField('Logo', 
                    validators=[FileAllowed(['jpg', 'png', 'svg'], 'Solo imágenes: jpg, png, svg')])
    
    timezone = SelectField('Zona Horaria',
                         choices=[(tz, tz) for tz in pytz.common_timezones],
                         validators=[DataRequired()])
    
    date_format = SelectField('Formato de Fecha',
                            choices=[
                                ('DD/MM/YYYY', 'DD/MM/YYYY'),
                                ('MM/DD/YYYY', 'MM/DD/YYYY'),
                                ('YYYY-MM-DD', 'YYYY-MM-DD')
                            ],
                            validators=[DataRequired()])

class ConfiguracionCorreoForm(FlaskForm):
    """Formulario para la configuración de ingesta de correo"""
    habilitar_ingesta = BooleanField('Habilitar Ingesta de Correo')
    
    email_monitorear = StringField('Correo Electrónico a Monitorear',
                                 validators=[Optional(), Email()])
    
    metodo_autenticacion = SelectField('Método de Autenticación',
                                     choices=[
                                         ('oauth2', 'OAuth 2.0 Flujo Web'),
                                         ('service_account', 'Cuenta de Servicio')
                                     ])
    
    # Credenciales OAuth 2.0
    client_id = StringField('Client ID')
    client_secret = PasswordField('Client Secret')
    
    # Credenciales Cuenta de Servicio
    service_account_key = FileField('Archivo de Clave JSON',
                                  validators=[FileAllowed(['json'], 'Solo archivos JSON')])
    
    carpeta_monitorear = StringField('Carpeta a Monitorear',
                                   default='INBOX',
                                   validators=[DataRequired()])
    
    intervalo_verificacion = SelectField('Intervalo de Verificación (minutos)',
                                       choices=[
                                           ('5', '5 minutos'),
                                           ('10', '10 minutos'),
                                           ('15', '15 minutos'),
                                           ('30', '30 minutos'),
                                           ('60', '1 hora')
                                       ],
                                       default='5')
    
    marcar_leidos = BooleanField('Marcar Correos como Leídos') 