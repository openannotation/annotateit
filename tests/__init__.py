import pyes

import annotateit

def setup():
    app = annotateit.create_app()
    try:
        annotateit.drop_all(app)
    except pyes.exceptions.ElasticSearchException:
        pass


class TestCase(object):
    def setup(self):
        self.app = annotateit.create_app()
        annotateit.create_all(self.app)
        self.ctx = self.app.test_request_context()
        self.ctx.push()

    def teardown(self):
        self.ctx.pop()
        annotateit.drop_all(self.app)
