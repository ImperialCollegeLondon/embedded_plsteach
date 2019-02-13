# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 14:38:34 2019
Define all user activities and functions under main.bp
@author: Sam Wan
"""

from flask import (
        Blueprint, flash, g, redirect, render_template, request, session, url_for, Flask
        )
from flaskr.auth import login_required
from flaskr.db import get_db
from . import mqtt
import json

bp = Blueprint('main', __name__, url_prefix='/main')
config_table = ['0xC3', '0xD3', '0xE3', '0xF3']
sub = 'IC.embedded/plzteach/result'

@bp.route('/home')
@login_required
def home():
    return render_template('main/home.html')

@bp.route('/plot')
@login_required
def plot():
    user_settings = get_settings_for_web()
    mqtt.subscribe(sub)
    return render_template('main/plot.html', user_settings = json.dumps(user_settings))

@bp.route('/status#/dashboard', methods=('GET','POST'))
@login_required
def status():
    g.user_settings = get_settings_for_web()
    #data = [{'sensor_name':'test1', 'pin': 1, 'topic':'t1'}, {'sensor_name':'test2', 'pin': 2, 'topic':'t2'}]
    print('user: ', g.user_settings)
    if request.method == 'POST':
        sensor_name = request.form['sensor_name']
        pin_no = int(request.form['pin'])
        print('Posted', sensor_name, pin_no)
        error = None
        config = config_table[pin_no]

        if len(g.user_settings) >=4:
            error = 'You can have at most 4 sensors.'
        elif sensor_name in g.user_settings:
            error = 'Sensor already exists.'
        if error is None:
            db = get_db()
            db.execute(
                    'INSERT INTO settings (user_id, sensor_name, config, pin_num) VALUES (?,?,?,?)',
                    (session.get('user_id'), sensor_name, config, pin_no))
            db.commit()
            #return render_template('main/status.html', data = json.dumps(g.user_settings))
            return redirect(url_for('main.status'))
    
    return render_template('main/status.html', data = json.dumps(g.user_settings))

@bp.route('/widget_settings', methods = ('GET', 'POST'))
@login_required
def widget_settings():
    if request.method == 'POST':
        print('here')
    return render_template('main/widget_settings.html')

@bp.route('/view')
@login_required
def view():
    return render_template('main/view.html')

def get_settings_for_web():
    user_id = session.get('user_id')
    db = get_db()
    db_list = list(db.execute(
            'SELECT sensor_name, pin_num FROM settings WHERE user_id=?', (user_id,)
            ).fetchall())
    settings = []
    for row_elem in db_list:
        settings.append(dict(row_elem))
    return settings
    
    
