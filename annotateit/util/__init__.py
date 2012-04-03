from decorator import decorator
from werkzeug.routing import BaseConverter
from flask import flash, redirect, url_for, g

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

@decorator
def require_user(func, *args, **kwargs):
    """
    Decorator: ensure the global user object exists, otherwise redirect to the
    login page before executing the content of the view handler.
    """
    if not g.user:
        flash('Please log in')
        return redirect(url_for('user.login'))
    else:
        return func(*args, **kwargs)
