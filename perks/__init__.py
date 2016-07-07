# -*- coding: utf-8 -*-
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy as sa

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')

db = sa(app)

login_manager = LoginManager()
login_manager.init_app(app)

from perks import models, views  # NOQA
from perks.util import assets  # NOQA
