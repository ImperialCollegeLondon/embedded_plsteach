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

__value = 0
__time = 0

class Connections(Namespace):

    def __init__(self, queue_length, namespace):
        super(Namespace, self).__init__(namespace)
        self.queue = Queue(10)
        self.evt = threading.Event()

    def on_connect(self):
        #mqtt
        print("WS Client is CONNECTED")
        self.sender = Consumer(self.queue, self.evt, True)
        self.grabber = Producer(self.queue, self.evt, True)   #need to pass mqtt object
        self.grabber.start()
        self.sender.start()
        print("Threads are STARTED")
        

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

        #self.mqtt.publish("IC.embedded/plzteach/config", "[[0xC3,0xE3]]")
        #time.sleep(0.1)

        while self.runThreads:
            self.event.wait()
            try:
                @self.mqtt.on_message()
                def handle_messages(client, userdata, message):
                    msg = (message.payload).decode()
                    msg_dict = json.loads(msg)
                    t=msg_dict["time"]
                    v=msg_dict["result"]
                    set_value(v,t)
                v,t = read_value()
                self.data.put([1,1],True, 50)
                print("PUT", (1,1))
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

@mqtt.on_disconnect()
def handle_disconect():
    print('MQTT Disconnected')
