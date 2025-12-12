import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///tutoring_system.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    JSON_SORT_KEYS = False
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Engagement thresholds
    ENGAGEMENT_THRESHOLDS = {
        'response_time_slow': 30,      # seconds
        'response_time_fast': 5,       # seconds
        'inactivity_threshold': 60,    # seconds
        'low_engagement_score': 0.3,
        'high_engagement_score': 0.7
    }
    
    # Adaptation parameters
    ADAPTATION_CONFIG = {
        'min_difficulty': 0.1,
        'max_difficulty': 0.9,
        'difficulty_step': 0.1,
        'max_retries': 3,
        'hint_threshold': 0.5
    }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
