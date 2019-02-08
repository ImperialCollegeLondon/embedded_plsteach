# -*- coding: utf-8 -*-
"""
Created on Fri Feb  8 19:17:08 2019
Connections Class Definition
@author: Sam Wan
"""
import time, threading
from queue import Queue
from . import socketio
class Connections():
        
    def __init__(self, queue_length):
        self.queue = Queue(queue_length)
        self.evt = threading.Event()
        self.sender = Consumer(self.queue, self.evt, True)
        self.grabber = Producer(self.queue, self.evt, True)
       
    def start_threads(self):
        self.grabber.start()
        self.sender.start()
    
    def start_transmit(self):
        self.evt.set()
        print('Event is SET')
        
    def stop_transmit(self):
        self.evt.clear()
        print('Event is CLEARED')
        
    def onDisconnect(self):
        self.grabber.runThreads = False #kill threads
        self.sender.runThreads = False #kill threads
                
class Consumer(threading.Thread):
    
    def __init__(self, queue, event, runThreads):
        threading.Thread.__init__(self)
        self.data = queue
        self.event = event
        self.runThreads = runThreads
    
    def run(self):
        print('running')
        while self.runThreads:
            self.event.wait()
            try:
                x, y = self.data.get(True, 5)
                socketio.emit('In_Data', {'x': x, 'y': y})
                print('GET', (x, y))
            except Queue.empty:
                print("Queue is empty")
                socketio.emit('Sensor_Dc')
                self.runThreads = False
            time.sleep(0.2)
            
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
