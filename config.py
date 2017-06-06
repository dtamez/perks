# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.
# Default configuation
# Can be overridden in instance/config.py
DEBUG = False
SECRET_KEY = 'some key'
SQL_ALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False

# flask_user configuration
USER_APP_NAME = 'Perks'
USER_ENABLE_CONFIRM_EMAIL = True
