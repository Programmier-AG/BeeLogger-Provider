from lib.hx711 import HX711
from database import Config

def get():
    hx = HX711(5, 6)

    hx.set_offset(Config.query.filter_by(key="scale_offset").first().value)
    hx.set_scale(Config.query.filter_by(key="scale_ratio").first().value)

    weight = hx.get_grams()

    return weight
