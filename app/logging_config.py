"""
Production logging configuration for Fleet Digital Twin.
Configures rotating file logs and console output.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logger(app):
    """Configures structured application logging."""
    base_dir = Path(__file__).resolve().parent.parent
    logs_dir = base_dir / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = logs_dir / 'fleet_twin.log'
    
    # Formatter for log messages
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s [%(pathname)s:%(lineno)d]: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Rotating File Handler (10MB max, keep up to 5 backups)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Console Stream Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)
    
    # Add handlers to Flask app logger
    app.logger.setLevel(logging.DEBUG if app.debug else logging.INFO)
    if not app.logger.handlers:
        app.logger.addHandler(file_handler)
        app.logger.addHandler(console_handler)
        
    app.logger.info("Fleet Digital Twin application logging initialized.")
