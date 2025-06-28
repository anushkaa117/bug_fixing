from flask import Flask, jsonify
from flask_login import LoginManager
from flask_mail import Mail
from flask_mongoengine import MongoEngine
import os
import mongoengine

# Import configuration based on environment
try:
    # Try Docker configuration first
    from config_docker import get_config, config
except ImportError:
    # Fall back to regular configuration
    from config import config
    get_config = lambda: config.get(os.environ.get('FLASK_ENV', 'development'), config['development'])

# Initialize extensions
db = MongoEngine()
login_manager = LoginManager()
mail = Mail()

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Use Docker configuration if available
    try:
        config_class = get_config()
        app.config.from_object(config_class)
    except:
        app.config.from_object(config[config_name])
    
    # Initialize MongoDB connection
    try:
        # Use MONGODB_SETTINGS for MongoEngine
        if 'MONGODB_SETTINGS' in app.config:
            mongoengine.connect(**app.config['MONGODB_SETTINGS'])
            print(f"✅ Connected to MongoDB via MONGODB_SETTINGS")
        else:
            # Fallback to old configuration
            mongoengine.connect(host=app.config.get('MONGODB_HOST', 'mongodb://localhost:27017/bugtracker'))
            print(f"✅ Connected to MongoDB via fallback")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        raise
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from models_mongo import User
        try:
            return User.objects(id=user_id).first()
        except:
            return None
    
    # Add template filter for newlines to <br> conversion
    @app.template_filter('nl2br')
    def nl2br_filter(text):
        """Convert newlines to HTML line breaks"""
        if text:
            return text.replace('\n', '<br>')
        return text
    
    # Health check endpoint for Docker
    @app.route('/health')
    def health_check():
        """Health check endpoint for Docker containers"""
        try:
            # Test MongoDB connection
            from pymongo import MongoClient
            from pymongo.server_api import ServerApi
            
            # Get MongoDB URI from config
            if 'MONGODB_SETTINGS' in app.config:
                uri = app.config['MONGODB_SETTINGS']['host']
                client = MongoClient(uri, server_api=ServerApi('1'), serverSelectionTimeoutMS=5000)
                client.admin.command('ping')
                client.close()
                
                return jsonify({
                    'status': 'healthy',
                    'database': 'connected',
                    'timestamp': str(mongoengine.datetime.datetime.utcnow())
                }), 200
            else:
                return jsonify({
                    'status': 'healthy',
                    'database': 'not_configured',
                    'timestamp': str(mongoengine.datetime.datetime.utcnow())
                }), 200
                
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': str(mongoengine.datetime.datetime.utcnow())
            }), 503
    
    # Register blueprints
    from routes import main
    app.register_blueprint(main)
    
    return app

app = create_app()

if __name__ == '__main__':
    # Run development server
    app.run(debug=True, host='0.0.0.0', port=5000)
