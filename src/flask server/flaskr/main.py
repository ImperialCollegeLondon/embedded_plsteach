# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 14:38:34 2019
Define all user activities
@author: Sam Wan
"""

import functools

from flask import (
        Blueprint, flash, g, redirect, render_template, request, session, url_for
        )

from flaskr.db import get_db

bp = Blueprint('main', __name__, url_prefix='/main')

@bp.route('/home')
def home():
    
    return render_template('main/home.html')

@bp.route('/plot')
def plot():
    
    return render_template('main/plot.html')
    