# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 14:38:34 2019
Define all user activities
@author: Sam Wan
"""

import time
import numpy as np
from flask import (
        Blueprint, flash, g, redirect, render_template, request, session, url_for,
        )

from flaskr.db import get_db
from flask_socketio import emit
from . import socketio

bp = Blueprint('main', __name__, url_prefix='/main')

class Communicator(object):
    send_toggle = False
    
    def __init__(self, socketio):
        self.socketio = socketio
        self.send_toggle = send_toggle
    
    def send(self):
        while self.send_toggle:
            
    
    def stop(self):
        self.send_toggle = False

@bp.route('/home')
def home():
    return render_template('main/home.html')

@bp.route('/plot')
def plot():
    return render_template('main/plot.html')

@socketio.on('connect_event')
def connect():
    print('CONNECTED')
    global pong
    pong = Communicator(socketio)
    pong.emit('server_ready')
    print('SERVER READY')

@socketio.on('start_transmit')
def send_data():
    y = grab_data()
    socketio.emit('server_response', {'x': i, 'y': y})

@socketio.on('stop_transmit')
def stop_data():
    pass

i = 0
def grab_data():
    nonlocal i
    i = i+1
    print(i)
    return i, np.random.randint(10)
