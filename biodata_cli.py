#!/usr/bin/env python2
from model._base import db
from biodata import get_base_app
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand


app = get_base_app()


migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
