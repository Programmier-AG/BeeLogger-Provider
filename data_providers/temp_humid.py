import config
import database

if not config.Flask.debug:
    import adafruit_dht

def get():
    model = database.Config.query.filter_by(key="dht_model").first().value
    pin = int(database.Config.query.filter_by(key="dht_dat").first().value)

    if model == "11":
        dht = adafruit_dht.DHT11(
            pin
        )
    elif model == "22":
        dht = adafruit_dht.DHT22(
            pin
        )
    else:
        print("No dht model was set! Skipping.")
        return

    temp = dht.temperature
    humid = dht.humidity

    return temp, humid
