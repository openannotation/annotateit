from . import TestCase, helpers as h

from annotateit.formats import HTMLFormatter, JSONFormatter

class TestHTMLFormatter(TestCase):
    def setup(self):
        super(TestHTMLFormatter, self).setup()
        self.render_patcher = h.patch('annotateit.formats.render_template')
        self.render = self.render_patcher.start()

    def teardown(self):
        self.render_patcher.stop()
        super(TestHTMLFormatter, self).teardown()

    def test_raises_without_template(self):
        formatter = HTMLFormatter()
        h.assert_raises(TypeError, formatter.configure)

    def test_render(self):
        formatter = HTMLFormatter()
        formatter.configure(template='foo.html')
        formatter.render({'foo': 'bar', 'a': 1})
        self.render.assert_called_once_with('foo.html', foo='bar', a=1)

class TestJSONFormatter(TestCase):
    def setup(self):
        super(TestJSONFormatter, self).setup()
        self.request_patcher = h.patch('annotateit.formats.request')
        self.request = self.request_patcher.start()
        self.request.is_xhr = True

    def teardown(self):
        self.request_patcher.stop()
        super(TestJSONFormatter, self).teardown()

    def test_no_key(self):
        formatter = JSONFormatter()
        formatter.configure()

        h.assert_equal(formatter.render({'foo': 'bar'}), '{"foo": "bar"}')

    def test_string_key(self):
        formatter = JSONFormatter()
        formatter.configure(key='foo')
        h.assert_equal(formatter.render({'foo': {'bar': 'baz'}}), '{"bar": "baz"}')

    def test_callable_key(self):
        formatter = JSONFormatter()
        formatter.configure(key=lambda x: x['foo'][::-1])
        h.assert_equal(formatter.render({'foo': 'bar'}), '"rab"')
