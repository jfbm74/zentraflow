"""
Formularios para la gestión de usuarios
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from modules.usuarios.models import Usuario, RolUsuario

class LoginForm(FlaskForm):
    """Formulario de inicio de sesión"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')

class UsuarioForm(FlaskForm):
    """Formulario para crear/editar un usuario"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    nombre = StringField('Nombre', validators=[DataRequired(), Length(min=2, max=100)])
    apellido = StringField('Apellido', validators=[Optional(), Length(max=100)])
    
    # Campo de contraseña opcional para edición (requerido para creación)
    password = PasswordField('Contraseña')
    confirm_password = PasswordField('Confirmar Contraseña', 
                                   validators=[EqualTo('password', message='Las contraseñas deben coincidir')])
    
    # Roles disponibles
    rol = SelectField('Rol', choices=[(rol.value, rol.name) for rol in RolUsuario])
    
    # Cliente ID (solo para super_admin)
    cliente_id = SelectField('Cliente', coerce=int)
    
    activo = BooleanField('Activo')
    submit = SubmitField('Guardar')
    
    def __init__(self, *args, **kwargs):
        self.usuario_id = kwargs.pop('usuario_id', None)
        self.es_creacion = kwargs.pop('es_creacion', False)
        super(UsuarioForm, self).__init__(*args, **kwargs)
        
        # Si es un formulario de creación, la contraseña es obligatoria
        if self.es_creacion:
            self.password.validators = [DataRequired(), Length(min=6)]
    
    def validate_email(self, field):
        """Validar que el email no esté duplicado"""
        usuario = Usuario.query.filter_by(email=field.data).first()
        if usuario and (not self.usuario_id or usuario.id != self.usuario_id):
            raise ValidationError('Ya existe un usuario con este email.')
    
    def validate_password(self, field):
        """Validar que la contraseña tenga el largo mínimo si se proporciona"""
        if field.data and len(field.data) < 6:
            raise ValidationError('La contraseña debe tener al menos 6 caracteres.')

class ForgotPasswordForm(FlaskForm):
    """Formulario para solicitar restablecimiento de contraseña"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Enviar Instrucciones')

class ResetPasswordForm(FlaskForm):
    """Formulario para restablecer contraseña"""
    password = PasswordField('Nueva Contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Contraseña', 
                                   validators=[DataRequired(), 
                                              EqualTo('password', message='Las contraseñas deben coincidir')])
    token = HiddenField('Token')
    submit = SubmitField('Restablecer Contraseña')