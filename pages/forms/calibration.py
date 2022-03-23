from flask_wtf import FlaskForm
from wtforms import IntegerField

class CalibrationForm(FlaskForm):
    offset = IntegerField('Waage-Offset')
    ratio = IntegerField('Waage-Ratio')
    tare = IntegerField("Waage-Tara Wert")
