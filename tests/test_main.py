from . import TestCase, helpers as h

from annotateit.model import User, Annotation

from flask import url_for

class TestMain(TestCase):
    def setup(self):
        super(TestMain, self).setup()
        self.cli = self.app.test_client()

        self.user = User('test', 'test@example.com', 'password')
        h.db_save(self.user)

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
        h.assert_in(a['quote'][:50], res.data)

    def test_view_annotation_logged_out(self):
        a = Annotation(user='test',
                       consumer='annotateit',
                       uri='http://example.com',
                       text='This is the annotation text',
                       quote='This is what was annotated')
        a.save()

        res = self.cli.get(url_for('main.view_annotation', id=a.id))

        h.assert_equal(401, res.status_code)

