"""
Backend for web annotation.

@copyright: (c) 2006-2012 Open Knowledge Foundation
"""

__all__ = ['__version__', '__license__', '__author__',
           'create_app', 'create_db', 'drop_db',
           'create_indices', 'drop_indices',
           'create_all', 'drop_all']

from flask import Flask
from flask import g, current_app, request
from flaskext.sqlalchemy import SQLAlchemy
from flaskext.mail import Mail
import pyes

from annotator import auth, authz, annotation, store

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
    from . import model
    app.extensions['pyes'] = pyes.ES(app.config['ELASTICSEARCH_HOST'])

    # Mount controllers
    from annotateit import user, home

    if app.config['MOUNT_STORE']:
        app.register_blueprint(store.store, url_prefix=app.config['MOUNT_STORE'])
    if app.config['MOUNT_USER']:
        app.register_blueprint(user.user, url_prefix=app.config['MOUNT_USER'])
    if app.config['MOUNT_HOME']:
        app.register_blueprint(home.home, url_prefix=app.config['MOUNT_HOME'])

    @app.before_request
    def before_request():
        g.db = current_app.extensions['sqlalchemy'].db
        g.es = current_app.extensions['pyes']
        g.mail = current_app.extensions['mail']

        g.Annotation = annotation.make_model(g.es, index=current_app.config['ELASTICSEARCH_INDEX'])

        # User from session
        g.session_user = user.get_current_user()

        # User from X-Annotator headers for API
        username = request.headers.get(auth.HEADER_PREFIX + 'user-id')
        if username:
            g.user = model.User.query.filter_by(username=username).first()
        else:
            g.user = None

        # Consumer from X-Annotator headers for API
        consumerkey = request.headers.get(auth.HEADER_PREFIX + 'consumer-key')
        if consumerkey:
            g.consumer = model.Consumer.fetch(consumerkey)
        else:
            g.consumer = None

        g.auth = auth.Authenticator(model.Consumer.fetch)
        g.authorize = authz.authorize

    return app

def create_indices(app):
    Annotation = annotation.make_model(app.extensions['pyes'],
                                       index=app.config['ELASTICSEARCH_INDEX'])
    with app.test_request_context():
        Annotation.create_all()

def drop_indices(app):
    Annotation = annotation.make_model(app.extensions['pyes'],
                                       index=app.config['ELASTICSEARCH_INDEX'])
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
