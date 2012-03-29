from setuptools import setup, find_packages

setup(
    name = 'annotateit',
    version = '2.1.2',
    packages = find_packages(),

    install_requires = [
        'annotator==0.7.6',
        'Flask==0.8',
        'Flask-Mail==0.6.1',
        'Flask-SQLAlchemy==0.15',
        'Flask-WTF==0.5.4',
        'SQLAlchemy==0.7.5',
        'itsdangerous==0.12',
        'decorator==3.3.2',
        'iso8601==0.1.4'
    ],

    test_requires = [
        'nose==1.1.2',
        'mock==0.8.0'
    ]
)
