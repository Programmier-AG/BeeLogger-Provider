from flask_wtf import FlaskForm
from wtforms import PasswordField

class LoginForm(FlaskForm):
    password = PasswordField('Passwort', validators=[])
