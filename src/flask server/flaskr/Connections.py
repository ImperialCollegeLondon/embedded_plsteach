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
from flaskr.main import get_settings

sub_config = "IC.embedded/plzteach/config"
__value = 0
__time = 0
__PIN = 0 # 0 = 0xc3, 1 = 0xd3

class Connections(Namespace):

    def __init__(self, queue_length, namespace):
        super(Namespace, self).__init__(namespace)
        self.queue = Queue(10)
        self.evt = threading.Event()
        self.RUN_FLAG = False
        self.INIT_FLAG = True

    def on_connect(self):
        print("Client is CONNECTED")
        self.queue = Queue(10)
        self.RUN_FLAG = False
        self.INIT_FLAG = True
        self.sender = Consumer(self.queue, self.evt, True)
        self.grabber = Producer(self.queue, self.evt, True)
        self.grabber.start()
        self.sender.start()
        print("Threads are STARTED")

        settings = get_settings(True)
        config_list = []
        for each_setting in settings:
            config_list.append(each_setting['config'] + ',0xE3')

        mqtt.publish(sub_config, "[[0xC3,0xE3],[0xD3,0xE3]]")

    def pause_plot(self):
        if self.RUN_FLAG == True:
            mqtt.publish(sub_config, "pause")
            self.RUN_FLAG = False


    def unpause_plot(self):
        if self.RUN_FLAG == False:
            mqtt.publish(sub_config, "unpause")
            self.RUN_FLAG = True

    def stop_plot(self):
        mqtt.publish(sub_config, "stop")
        self.INIT_FLAG = True

    def start_plot(self):
        if self.INIT_FLAG == True:
            mqtt.publish(sub_config, "unpause")
            self.RUN_FLAG = True
            self.INIT_FLAG = False

    def on_start_transmit(self):
        self.start_plot()
        self.unpause_plot()
        self.evt.set()
        print('Event is SET')

    def on_stop_transmit(self):
        self.pause_plot()
        self.evt.clear()
        print('Event is CLEARED')

    def on_stop(self):
        print("Plotting is STOPPING")
        self.stop_plot()
        self.evt.clear()
        self.grabber.runThreads = False #kill threads
        self.sender.runThreads = False #kill threads
        print("Plotting is STOPPED")

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
    
    def on_process(self):
        pass

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
                x, y, p = self.data.get(True, 50)
                self.list.append((x,y,p))
                socketio.emit('data_in', {'x': x, 'y': y, 'p':p})
                print('GET', (x, y, p))
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

        while self.runThreads:
            self.event.wait()
            try:
                x,y = read_value()
                p = read_pin()
                print([x,y,p])
                self.data.put([x,y,p],True, 50)
                print("PUT", [x,y,p])
            except Queue.full:
                print("Queue is full")
                self.runThreads = False
            time.sleep(0.2)

def read_value(): #getter
    global __value
    global __time
    global __
    return __time, __value

def set_value(y, x): #setter
    global __value
    global __time
    __value = y
    __time = x

def set_pin(x):
    if x != None:
        global __PIN
        __PIN = x

def read_pin():
    global __PIN
    return __PIN

@mqtt.on_connect()
def handle_connect():
    print("MQTT is Connected")

@mqtt.on_disconnect()
def handle_disconect():
    print('MQTT Disconnected')

@mqtt.on_message()
def handle_messages(client, userdata, message):
    msg = (message.payload).decode()
    msg_dict = json.loads(msg)
    t=msg_dict["time"]
    if "0xc3" in msg_dict:
        v = msg_dict["0xc3"]
        set_pin(0)
    if "0xd3" in msg_dict:
        v = msg_dict["0xd3"]
        set_pin(1)
    set_value(v,t)
