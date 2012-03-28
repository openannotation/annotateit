from . import TestCase, helpers as h

from annotateit.negotiate import Formatter, FormatterNotFound, Negotiator, negotiate

class MockResponse(object):
    def __init__(self, response, content_type=None, *args, **kwargs):
        self._response = response
        self._content_type = content_type

    @property
    def response(self):
        return self._response

    @property
    def content_type(self):
        return self._content_type

def make_mock_formatter(format, mimetypes=None):
    class MockFormatter(Formatter):
        def render(self, obj):
            return self.format

        def configure(self, *args, **kwargs):
            self.configured_with = (args, kwargs)

    MockFormatter.format = format
    MockFormatter.mimetypes = mimetypes if mimetypes is not None else ['application/'+format]

    return MockFormatter

class NegotiatorTestCase(TestCase):
    def setup(self):
        super(NegotiatorTestCase, self).setup()

        self.abort_patcher = h.patch('annotateit.negotiate.abort')
        self.abort = self.abort_patcher.start()

        self.request_patcher = h.patch('annotateit.negotiate.request')
        self.request = self.request_patcher.start()
        self.request.accept_mimetypes.best_match.return_value = 'text/html'

        self.response_patcher = h.patch('annotateit.negotiate.Response', MockResponse)
        self.Response = self.response_patcher.start()

        def my_view(format=None):
            return {'foo': 'bar'}
        self.view = my_view

    def teardown(self):
        self.abort_patcher.stop()
        self.request_patcher.stop()
        self.response_patcher.stop()

        super(NegotiatorTestCase, self).teardown()

    def set_request_mimetype(self, mimetype):
        self.request.accept_mimetypes.best_match.return_value = mimetype

class TestNegotiator(NegotiatorTestCase):
    def setup(self):
        super(TestNegotiator, self).setup()
        self.n = Negotiator(self.view)

    def test_get_formatter_errors(self):
        h.assert_raises(TypeError, self.n.get_formatter)

        with h.assert_raises(FormatterNotFound) as e:
            self.n.get_formatter(format='html')
        h.assert_true("Formatter for format 'html' not found!" in e.exception.message)

        with h.assert_raises(FormatterNotFound) as e:
            self.n.get_formatter(mimetype='text/html')
        h.assert_true("Formatter for mimetype 'text/html' not found!" in e.exception.message)

    def test_get_formatter_by_format(self):
        FooFormatter = make_mock_formatter('foo')
        self.n.register_formatter(FooFormatter)
        h.assert_is_instance(self.n.get_formatter(format='foo'), FooFormatter)

    def test_get_formatter_by_mimetype(self):
        FooFormatter = make_mock_formatter('foo', ['application/foo', 'application/bar'])
        self.n.register_formatter(FooFormatter)
        h.assert_is_instance(self.n.get_formatter(mimetype='application/foo'), FooFormatter)
        h.assert_is_instance(self.n.get_formatter(mimetype='application/bar'), FooFormatter)

    def test_get_formatter_precedence(self):
        FooFormatter = make_mock_formatter('foo', ['application/foo'])
        BarFormatter = make_mock_formatter('bar', ['application/foo'])
        BazFormatter = make_mock_formatter('foo', ['application/bar'])

        # When used as a decorator, the @negotiate function should list
        # available formats from most general to most specific, and when
        # evaluating which formatter to use, the negotiator will pick the
        # most specific formatter which matches the criteria.
        #
        #   e.g.
        #
        #   @negotiate(JSONFormatter)
        #   @negotiate(APIFormatterV1)
        #   @negotiate(APIFormatterV2)
        #   def my_view():
        #       ...
        #
        #  N.B. In the below, this calls proceed in *reverse* order to that
        #  seen when the decorator is used.

        self.n.register_formatter(FooFormatter) # specific
        self.n.register_formatter(BarFormatter) #   \/
        self.n.register_formatter(BazFormatter) # general

        h.assert_is_instance(self.n.get_formatter(mimetype='application/foo'), FooFormatter)
        h.assert_is_instance(self.n.get_formatter(format='foo'), FooFormatter)

    def test_get_formatter_args(self):
        FooFormatter = make_mock_formatter('foo')
        self.n.register_formatter(FooFormatter, 'a', foo='bar')
        formatter = self.n.get_formatter(format='foo')
        h.assert_equal(formatter.configured_with, (('a',), {'foo': 'bar'}))

    def test_accept_mimetypes(self):
        FooFormatter = make_mock_formatter('foo')
        BarFormatter = make_mock_formatter('bar')
        BazFormatter = make_mock_formatter('baz')
        self.n.register_formatter(FooFormatter)
        self.n.register_formatter(BarFormatter)
        self.n.register_formatter(BazFormatter)
        h.assert_equal(
            self.n.accept_mimetypes,
            # should be first-added first
            ['application/foo', 'application/bar', 'application/baz']
        )

    def test_negotiate_404(self):
        self.n()
        self.abort.assert_called_once_with(404, "Formatter for mimetype 'text/html' not found!")

    def test_negotiate_calls_formatter(self):
        self.n.get_formatter = h.Mock()
        formatter = self.n.get_formatter.return_value
        resp = self.n()
        formatter.assert_called_once_with(self.view())


class TestNegotiateDecorator(NegotiatorTestCase):

    def test_negotiate_adds_negotiator(self):
        HTMLFormatter = make_mock_formatter('html', ['text/html'])
        view = negotiate(HTMLFormatter)(self.view)

        h.assert_is_instance(view.negotiator, Negotiator)

    def test_negotiate_calls_negotiator(self):
        HTMLFormatter = make_mock_formatter('html', ['text/html'])
        view = negotiate(HTMLFormatter)(self.view)

        resp = view()
        h.assert_equal(resp.response, "html")

    def test_negotiate_chains_formatters(self):
        FooFormatter1 = make_mock_formatter('foo')
        FooFormatter2 = make_mock_formatter('foo')
        FooFormatter3 = make_mock_formatter('foo')

        view = negotiate(FooFormatter3)(self.view)
        view = negotiate(FooFormatter2)(view)
        view = negotiate(FooFormatter1)(view)

        h.assert_equal(len(view.negotiator._formatters_by_format['foo']), 3)


class TestFormatter(NegotiatorTestCase):

    def test_formatter_raises_with_empty_mimetypes(self):
        FooFormatter = make_mock_formatter('foo', [])
        h.assert_raises(NotImplementedError, FooFormatter)

    def test_formatter_render_raises(self):
        class MockFormatter(Formatter):
            format = 'json'
            mimetypes = ['application/json']

        mf = MockFormatter()
        h.assert_raises(NotImplementedError, mf.render, 'whatever')
