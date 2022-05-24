import statistics
import time
from datetime import datetime

import requests
import schedule
from requests.adapters import HTTPAdapter, Retry

import config
import data_providers
from database import *

if not config.Flask.debug:
    import RPi.GPIO as GPIO

def get_data(ctx=None):
    if config.Flask.debug:
        return 1, 2, 3

    with ctx.app_context():
        weights = []
        temps = []
        humids = []
        for i in range(4):
            weights.append(data_providers.weight.get(ctx=ctx))
            time.sleep(1)
            if temps != [0] or humids != [0]:
                temp, humid = data_providers.temp_humid.get()
                temps.append(temp)
                humids.append(humid)

        # Check for weight fluctuations
        while statistics.pstdev(weights) > 5:
            print("WARNING: Weight variance is high! Trying again...")
            print("Variance:", statistics.pstdev(weights), "Data:", weights)
            client.session.add(Logs(time=datetime.now(), source="measure", message="Hight weight variance: %s" % statistics.pstdev(weights), code=0))

            time.sleep(0.3)

            # Updating list until weight variance is low; discarding first value
            weights.pop(0)
            weights.append(data_providers.weight.get(ctx=ctx))

        weight = statistics.mean(weights)
        weight -= float(Config.query.filter_by(key="scale_tare").first().value)
        temp = statistics.mean(temps)
        humid = statistics.mean(humids)

    if not config.Flask.debug:
        GPIO.cleanup()

    return weight, temp, humid
def run_data_push(ctx):
    if config.Flask.debug:
        print("running the data push...")
    else:
        weight, temp, humid = get_data(ctx=ctx)

        print("Pushing data:")
        print("Weight:", weight)
        print("Temp:", temp)
        print("Humid:", humid)

        with ctx.app_context():
            client.session.add(DataBackup(temperature=temp, humidity=humid, weight=weight, measured=datetime.now()))
            client.session.commit()  # DO NOT REMOVE; prevents data loss when request fails

            url = Config.query.filter_by(key="server_address").first().value
            if url.endswith("/"): url = url[:-1]
            print("Using URL:", url)
            token = Config.query.filter_by(key="server_token").first().value

            """
            res = requests.get(url + "/api/data/insert",
                               params={"token": token, "t": temp, "h": humid, "w": weight},
                               cookies={"opt-in": "true"}
                               )
            """

            insert_session = requests.Session()
            insert_session.mount("https://",  # Set retry policy for insert requests; retry 5 times with .1 increses
                                 HTTPAdapter(
                                     max_retries=Retry(
                                         total=5,
                                         backoff_factor=0.1,
                                         status_forcelist=[500, 502, 503, 504]  # Always retry on server errors
                                     )
                                 ))

            insert_session.cookies.update({"opt-in": "true"})
            res = insert_session.get(url + "/api/data/insert",
                                     params={"token": token, "t": temp, "h": humid, "w": weight})
            insert_session.close()

            client.session.add(Logs(time=datetime.now(), source="insert", message=res.text, code=res.status_code))
            client.session.commit()

def interval_getter(ctx):
    with ctx.app_context():
        seconds = Config.query.filter_by(key="interval_sec").first()
        minutes = Config.query.filter_by(key="interval_min").first()
        hours = Config.query.filter_by(key="interval_h").first()

        if None in [seconds, minutes, hours]:
            return None

        interval = int(seconds.value) + (int(minutes.value) * 60) + (int(hours.value) * 60 * 60)

        return interval

def run_tasks(ctx=None, stop=None):
    interval = interval_getter(ctx)
    if interval is None:
        return lambda: print("Scheduler not started because of missing configuration!")

    data_push = schedule.Scheduler()

    print("Running tasks every %s seconds" % interval)
    data_push.every(interval).seconds.do(lambda: run_data_push(ctx))

    print("Scheduler started...")

    def worker():
        while True:
            if stop.is_set():
                print("stopping")
                data_push.clear()
                exit()
            data_push.run_pending()
            time.sleep(1)

    return worker


if __name__ == "__main__":
    run_tasks()
