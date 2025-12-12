from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

db = SQLAlchemy()

def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__)
    
    # Load configuration
    from config import config
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Register blueprints
    from app.cbt.routes import cbt_bp
    from app.engagement.routes import engagement_bp
    from app.analytics.routes import analytics_bp
    from app.adaptation.routes import adaptation_bp
    
    app.register_blueprint(cbt_bp, url_prefix='/api/cbt')
    app.register_blueprint(engagement_bp, url_prefix='/api/engagement')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(adaptation_bp, url_prefix='/api/adaptation')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
