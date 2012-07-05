import os
import annotateit

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    app = annotateit.create_app()
    app.run(port=port, host=host)
