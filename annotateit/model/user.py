from hashlib import md5
from datetime import datetime
from werkzeug import generate_password_hash, check_password_hash

from annotateit import db
from annotateit.model import Consumer
from annotateit.model.timestamps import Timestamps

__all__ = ['User']

class User(db.Model, Timestamps):
    _id = db.Column('id', db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True)
    email = db.Column(db.String(128), unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)

    # NB: there is a *big* difference between `consumer` and `consumers`
    #
    # `consumer`  - the consumer to which this user belongs (namely AnnotateIt), used by
    #               auth/authz etc.
    #
    # `consumers` - the list of consumers created for this user
    #
    consumers = db.relationship('Consumer', backref='user', lazy='dynamic')

    @classmethod
    def fetch(cls, username):
        return cls.query.filter_by(username=username).first()

    def __init__(self, username, email, password=None):
        self.username = username
        self.email = email
        if password:
            self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

    def _password_set(self, v):
        self.password_hash = generate_password_hash(v)

    password = property(None, _password_set)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    # Alias username to id for the purposes of authentication
    @property
    def id(self):
        return self.username

    @property
    def consumer(self):
        if not hasattr(self, '_consumer'):
            self._consumer = Consumer.fetch('annotateit')
        return self._consumer

    @property
    def gravatar_url(self):
        hsh = md5(self.email.strip().lower().encode('utf-8')).hexdigest()
        url = 'http://www.gravatar.com/avatar/{hash}?d=mm'.format(hash=hsh)
        return url
