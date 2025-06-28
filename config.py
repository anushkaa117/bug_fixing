import os
from datetime import timedelta

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # MongoDB settings
    MONGODB_HOST = os.environ.get('DATABASE_URL') or 'mongodb://localhost:27017/bugtracker'
    MONGODB_CONNECT = False  # Disable automatic connection
    
    # Mail settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER') 
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Application settings
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') 
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') 
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') 
    
    # Security settings
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Pagination
    BUGS_PER_PAGE = 10
    
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    MONGODB_HOST = os.environ.get('DATABASE_URL') or 'mongodb://localhost:27017/bugtracker_dev'
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    
    # Use environment variables for production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for production environment")
    
    # Production database URL is required
    MONGODB_HOST = os.environ.get('DATABASE_URL')
    if not MONGODB_HOST:
        raise ValueError("No DATABASE_URL set for production environment")
    
    # Security settings for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    MONGODB_HOST = 'mongodb://localhost:27017/bugtracker_test'
    WTF_CSRF_ENABLED = False
    
# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
