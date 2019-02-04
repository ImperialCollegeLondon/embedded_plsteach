# -*- coding: utf-8 -*-
"""
Created on Fri Feb  1 11:29:21 2019
Views: handle and respond incoming  requests
Blueprints: group related views
Blueprints registered to application when available
This file contains the authentication views (blueprint)
@author: Sam Wan
"""

import functools

from flask import (
        Blueprint, flash, g, redirect, render_template, request, session, url_for
        )
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth') #url prefix 

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username'] #dict like
        password = request.form['password']
        db = get_db()
        error = None
        
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
                'SELECT id FROM user WHERE username =?', (username,)).fetchone() is not None:
            error = 'User {} is alreqady registered.'.format(username)
        
        if error is None:
            db.execute(
                    'INSERT INTO user (username, password) VALUES (?,?)',
                    (username, generate_password_hash(password)))
            db.commit() #require to save data modifications
            return redirect(url_for('auth.login')) #generate redirect response 
                                                    #url based on view name
                                                    #link is prepended to bp
        
        flash(error)
        
    return render_template('auth/register.html') #return html

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear() #session is dict that stores data across requests
            session['user_id'] = user['id'] #user info loaded and made available to other views after logins
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request # function that runs before any view
def load_logged_in_user(): #checks if a user id is in a session, then fetch data
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()
        
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
        
