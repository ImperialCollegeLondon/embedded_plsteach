# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 14:38:34 2019
Define all user activities
@author: Sam Wan
"""

import functools, time
import numpy as np
from flask import (
        Blueprint, flash, g, redirect, render_template, request, session, url_for,
        )

from flaskr.db import get_db
from flask_socketio import send, emit
from . import socketio

bp = Blueprint('main', __name__, url_prefix='/main')

@bp.route('/home')
def home():
    
    return render_template('main/home.html')

@bp.route('/plot')
def plot():
    
    return render_template('main/plot.html')

@socketio.on('connect_event')
def send_data():
    print('CONNECTED')
    for i in range(20):
        num = np.random.randint(10)
        emit('server_response', {'time': i, 'data': num})
        print('SENT: ', num )
        time.sleep(0.5)
    