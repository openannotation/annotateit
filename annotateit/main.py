from flask import Blueprint
from flask import current_app, g, request
from flask import abort, render_template, session

from annotator import auth, authz

from annotateit.model import Annotation, User, Consumer
from annotateit import user

main = Blueprint('main', __name__)

# This is not decorated here as it's the before_request handler for
# the entire application. See annotateit.create_app.
def before_request():
    # User from session
    g.session_user = _get_session_user()

    # User from X-Annotator headers for API
    username = request.headers.get(auth.HEADER_PREFIX + 'user-id')
    if username is not None:
        g.user = User.fetch(username)
    else:
        g.user = None

    # Consumer from X-Annotator headers for API
    consumerkey = request.headers.get(auth.HEADER_PREFIX + 'consumer-key')
    if consumerkey is not None:
        g.consumer = Consumer.fetch(consumerkey)
    else:
        g.consumer = None

    g.auth = auth.Authenticator(Consumer.fetch)
    g.authorize = authz.authorize

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/a/<id>')
def view_annotation(id):
    ann = Annotation.fetch(id)

    if ann is None:
        return abort(404)

    return render_template('annotation.html', annotation=ann)

def _get_session_user():
    username = session.get('user')
    if username is None:
        return None
    else:
        return User.fetch(username)
