# -*- coding: utf-8 -*-
"""
Created on Fri Feb  1 10:36:33 2019
Setup database connection, teardown function and CLI function
@author: Sam Wan
"""

import sqlite3

import click
from flask import current_app, g #g stores data for multiple access
from flask.cli import with_appcontext

#connection tied to request

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect( #g holds application_level context
                current_app.config['DATABASE'],
                detect_types=sqlite3.PARSE_DECLTYPES
                )
        g.db.row_factory = sqlite3.Row #connection returns rows like dicts
        
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    
    if db is not None:
        db.close()
        
def init_db():
    db = get_db()
    
    with current_app.open_resource('schema.sql') as f:# open file relative to flaskr package
        db.executescript(f.read().decode('utf8'))
        
@click.command('init-db') #command definition
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Initialized the database.')

#close_db() and init_db_command() needs to be registered
#with application instance, for factory function:

def init_app(app):
    app.teardown_appcontext(close_db) #clean up after response (called when request or app context popped)
    app.cli.add_command(init_db_command) #add command callable by flask cli command