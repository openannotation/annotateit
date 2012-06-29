from os import environ as env

class ConfigError(Exception):
    pass

def configure(app):
    c = app.config

    c['DEBUG']        = _switch('DEBUG', False)
    c['TESTING']      = _switch('TESTING', False)
    c['CSRF_ENABLED'] = _switch('CSRF_ENABLED', True)
    c['AUTH_ON']      = _switch('AUTH_ON', True)
    c['AUTHZ_ON']     = _switch('AUTHZ_ON', True)

    # Required settings
    c['SECRET_KEY']            = _required('SECRET_KEY')
    c['RECAPTCHA_PUBLIC_KEY']  = _required('RECAPTCHA_PUBLIC_KEY')
    c['RECAPTCHA_PRIVATE_KEY'] = _required('RECAPTCHA_PRIVATE_KEY')

    # Optional settings
    c.setdefault('SQLALCHEMY_DATABASE_URI', env.get('DATABASE_URL',
                                                    'sqlite:///%s/annotateit.db' % app.instance_path))
    c.setdefault('DEFAULT_MAIL_SENDER', env.get('DEFAULT_MAIL_SENDER',
                                                'AnnotateIt <no-reply@annotateit.org>'))

    # ElasticSearch config
    c.setdefault('ELASTICSEARCH_HOST', env.get('ELASTICSEARCH_HOST', '127.0.0.1:9200'))
    c.setdefault('ELASTICSEARCH_INDEX', env.get('ELASTICSEARCH_INDEX', 'annotateit'))

    # Bonsai (on Heroku)
    bonsai_url = env.get('BONSAI_INDEX_URL')
    if bonsai_url:
        url = urlparse.urlparse(bonsai_url)
        c['ELASTICSEARCH_HOST']  = url.netloc
        c['ELASTICSEARCH_INDEX'] = url.path[1:]

def _required(key):
    val = env.get(key)
    if val is None:
        raise ConfigError("You must set the %s environment variable! "
                          "See annotateit/config.py for details."
                          % key)
    return val

def _switch(key, default=False):
    if key in env:
        return env[key].lower() != 'false'
    else:
        return default
