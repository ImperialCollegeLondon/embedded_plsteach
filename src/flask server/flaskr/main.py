# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 14:38:34 2019
Define all user activities and functions under main.bp
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

bp = Blueprint('main', __name__, url_prefix='/main')
class Connections(Namespace):
        
    def __init__(self, queue_length, namespace):
        super(Namespace, self).__init__(namespace)
        self.queue = Queue(10)
        self.evt = threading.Event()
        self.sender = Consumer(self.queue, self.evt, True)
        self.grabber = Producer(self.queue, self.evt, True)
       
    def start_threads(self):
        self.grabber.start()
        self.sender.start()
    
    def on_start_transmit(self):
        self.evt.set()
        print('Event is SET')
        
    def on_stop_transmit(self):
        self.evt.clear()
        print('Event is CLEARED')
        
    def on_disconnect(self):
        self.grabber.runThreads = False #kill threads
        self.sender.runThreads = False #kill threads
    
    """def on_save(self):
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
            js = connector.generateJS()
            db.execute(
                        'INSERT INTO sess_records (user_id, title, series) VALUES (?,?,?)',
                        (session.get('user_id'), title, js))
            db.commit()
            print("Successfully saved.")
        return self.sender.gen_JS()"""
                
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
        
    def run(self):
        while self.runThreads:
            self.event.wait()
            try: 
                tmp = gen_data()
                self.data.put(tmp,True, 5)
                print("PUT", tmp)
            except Queue.full:
                print("Queue is full")
                self.runThreads = False
            time.sleep(0.2)

@bp.route('/home')
@login_required
def home():
    return render_template('main/home.html')

@bp.route('/plot')
@login_required
def plot():
    return render_template('main/plot.html')

@bp.route('/status')
@login_required
def status():
    return render_template('main/status.html')

@bp.route('/widget_settings')
@login_required
def widget_settings():
    return render_template('main/widget_settings.html')   

@bp.route('/view')
@login_required
def view():
    return render_template('main/view.html') 

@socketio.on('connect', namespace='/main/plot')
def OnConnect():
    print('WS Client is CONNECTED')
    #connector = socketio.on_namespace(Connections(10,'/main/plot'))
    #connector = Connections(10, '/main/plot')
    #connector.start_threads()
    print('SERVER is READY')
    socketio.emit('Server_Ready')

"""
@socketio.on('start_transmit')
def start_transmit():
    connector.start_transmit()
    
@socketio.on('stop_transmit')
def stop_transmit():
    connector.stop_transmit()

@socketio.on('disconnect')
def Disconnect():
    print('WS Client is DISCONNECTED')
    connector.onDisconnect()
    print('Threads STOPPED')

@socketio.on('save')
def save_record():
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
        js = connector.generateJS()
        db.execute(
                    'INSERT INTO sess_records (user_id, title, series) VALUES (?,?,?)',
                    (session.get('user_id'), title, js))
        db.commit()
        print("Successfully saved.")
        """
i = 0 #!!!!!!!!!!
def gen_data():
    global i 
    i = i+0.1
    return i,np.random.randint(10)