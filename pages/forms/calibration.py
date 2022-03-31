from flask_wtf import FlaskForm
from wtforms import FloatField

class CalibrationForm(FlaskForm):
    offset = FloatField('Waage-Offset')
    ratio = FloatField('Waage-Ratio')
    tare = FloatField("Waage-Tara Wert")
