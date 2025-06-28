from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import User

class LoginForm(FlaskForm):
    """Login form - replaces PHP login form validation"""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    """Registration form - replaces PHP registration form validation"""
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=3, max=50)
    ])
    email = StringField('Email', validators=[
        DataRequired(), 
        Email(),
        Length(max=100)
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        """Check if username already exists"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        """Check if email already exists"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please choose a different one.')

class BugForm(FlaskForm):
    """Bug creation/editing form - replaces PHP bug form validation"""
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=5, max=255, message='Title must be between 5 and 255 characters')
    ])
    description = TextAreaField('Description', validators=[
        DataRequired(),
        Length(min=10, message='Description must be at least 10 characters long')
    ])
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], default='medium', validators=[DataRequired()])
    
    category = StringField('Category', validators=[Length(max=100)])
    
    status = SelectField('Status', choices=[
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    ], default='new', validators=[DataRequired()])
    
    assigned_to = SelectField('Assigned To', coerce=int, validators=[])
    comments = TextAreaField('Comments')
    
    submit = SubmitField('Save Bug')
    
    def __init__(self, *args, **kwargs):
        super(BugForm, self).__init__(*args, **kwargs)
        # Populate assigned_to choices with users
        self.assigned_to.choices = [(0, 'Unassigned')] + [
            (user.id, user.username) for user in User.query.all()
        ]

class ReportBugForm(FlaskForm):
    """Simple bug reporting form - replaces PHP report_bug form"""
    title = StringField('Bug Title', validators=[
        DataRequired(),
        Length(min=5, max=255, message='Title must be between 5 and 255 characters')
    ])
    description = TextAreaField('Description', validators=[
        DataRequired(),
        Length(min=10, message='Please provide a detailed description (at least 10 characters)')
    ])
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], default='medium', validators=[DataRequired()])
    
    category = StringField('Category', validators=[Length(max=100)])
    
    submit = SubmitField('Report Bug')

class CommentForm(FlaskForm):
    """Comment form for bugs"""
    comment = TextAreaField('Add Comment', validators=[
        DataRequired(),
        Length(min=5, message='Comment must be at least 5 characters long')
    ])
    submit = SubmitField('Add Comment')

class ForgotPasswordForm(FlaskForm):
    """Forgot password form"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Reset Password')

class ResetPasswordForm(FlaskForm):
    """Reset password form"""
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')
