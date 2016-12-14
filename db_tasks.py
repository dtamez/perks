#! /usr/bin/env python
# -*- coding: utf-8 -*-
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from perks import app, db


migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


if __name__ == "__main__":
    manager.run()
