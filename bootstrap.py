from __future__ import print_function

from getpass import getpass
import readline
import sys

import migrate.versioning.api as migrate

import annotateit
from annotateit import db
from annotateit.model import Consumer, User

if __name__ == '__main__':
    r = raw_input("This migration will perform initial setup of the annotation \n"
                  "store, and create the required admin accounts. Proceed? [Y/n] ")

    if r and r[0] in ['n', 'N']:
        sys.exit(1)

    print("\nCreating SQLite database and ElasticSearch indices... ", end="")

    app = annotateit.create_app()
    annotateit.create_indices(app)

    migrate_args = dict(url=app.config['SQLALCHEMY_DATABASE_URI'], debug='False', repository='migration')
    migrate.version_control(**migrate_args)
    migrate.upgrade(**migrate_args)

    print("done.\n")

    username = raw_input("Admin username [admin]: ").strip()
    if not username:
        username = 'admin'

    email = ''
    while not email:
        email = raw_input("Admin email: ").strip()

    password = ''
    while not password:
        password = getpass("Admin password: ")

    ckey = raw_input("Primary consumer key [annotateit]: ").strip()
    if not ckey:
        ckey = 'annotateit'

    with app.test_request_context():
        print("\nCreating admin user... ", end="")

        u = User(username, email, password)
        u.is_admin = True

        db.session.add(u)
        db.session.commit()

        print("done.")

        print("Creating primary consumer... ", end="")

        c = Consumer(ckey)
        c.user_id = u.id

        db.session.add(c)
        db.session.commit()

        print("done.\n")

        print("Primary consumer secret: %s" % c.secret)
