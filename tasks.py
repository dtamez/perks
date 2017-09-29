#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.
from datetime import date
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from app import create_app, db


app = create_app('development')
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


@manager.command
def test():
    """Run the unit tests"""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == "__main__":
    manager.run()
