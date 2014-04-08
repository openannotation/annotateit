from .. import TestCase, helpers as h

from flask import g
from annotateit.model import Annotation

class TestAnnotation(TestCase):

    def test_stats_for_user(self):
        g.user = h.MockUser('alice', 'fooconsumer')
        Annotation({'user': 'alice', 'consumer': 'fooconsumer', 'uri': 'a'}).save()
        Annotation({'user': 'alice', 'consumer': 'fooconsumer', 'uri': 'a'}).save()
        Annotation({'user': 'alice', 'consumer': 'fooconsumer', 'uri': 'b'}).save()
        Annotation({'user': 'bob', 'consumer': 'fooconsumer', 'uri': 'b'}).save()

        Annotation.es.conn.cluster.health(wait_for_status='yellow')

        stats = Annotation.stats_for_user(g.user)
        h.assert_equal(stats['num_annotations'], 3)
        h.assert_equal(stats['num_uris'], 2)
