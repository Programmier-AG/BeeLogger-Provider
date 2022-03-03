import time

import schedule

from database import Config

def run_data_push():
    print("running the data push...")  # This is obviously work in progress...

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
    data_push.every(interval).seconds.do(run_data_push)

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
