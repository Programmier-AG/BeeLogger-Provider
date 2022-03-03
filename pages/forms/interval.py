from flask_wtf import FlaskForm
from wtforms import IntegerField

class IntervalForm(FlaskForm):
    seconds = IntegerField('Sekunden')
    minutes = IntegerField('Minuten')
    hours = IntegerField('Stunden')
