# -*- coding: utf-8 -*-
import logging

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy as sa

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')

db = sa(app)
mail = Mail(app)
migrate = Migrate(app)

logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
engine = db.create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True)
login_manager = LoginManager()
login_manager.init_app(app)

toolbar = DebugToolbarExtension(app)

from perks import models, views  # NOQA
from perks.util import assets  # NOQA
models.Base.metadata.bind = engine


@app.teardown_appcontext
def shutdown_session(exception=None):
        db.session.remove()


if __name__ == '__main__':
    app.run()
