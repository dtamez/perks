# -*- coding: utf-8 -*-
from flask import render_template

from flask_user import login_required

from perks import app


@app.route('/')
@login_required
def index():
    return render_template('index.html')
