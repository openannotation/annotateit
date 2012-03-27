"""
Backend for web annotation.

@copyright: (c) 2006-2012 Open Knowledge Foundation
"""

__all__ = ['__version__', '__license__', '__author__',
           'create_app', 'create_db', 'drop_db',
           'create_indices', 'drop_indices',
           'create_all', 'drop_all']

import logging

from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy
from flaskext.mail import Mail

from annotator import es # ElasticSearch object
db = SQLAlchemy()
mail = Mail()

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object('annotateit.default_settings')
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'] % app.instance_path

    app.config.from_pyfile('annotateit.cfg', silent=True)
    app.config.from_envvar('ANNOTATEIT_CONFIG', silent=True)

    # Configure database
    db.init_app(app)

    # Configure mailer
    mail.init_app(app)
    app.extensions['mail'] = mail

    # Configure ES
    es.init_app(app)

    # Mount views
    from annotator import store
    from annotateit import user, main
    app.register_blueprint(store.store, url_prefix='/api')
    app.register_blueprint(user.user, url_prefix='/user')
    app.register_blueprint(main.main)

    app.before_request(main.before_request)
    app.errorhandler(404)(main.page_not_found)
    app.errorhandler(401)(main.not_authorized)

    return app

def create_indices(app):
    from .model import Annotation
    with app.test_request_context():
        Annotation.create_all()

def drop_indices(app):
    from .model import Annotation
    with app.test_request_context():
        Annotation.drop_all()

def create_db(app):
    from . import model
    with app.test_request_context():
        db.create_all()

def drop_db(app):
    from . import model
    with app.test_request_context():
        db.drop_all()

def create_all(app):
    create_indices(app)
    create_db(app)

def drop_all(app):
    drop_indices(app)
    drop_db(app)
