import json

from flask import url_for
import jwt

from . import TestCase, helpers as h

from annotateit.model import User, Consumer, Annotation

from annotateit import db

class TestMain(TestCase):
    def setup(self):
        super(TestMain, self).setup()
        self.cli = self.app.test_client()

        self.user = User('test', 'test@example.com', 'password')
        self.consumer = Consumer('annotateit')
        self.consumer.secret = 'secret'

        db.session.add(self.user)
        db.session.add(self.consumer)
        db.session.commit()

    def login(self):
        with self.cli.session_transaction() as sess:
            sess['user'] = 'test'

    def logout(self):
        with self.cli.session_transaction() as sess:
            del sess['user']

    def test_home_nav_logged_out(self):
        res = self.cli.get(url_for('main.index'))
        h.assert_in("Sign up", res.data)
        h.assert_in("Log in", res.data)
        h.assert_not_in("My account", res.data)
        h.assert_not_in("Log out", res.data)

    def test_home_nav_logged_in(self):
        self.login()
        res = self.cli.get(url_for('main.index'))
        h.assert_not_in("Sign up", res.data)
        h.assert_not_in("Log in", res.data)
        h.assert_in("My account", res.data)
        h.assert_in("Log out", res.data)

    def test_view_annotation(self):
        a = Annotation(user='test',
                       consumer='annotateit',
                       uri='http://example.com',
                       text='This is the annotation text',
                       quote='This is what was annotated')
        a.save()

        self.login()
        res = self.cli.get(url_for('main.view_annotation', id=a.id))

        h.assert_in(a['user'], res.data)
        h.assert_in(a['uri'], res.data)
        h.assert_in(a['text'], res.data)
        h.assert_in(a['quote'][:25], res.data)

    def test_view_annotation_logged_out(self):
        a = Annotation(user='test',
                       consumer='annotateit',
                       uri='http://example.com',
                       text='This is the annotation text',
                       quote='This is what was annotated',
                       permissions={'read': []})
        a.save()

        res = self.cli.get(url_for('main.view_annotation', id=a.id))

        h.assert_equal(401, res.status_code)

    def test_api_token_logged_out(self):
        res = self.cli.get(url_for('main.auth_token'))
        h.assert_equal(401, res.status_code)

    def test_api_token_logged_in(self):
        self.login()
        res = self.cli.get(url_for('main.auth_token'))
        token = jwt.decode(res.data, 'secret')

        h.assert_equal(token['consumerKey'], 'annotateit')
        h.assert_equal(token['userId'], 'test')
        h.assert_equal(token['ttl'], 86400)
        h.assert_true('issuedAt' in token)

    def test_api_token_admin(self):
        self.user.is_admin = True
        db.session.commit()

        self.login()
        res = self.cli.get(url_for('main.auth_token'))
        token = jwt.decode(res.data, 'secret')

        h.assert_equal(token['admin'], True)

    def test_cors_preflight(self):
        response = self.cli.open('/api/token', method="OPTIONS", headers={'Origin': 'foo'})
        headers = dict(response.headers)

        h.assert_equal(headers['Access-Control-Allow-Methods'], 'GET, OPTIONS')
        h.assert_equal(headers['Access-Control-Allow-Origin'], 'foo')
        h.assert_equal(headers['Access-Control-Expose-Headers'], 'Location, Content-Type, Content-Length')

