import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify, request
from flask_cors import CORS
from mongoengine import connect, disconnect
from flask_jwt_extended import JWTManager
from flask_caching import Cache
import redis
from dotenv import load_dotenv
import urllib.parse

# Load environment variables
load_dotenv()

app = Flask(__name__)

# CORS configuration for React frontend
CORS(app, origins=['http://localhost:3000', 'https://*.vercel.app'])

# JWT configuration
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
jwt = JWTManager(app)

# MongoDB configuration
username = os.getenv('MONGO_USERNAME')
password = os.getenv('MONGO_PASSWORD')
cluster = os.getenv('MONGO_CLUSTER')
database = os.getenv('MONGO_DATABASE', 'bugtracker')

if username and password and cluster:
    encoded_password = urllib.parse.quote_plus(password)
    mongodb_uri = f"mongodb+srv://{username}:{encoded_password}@{cluster}/{database}?retryWrites=true&w=majority&appName=Cluster0"
else:
    mongodb_uri = 'mongodb://localhost:27017/bugtracker'

# Connect to MongoDB using native MongoEngine
connect(db=database, host=mongodb_uri)

# Redis configuration
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    db=0,
    decode_responses=True
)

# Flask-Caching configuration
cache_config = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}/0",
    'CACHE_DEFAULT_TIMEOUT': 300,  # 5 minutes
    'CACHE_KEY_PREFIX': 'bugtracker_'
}

cache = Cache(app, config=cache_config)

# Import models
from models_mongo import User, Bug, BugComment

# Import and register API blueprints
from routes.auth_routes import auth_bp
from routes.bug_routes import bug_bp
from routes.user_routes import user_bp

app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(bug_bp, url_prefix='/api/bugs')
app.register_blueprint(user_bp, url_prefix='/api/users')

# Initialize cache
@app.before_first_request
def initialize_cache():
    """Initialize cache on first request"""
    try:
        cache.init_app(app, config=cache_config)
    except Exception as e:
        print(f"Cache initialization failed: {e}")

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        User.objects.count()
        return jsonify({
            'status': 'healthy',
            'message': 'Bug Tracker API is running',
            'database': 'connected'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'message': 'Database connection failed',
            'error': str(e)
        }), 500

@app.route('/api')
def api_root():
    """API root endpoint"""
    return jsonify({
        'message': 'Bug Tracker API',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/auth',
            'bugs': '/api/bugs',
            'users': '/api/users',
            'health': '/api/health'
        }
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
