"""
WSGI Application Entrypoint for Production Web Servers (Gunicorn / Waitress / uWSGI).
"""

import os
from app import create_app

env_name = os.environ.get('FLASK_CONFIG', 'production')
application = create_app(env_name)
app = application  # Alias for WSGI servers expecting 'app'

if __name__ == '__main__':
    # Fallback development launcher
    application.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
