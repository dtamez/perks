# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.
import os
basedir = os.path.abspath(os.path.dirname(__file__))
DEBUG = False  # os.getenv('DEBUG', False)
DEBUG_TB_INTERCEPT_REDIRECTS = os.getenv('DEBUG_TB_INTERCEPT_REDIRECTS', False)
SECRET_KEY = os.getenv('SECRET_KEY', 'Not very secret')  # '78asfoijja*sd0^0qwer098nq535)N&)N)wrjq0w450'

SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQL_ALCHEMY_ECHO = False   # os.getenv('SQL_ALCHEMY_ECHO', False)
SQLALCHEMY_RECORD_QUERIES = False  # DEBUG
SQLALCHEMY_TRACK_MODIFICATIONS = False   # os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', False)

MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = os.getenv('MAIL_USERNAME')  #
MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')  # 'jmbwkcdfcarnifxl'
MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@perks.co')

ADMINS = [os.getenv('ADMINS')]
