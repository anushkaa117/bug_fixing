#!/usr/bin/env python3
"""
Add Test Data to MongoDB
Insert additional users and bugs to test the database
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
import mongoengine
from werkzeug.security import generate_password_hash

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_connection():
    """Setup MongoDB connection"""
    load_dotenv()
    
    username = os.getenv('MONGO_USERNAME')
    password = os.getenv('MONGO_PASSWORD')
    cluster = os.getenv('MONGO_CLUSTER')
    database = os.getenv('MONGO_DATABASE', 'Practice')
    
    # URL encode password
    import urllib.parse
    encoded_password = urllib.parse.quote_plus(password)
    
    # Build connection string
    uri = f"mongodb+srv://{username}:{encoded_password}@{cluster}/{database}?retryWrites=true&w=majority&appName=Cluster0"
    
    try:
        mongoengine.connect(host=uri)
        print(f"Connected to MongoDB database: {database}")
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

def create_models():
    """Define MongoDB models"""
    
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

def add_test_users(User):
    """Add test users"""
    print("Adding test users...")
    
    test_users = [
        {
            'username': 'john_doe',
            'email': 'john@example.com',
            'password': 'password123'
        },
        {
            'username': 'jane_smith',
            'email': 'jane@example.com',
            'password': 'password123'
        },
        {
            'username': 'dev_user',
            'email': 'dev@company.com',
            'password': 'devpass123'
        },
        {
            'username': 'tester',
            'email': 'test@company.com',
            'password': 'testpass123'
        }
    ]
    
    created_users = []
    for user_data in test_users:
        try:
            # Check if user already exists
            existing_user = User.objects(username=user_data['username']).first()
            if existing_user:
                print(f"  User '{user_data['username']}' already exists")
                created_users.append(existing_user)
                continue
            
            # Create new user
            user = User(
                username=user_data['username'],
                email=user_data['email']
            )
            user.set_password(user_data['password'])
            user.save()
            
            print(f"  Created user: {user_data['username']}")
            created_users.append(user)
            
        except Exception as e:
            print(f"  Error creating user {user_data['username']}: {e}")
    
    return created_users

def add_test_bugs(Bug, BugComment, users):
    """Add test bugs with various statuses and priorities"""
    print("Adding test bugs...")
    
    # Get usernames for assignment
    usernames = [user.username for user in users]
    admin_username = 'admin'
    
    test_bugs = [
        {
            'title': 'User registration form validation error',
            'description': 'Email validation is not working properly on the registration form. Users can register with invalid email formats.',
            'status': 'new',
            'priority': 'high',
            'category': 'Frontend',
            'created_by': admin_username,
            'assigned_to': usernames[0] if usernames else None,
            'comments': [
                {'author': admin_username, 'comment': 'This is affecting user onboarding. High priority fix needed.'},
                {'author': usernames[0] if usernames else admin_username, 'comment': 'I can reproduce this issue. Working on a fix.'}
            ]
        },
        {
            'title': 'API response time is slow',
            'description': 'The /api/bugs endpoint is taking more than 5 seconds to respond when there are more than 100 bugs.',
            'status': 'in_progress',
            'priority': 'medium',
            'category': 'Backend',
            'created_by': usernames[1] if len(usernames) > 1 else admin_username,
            'assigned_to': usernames[2] if len(usernames) > 2 else admin_username,
            'comments': [
                {'author': usernames[1] if len(usernames) > 1 else admin_username, 'comment': 'Performance testing shows significant slowdown with large datasets.'},
                {'author': usernames[2] if len(usernames) > 2 else admin_username, 'comment': 'Added database indexing. Testing the improvement.'}
            ]
        },
        {
            'title': 'Mobile app crashes on iOS 17',
            'description': 'The mobile application crashes when users try to upload images on iOS 17 devices.',
            'status': 'new',
            'priority': 'high',
            'category': 'Mobile',
            'created_by': usernames[3] if len(usernames) > 3 else admin_username,
            'assigned_to': None,
            'comments': [
                {'author': usernames[3] if len(usernames) > 3 else admin_username, 'comment': 'Multiple users reporting this issue. Affects latest iOS version only.'}
            ]
        },
        {
            'title': 'Dark mode toggle not working',
            'description': 'Users cannot switch between light and dark themes. The toggle button appears to be non-functional.',
            'status': 'resolved',
            'priority': 'low',
            'category': 'UI/UX',
            'created_by': admin_username,
            'assigned_to': usernames[0] if usernames else admin_username,
            'comments': [
                {'author': admin_username, 'comment': 'CSS classes were not properly applied.'},
                {'author': usernames[0] if usernames else admin_username, 'comment': 'Fixed the CSS issue. Theme switching now works correctly.'}
            ]
        },
        {
            'title': 'Database connection pool exhaustion',
            'description': 'Server runs out of database connections during peak hours, causing 500 errors.',
            'status': 'closed',
            'priority': 'high',
            'category': 'Infrastructure',
            'created_by': usernames[2] if len(usernames) > 2 else admin_username,
            'assigned_to': admin_username,
            'comments': [
                {'author': usernames[2] if len(usernames) > 2 else admin_username, 'comment': 'Critical issue affecting production stability.'},
                {'author': admin_username, 'comment': 'Increased connection pool size and added connection monitoring.'},
                {'author': admin_username, 'comment': 'Issue resolved. No more connection exhaustion reported.'}
            ]
        }
    ]
    
    created_bugs = []
    for bug_data in test_bugs:
        try:
            # Create bug
            bug = Bug(
                title=bug_data['title'],
                description=bug_data['description'],
                status=bug_data['status'],
                priority=bug_data['priority'],
                category=bug_data['category'],
                created_by_username=bug_data['created_by'],
                assigned_to_username=bug_data['assigned_to']
            )
            
            # Add comments
            for comment_data in bug_data['comments']:
                comment = BugComment(
                    author_username=comment_data['author'],
                    comment=comment_data['comment']
                )
                bug.comments.append(comment)
            
            bug.save()
            print(f"  Created bug: {bug_data['title'][:50]}...")
            created_bugs.append(bug)
            
        except Exception as e:
            print(f"  Error creating bug: {e}")
    
    return created_bugs

def display_database_contents(User, Bug):
    """Display current database contents"""
    print("\n" + "="*60)
    print("CURRENT DATABASE CONTENTS")
    print("="*60)
    
    # Display users
    print(f"\nUSERS ({User.objects.count()}):")
    print("-" * 40)
    for user in User.objects.order_by('created_at'):
        print(f"  {user.username:15} | {user.email:25} | {user.created_at.strftime('%Y-%m-%d %H:%M')}")
    
    # Display bugs
    print(f"\nBUGS ({Bug.objects.count()}):")
    print("-" * 40)
    for bug in Bug.objects.order_by('-created_at'):
        status_color = {
            'new': '🆕',
            'in_progress': '🔄',
            'resolved': '✅',
            'closed': '🔒'
        }.get(bug.status, '❓')
        
        priority_color = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }.get(bug.priority, '⚪')
        
        print(f"  {status_color} {priority_color} {bug.title[:45]:45} | {bug.category:12} | {bug.created_by_username:10}")
        print(f"      Created: {bug.created_at.strftime('%Y-%m-%d %H:%M')} | Comments: {len(bug.comments)}")
        
        # Show recent comments
        if bug.comments:
            latest_comment = bug.comments[-1]
            print(f"      Latest: {latest_comment.comment[:60]}...")
        print()

def main():
    """Main function"""
    print("Adding Test Data to MongoDB")
    print("=" * 40)
    
    # Setup connection
    if not setup_connection():
        sys.exit(1)
    
    # Create models
    User, Bug, BugComment = create_models()
    
    # Add test data
    users = add_test_users(User)
    bugs = add_test_bugs(Bug, BugComment, users)
    
    print(f"\nSummary:")
    print(f"  Users added: {len(users)}")
    print(f"  Bugs added: {len(bugs)}")
    
    # Display current database contents
    display_database_contents(User, Bug)

if __name__ == "__main__":
    main()
