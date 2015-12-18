from flask import Flask, g
from flask_ini import FlaskIni
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from controller import basebp


def get_app(testing = False):
    """
    Setup the application.

    The application is setup, including all request handlers and configuration.
    This way, all setup code is handled in one function and circular import
    problems, and problems with setup code being called after the first request
    was issued is avoided.

    :param testing: Indicates if the application should be running in testing mode. (Default False)
    """
    app = get_base_app(testing)
    bind_db(app)
    setup_db(app)
    @app.before_request
    def load_db():
        g.db = g.get('db', db )

    app.register_blueprint(basebp)
    return app

def bind_db(app):
    global db
    with app.app_context():
        db.init_app(app)

def get_base_app(testing = False):
    app = Flask('biodata')
    with app.app_context():
        app.iniconfig = FlaskIni()
        app.iniconfig.read('settings.cfg')
    app.config['TESTING'] = testing
    config_db(app)
    return app


def config_db(app):
    if app.config['TESTING']:
        app.config['SQLALCHEMY_DATABASE_URI'] = \
            app.iniconfig.get('database','testing_uri')
    elif app.config['ACCEPTANCE']:
        app.config['SQLALCHEMY_DATABASE_URI'] = \
            app.iniconfig.get('database','acceptance_uri')
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = \
            app.iniconfig.get('database','production_uri')

def setup_db(app):
    with app.app_context():
        db.create_all()

