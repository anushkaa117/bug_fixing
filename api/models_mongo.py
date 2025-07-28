"""
MongoDB Models for Bug Tracker Application
Using MongoEngine for MongoDB integration
"""

from datetime import datetime
from flask_login import UserMixin
from mongoengine import Document, EmbeddedDocument, fields
from werkzeug.security import generate_password_hash, check_password_hash

class User(Document, UserMixin):
    """User model for authentication and profile management"""
    
    meta = {
        'collection': 'users',
        'indexes': ['username', 'email', 'google_id']
    }
    
    username = fields.StringField(max_length=50, required=True, unique=True)
    email = fields.EmailField(required=True, unique=True)
    password_hash = fields.StringField(required=False)  # Make optional for Google OAuth
    google_id = fields.StringField(unique=True, sparse=True)  # For Google OAuth
    google_picture = fields.URLField()  # Profile picture from Google
    role = fields.StringField(max_length=20, default='user', choices=['user', 'admin'])
    created_at = fields.DateTimeField(default=datetime.utcnow)
    is_active = fields.BooleanField(default=True)
    auth_provider = fields.StringField(default='local', choices=['local', 'google'])  # Track auth method
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Return user ID for Flask-Login"""
        return str(self.id)
    
    def __str__(self):
        return f'<User {self.username}>'

class BugComment(EmbeddedDocument):
    """Embedded document for bug comments"""
    
    author = fields.ReferenceField(User, required=True)
    content = fields.StringField(required=True)
    created_at = fields.DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f'<Comment by {self.author.username}>'

class Bug(Document):
    """Bug model for tracking issues"""
    
    meta = {
        'collection': 'bugs',
        'indexes': ['status', 'priority', 'reporter', 'assignee', 'created_at']
    }
    
    # Bug Status Choices
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    ]
    
    # Priority Choices
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ]
    
    title = fields.StringField(max_length=200, required=True)
    description = fields.StringField(required=True)
    status = fields.StringField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = fields.StringField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    tags = fields.ListField(fields.StringField(max_length=50))
    
    # Additional fields for detailed bug tracking
    steps_to_reproduce = fields.StringField()
    expected_behavior = fields.StringField()
    environment = fields.StringField(max_length=200)
    
    # User references
    reporter = fields.ReferenceField(User, required=True, reverse_delete_rule=2)  # CASCADE
    assignee = fields.ReferenceField(User, reverse_delete_rule=4)  # NULLIFY
    
    # Timestamps
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    
    # Comments as embedded documents
    comments = fields.ListField(fields.EmbeddedDocumentField(BugComment))
    
    def save(self, *args, **kwargs):
        """Override save to update timestamp"""
        self.updated_at = datetime.utcnow()
        return super(Bug, self).save(*args, **kwargs)
    
    @property
    def status_badge_class(self):
        """Return Bootstrap badge class for bug status"""
        status_classes = {
            'open': 'bg-danger',
            'in_progress': 'bg-warning',
            'resolved': 'bg-success',
            'closed': 'bg-secondary'
        }
        return status_classes.get(self.status, 'bg-secondary')
    
    @property
    def priority_badge_class(self):
        """Return Bootstrap badge class for bug priority"""
        priority_classes = {
            'low': 'bg-success',
            'medium': 'bg-info',
            'high': 'bg-warning',
            'critical': 'bg-danger'
        }
        return priority_classes.get(self.priority, 'bg-secondary')
    
    def __str__(self):
        return f'<Bug {self.title}>'
