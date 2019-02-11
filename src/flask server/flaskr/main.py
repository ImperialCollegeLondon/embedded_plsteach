# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 14:38:34 2019
Define all user activities and functions under main.bp
@author: Sam Wan
"""

from flask import (
        Blueprint, flash, g, redirect, render_template, request, session, url_for, Flask
        )
from flaskr.auth import login_required
from flask_mqtt import Mqtt
from flaskr.db import get_db

bp = Blueprint('main', __name__, url_prefix='/main')

sub = 'IC.embedded/plzteach/#'
topic = 'IC.embedded/plzteach/test'
broker = 'test.mosquitto.org'
app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = broker
app.config['MQTT_BROKER_PORT'] = 1883
mqtt = Mqtt(app)
config_table = ['0xC3', '0xD3', '0xE3', '0xF3']

@bp.route('/home')
@login_required
def home():
    return render_template('main/home.html')

@bp.route('/plot')
@login_required
def plot():
    #chdeck db for settings for mqtt
    #call initilization
    mqtt.subscribe(sub) #currently doesn't do anything, need to pass to producer object
                    #atm there's a subscribe call in producer.run()
    return render_template('main/plot.html')

@bp.route('/status', methods=('GET','POST'))
@login_required
def status():

    user_id = session.get('user_id')
    db = get_db()
    g.user_settings = db.execute(
            'SELECT * FROM settings WHERE user_id = ?', (user_id,)
                ).fetchall()
    print('user: ', g.user_settings)
    if request.method == 'POST':
        sensor_name = request.form['sensor_name']
        pin_no = request.form['pin']
        print('Posted', sensor_name, pin_no)
        error = None
        config = config_table[pin_no]

        if len(g.user_setting) >=4:
            error = 'You can have at most 4 sensors.'
        elif sensor_name in g.user_settings:
            error = 'Sensor already exists.'

        if error is None:
            db.execute(
                    'INSERT INTO settings (user_id, sensor_name, config) VALUES (?,?,?)',
                    (user_id, sensor_name, config))
            db.commit()
            return redirect(url_for('main.status'))
        flash(error)
    else:

        return render_template('main/status.html')

@bp.route('/widget_settings', methods = ('GET', 'POST'))
@login_required
def widget_settings():
    if request.method == 'POST':
        print('here')
    return render_template('main/widget_settings.html')

@bp.route('/view')
@login_required
def view():
    return render_template('main/view.html')
