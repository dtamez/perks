#! /usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import date
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from perks import app, db


migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
@manager.option('-e', '--email', help='Admin email address')
def create_admin(email):
    from perks.models import Role, User, user_manager

    role = Role.query.filter(Role.name == 'admin').first()
    if not role:
        role = Role()
        role.label = 'Administrator'
        role.name = 'admin'

    admin = User()
    admin.active = True
    admin.confirmed_at = date.today()
    admin.email = email
    admin.roles.append(role)
    admin.username = 'admin'
    password = user_manager.hash_password('password')
    user_manager.update_password(admin, password)

    db.session.add(admin)
    db.session.commit()


if __name__ == "__main__":
    manager.run()
