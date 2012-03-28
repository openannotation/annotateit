from collections import defaultdict
from decorator import decorator
from inspect import getcallargs

from flask import abort, request, Response

class FormatterNotFound(Exception):
    pass

class Formatter(object):
    format = None
    mimetypes = []

    def __init__(self, request_mimetype=None):
        if request_mimetype is None or request_mimetype not in self.mimetypes:
            try:
                self.response_mimetype = self.mimetypes[0]
            except IndexError:
                raise NotImplementedError("%s.mimetypes should be a non-empty list" % self.__class__.__name__)
        else:
            self.response_mimetype = request_mimetype

    def configure(self):
        pass

    def render(self, obj):
        raise NotImplementedError("render() should be implemented by Formatter subclasses")

    def __call__(self, obj):
        return Response(self.render(obj), content_type=self.response_mimetype)

class Negotiator(object):

    def __init__(self, func):
        self.func = func
        self._formatters = []
        self._formatters_by_format = defaultdict(list)
        self._formatters_by_mimetype = defaultdict(list)

    def __call__(self, *args, **kwargs):
        result = self.func(*args, **kwargs)
        format = getcallargs(self.func, *args, **kwargs).get('format')
        mimetype = request.accept_mimetypes.best_match(self.accept_mimetypes, 'text/html')

        try:
            formatter = self.get_formatter(format, mimetype)
        except FormatterNotFound as e:
            return abort(404, e.message)

        return formatter(result)

    def register_formatter(self, formatter, *args, **kwargs):
        self._formatters.append(formatter)
        self._formatters_by_format[formatter.format].append((formatter, args, kwargs))
        for mimetype in formatter.mimetypes:
            self._formatters_by_mimetype[mimetype].append((formatter, args, kwargs))

    def get_formatter(self, format=None, mimetype=None):
        if format is None and mimetype is None:
            raise TypeError("get_formatter expects one of the 'format' or 'mimetype' kwargs to be set")

        if format is not None:
            try:
                # the first added will be the most specific
                formatter_cls, args, kwargs = self._formatters_by_format[format][0]
            except IndexError:
                raise FormatterNotFound("Formatter for format '%s' not found!" % format)
        elif mimetype is not None:
            try:
                # the first added will be the most specific
                formatter_cls, args, kwargs = self._formatters_by_mimetype[mimetype][0]
            except IndexError:
                raise FormatterNotFound("Formatter for mimetype '%s' not found!" % mimetype)

        formatter = formatter_cls(request_mimetype=mimetype)
        formatter.configure(*args, **kwargs)
        return formatter

    @property
    def accept_mimetypes(self):
        return [m for f in self._formatters for m in f.mimetypes]

def negotiate(formatter_cls, *args, **kwargs):
    def _negotiate(f, *args, **kwargs):
        return f.negotiator(*args, **kwargs)

    def decorate(f):
        if not hasattr(f, 'negotiator'):
            f.negotiator = Negotiator(f)

        f.negotiator.register_formatter(formatter_cls, *args, **kwargs)
        return decorator(_negotiate, f)

    return decorate
