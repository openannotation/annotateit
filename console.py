from IPython import embed

from flask import request

import annotateit
from annotator import auth

app = annotateit.create_app()
ctx = app.test_request_context()
ctx.push()

from annotateit import model, db, es

token = auth.generate_token(model.Consumer.fetch('annotateit'), 'admin')

ctx.pop()

# Push new test context with auth headers attached
ctx = app.test_request_context(headers=auth.headers_for_token(token).items())
ctx.push()

embed(display_banner=False)
