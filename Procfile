web: gunicorn 'annotateit:create_app()' -b 0.0.0.0:$PORT -w 2 -k gevent -t 10 --name annotateit --log-config logging.cfg
