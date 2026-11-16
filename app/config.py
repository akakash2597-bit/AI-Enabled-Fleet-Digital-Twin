import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fleet-digital-twin-secret-key-2026')
    DATABASE_PATH = BASE_DIR / 'database' / 'fleet_data.db'
    
    # ML Pipeline Model Paths
    SAVED_MODELS_DIR = BASE_DIR / 'ml_pipeline' / 'saved_models'
    MODEL_PATH = SAVED_MODELS_DIR / 'failure_prediction_model.pkl'
    SCALER_PATH = SAVED_MODELS_DIR / 'feature_scaler.pkl'
    
    # Dataset Configuration
    DATASET_PATH = BASE_DIR / 'ml_pipeline' / 'dataset' / 'sample_telemetry.csv'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
