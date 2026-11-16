from flask import Flask
from app.config import config
import os

def create_app(config_name=None):
    """Application factory for Flask application."""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Register blueprints (routes)
    from app.routes.views import views_bp
    from app.routes.api import api_bp
    from app.models.db import close_db

    app.register_blueprint(views_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    # Register teardown
    app.teardown_appcontext(close_db)

    return app
