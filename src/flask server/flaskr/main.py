# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 14:38:34 2019
Define all user activities
@author: Sam Wan
"""

import time, threading
from queue import Queue
import numpy as np
from flask import (
        Blueprint, flash, g, redirect, render_template, request, session, url_for,
        )

from flaskr.db import get_db
from flask_socketio import emit
from . import socketio

bp = Blueprint('main', __name__, url_prefix='/main')
e = threading.Event() #!!!!!!!!!!!!!! global for test only

class Consumer(threading.Thread):
    
    def __init__(self, queue, event, socketio):
        threading.Thread.__init__(self)
        self.data = queue
        self.event = event
        self.socketio = socketio
    
    def run(self):
        while 1:
            self.event.wait()
            try:
                time, y = self.data.get(True, 5)
                socketio.emit('In_Data', {'x': time, 'y': y})
            except Queue.Empty:
                print("Queue is empty")
                disconnectHandle(Queue.Empty)
            time.sleep(1)
            
class Producer(threading.Thread):

    def __init__(self, queue, event):
        threading.Thread.__init__(self)
        self.data = queue
        self.event = event
        
    def run(self):
        while 1:
            self.event.wait()
            try: 
                tmp = gen_data()
                self.data.put(tmp,True, 5)
                print("PUT", tmp)
            except Queue.Full:
                print("Queue is full")
                disconnectHandle(Queue.Full)
            time.sleep(1)
       

@bp.route('/home')
def home():
    return render_template('main/home.html')

@bp.route('/plot')
def plot():
    return render_template('main/plot.html')
        
@socketio.on('connect_event')
def OnConnect():
    print('CONNECTED')
    sender = Consumer(e)
    grabber = Producer(e)
    grabber.start()
    sender.start()
    print('SERVER READY')
    socketio.emit('Server_Ready')

@socketio.on('start_transmit')
def start_transmit():
    e.set()

@socketio.on('stop_transmit')
def stop_transmit():
    e.clear()
    
def disconnectHandle(reason):
    pass
i=0 #!!!!!!!!!!
def gen_data():
    nonlocal i
    i+=1
    return i, np.random.randint(10)