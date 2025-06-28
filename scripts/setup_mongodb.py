#!/usr/bin/env python3
"""
Complete MongoDB Setup Script for Bug Tracker
- Tests connection
- Fixes URL encoding issues
- Creates database structure
- Initializes with sample data
- All-in-one solution
"""

import os
import sys
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv
import mongoengine
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from werkzeug.security import generate_password_hash

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_environment():
    """Load and validate environment variables"""
    load_dotenv()
    
    username = os.getenv('MONGO_USERNAME')
    password = os.getenv('MONGO_PASSWORD')
    cluster = os.getenv('MONGO_CLUSTER')
    database = os.getenv('MONGO_DATABASE', 'bugtracker')
    
    if not all([username, password, cluster]):
        print("ERROR: Missing MongoDB configuration in .env file")
        print("Required: MONGO_USERNAME, MONGO_PASSWORD, MONGO_CLUSTER")
        return None
    
    # URL encode the password to handle special characters
    encoded_password = urllib.parse.quote_plus(password)
    
    # Build connection string with database name
    uri = f"mongodb+srv://{username}:{encoded_password}@{cluster}/{database}?retryWrites=true&w=majority&appName=Cluster0"
    return uri

def build_mongodb_uri():
    """Build MongoDB URI from environment variables"""
    print("Building MongoDB connection string...")
    
    username = os.getenv('MONGO_USERNAME')
    password = os.getenv('MONGO_PASSWORD')
    cluster = os.getenv('MONGO_CLUSTER')
    
    print(f"Username: {username}")
    print(f"Cluster: {cluster}")
    print(f"Password: {'*' * len(password) if password else 'Not set'}")
    
    # URL encode the password to handle special characters
    encoded_password = urllib.parse.quote_plus(password)
    
    uri = f"mongodb+srv://{username}:{encoded_password}@{cluster}/?retryWrites=true&w=majority&appName=Cluster0"
    return uri

def test_connection(uri):
    """Test MongoDB connection using ServerApi"""
    print("Testing MongoDB connection...")
    
    try:
        # Create a new client and connect to the server
        client = MongoClient(uri, server_api=ServerApi('1'))
        
        # Send a ping to confirm a successful connection
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        
        # Get database info
        db_name = client.get_default_database().name
        server_info = client.server_info()
        
        print(f"Database: {db_name}")
        print(f"MongoDB Version: {server_info.get('version', 'Unknown')}")
        
        # List existing collections
        collections = client.get_default_database().list_collection_names()
        if collections:
            print(f"Existing Collections: {', '.join(collections)}")
        else:
            print("No existing collections (fresh database)")
        
        client.close()
        return True
        
    except ConnectionFailure as e:
        print(f"Connection Failed: {e}")
        return False
    except ServerSelectionTimeoutError as e:
        print(f"Server Selection Timeout: {e}")
        return False
    except Exception as e:
        print(f"Connection Error: {e}")
        return False

def setup_mongoengine(url):
    """Setup MongoEngine connection"""
    try:
        mongoengine.connect(host=url)
        print("MongoEngine connected successfully")
        return True
    except Exception as e:
        print(f"MongoEngine connection failed: {e}")
        return False

def create_models():
    """Define MongoDB models inline"""
    
    class User(mongoengine.Document):
        meta = {'collection': 'users'}
        
        username = mongoengine.StringField(max_length=50, required=True, unique=True)
        email = mongoengine.EmailField(required=True, unique=True)
        password_hash = mongoengine.StringField(required=True)
        created_at = mongoengine.DateTimeField(default=datetime.utcnow)
        is_active = mongoengine.BooleanField(default=True)
        
        def set_password(self, password):
            self.password_hash = generate_password_hash(password)
        
        def get_id(self):
            return str(self.id)
    
    class BugComment(mongoengine.EmbeddedDocument):
        author_username = mongoengine.StringField(required=True)
        comment = mongoengine.StringField(required=True)
        created_at = mongoengine.DateTimeField(default=datetime.utcnow)
    
    class Bug(mongoengine.Document):
        meta = {'collection': 'bugs'}
        
        STATUS_CHOICES = [('new', 'New'), ('in_progress', 'In Progress'), 
                         ('resolved', 'Resolved'), ('closed', 'Closed')]
        PRIORITY_CHOICES = [('low', 'Low'), ('medium', 'Medium'), ('high', 'High')]
        
        title = mongoengine.StringField(max_length=200, required=True)
        description = mongoengine.StringField(required=True)
        status = mongoengine.StringField(max_length=20, choices=STATUS_CHOICES, default='new')
        priority = mongoengine.StringField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
        category = mongoengine.StringField(max_length=50)
        
        created_by_username = mongoengine.StringField(required=True)
        assigned_to_username = mongoengine.StringField()
        
        created_at = mongoengine.DateTimeField(default=datetime.utcnow)
        updated_at = mongoengine.DateTimeField(default=datetime.utcnow)
        
        comments = mongoengine.ListField(mongoengine.EmbeddedDocumentField(BugComment))
        
        def save(self, *args, **kwargs):
            self.updated_at = datetime.utcnow()
            return super().save(*args, **kwargs)
    
    return User, Bug, BugComment

def create_admin_user(User):
    """Create admin user"""
    print("Creating admin user...")
    
    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@bugtracker.local')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    try:
        # Check if admin exists
        existing_admin = User.objects(username=admin_username).first()
        if existing_admin:
            print(f"Admin user '{admin_username}' already exists")
            return existing_admin
        
        # Create new admin
        admin = User(
            username=admin_username,
            email=admin_email
        )
        admin.set_password(admin_password)
        admin.save()
        
        print(f"Admin user created: {admin_username}")
        return admin
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
        return None

def create_sample_data(User, Bug, BugComment):
    """Create sample bug data"""
    print("Creating sample data...")
    
    try:
        # Check if data exists
        if Bug.objects.count() > 0:
            print(f"Found {Bug.objects.count()} existing bugs, skipping sample data")
            return True
        
        admin = User.objects(username='admin').first()
        if not admin:
            print("Admin user not found, cannot create sample data")
            return False
        
        # Sample bugs
        sample_bugs = [
            {
                'title': 'Login page not responsive on mobile',
                'description': 'The login form is not properly displayed on mobile devices.',
                'status': 'new',
                'priority': 'high',
                'category': 'UI/UX'
            },
            {
                'title': 'Database connection timeout',
                'description': 'Users experiencing timeout errors during peak hours.',
                'status': 'in_progress',
                'priority': 'high',
                'category': 'Backend'
            },
            {
                'title': 'Email notifications not working',
                'description': 'Users not receiving email notifications for assignments.',
                'status': 'new',
                'priority': 'medium',
                'category': 'Email'
            }
        ]
        
        created_bugs = []
        for bug_data in sample_bugs:
            bug = Bug(
                title=bug_data['title'],
                description=bug_data['description'],
                status=bug_data['status'],
                priority=bug_data['priority'],
                category=bug_data['category'],
                created_by_username=admin.username
            )
            
            if bug_data['status'] == 'in_progress':
                bug.assigned_to_username = admin.username
            
            bug.save()
            created_bugs.append(bug)
        
        # Add sample comments
        if created_bugs:
            comment = BugComment(
                author_username=admin.username,
                comment="I've reproduced this issue. Working on a fix."
            )
            created_bugs[0].comments.append(comment)
            created_bugs[0].save()
        
        print(f"Created {len(created_bugs)} sample bugs")
        return True
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        return False

def display_stats(User, Bug):
    """Display database statistics"""
    print("\nDatabase Statistics:")
    print("=" * 30)
    
    try:
        print(f"Users: {User.objects.count()}")
        print(f"Total Bugs: {Bug.objects.count()}")
        print(f"New Bugs: {Bug.objects(status='new').count()}")
        print(f"In Progress: {Bug.objects(status='in_progress').count()}")
        print(f"Resolved: {Bug.objects(status='resolved').count()}")
        print(f"Closed: {Bug.objects(status='closed').count()}")
        
        recent_bugs = Bug.objects.order_by('-created_at').limit(3)
        if recent_bugs:
            print("\nRecent Bugs:")
            for bug in recent_bugs:
                print(f"  - {bug.title} ({bug.status})")
        
    except Exception as e:
        print(f"Error displaying stats: {e}")

def main():
    """Main setup function"""
    print("MongoDB Setup for Bug Tracker")
    print("=" * 40)
    
    # Step 1: Load environment and build URI
    uri = load_environment()
    if not uri:
        sys.exit(1)
    
    # Step 2: Test connection
    if not test_connection(uri):
        print("Connection test failed")
        sys.exit(1)
    
    # Step 3: Setup MongoEngine
    if not setup_mongoengine(uri):
        print("MongoEngine setup failed")
        sys.exit(1)
    
    # Step 5: Create models
    User, Bug, BugComment = create_models()
    
    # Step 6: Create admin user
    admin = create_admin_user(User)
    if not admin:
        print("Failed to create admin user")
        sys.exit(1)
    
    # Step 7: Create sample data
    create_sample_data(User, Bug, BugComment)
    
    # Step 8: Display statistics
    display_stats(User, Bug)
    
    print("\nSetup completed successfully!")
    print(f"Admin Login - Username: {admin.username}")
    print("You can now start the Flask application")

if __name__ == "__main__":
    main()
