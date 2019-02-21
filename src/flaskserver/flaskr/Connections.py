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

#thresholding values for identifying sensor activation
P_thres = [14000, 15000]
K_thres = 15000

sub_config = "IC.embedded/plzteach/config"
__value = 0
__time = 0
__PIN = 0 # 0 = 0xc3, 1 = 0xd3

class Connections(Namespace): # definition of class-based namespace
                              #for websocket

    def __init__(self, queue_length, namespace):
        super(Namespace, self).__init__(namespace)
        self.queue = Queue(10)
        self.evt = threading.Event()
        self.RUN_FLAG = False
        self.INIT_FLAG = True
        self.sen_num = 0

    def on_connect(self):
        # called when request to main/plot.html is made
        print("Client is CONNECTED")
        self.queue = Queue(20)
        self.RUN_FLAG = False
        self.INIT_FLAG = True
        self.sender = Consumer(self.queue, self.evt, True)
        self.grabber = Producer(self.queue, self.evt, True)
        self.grabber.start()
        self.sender.start()
        print("Threads are STARTED")

        #get settings from db
        settings = get_settings(True)
        self.sen_num = len(settings)

        config_list = []
        signal = []
        #from the settings obtained from db, produce initilization code for pi
        for each_setting in settings:
            config_list.append(each_setting['config'])
        signal.append("[")
        for x in config_list:
            signal.append("[" + x + ", 0xE3]")
            signal.append(",")
        signal[-1] = "]"
        sigstr = ''.join(map(str,signal))
        mqtt.publish(sub_config, sigstr)
        #initialize values before plotting
        set_value(0,0)

        # pause function
    def pause_plot(self):
        if self.RUN_FLAG == True:
            mqtt.publish(sub_config, "pause")
            self.RUN_FLAG = False
        # unpause function
    def unpause_plot(self):
        if self.RUN_FLAG == False:
            mqtt.publish(sub_config, "unpause")
            self.RUN_FLAG = True
        #stop function
    def stop_plot(self):
        mqtt.publish(sub_config, "stop")
        self.INIT_FLAG = True
        set_value(0,0)
        #start function
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

        #socketio.emit('processed_in', [[{'x': 0, 'y': 2}, {'x': 1, 'y': 2}, {'x': 2, 'y': 2}, {'x': 3, 'y': 0}, {'x': 4, 'y': 0}, {'x': 5, 'y': 1}, {'x': 6, 'y': 1}, {'x': 7, 'y': 2}, {'x': 8, 'y': 0}], [{'x': 0, 'y': 2}, {'x': 1, 'y': 0}], [{'x':1, 'y': 2.2}], [{'x': 2, 'y': 2.2}]])

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
        ovlay_list_x = []
        ovlay_list_y = []
        discr_list = []
        for i in range(self.sen_num):
            ovlay_list_x.append([])
            ovlay_list_y.append([])
            discr_list.append([])

        discret_proc(self.sender.list ,discr_list ,ovlay_list_x, ovlay_list_y , self.sen_num)
        print("LIST_X: ",ovlay_list_x)
        print("LIST_Y: ",ovlay_list_y)

        """if self.sen_num == 2:
            proc_result = direct(ovlay_list_x[0], ovlay_list_y[0], ovlay_list_x[1], ovlay_list_y[1])
            final_result = discr_list.append(proc_result)
        else:"""
        final_result = discr_list
        #concatenate as {sensor 0 - 3, direct_start, direct_end}

        socketio.emit('processed_in', final_result) #!!!!



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
                # pop the data from the queue (FIFO) that is pushed by the 
                # Producer object
                x, y, p = self.data.get(True, 50)
                self.list.append((x,y,p))
                socketio.emit('data_in', {'x': x, 'y': y, 'p':p})
                print('GET', (x, y, p))
            except Queue.empty:
                print("Queue is empty")
                self.runThreads = False
            time.sleep(0.5)

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
                # get global variables for voltage and time saved at this moment
                x,y = read_value()
                # get global variable for pin number saved at this moment
                p = read_pin()
                # push the data into the queue (FIFO) to be popped by the
                # Consumer object
                self.data.put([x,y,p],True, 50)
                print("PUT", [x,y,p])
            except Queue.empty:
                print("Queue is full")
                self.runThreads = False
            time.sleep(0.5)
# handles global values that corresponds to the voltage, time and device pin of
# the message received on the subscribed mqtt topic. We are using global values
# because the mqtt callbacks on flask does not play well with containers and
# local variables for some reason. We suspect that this is due to the decorator
# function. Global variable is an easy fix to this solution but should not be
# a permanent solution.

# getter for time and voltage
def read_value():
    global __value
    global __time
    global __
    return __time, __value
# setter for time and voltage
def set_value(y, x):
    global __value
    global __time
    __value = y
    __time = x
# getter for pin
def read_pin():
    global __PIN
    return __PIN

#setter for pin
def set_pin(x):
    if x != None:
        global __PIN
        __PIN = x
# callback on connect from mqtt broker
@mqtt.on_connect()
def handle_connect():
    print("MQTT is Connected")
# callback on disconnect from mqtt broker
@mqtt.on_disconnect()
def handle_disconect():
    print('MQTT Disconnected')
# callback on message received on subscribed mqtt topic
@mqtt.on_message()
def handle_messages(client, userdata, message):
    # decoding required when reading in msg for some reason
    msg = (message.payload).decode()
    # decode the actual json string and convert it to a python dictionary
    msg_dict = json.loads(msg)
    # get the timestamp of the data sampled by pi
    t=msg_dict["time"]
    # there are two possible sensors at the moment, the 2 hex codes correspond
    # to the sensor configuration code that's sent to the pi, we don't actually
    # need to use 0xc3 or 0xd3 it can be any string that identifies the both,
    # we are using these strings arbitrarily
    if "0xc3" in msg_dict:
    # key to voltage in python dictionary is the corresponding hex code to the
    # sensor
        v = msg_dict["0xc3"]
    # setting the pin so that we can identify which device is the message sent
    # from
        set_pin(0)
    # same as above
    if "0xd3" in msg_dict:
        v = msg_dict["0xd3"]
        set_pin(1)
    # update global variables
    set_value(v,t)

def discret_proc(raw_data, discr_list, ovlay_list_x, ovlay_list_y, sen_num):
    temp_locator = []
    for i in range(sen_num):
        temp_locator.append(0)

    for (ind,elem) in enumerate(raw_data):
        x, y, p = elem[0], elem[1], elem[2]

        if p == 0: #pedal(default)
            if y < P_thres[0]:
                y = 0
            elif y < P_thres[1]:
                y = 1
            else:
                y = 2
        elif p == 1: #key/drum
            if y > K_thres:
                y = 2
            else:
                y = 0

        discr_list[p].append({'x': x, 'y': y})
        if temp_locator[p] != y: #change in value
            temp_locator[p] = y
            ovlay_list_x[p].append(x)
            ovlay_list_y[p].append(y)
