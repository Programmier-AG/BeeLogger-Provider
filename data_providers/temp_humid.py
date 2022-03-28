import config
import database

if not config.Flask.debug:
    import Adafruit_DHT

def get():
    model = database.Config.query.filter_by(key="dht_model").first().value
    pin = int(database.Config.query.filter_by(key="dht_dat").first().value)

    if model == "11":
        sensor = Adafruit_DHT.DHT11
    elif model == "22":
        sensor = Adafruit_DHT.DHT22
    else:
        print("No dht model was set! Skipping.")
        return 0, 0

    humid = temp = None
    i = 0
    while humid is None or temp is None:
        if i > 5:
            print("GETTING TEMP/HUMID FAILED AFTER 5 TRIES!!")
            return 0, 0
        i += 1
        humid, temp = Adafruit_DHT.read_retry(sensor, pin)

    return temp, humid
