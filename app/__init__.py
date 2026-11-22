"""
Flask Application Factory for AI-Enabled Fleet Digital Twin.
Registers blueprints, error handlers, database teardowns, and production logging.
"""

import os
from flask import Flask, render_template, request, jsonify
from app.config import config
from app.logging_config import setup_logger

def create_app(config_name=None):
    """Application factory for Flask application."""
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize structured logging
    setup_logger(app)

    # Register blueprints (routes)
    from app.routes.views import views_bp
    from app.routes.api import api_bp
    from app.models.db import close_db

    app.register_blueprint(views_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    # Register database connection teardown
    app.teardown_appcontext(close_db)

    # Request logger
    @app.after_request
    def log_request(response):
        if not request.path.startswith('/static'):
            app.logger.info(
                f"{request.remote_addr} - {request.method} {request.path} -> {response.status_code}"
            )
        return response

    # -------------------------------------------------------------
    # Error Handlers (Dual JSON/HTML Support)
    # -------------------------------------------------------------
    @app.errorhandler(400)
    def bad_request_error(error):
        if request.path.startswith('/api/'):
            return jsonify({
                "status": "error",
                "code": 400,
                "message": getattr(error, 'description', 'Bad Request: Invalid parameters provided.')
            }), 400
        return render_template('errors/400.html'), 400

    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith('/api/'):
            return jsonify({
                "status": "error",
                "code": 404,
                "message": getattr(error, 'description', 'Resource not found in fleet database.')
            }), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal server error: {error}", exc_info=True)
        if request.path.startswith('/api/'):
            return jsonify({
                "status": "error",
                "code": 500,
                "message": "Internal server error in predictive telemetry engine."
            }), 500
        return render_template('errors/500.html'), 500

    return app
