# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.
import logging

from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from flask_errormail import mail_on_500
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy as sa

from config import config


db = sa()
mail = Mail()
migrate = Migrate()
toolbar = DebugToolbarExtension()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    cfg = config[config_name]
    app.config.from_object(cfg)
    cfg.init_app(app)

    db.init_app(app)
    mail.init_app(app)
    mail_on_500(app, cfg.ADMINS)
    migrate.init_app(app)
    login_manager.init_app(app)
    toolbar.init_app(app)

    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    if not app.debug and not app.testing and not app.config['SSL_DISABLE']:
        from flask_sslify import SSLify
        sslify = SSLify()
        sslify.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app

    @app.teardown_appcontext
    def shutdown_session(exception=None):
            db.session.remove()


if __name__ == '__main__':
    app = create_app('development')
    app.run()
