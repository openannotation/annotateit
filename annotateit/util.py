from functools import update_wrapper

from flask import flash, redirect, url_for, g

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
