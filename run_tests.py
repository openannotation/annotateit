from os import environ as env
import nose

if __name__ == '__main__':

    env['DEBUG'] = 'True'
    env['TESTING'] = 'True'
    env['CSRF_ENABLED'] = 'False'
    env['DATABASE_URL'] = 'sqlite:///:memory:'
    env['ELASTICSEARCH_INDEX'] = 'annotator_test'
    env['SECRET_KEY'] = 'test-random-secret-key'

    nose.run()


