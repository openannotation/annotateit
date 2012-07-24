from flask import g

from annotator.annotation import Annotation as Annotation_
from annotator.authz import permissions_filter

class Annotation(Annotation_):

    @classmethod
    def stats_for_user(cls, user):
        stats = {}

        q = {'query': {'match_all': {}},
             'filter': {'and': [permissions_filter(g.user),
                                {'or': [{'term': {'user': user.id}},
                                        {'term': {'user.id': user.id}}]}]}}

        res = cls.es.conn.count({'filtered': q}, cls.es.index, cls.__type__)
        stats['num_annotations'] = res['count']

        uris_res = cls.es.conn.search_raw({
            'query': {'filtered': q},
            'facets': {'uri': {'terms': {'field': 'uri'}}},
            'size': 0
        }, cls.es.index, cls.__type__)
        stats['num_uris'] = len(uris_res['facets']['uri']['terms'])

        return stats
