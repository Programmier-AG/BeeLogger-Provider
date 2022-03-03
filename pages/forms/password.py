from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms.validators import DataRequired

class PasswordChangeForm(FlaskForm):
    old_password = PasswordField('Altes Passwort', validators=[DataRequired()])
    new_password = PasswordField('Neues Passwort', validators=[DataRequired()])
