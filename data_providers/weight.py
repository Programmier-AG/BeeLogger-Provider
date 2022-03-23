import config
import database

if not config.Flask.debug:
    from lib.hx711 import HX711

def get():
    hx = HX711(
        database.Config.query.filter_by(key="scale_dout").first().value,
        database.Config.query.filter_by(key="scale_clk").first().value
    )

    hx.set_offset(database.Config.query.filter_by(key="scale_offset").first().value)
    hx.set_scale(database.Config.query.filter_by(key="scale_ratio").first().value)

    weight = hx.get_grams()

    return weight
