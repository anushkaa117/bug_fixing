#!/usr/bin/env python3
"""
Database Initialization Script for Bug Tracker
Connects to MongoDB and creates collections with sample data
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import mongoengine
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Load environment variables
load_dotenv()

# Import models
from models_mongo import User, Bug, BugComment

def connect_to_database():
    """Connect to MongoDB using DATABASE_URL from environment"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL not found in environment variables")
        print("Please add DATABASE_URL to your .env file")
        return False
    
    try:
        print("🔗 Connecting to MongoDB...")
        print(f"📍 URL: {database_url[:50]}...")
        
        # Connect using MongoEngine
        mongoengine.connect(host=database_url)
        
        # Test connection
        client = MongoClient(database_url, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        
        print("✅ Successfully connected to MongoDB!")
        return True
        
    except ConnectionFailure as e:
        print(f"❌ Connection failed: {e}")
        return False
    except ServerSelectionTimeoutError as e:
        print(f"❌ Server selection timeout: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def create_indexes():
    """Create database indexes for better performance"""
    print("📊 Creating database indexes...")
    
    try:
        # Create indexes for User collection
        User.create_index([("username", 1)], unique=True)
        User.create_index([("email", 1)], unique=True)
        
        # Create indexes for Bug collection
        Bug.create_index([("status", 1)])
        Bug.create_index([("priority", 1)])
        Bug.create_index([("created_by", 1)])
        Bug.create_index([("assigned_to", 1)])
        Bug.create_index([("created_at", -1)])
        
        print("✅ Database indexes created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating indexes: {e}")
        return False

def create_admin_user():
    """Create default admin user"""
    print("👤 Creating admin user...")
    
    try:
        # Check if admin user already exists
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@bugtracker.local')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        
        existing_admin = User.objects(username=admin_username).first()
        if existing_admin:
            print(f"⚠️  Admin user '{admin_username}' already exists")
            return existing_admin
        
        # Create new admin user
        admin_user = User(
            username=admin_username,
            email=admin_email
        )
        admin_user.set_password(admin_password)
        admin_user.save()
        
        print(f"✅ Admin user created successfully!")
        print(f"   Username: {admin_username}")
        print(f"   Email: {admin_email}")
        print(f"   Password: {admin_password}")
        
        return admin_user
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return None

def create_sample_data(admin_user):
    """Create sample bug data for testing"""
    print("🐛 Creating sample bug data...")
    
    try:
        # Check if sample data already exists
        existing_bugs = Bug.objects.count()
        if existing_bugs > 0:
            print(f"⚠️  Found {existing_bugs} existing bugs, skipping sample data creation")
            return True
        
        # Sample bugs data
        sample_bugs = [
            {
                'title': 'Login page not responsive on mobile',
                'description': 'The login form is not properly displayed on mobile devices. The form fields are too small and the submit button is cut off.',
                'status': 'new',
                'priority': 'high',
                'category': 'UI/UX'
            },
            {
                'title': 'Database connection timeout',
                'description': 'Users are experiencing timeout errors when trying to load the bug list page. This seems to happen during peak hours.',
                'status': 'in_progress',
                'priority': 'high',
                'category': 'Backend'
            },
            {
                'title': 'Email notifications not working',
                'description': 'Users are not receiving email notifications when bugs are assigned to them or when comments are added.',
                'status': 'new',
                'priority': 'medium',
                'category': 'Email'
            },
            {
                'title': 'Search functionality improvement',
                'description': 'The current search only looks for exact matches. We need to implement fuzzy search and search in descriptions as well.',
                'status': 'resolved',
                'priority': 'low',
                'category': 'Feature'
            },
            {
                'title': 'Add dark mode support',
                'description': 'Users have requested a dark mode theme for better usability during night hours.',
                'status': 'new',
                'priority': 'low',
                'category': 'Feature'
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
                created_by=admin_user
            )
            
            # Assign some bugs to admin user
            if bug_data['status'] == 'in_progress':
                bug.assigned_to = admin_user
            
            bug.save()
            created_bugs.append(bug)
        
        # Add sample comments to some bugs
        if len(created_bugs) >= 2:
            # Add comment to first bug
            created_bugs[0].add_comment(
                admin_user, 
                "I've reproduced this issue on iPhone 12. The CSS media queries need to be updated."
            )
            
            # Add comment to second bug
            created_bugs[1].add_comment(
                admin_user,
                "Investigating the database connection pool settings. Might need to increase the timeout values."
            )
        
        print(f"✅ Created {len(created_bugs)} sample bugs with comments!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return False

def display_statistics():
    """Display database statistics"""
    print("\n📊 Database Statistics:")
    print("=" * 40)
    
    try:
        # User statistics
        total_users = User.objects.count()
        print(f"👥 Total Users: {total_users}")
        
        # Bug statistics
        stats = Bug.get_stats()
        print(f"🐛 Total Bugs: {stats['total_bugs']}")
        print(f"🆕 New Bugs: {Bug.objects(status='new').count()}")
        print(f"🔄 In Progress: {stats['in_progress_bugs']}")
        print(f"✅ Resolved: {stats['resolved_bugs']}")
        print(f"🔒 Closed: {stats['closed_bugs']}")
        
        # Recent bugs
        recent_bugs = Bug.get_recent_bugs(3)
        if recent_bugs:
            print(f"\n📋 Recent Bugs:")
            for bug in recent_bugs:
                print(f"   • {bug.title} ({bug.status})")
        
        print("=" * 40)
        
    except Exception as e:
        print(f"❌ Error displaying statistics: {e}")

def main():
    """Main initialization function"""
    print("🚀 Bug Tracker Database Initialization")
    print("=" * 50)
    
    # Step 1: Connect to database
    if not connect_to_database():
        print("❌ Database connection failed. Exiting...")
        sys.exit(1)
    
    # Step 2: Create indexes
    if not create_indexes():
        print("⚠️  Warning: Failed to create some indexes")
    
    # Step 3: Create admin user
    admin_user = create_admin_user()
    if not admin_user:
        print("❌ Failed to create admin user. Exiting...")
        sys.exit(1)
    
    # Step 4: Create sample data
    if not create_sample_data(admin_user):
        print("⚠️  Warning: Failed to create sample data")
    
    # Step 5: Display statistics
    display_statistics()
    
    print("\n🎉 Database initialization completed successfully!")
    print("🌐 You can now start the application and login with:")
    print(f"   Username: {admin_user.username}")
    print(f"   Password: {os.getenv('ADMIN_PASSWORD', 'admin123')}")

if __name__ == "__main__":
    main()
