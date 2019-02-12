from flask import Flask, render_template
from flask_mqtt import Mqtt

app = Flask(__name__)
app.config['SECRET'] = 'my secret key'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MQTT_BROKER_URL'] = "test.mosquitto.org"
app.config['MQTT_BROKER_PORT'] = 1883

mqtt = Mqtt(app)
mqtt.subscribe('IC.embedded/plzteach/#')
               
print('started')

@mqtt.on_connect()
def con_handler(client, userdata, flags, rc):
    print('connected')
    
@mqtt.on_message()
def msg_handler(client, userdata, message):
    print('Received msg: ', message.payload.decode())


