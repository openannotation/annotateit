from IPython import embed

import annotateit
from annotateit import model, db, es

app = annotateit.create_app()

with app.test_request_context():
    from annotator import auth
    consumer = model.Consumer.fetch('annotateit')
    token = auth.generate_token(consumer, {'userId': 'admin'})
    headers = {'x-annotator-auth-token': token)

# Push new test context with auth headers attached
with app.test_request_context(headers=headers):
    embed(display_banner=False)
