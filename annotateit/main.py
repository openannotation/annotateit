from flask import Blueprint, Response
from flask import current_app, g, request, session
from flask import abort, flash, redirect, render_template, url_for
from flaskext.wtf import Form, fields as f, validators as v, html5
from flaskext.mail import Message
from negotiate.flask import negotiate

from annotator import auth, authz

from annotateit import mail
from annotateit.model import Annotation, User, Consumer
from annotateit.formats import HTMLFormatter, JSEmbedFormatter, HTMLEmbedFormatter, JSONFormatter

main = Blueprint('main', __name__)

class ContactForm(Form):
    name = f.TextField('Name', [])
    email = html5.EmailField('Email address', [v.Email(message="This should be a valid email address.")])
    message = f.TextAreaField('Message')

# This is not decorated here as it's the before_request handler for
# the entire application. See annotateit.create_app.
def before_request():
    g.debug = current_app.debug

    # User from session
    username = session.get('user')
    g.user = User.fetch(username)

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
    bookmarklet = render_template('bookmarklet.js', root=request.host_url.rstrip('/'))
    return render_template('index.html', bookmarklet=bookmarklet)

@main.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()

    if form.validate_on_submit():
        msg = Message(
            "AnnotateIt.org contact form",
            recipients=current_app.config['CONTACT_RECIPIENTS']
        )
        msg.body = render_template('contact_email.txt', **form.data)
        mail.send(msg)

        flash('Your message was sent successfully. Thanks!', 'success')
        return redirect(url_for('.index'))

    return render_template('contact.html', form=form)

@main.route('/annotations')
def annotations_index():
    annotations = Annotation.search(limit=20)
    return render_template('401.html'), 401

@main.route('/annotations/<regex("[^\.]+"):id>')
@main.route('/annotations/<regex("[^\.]+"):id>.<format>')
@negotiate(JSEmbedFormatter, template='annotation.embed.js')
@negotiate(HTMLEmbedFormatter, template='annotation.embed.html')
@negotiate(JSONFormatter, key='annotation')
@negotiate(HTMLFormatter, template='annotation.html')
def view_annotation(id, format=None):
    ann = Annotation.fetch(id)

    if ann is None:
        return abort(404)

    if g.authorize(ann, 'read', g.user):

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
        if g.user.is_admin:
            payload['admin'] = True
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
