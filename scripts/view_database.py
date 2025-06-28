#!/usr/bin/env python3
"""
View Database Contents
Display all users and bugs in the MongoDB database
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import mongoengine

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
    
    return User, Bug, BugComment

def display_database_contents(User, Bug):
    """Display current database contents"""
    print("\n" + "="*60)
    print("CURRENT DATABASE CONTENTS")
    print("="*60)
    
    # Display users
    print(f"\nUSERS ({User.objects.count()}):")
    print("-" * 60)
    for user in User.objects.order_by('created_at'):
        print(f"  {user.username:15} | {user.email:25} | {user.created_at.strftime('%Y-%m-%d %H:%M')}")
    
    # Display bugs with status counts
    print(f"\nBUGS ({Bug.objects.count()}):")
    print("-" * 60)
    
    # Status summary
    status_counts = {}
    priority_counts = {}
    
    for bug in Bug.objects:
        status_counts[bug.status] = status_counts.get(bug.status, 0) + 1
        priority_counts[bug.priority] = priority_counts.get(bug.priority, 0) + 1
    
    print("Status Summary:")
    for status, count in status_counts.items():
        print(f"  {status.upper():12}: {count}")
    
    print("\nPriority Summary:")
    for priority, count in priority_counts.items():
        print(f"  {priority.upper():12}: {count}")
    
    print("\nDetailed Bug List:")
    print("-" * 60)
    
    for i, bug in enumerate(Bug.objects.order_by('-created_at'), 1):
        status_symbol = {
            'new': '[NEW]',
            'in_progress': '[PROG]',
            'resolved': '[DONE]',
            'closed': '[CLOSED]'
        }.get(bug.status, '[?]')
        
        priority_symbol = {
            'high': '[HIGH]',
            'medium': '[MED]',
            'low': '[LOW]'
        }.get(bug.priority, '[?]')
        
        print(f"{i:2}. {status_symbol} {priority_symbol} {bug.title}")
        print(f"    Category: {bug.category or 'None'}")
        print(f"    Created by: {bug.created_by_username}")
        if bug.assigned_to_username:
            print(f"    Assigned to: {bug.assigned_to_username}")
        print(f"    Created: {bug.created_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"    Comments: {len(bug.comments)}")
        
        # Show comments
        if bug.comments:
            print("    Recent Comments:")
            for comment in bug.comments[-2:]:  # Show last 2 comments
                print(f"      - {comment.author_username}: {comment.comment[:50]}...")
        print()

def display_statistics(User, Bug):
    """Display database statistics"""
    print("\n" + "="*60)
    print("DATABASE STATISTICS")
    print("="*60)
    
    total_users = User.objects.count()
    total_bugs = Bug.objects.count()
    
    print(f"Total Users: {total_users}")
    print(f"Total Bugs: {total_bugs}")
    
    if total_bugs > 0:
        # Bug statistics
        new_bugs = Bug.objects(status='new').count()
        in_progress_bugs = Bug.objects(status='in_progress').count()
        resolved_bugs = Bug.objects(status='resolved').count()
        closed_bugs = Bug.objects(status='closed').count()
        
        high_priority = Bug.objects(priority='high').count()
        medium_priority = Bug.objects(priority='medium').count()
        low_priority = Bug.objects(priority='low').count()
        
        print(f"\nBug Status Breakdown:")
        print(f"  New: {new_bugs} ({new_bugs/total_bugs*100:.1f}%)")
        print(f"  In Progress: {in_progress_bugs} ({in_progress_bugs/total_bugs*100:.1f}%)")
        print(f"  Resolved: {resolved_bugs} ({resolved_bugs/total_bugs*100:.1f}%)")
        print(f"  Closed: {closed_bugs} ({closed_bugs/total_bugs*100:.1f}%)")
        
        print(f"\nPriority Breakdown:")
        print(f"  High: {high_priority} ({high_priority/total_bugs*100:.1f}%)")
        print(f"  Medium: {medium_priority} ({medium_priority/total_bugs*100:.1f}%)")
        print(f"  Low: {low_priority} ({low_priority/total_bugs*100:.1f}%)")
        
        # Category breakdown
        categories = {}
        for bug in Bug.objects:
            cat = bug.category or 'Uncategorized'
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"\nCategory Breakdown:")
        for category, count in sorted(categories.items()):
            print(f"  {category}: {count}")

def main():
    """Main function"""
    print("MongoDB Database Viewer")
    print("=" * 40)
    
    # Setup connection
    if not setup_connection():
        sys.exit(1)
    
    # Create models
    User, Bug, BugComment = create_models()
    
    # Display database contents
    display_database_contents(User, Bug)
    
    # Display statistics
    display_statistics(User, Bug)

if __name__ == "__main__":
    main()
