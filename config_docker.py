"""
Docker Configuration for Flask Bug Tracker
Handles both local MongoDB (Docker) and MongoDB Atlas configurations
"""

import os
import urllib.parse
from datetime import timedelta

class Config:
    """Base configuration"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'development'
    DEBUG = os.environ.get('FLASK_DEBUG', '0') == '1'
    
    # MongoDB Configuration
    @staticmethod
    def get_mongodb_uri():
        """Build MongoDB URI based on environment variables"""
        
        # Check if we're using MongoDB Atlas (cloud)
        mongo_cluster = os.environ.get('MONGO_CLUSTER')
        if mongo_cluster:
            # MongoDB Atlas configuration
            username = os.environ.get('MONGO_USERNAME')
            password = os.environ.get('MONGO_PASSWORD')
            database = os.environ.get('MONGO_DATABASE', 'bugtracker')
            
            if not all([username, password, mongo_cluster]):
                raise ValueError("Missing MongoDB Atlas configuration")
            
            # URL encode the password
            encoded_password = urllib.parse.quote_plus(password)
            
            # Build Atlas connection string
            uri = f"mongodb+srv://{username}:{encoded_password}@{mongo_cluster}/{database}?retryWrites=true&w=majority&appName=Cluster0"
            return uri
        
        else:
            # Local MongoDB (Docker) configuration
            username = os.environ.get('MONGO_USERNAME', 'bugtracker')
            password = os.environ.get('MONGO_PASSWORD', 'bugtracker123')
            host = os.environ.get('MONGO_HOST', 'localhost')
            port = os.environ.get('MONGO_PORT', '27017')
            database = os.environ.get('MONGO_DATABASE', 'bugtracker')
            
            # Build local connection string
            uri = f"mongodb://{username}:{password}@{host}:{port}/{database}?authSource=admin"
            return uri
    
    # Get MongoDB URI
    MONGODB_SETTINGS = {
        'host': get_mongodb_uri.__func__()
    }
    
    # Admin User Configuration
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@bugtracker.local')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
    
    # Mail Configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', '1') == '1'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', '0') == '1'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@bugtracker.local')
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # WTF Configuration
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration"""
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'
    SESSION_COOKIE_SECURE = True
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Log to stderr in production
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    WTF_CSRF_ENABLED = False
    
    # Use in-memory database for testing
    MONGODB_SETTINGS = {
        'host': 'mongomock://localhost'
    }

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    config_name = os.environ.get('FLASK_ENV', 'development')
    return config.get(config_name, config['default'])
