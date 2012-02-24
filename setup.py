from setuptools import setup, find_packages

setup(
    name = 'annotateit',
    version = '2.0.0',
    packages = find_packages(),

    install_requires = [
        'annotator==0.6.1',
        'Flask==0.8',
        'Flask-Mail==0.6.1',
        'Flask-SQLAlchemy==0.15',
        'Flask-WTF==0.5.2',
        'SQLAlchemy==0.7.4',
        'nose==1.0.0',
        'mock==0.7.2',
        'itsdangerous==0.11'
    ]
)
