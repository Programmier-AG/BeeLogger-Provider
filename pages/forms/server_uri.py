from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import data_required

class ServerAdress(FlaskForm):
    uri = StringField('Server Adresse', validators=[data_required()])
    token = StringField('Insert Token', validators=[data_required()])
