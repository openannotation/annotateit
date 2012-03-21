from .. import TestCase, helpers as h

from annotateit import db
from annotateit.model import Consumer

class TestConsumer(TestCase):
    def setup(self):
        super(TestConsumer, self).setup()
        c = Consumer('foo')
        db.session.add(c)
        db.session.commit()

    def test_key(self):
        c = Consumer.fetch('foo')
        h.assert_equal(c.key, 'foo')

    def test_secret(self):
        c = Consumer.fetch('foo')
        assert c.secret, 'Consumer secret should be set!'

    def test_default_ttl(self):
        c = Consumer.fetch('foo')
        h.assert_equal(c.ttl, 86400)
