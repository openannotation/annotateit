from sqlalchemy import *
from migrate import *

import annotateit
from annotateit import db
from annotateit.model import Consumer, User

meta = MetaData()

consumer = Table('consumer', meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('key', String),
    Column('secret', String),
    Column('ttl', Integer),
    Column('created_at', DateTime),
    Column('updated_at', DateTime),
    Column('user_id', Integer, ForeignKey('user.id')),
)

user = Table('user', meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('username', String),
    Column('email', String),
    Column('password_hash', String),
    Column('created_at', DateTime),
    Column('updated_at', DateTime),
)

def upgrade(migrate_engine):
    meta.bind = migrate_engine
    user.create()
    consumer.create()

def downgrade(migrate_engine):
    meta.bind = migrate_engine
    consumer.drop()
    user.drop()
