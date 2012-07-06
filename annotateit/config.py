from os import environ as env
import urlparse

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
    c['SECRET_KEY']            = env.get('SECRET_KEY')
    c['RECAPTCHA_PUBLIC_KEY']  = env.get('RECAPTCHA_PUBLIC_KEY')
    c['RECAPTCHA_PRIVATE_KEY'] = env.get('RECAPTCHA_PRIVATE_KEY')

    # Optional settings
    c.setdefault('SQLALCHEMY_DATABASE_URI', env.get('DATABASE_URL',
                                                    'sqlite:///%s/annotateit.db' % app.instance_path))
    c.setdefault('DEFAULT_MAIL_SENDER', env.get('DEFAULT_MAIL_SENDER',
                                                'AnnotateIt <no-reply@annotateit.org>'))

    # ElasticSearch config
    c.setdefault('ELASTICSEARCH_HOST', env.get('ELASTICSEARCH_HOST', 'http://127.0.0.1:9200'))
    c.setdefault('ELASTICSEARCH_INDEX', env.get('ELASTICSEARCH_INDEX', 'annotateit'))

    # Bonsai (on Heroku)
    bonsai_url = env.get('BONSAI_INDEX_URL')
    if bonsai_url:
        url = urlparse.urlparse(bonsai_url)
        c['ELASTICSEARCH_HOST']  = '%s://%s' % (url.scheme, url.netloc)
        c['ELASTICSEARCH_INDEX'] = url.path[1:]

    # Postgres (on Heroku)
    postgres_url = env.get('HEROKU_POSTGRESQL_CYAN_URL')
    if postgres_url:
        c['SQLALCHEMY_DATABASE_URI'] = postgres_url

    # Load from file if available
    c.from_envvar('ANNOTATEIT_CONFIG', silent=True)

    # Throw errors
    _require(c, 'SECRET_KEY')
    _require(c, 'RECAPTCHA_PUBLIC_KEY')
    _require(c, 'RECAPTCHA_PRIVATE_KEY')

def _require(config, key):
    if config.get(key) is None:
        raise ConfigError("You must set the %s environment variable! "
                          "See annotateit/config.py for details."
                          % key)

def _switch(key, default=False):
    if key in env:
        return env[key].lower() != 'false'
    else:
        return default
