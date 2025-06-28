from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model - converted from PHP users table"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    created_bugs = db.relationship('Bug', foreign_keys='Bug.created_by', backref='creator', lazy='dynamic')
    assigned_bugs = db.relationship('Bug', foreign_keys='Bug.assigned_to', backref='assignee', lazy='dynamic')
    comments = db.relationship('BugComment', backref='author', lazy='dynamic')
    
    def set_password(self, password):
        """Set password hash - replaces PHP password_hash()"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password - replaces PHP password_verify()"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Bug(db.Model):
    """Bug model - converted from PHP bugs table"""
    __tablename__ = 'bugs'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('new', 'in_progress', 'resolved', 'closed', name='bug_status'), 
                      default='new', nullable=False)
    priority = db.Column(db.Enum('low', 'medium', 'high', name='bug_priority'), 
                        default='medium', nullable=False)
    category = db.Column(db.String(100))
    
    # Foreign Keys
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    comments = db.relationship('BugComment', backref='bug', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def status_badge_class(self):
        """Get Bootstrap badge class for status"""
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

    def __repr__(self):
        return f'<Bug {self.id}: {self.title}>'

class BugComment(db.Model):
    """Bug Comment model - converted from PHP bug_comments table"""
    __tablename__ = 'bug_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    bug_id = db.Column(db.Integer, db.ForeignKey('bugs.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<BugComment {self.id} on Bug {self.bug_id}>'

# Database initialization function
def init_db(app):
    """Initialize database with app context"""
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create default admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@bugtracker.com'
            )
            admin.set_password('admin123')  # Change this in production
            db.session.add(admin)
            db.session.commit()
            print("Default admin user created: admin/admin123")
