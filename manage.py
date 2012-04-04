#!/usr/bin/env python
from migrate.versioning.shell import main

if __name__ == '__main__':
    import annotateit
    app = annotateit.create_app()
    main(url=app.config['SQLALCHEMY_DATABASE_URI'], debug='False', repository='migration')
