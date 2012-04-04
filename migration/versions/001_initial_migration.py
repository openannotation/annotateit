from __future__ import print_function
from getpass import getpass
import readline
import sys

from sqlalchemy import *
from migrate import *
from migrate.changeset.constraint import ForeignKeyConstraint

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
    Column('user_id', Integer),
)

user = Table('user', meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('username', String),
    Column('email', String),
    Column('password_hash', String),
    Column('created_at', DateTime),
    Column('updated_at', DateTime),
)

consumer_user_id_fkey = ForeignKeyConstraint([consumer.c.user_id], [user.c.id])

def upgrade(migrate_engine):
    meta.bind = migrate_engine
    consumer.create()
    user.create()
    consumer_user_id_fkey.create()

def downgrade(migrate_engine):
    meta.bind = migrate_engine
    consumer_user_id_fkey.create()
    user.drop()
    consumer.drop()
