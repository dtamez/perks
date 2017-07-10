# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.
# Default configuation
# Can be overridden in instance/config.py
DEBUG = False
SQLALCHEMY_RECORD_QUERIES = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQL_ALCHEMY_ECHO = False

# flask_user configuration
USER_APP_NAME = 'Perks'
USER_ENABLE_CONFIRM_EMAIL = True

# to be supplied in instance cfg files
SECRET_KEY = ''
SQLALCHEMY_DATABASE_URI = ''
MAIL_SERVER = ''
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = ''
MAIL_PASSWORD = ''
MAIL_DEFAULT_SENDER = ''
