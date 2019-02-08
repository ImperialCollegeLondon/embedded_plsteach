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
from flaskr.auth import login_required
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
                x, y = self.data.get(True, 5)
                socketio.emit('In_Data', {'x': x, 'y': y})
                print('GET', (x, y))
            except Queue.empty:
                print("Queue is empty")
                disconnectHandle(Queue.empty)
            time.sleep(0.2)
            
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
            except Queue.full:
                print("Queue is full")
                disconnectHandle(Queue.full)
            time.sleep(0.2)

@bp.route('/home')
@login_required()
def home():
    return render_template('main/home.html')

@bp.route('/plot')
@login_required()
def plot():
    return render_template('main/plot.html')

@bp.route('/status')
@login_required()
def status():
    return render_template('main/status.html')
        
@socketio.on('connect_event')
def OnConnect():
    print('Web Socket is Connected')
    queue = Queue(10)
    sender = Consumer(queue, e, socketio)
    grabber = Producer(queue, e)
    grabber.start()
    sender.start()
    print('SERVER is READY')
    socketio.emit('Server_Ready')

@socketio.on('start_transmit')
def start_transmit():
    print('Event set')
    e.set()

@socketio.on('stop_transmit')
def stop_transmit():
    print('Event clear')
    e.clear()
    
def disconnectHandle(reason):
    pass
i = 0 #!!!!!!!!!!
def gen_data():
    global i 
    i = i+0.1
    return i,np.random.randint(10)