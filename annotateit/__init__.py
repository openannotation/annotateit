"""
Backend for web annotation.

@copyright: (c) 2006-2012 Open Knowledge Foundation
"""

__all__ = ['create_app', 'create_db', 'drop_db',
           'create_indices', 'drop_indices',
           'create_all', 'drop_all']

from logging import getLogger

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flaskext.mail import Mail

from annotator import es # ElasticSearch object

from annotateit.config import configure

log = getLogger(__name__)
db = SQLAlchemy()
mail = Mail()

def create_app():
    log.debug("Creating %s application", __name__)
    app = Flask(__name__)

    configure(app)

    # Configure database
    db.init_app(app)

    # Configure mailer
    mail.init_app(app)
    app.extensions['mail'] = mail

    # Configure ES
    es.init_app(app)

    # Add regex converter
    from annotateit.util import RegexConverter
    app.url_map.converters['regex'] = RegexConverter

    # Add filters
    from annotateit.util import filters
    for name, func in vars(filters).iteritems():
        if not name.startswith('_'):
            app.template_filter()(func)

    # Mount views
    from annotator import store
    from annotateit import user, main
    app.register_blueprint(store.store, url_prefix='/api')
    app.register_blueprint(user.user, url_prefix='/user')
    app.register_blueprint(main.main)

    app.before_request(main.before_request)
    app.errorhandler(404)(main.page_not_found)
    app.errorhandler(401)(main.not_authorized)

    log.debug("Successfully created %s application", __name__)
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
