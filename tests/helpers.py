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

class MockConsumer(object):
    def __init__(self, key='mockconsumer'):
        self.key = key
        self.secret = 'top-secret'
        self.ttl = 86400

class MockUser(object):
    def __init__(self, id='alice', consumer=None):
        self.id = id
        self.consumer = MockConsumer(consumer if consumer is not None else 'mockconsumer')
        self.is_admin = False
