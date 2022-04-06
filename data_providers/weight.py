import config
import database

if not config.Flask.debug:
    from lib.hx711 import HX711

def get(ctx):
    with ctx.app_context():
        dout = int(database.Config.query.filter_by(key='scale_dout').first().value)
        clk = int(database.Config.query.filter_by(key='scale_clk').first().value)
        offset = float(database.Config.query.filter_by(key='scale_offset').first().value)
        ratio = float(database.Config.query.filter_by(key='scale_ratio').first().value)

    hx = HX711(
        dout, clk
    )

    hx.set_offset(offset)
    hx.set_scale(ratio)

    weight = hx.get_grams()

    return weight
