#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.
from datetime import date
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell
import logging
import logzero
import os

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

if os.path.exists('.env'):
    print('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

from app import create_app, db  # NOQA


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def seed_data():
    from app.models import IRSLimits

    limits = IRSLimits()
    limits.max_401k_salary_deferal = 100000
    limits.max_401k_salary_deferal_over_50 = 11000
    limits.max_fsa_dependent_care_contribution = 2200
    limits.max_fsa_medical_contribution = 3000
    limits.max_hsa_family_contribution = 4600
    limits.max_hsa_family_over_55_contribution = 5500
    limits.max_hsa_individual_contribution = 2600

    db.session.add(limits)
    db.session.commit()


@manager.command
@manager.option('-e', '--email', help='Admin email address')
def create_admin(email, password):
    from app.models import User

    admin = User()
    admin.active = True
    admin.confirmed_at = date.today()
    admin.email = email
    admin.password = password
    admin.is_admin = True

    db.session.add(admin)
    db.session.commit()


def make_shell_context():
    from app import models
    return dict(app=app, db=db, models=models)


manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
def test(coverage=False):
    """Run the unit tests."""
    logzero.loglevel(level=logging.FATAL)
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


if __name__ == "__main__":
    manager.run()
