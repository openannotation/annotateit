from nose.tools import *
from mock import MagicMock, Mock, patch

if 'assert_in' not in globals():
    def assert_in(obj, collection, *args, **kwargs):
        assert_true(obj in collection, *args, **kwargs)

if 'assert_not_in' not in globals():
    def assert_not_in(obj, collection, *args, **kwargs):
        assert_true(obj not in collection, *args, **kwargs)

if 'assert_is_instance' not in globals():
    def assert_is_instance(obj, cls, *args, **kwargs):
        assert_true(isinstance(obj, cls), *args, **kwargs)

if 'assert_is_not_none' not in globals():
    def assert_is_not_none(obj, *args, **kwargs):
        assert_true(obj is not None, *args, **kwargs)
