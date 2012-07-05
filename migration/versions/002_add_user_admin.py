from sqlalchemy import *
from migrate import *

meta = MetaData()

def upgrade(migrate_engine):
    meta.bind = migrate_engine
    user = Table('user', meta, autoload=True)
    is_admin = Column('is_admin', Boolean, default=False)
    is_admin.create(user, populate_default=True)

def downgrade(migrate_engine):
    raise NotImplementedError("Due to sqlalchemy-migrate issue #143, this migration can't be undone.")
    # meta.bind = migrate_engine
    # user = Table('user', meta, autoload=True)
    # user.c.is_admin.drop()
