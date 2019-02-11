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

bp = Blueprint('main', __name__, url_prefix='/main')

sub = 'IC.embedded/plzteach/#'
topic = 'IC.embedded/plzteach/test'
broker = 'test.mosquitto.org'
app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = broker
app.config['MQTT_BROKER_PORT'] = 1883
mqtt = Mqtt(app)

@bp.route('/home')
@login_required
def home():
    return render_template('main/home.html')

@bp.route('/plot')
@login_required
def plot():
    #chdeck db for settings for mqtt
    #call initilization
    return render_template('main/plot.html')

@bp.route('/status')
@login_required
def status():
    return render_template('main/status.html')

@bp.route('/widget_settings')
@login_required
def widget_settings():
    return render_template('main/widget_settings.html')

@bp.route('/view')
@login_required
def view():
    return render_template('main/view.html')

"""@socketio.on('connect', namespace='/main/plot')
def OnConnect():
    print('WS Client is CONNECTED')
    #connector = socketio.on_namespace(Connections(10,'/main/plot'))
    #connector = Connections(10, '/main/plot')
    #connector.start_threads()
    print('SERVER is READY')
    socketio.emit('Server_Ready')

@socketio.on('start_transmit')
def start_transmit():
    connector.start_transmit()

@socketio.on('stop_transmit')
def stop_transmit():
    connector.stop_transmit()

@socketio.on('disconnect')
def Disconnect():
    print('WS Client is DISCONNECTED')
    connector.onDisconnect()
    print('Threads STOPPED')

@socketio.on('save')
def save_record():
    db = get_db()
    error = None
    #ask for title
    title = "testing"
    if not title:
        error = "Please name your record."

    elif  db.execute(
                'SELECT title FROM sess_records WHERE title =?', (title,)).fetchone() is not None:
            error = 'Title {} is already there.'.format(title) #no replace

    flash(error)

    if error is None:
        js = connector.generateJS()
        db.execute(
                    'INSERT INTO sess_records (user_id, title, series) VALUES (?,?,?)',
                    (session.get('user_id'), title, js))
        db.commit()
        print("Successfully saved.")
        """
############################################################

DEBUG = 0

@mqtt.on_connect()
def handle_connect(client,userdata,flags,rc):
    print('Connected to broker: ' + broker)

@mqtt.on_message()
def handle_messages(client, userdata, message):
    msg = (message.payload).decode('utf-8')
    msg_dict = json.loads(msg)
    t=msg_dict["time"]
    res=msg_dict["result"]
    #return res
    print("t={}\t\t\t\tval={}".format(t,res))
    if DEBUG:
        passprint('Received message on topic {}: {}'
          .format(message.topic, message.payload.decode()))

@mqtt.on_publish()
def handle_publish(client, userdata, mid):
    if DEBUG:
        print('Published message with mid {}.'
          .format(mid))
@mqtt.on_subscribe()
def handle_subscribe(client, userdata, mid, granted_qos):
    if DEBUG:
        print('Subscription id {} granted with qos {}.'
          .format(mid, granted_qos))

@mqtt.on_disconnect()
def handle_disconect():
    print('Disconnected')
"""
@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    print(client, userdata, level, buf)
"""
############################################################

mqtt.subscribe(sub)


i = 0
def gen_data():
    global i
    i = i+0.1
    return i.np.random.randint(10)
