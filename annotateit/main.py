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
    username = session.get('user')
    g.session_user = User.fetch(username) if username is not None else None

    # User from X-Annotator headers for API
    username = request.headers.get(auth.HEADER_PREFIX + 'user-id')
    g.user = User.fetch(username) if username is not None else None

    # Consumer from X-Annotator headers for API
    consumerkey = request.headers.get(auth.HEADER_PREFIX + 'consumer-key')
    g.consumer = Consumer.fetch(consumerkey) if consumerkey is not None else None

    g.auth = auth.Authenticator(Consumer.fetch)
    g.authorize = authz.authorize

def page_not_found(e):
    return render_template('404.html'), 404

def not_authorized(e):
    return render_template('401.html'), 401

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/a/<id>')
def view_annotation(id):
    ann = Annotation.fetch(id)

    if ann is None:
        return abort(404)

    if g.authorize(ann, 'read', g.session_user.username if g.session_user else None, 'annotateit'):

        if ann['consumer'] == 'annotateit':
            user = User.fetch(ann['user'])
        else:
            user = None

        return render_template('annotation.html', annotation=ann, user=user)

    abort(401)

def _get_session_user():
    username = session.get('user')
    if username is None:
        return None
    else:
        return User.fetch(username)
