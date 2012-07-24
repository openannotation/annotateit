from os import environ as env
import nose

if __name__ == '__main__':

    env.update({
        'DEBUG': 'True',
        'TESTING': 'True',
        'CSRF_ENABLED': 'False',
        'DATABASE_URL': 'sqlite:///:memory:',
        'ELASTICSEARCH_INDEX': 'annotator_test',
        'SECRET_KEY': 'test-random-secret-key',
        'RECAPTCHA_PUBLIC_KEY': 'test-recaptcha-public-key',
        'RECAPTCHA_PRIVATE_KEY': 'test-recaptcha-private-key'
    })

    nose.main()
