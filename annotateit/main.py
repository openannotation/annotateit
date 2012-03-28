from flask import Blueprint, Response, url_for
from flask import g, request
from flask import abort, render_template, session

from annotator import auth, authz

from annotateit.model import Annotation, User, Consumer
from annotateit.negotiate import negotiate
from annotateit.formats import HTMLFormatter, HTMLEmbedFormatter, JSONFormatter

main = Blueprint('main', __name__)

# This is not decorated here as it's the before_request handler for
# the entire application. See annotateit.create_app.
def before_request():
    # User from session
    username = session.get('user')
    g.user = User.fetch(username) if username is not None else None

    g.auth = auth.Authenticator(Consumer.fetch)
    g.authorize = authz.authorize

    g.after_annotation_create = _add_annotation_link
    g.before_annotation_update = _add_annotation_link

def page_not_found(e):
    return render_template('404.html'), 404

def not_authorized(e):
    return render_template('401.html'), 401

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/annotations/<regex("[^\.]+"):id>')
@main.route('/annotations/<regex("[^\.]+"):id>.<format>')
@negotiate(JSONFormatter, key='annotation')
@negotiate(HTMLEmbedFormatter, template='annotation.embed.html')
@negotiate(HTMLFormatter, template='annotation.html')
def view_annotation(id, format=None):
    ann = Annotation.fetch(id)

    if ann is None:
        return abort(404)

    if g.authorize(ann, 'read', g.user.username if g.user else None, 'annotateit'):

        if ann['consumer'] == 'annotateit':
            user = User.fetch(ann['user'])
        else:
            user = None

        return {'annotation': ann, 'user': user}

    abort(401)

# AUTH TOKEN
@main.route('/api/token', methods=['GET', 'OPTIONS'])
def auth_token():
    ac = 'Access-Control-'
    headers = {}

    if 'origin' in request.headers:
        headers[ac + 'Allow-Origin']      = request.headers['origin']
        headers[ac + 'Allow-Credentials'] = 'true'
        headers[ac + 'Expose-Headers']    = 'Location, Content-Type, Content-Length'

        if request.method == 'OPTIONS':
            headers[ac + 'Allow-Headers'] = 'X-Requested-With, Content-Type, Content-Length'
            headers[ac + 'Allow-Methods'] = 'GET, OPTIONS'
            headers[ac + 'Max-Age']       = '86400'

    if g.user:
        c = Consumer.fetch('annotateit')
        payload = {'consumerKey': c.key, 'userId': g.user.username, 'ttl': c.ttl}
        token = auth.encode_token(payload, c.secret)
        return Response(token, headers=headers, mimetype='text/plain')
    else:
        return Response('Please go to {0} to log in!'.format(request.host_url), status=401, headers=headers, mimetype='text/plain')

def _get_session_user():
    username = session.get('user')
    if username is None:
        return None
    else:
        return User.fetch(username)

def _add_annotation_link(annotation):
    links = annotation['links'] = annotation.get('links', [])
    html_link = {
        'rel': 'alternate',
        'type': 'text/html',
        'href': url_for('main.view_annotation', id=annotation['id'], _external=True)
    }
    # We really can't do anything useful if links is already set and isn't a list
    if isinstance(links, list) and html_link not in links:
        links.append(html_link)
