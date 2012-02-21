DEBUG = False

SQLALCHEMY_DATABASE_URI = 'sqlite:///%s/annotateit.db'

ELASTICSEARCH_HOST = '127.0.0.1:9200'
ELASTICSEARCH_INDEX = 'annotateit'

DEFAULT_MAIL_SENDER = ('AnnotateIt', 'no-reply@annotateit.org')

AUTH_ON = True
AUTHZ_ON = True
