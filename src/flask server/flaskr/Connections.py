# -*- coding: utf-8 -*-
"""
Created on Mon Feb 11 01:16:15 2019

@author: Sam Wan
"""
import time, threading, json
from queue import Queue
import numpy as np
from flask import (
        Blueprint, flash, g, redirect, render_template, request, session, url_for, Flask
        )
from flaskr.auth import login_required
from flaskr.db import get_db
from flask_socketio import emit, Namespace
from . import socketio
from . import mqtt

sub_config = "IC.embedded/plzteach/config"
#sub_result = "IC.embedded/plzteach/result"
__value = 0
__time = 0
__RUN_FLAG = False

class Connections(Namespace):

    def __init__(self, queue_length, namespace):
        super(Namespace, self).__init__(namespace)
        self.queue = Queue(10)
        self.evt = threading.Event()

    def on_connect(self):
        #mqtt
        print("WS Client is CONNECTED")
        self.sender = Consumer(self.queue, self.evt, True)
        self.grabber = Producer(self.queue, self.evt, True)
        self.grabber.start()
        self.sender.start()
        print("Threads are STARTED")

    def pause_plot(self):
        global __RUN_FLAG
        if not __RUN_FLAG:
            mqtt.publish(sub_config, "pause")
            __RUN_FLAG = False

    def unpause_plot(self):
        global __RUN_FLAG
        if not __RUN_FLAG:
            mqtt.publish(sub_config, "unpause")
            __RUN_FLAG = False

    def stop_plot(self):
        global __RUN_FLAG
        if not __RUN_FLAG:
            mqtt.publish(sub_config, "stop")
            __RUN_FLAG = False

    def device_sel(self, sel):
        global __DEVICE
        if sel == 1 or 2 or 3:
            __DEVICE = sel

    def on_start_transmit(self):
        self.evt.set()
        print('Event is SET')

    def on_stop_transmit(self):
        self.evt.clear()
        print('Event is CLEARED')

    def on_disconnect(self):
        print("WS Client is DISCONNECTED")
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
                x, y = self.data.get(True, 50)
                self.list.append((x,y))
                socketio.emit('data_in', {'x': x, 'y': y})
                print('GET', (x, y))
            except Queue.empty:
                print("Queue is empty")
                #emit('Sensor_Dc')
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
        #send starting signal to pi
        self.mqtt.publish(sub_config, "[[0xC3,0xE3]]")
        global __RUN_FLAG
        __RUN_FLAG = True
        time.sleep(0.1)

        while self.runThreads:
            self.event.wait()
            try:
                v,t = read_value()
                self.data.put([t,v],True, 50)
                print("PUT", (t,v))
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
@mqtt.on_connect()
def handle_connect():
    print("MQTT is Connected!")

@mqtt.on_disconnect()
def handle_disconect():
    print('MQTT Disconnected REEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')

@mqtt.on_message()
def handle_messages(client, userdata, message):
    global __DEVICE_LIST, __DEVICE
    msg = (message.payload).decode()
    msg_dict = json.loads(msg)
    t=msg_dict["time"]
    v=msg_dict["0xC3"]
    v = v-1.5
    set_value(v,t)
