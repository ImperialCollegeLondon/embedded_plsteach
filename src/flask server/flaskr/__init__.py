# -*- coding: utf-8 -*-
"""
Created on Fri Feb  1 10:04:54 2019

@author: Sam Wan
"""
import os

from flask import Flask, render_template, g, redirect, url_for
from flask_mqtt import Mqtt


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True) #instance folder is relative
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'), # .../instance/flaskr.sqlite saved only,
                                                                    #init. done in db.py
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True) #search done in instance folder
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/')
    def index():
        if g.user is None:
            return render_template('index.html')
        else:
            return redirect(url_for('main.home'))
            
    
    from . import db
    db.init_app(app) #register command and set up teardown
    
    from . import auth
    app.register_blueprint(auth.bp)
    
    from. import main
    app.register_blueprint(main.bp)
    
    #mqtt = Mqtt(app)
    
    return app