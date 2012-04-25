from IPython import embed

import annotateit
from annotateit import model, db, es
from flask import g

def main():
    app = annotateit.create_app()

    with app.test_request_context():
        g.user = model.User.fetch('admin')
        embed(display_banner=False)

if __name__ == '__main__':
    main()

