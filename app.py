"""
                   BeeLogger-Provider

     Copyright (c) 2022 Fabian Reinders, Sönke Klock
"""
import hashlib
import requests
import secrets
import threading
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user

import config
import database as db
from pages.forms.calibration import CalibrationForm
from pages.forms.interval import IntervalForm
from pages.forms.login import LoginForm
from pages.forms.password import PasswordChangeForm
import scheduler
from pages.forms.pins import PinForm
from pages.forms.server_uri import ServerAdress


app = Flask("BeeLogger", static_folder='public', static_url_path='', template_folder='pages')
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config["SECRET_KEY"] = config.Flask.secret_key
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///persistant/db.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.client.init_app(app)
db.client.create_all(app=app)

with app.app_context():
    if db.Config.query.filter_by(key="password").first() is None:
        db.client.session.add(db.Config(key="password", value=hashlib.sha256(config.password.encode()).hexdigest()))
        db.client.session.commit()

login_manager = LoginManager(app)
login_manager.session_protection = "strong"
login_manager.login_message = False
login_manager.login_view = "login"

@login_manager.user_loader
def user_dummy(user_id):
    class User(UserMixin):
        id = user_id
        name = "admin"
        is_authenticated = True
        is_active = True

    user = User()
    return user


scheduler_stop = threading.Event()

@app.route("/")
@login_required
def index():
    pwform = PasswordChangeForm()
    intervalform = IntervalForm()
    serverform = ServerAdress()
    caliform = CalibrationForm()
    pinform = PinForm()

    try:
        serverform.uri.data = db.Config.query.filter_by(key="server_address").first().value
        serverform.token.data = db.Config.query.filter_by(key="server_token").first().value
    except AttributeError:
        pass

    try:
        caliform.offset.data = db.Config.query.filter_by(key="scale_offset").first().value
        caliform.ratio.data = db.Config.query.filter_by(key="scale_ratio").first().value
        caliform.tare.data = db.Config.query.filter_by(key="scale_tare").first().value
    except AttributeError:
        pass

    try:
        pinform.scale_dout.data = db.Config.query.filter_by(key="scale_dout").first().value
        pinform.scale_clk.data = db.Config.query.filter_by(key="scale_clk").first().value
        pinform.dht_dat.data = db.Config.query.filter_by(key="dht_dat").first().value
        pinform.dht_model.data = db.Config.query.filter_by(key="dht_model").first().value
    except AttributeError:
        pass

    return render_template("index.html",
                           station_number=db.Config.query.filter_by(key="station_number").first(),
                           pwform=pwform,
                           intervalform=intervalform,
                           serverform=serverform,
                           caliform=caliform,
                           pinform=pinform,
                           current_interval=scheduler.interval_getter(app),
                           current_server=serverform.uri.data,
                           )

@app.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.is_submitted():
        entered_pass = hashlib.sha256(form.password.data.encode()).hexdigest()
        check_password = db.Config.query.filter_by(key="password").first().value
        if entered_pass == check_password:
            login_user(user_dummy(secrets.token_urlsafe(10)), remember=True)
            flash("Erfolgreich eingeloggt!")
            return redirect(url_for("index"))
        else:
            flash("Passwort falsch!", category="error")

    elif request.method == "POST":
        flash("Vermutlich gab es gerade ein Problem beim Loginvorgang. "
              "Versuche es bitte erneut, oder wende dich an einen Administrator.", category="error")

    return render_template("login.html", loginform=form, next=request.values.get("next"))

@app.route("/logout/", methods=["GET", "POST"])
def logout():
    if not current_user.is_authenticated:
        return redirect(url_for("index"))

    logout_user()
    flash("Erfolgreich ausgeloggt!")
    return redirect(url_for("index"))

@app.route("/push_now/")
@login_required
def push_now():
    try:
        scheduler.run_data_push(app)
        flash("Daten gesendet!")
    except Exception as e:
        flash("Das hat nicht geklappt.")
        flash(str(e))

    return redirect(url_for("index"))

@app.route("/get_data/")
@login_required
def get_data():
    weight, temp, humid = scheduler.get_data()

    flash("Daten gemessen:")
    flash("Gewicht: %s" % weight)
    flash("Temperatur: %s" % temp)
    flash("Luftfeuchte: %s" % humid)

    return redirect(url_for("index"))


@app.route("/change_pinout/", methods=["POST"])
@login_required
def change_pinout():
    pinform = PinForm()

    if pinform.validate_on_submit():
        pinout = {
            "scale_dout": pinform.scale_dout.data,
            "scale_clk": pinform.scale_clk.data,
            "dht_dat": pinform.dht_dat.data,
            "dht_model": pinform.dht_model.data
        }

        print(pinout.values())

        for key, val in pinout.items():
            db.client.session.merge(db.Config(key=key, value=val))
        db.client.session.commit()

        flash("Erfolgreich gespeichert!")
    else:
        flash("Ungültiges Formular!", category="error")

    return redirect(url_for("index"))

@app.route("/change_calibration/", methods=["POST"])
@login_required
def change_calibration():
    caliform = CalibrationForm()

    if caliform.validate_on_submit():
        scale = {
            "offset": caliform.offset.data,
            "ratio": caliform.ratio.data,
            "tare": caliform.tare.data
        }
        db.client.session.merge(db.Config(key="scale_offset", value=scale["offset"]))
        db.client.session.merge(db.Config(key="scale_ratio", value=scale["ratio"]))
        db.client.session.merge(db.Config(key="scale_tare", value=scale["tare"]))

        db.client.session.commit()

        flash("Erfolgreich gespeichert!")
    else:
        flash("Ungültiges Formular!", category="error")
    return redirect(url_for("index"))

@app.route("/change_pw/", methods=["POST"])
@login_required
def change_pw():
    form = PasswordChangeForm()
    if form.is_submitted():
        entered_pass = hashlib.sha256(form.old_password.data.encode()).hexdigest()
        check_password = db.Config.query.filter_by(key="password").first().value
        if not entered_pass == check_password:
            flash("Falsches Passwort für den Änderungsversuch eingegeben!", category="error")
            return redirect(url_for("index"))

        db.Config.query.filter_by(key="password").first().value = hashlib.sha256(form.new_password.data.encode()).hexdigest()
        db.client.session.commit()

        flash("Passwort wurde geändert.")
        flash("Bitte erneut einloggen!")

        logout_user()

    return redirect(url_for("index"))

@app.route("/change_address/", methods=["POST"])
@login_required
def change_address():
    form = ServerAdress()

    if form.validate_on_submit():
        try:
            req = requests.get(form.uri.data)
        except:
            flash("Ungültiger URI! Konnte Server nicht anpingen!", category="error")
            return redirect(url_for("index"))

        if req.status_code != 200:
            flash("Server Adresse konnte nicht angepingt werden! Status %s" % req.status_code, category="error")
            return redirect(url_for("index"))

        db.client.session.merge(db.Config(key="server_address", value=form.uri.data))
        db.client.session.merge(db.Config(key="server_token", value=form.token.data))
        db.client.session.commit()

        flash("Server Adresse wurde aktualisiert.")
        return redirect(url_for("index"))

@app.route("/change_interval/", methods=["POST"])
@login_required
def change_interval():
    form = IntervalForm()

    if form.is_submitted():
        db.client.session.merge(db.Config(key="interval_sec", value=form.seconds.data or 0))
        db.client.session.merge(db.Config(key="interval_min", value=form.minutes.data or 0))
        db.client.session.merge(db.Config(key="interval_h", value=form.hours.data or 0))

        db.client.session.commit()
        flash("Intervall erfolgreich aktualisiert.")
        flash("Der nächste Daten-Push wird nach dem Intervall unternommen.")

        try:
            thread = [x for x in threading.enumerate() if x.name == "scheduler"][0]
            scheduler_stop.set()
            thread.join()
            scheduler_stop.clear()
        except IndexError:
            pass

        setup_scheduling()
    else:
        flash("Formularvalidierung fehlgeschlagen!", category="error")
    return redirect(url_for("index"))

def setup_scheduling():
    # scheduler = importlib.import_module("scheduler")
    # scheduler_thread = threading.Thread(name="scheduler", target=getattr(scheduler, "run_tasks")(ctx=app, stop=scheduler_stop))
    scheduler_thread = threading.Thread(name="scheduler",
                                        target=scheduler.run_tasks(ctx=app, stop=scheduler_stop))
    scheduler_thread.daemon = True
    scheduler_thread.start()


setup_scheduling()

if __name__ == "__main__":
    app.run(config.Flask.host, config.Flask.port)

