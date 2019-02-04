# -*- coding: utf-8 -*-
"""
Created on Fri Feb  1 11:29:21 2019
Views: handle and respond incoming requests
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

bp = Blueprint('main', __name__, url_prefix='/main') #url prefix 

@bp.route('/home')
def home():
        
    return render_template('main/home.html')

@bp.route('/plot')
def plot():
   

    return render_template('main/')

        
