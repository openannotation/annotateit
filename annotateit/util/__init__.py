from functools import update_wrapper

from werkzeug.routing import BaseConverter
from flask import current_app, flash, redirect, url_for, g

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

def require_user(func):
    """
    Decorator: ensure the global user object exists, otherwise redirect to the
    login page before executing the content of the view handler.
    """
    def requiring_user_first(*args, **kwargs):
        if not g.user:
            flash('Please log in')
            return redirect(url_for('user.login'))
        else:
            return func(*args, **kwargs)
    return update_wrapper(requiring_user_first, func)
