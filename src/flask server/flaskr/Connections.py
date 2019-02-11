# -*- coding: utf-8 -*-
"""
Created on Mon Feb 11 01:16:15 2019

@author: Sam Wan
"""
import time, threading, json
from queue import Queue
import numpy as np
from flask import (
        Blueprint, flash, g, redirect, render_template, request, session, url_for,
        )
from flaskr.auth import login_required
from flaskr.db import get_db
from flask_socketio import emit, Namespace
from . import socketio
from flask_mqtt import Mqtt

__value = 0
__time = 0

class Connections(Namespace):

    def __init__(self, queue_length, namespace):
        super(Namespace, self).__init__(namespace)
        self.queue = Queue(10)
        self.evt = threading.Event()

    def on_connect(self):
        #mqtt
        sub = 'IC.embedded/plzteach/thomas'
        topic = 'IC.embedded/plzteach/test'
        broker = 'test.mosquitto.org'
        app = Flask(__name__)
        app.config['MQTT_BROKER_URL'] = broker
        app.config['MQTT_BROKER_PORT'] = 1883
        mqtt = Mqtt(app)

        print("WS Client is CONNECTED")
        self.sender = Consumer(self.queue, self.evt, True)
        self.grabber = Producer(self.queue, self.evt, True, mqtt)   #need to pass mqtt object
        self.grabber.start()
        self.sender.start()
        print("Threads are STARTED")
        socketio.emit('Ready')

    def on_start_transmit(self):
        self.evt.set()
        print('Event is SET')

    def on_stop_transmit(self):
        self.evt.clear()
        print('Event is CLEARED')

    def on_disconnect(self):
        self.evt.clear()
        self.grabber.runThreads = False #kill threads
        self.sender.runThreads = False #kill threads

    def on_save(self):
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
            js = self.sender.generateJS()
            db.execute(
                        'INSERT INTO sess_records (user_id, title, series) VALUES (?,?,?)',
                        (session.get('user_id'), title, js))
            db.commit()
            print("Successfully saved.")
        return self.sender.gen_JS()

class Consumer(threading.Thread):

    def __init__(self, queue, event, runThreads):
        threading.Thread.__init__(self)
        self.data = queue
        self.event = event
        self.runThreads = runThreads
        self.list = []

    def run(self):
        while self.runThreads:
            self.event.wait()
            try:
                x, y = self.data.get(True, 5)
                self.list.append((x,y))
                socketio.emit('In_Data', {'x': x, 'y': y})
                print('GET', (x, y))
            except Queue.empty:
                print("Queue is empty")
                socketio.emit('Sensor_Dc')
                self.runThreads = False
            time.sleep(0.2)

    def gen_JS(self):
        return json.dumps(dict(list))

class Producer(threading.Thread):

    def __init__(self, queue, event, runThreads):
        threading.Thread.__init__(self)
        self.data = queue
        self.event = event
        self.runThreads = runThreads
        self.mqtt = mqtt

    def run(self):
    while self.runThreads:
        self.event.wait()
        self.mqtt.subscribe("IC.embedded/plzteach/thomas")
        try:
            @self.mqtt.on_message()
            def handle_messages(client, userdata, message):
                msg = (message.payload).decode('utf-8')
                msg_dict = json.loads(msg)
                t=msg_dict["time"]
                v=msg_dict["result"]
                set_value(v,t)
            v,t = read_value()
            self.data.put([v,t],True, 5)
            print("PUT", v)
        except Queue.full:
            print("Queue is full")
            self.runThreads = False
        time.sleep(0.2)

def read_value(): #getter
    global __value
    global __time
    return __value, __time
def set_value(y, x): #setter
    global __value
    global __time
    __value = y
    __time = x
