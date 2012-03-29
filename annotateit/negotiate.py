from collections import defaultdict
from decorator import decorator

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
            return abort(404, str(e))

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

###

try:
    from inspect import getcallargs # Python 2.7
except ImportError:

    from inspect import ismethod, getargspec

    def getcallargs(func, *positional, **named):
        """Get the mapping of arguments to values.

        A dict is returned, with keys the function argument names (including the
        names of the * and ** arguments, if any), and values the respective bound
        values from 'positional' and 'named'."""
        args, varargs, varkw, defaults = getargspec(func)
        f_name = func.__name__
        arg2value = {}

        # The following closures are basically because of tuple parameter unpacking.
        assigned_tuple_params = []
        def assign(arg, value):
            if isinstance(arg, str):
                arg2value[arg] = value
            else:
                assigned_tuple_params.append(arg)
                value = iter(value)
                for i, subarg in enumerate(arg):
                    try:
                        subvalue = next(value)
                    except StopIteration:
                        raise ValueError('need more than %d %s to unpack' %
                                         (i, 'values' if i > 1 else 'value'))
                    assign(subarg,subvalue)
                try:
                    next(value)
                except StopIteration:
                    pass
                else:
                    raise ValueError('too many values to unpack')
        def is_assigned(arg):
            if isinstance(arg,str):
                return arg in arg2value
            return arg in assigned_tuple_params
        if ismethod(func) and func.im_self is not None:
            # implicit 'self' (or 'cls' for classmethods) argument
            positional = (func.im_self,) + positional
        num_pos = len(positional)
        num_total = num_pos + len(named)
        num_args = len(args)
        num_defaults = len(defaults) if defaults else 0
        for arg, value in zip(args, positional):
            assign(arg, value)
        if varargs:
            if num_pos > num_args:
                assign(varargs, positional[-(num_pos-num_args):])
            else:
                assign(varargs, ())
        elif 0 < num_args < num_pos:
            raise TypeError('%s() takes %s %d %s (%d given)' % (
                f_name, 'at most' if defaults else 'exactly', num_args,
                'arguments' if num_args > 1 else 'argument', num_total))
        elif num_args == 0 and num_total:
            if varkw:
                if num_pos:
                    # XXX: We should use num_pos, but Python also uses num_total:
                    raise TypeError('%s() takes exactly 0 arguments '
                                    '(%d given)' % (f_name, num_total))
            else:
                raise TypeError('%s() takes no arguments (%d given)' %
                                (f_name, num_total))
        for arg in args:
            if isinstance(arg, str) and arg in named:
                if is_assigned(arg):
                    raise TypeError("%s() got multiple values for keyword "
                                    "argument '%s'" % (f_name, arg))
                else:
                    assign(arg, named.pop(arg))
        if defaults:    # fill in any missing values with the defaults
            for arg, value in zip(args[-num_defaults:], defaults):
                if not is_assigned(arg):
                    assign(arg, value)
        if varkw:
            assign(varkw, named)
        elif named:
            unexpected = next(iter(named))
            if isinstance(unexpected, unicode):
                unexpected = unexpected.encode(sys.getdefaultencoding(), 'replace')
            raise TypeError("%s() got an unexpected keyword argument '%s'" %
                            (f_name, unexpected))
        unassigned = num_args - len([arg for arg in args if is_assigned(arg)])
        if unassigned:
            num_required = num_args - num_defaults
            raise TypeError('%s() takes %s %d %s (%d given)' % (
                f_name, 'at least' if defaults else 'exactly', num_required,
                'arguments' if num_required > 1 else 'argument', num_total))
        return arg2value
