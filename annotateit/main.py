import json

from flask import Blueprint, Response
from flask import current_app, g, request
from flask import abort, render_template, session

from annotator import auth, authz

from annotateit.model import Annotation, User, Consumer
from annotateit import user

main = Blueprint('main', __name__)

# We define our own jsonify rather than using flask.jsonify because we wish
# to jsonify arbitrary objects (e.g. index returns a list) rather than kwargs.
def jsonify(obj, *args, **kwargs):
    res = json.dumps(obj, indent=None if request.is_xhr else 2)
    return Response(res, mimetype='application/json', *args, **kwargs)

# This is not decorated here as it's the before_request handler for
# the entire application. See annotateit.create_app.
def before_request():
    # User from session
    username = session.get('user')
    g.user = User.fetch(username) if username is not None else None

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

    if g.authorize(ann, 'read', g.user.username if g.user else None, 'annotateit'):

        if ann['consumer'] == 'annotateit':
            user = User.fetch(ann['user'])
        else:
            user = None

        return render_template('annotation.html', annotation=ann, user=user)

    abort(401)

# AUTH TOKEN
@main.route('/api/token', methods=['GET', 'OPTIONS'])
def auth_token():
    ac = 'Access-Control-'
    headers = {}

    headers[ac + 'Allow-Origin']      = request.headers.get('origin', '*')
    headers[ac + 'Allow-Credentials'] = 'true'
    headers[ac + 'Expose-Headers']    = 'Location, Content-Type, Content-Length'

    if request.method == 'OPTIONS':
        headers[ac + 'Allow-Headers'] = 'X-Requested-With, Content-Type, Content-Length'
        headers[ac + 'Allow-Methods'] = 'GET, OPTIONS'
        headers[ac + 'Max-Age']       = '86400'

    if g.user:
        return jsonify(g.auth.generate_token('annotateit', g.user.username), headers=headers)
    else:
        return jsonify('Please go to {0} to log in!'.format(request.host_url), status=401, headers=headers)

def _get_session_user():
    username = session.get('user')
    if username is None:
        return None
    else:
        return User.fetch(username)
