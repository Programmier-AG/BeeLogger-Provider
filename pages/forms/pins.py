from flask_wtf import FlaskForm
from wtforms import IntegerField
from wtforms.validators import NumberRange, AnyOf

class PinForm(FlaskForm):
    scale_dout = IntegerField('Waage DOUT', validators=[NumberRange(2, 27)])
    scale_clk = IntegerField('Waage CLK/PWD', validators=[NumberRange(2, 27)])
    dht_dat = IntegerField('DHT Data', validators=[NumberRange(2, 27)])
    dht_model = IntegerField('DHT Model (11/22)', validators=[AnyOf([11, 22])])
