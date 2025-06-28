"""
MongoDB Models for Bug Tracker Application
Using MongoEngine for MongoDB integration
"""

from datetime import datetime
from flask_login import UserMixin
from mongoengine import Document, EmbeddedDocument, fields
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt

class User(Document, UserMixin):
    """User model for authentication and profile management"""
    
    meta = {
        'collection': 'users',
        'indexes': ['username', 'email']
    }
    
    username = fields.StringField(max_length=50, required=True, unique=True)
    email = fields.EmailField(required=True, unique=True)
    password_hash = fields.StringField(required=True)
    created_at = fields.DateTimeField(default=datetime.utcnow)
    is_active = fields.BooleanField(default=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Return user ID for Flask-Login"""
        return str(self.id)
    
    def __str__(self):
        return f'<User {self.username}>'

class BugComment(EmbeddedDocument):
    """Embedded document for bug comments"""
    
    author = fields.ReferenceField(User, required=True)
    comment = fields.StringField(required=True)
    created_at = fields.DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f'<Comment by {self.author.username}>'

class Bug(Document):
    """Bug model for tracking issues"""
    
    meta = {
        'collection': 'bugs',
        'indexes': ['status', 'priority', 'created_by', 'assigned_to', 'created_at']
    }
    
    # Bug Status Choices
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    ]
    
    # Priority Choices
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ]
    
    title = fields.StringField(max_length=200, required=True)
    description = fields.StringField(required=True)
    status = fields.StringField(max_length=20, choices=STATUS_CHOICES, default='new')
    priority = fields.StringField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    category = fields.StringField(max_length=50)
    
    # User references
    created_by = fields.ReferenceField(User, required=True, reverse_delete_rule=2)  # CASCADE
    assigned_to = fields.ReferenceField(User, reverse_delete_rule=4)  # NULLIFY
    
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
            'new': 'bg-primary',
            'in_progress': 'bg-warning',
            'resolved': 'bg-success',
            'closed': 'bg-secondary'
        }
        return status_classes.get(self.status, 'bg-secondary')
    
    @property
    def priority_badge_class(self):
        """Return Bootstrap badge class for bug priority"""
        priority_classes = {
            'high': 'bg-danger',
            'medium': 'bg-warning',
            'low': 'bg-info'
        }
        return priority_classes.get(self.priority, 'bg-secondary')
    
    @property
    def creator(self):
        """Get bug creator (for template compatibility)"""
        return self.created_by
    
    @property
    def assignee(self):
        """Get bug assignee (for template compatibility)"""
        return self.assigned_to
    
    def add_comment(self, author, comment_text):
        """Add a comment to the bug"""
        comment = BugComment(author=author, comment=comment_text)
        self.comments.append(comment)
        self.save()
        return comment
    
    def get_comments(self):
        """Get all comments (for template compatibility)"""
        return self.comments
    
    @classmethod
    def get_stats(cls):
        """Get bug statistics"""
        total_bugs = cls.objects.count()
        open_bugs = cls.objects(status__in=['new', 'in_progress']).count()
        resolved_bugs = cls.objects(status='resolved').count()
        closed_bugs = cls.objects(status='closed').count()
        in_progress_bugs = cls.objects(status='in_progress').count()
        
        return {
            'total_bugs': total_bugs,
            'open_bugs': open_bugs,
            'resolved_bugs': resolved_bugs,
            'closed_bugs': closed_bugs,
            'in_progress_bugs': in_progress_bugs
        }
    
    @classmethod
    def get_recent_bugs(cls, limit=10):
        """Get recent bugs"""
        return cls.objects.order_by('-created_at').limit(limit)
    
    def __str__(self):
        return f'<Bug {self.id}: {self.title}>'

# For backward compatibility with existing code
class BugCommentStandalone(Document):
    """Standalone comment model (if needed for complex queries)"""
    
    meta = {
        'collection': 'bug_comments',
        'indexes': ['bug', 'author', 'created_at']
    }
    
    bug = fields.ReferenceField(Bug, required=True, reverse_delete_rule=2)  # CASCADE
    author = fields.ReferenceField(User, required=True, reverse_delete_rule=2)  # CASCADE
    comment = fields.StringField(required=True)
    created_at = fields.DateTimeField(default=datetime.utcnow)
    
    def __str__(self):
        return f'<Comment on Bug {self.bug.id} by {self.author.username}>'
