from flask import Flask
from flask_ini import FlaskIni
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask('biodata')
with app.app_context():
    app.iniconfig = FlaskIni()
    app.iniconfig.read('settings.cfg')
db = SQLAlchemy()

def init_db():
    if app.config['TESTING']:
        app.config['SQLALCHEMY_DATABASE_URI'] = \
            app.iniconfig.get('database','testing_uri')
    elif app.config['ACCEPTANCE']:
        app.config['SQLALCHEMY_DATABASE_URI'] = \
            app.iniconfig.get('database','acceptance_uri')
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = \
            app.iniconfig.get('database','production_uri')
    with app.app_context():
        db.init_app(app)
        db.create_all()
