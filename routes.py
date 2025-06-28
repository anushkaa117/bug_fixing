from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Bug, BugComment
from forms import LoginForm, RegistrationForm, BugForm, ReportBugForm, CommentForm
from sqlalchemy import func

def init_routes(app):
    """Initialize all routes - replaces PHP routing"""
    
    @app.route('/')
    @app.route('/home')
    def home():
        """Home page with dashboard - replaces PHP index logic"""
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        
        # Get bug statistics (replaces PHP dashboard queries)
        total_bugs = Bug.query.count()
        open_bugs = Bug.query.filter(Bug.status.in_(['new', 'in_progress'])).count()
        resolved_bugs = Bug.query.filter_by(status='resolved').count()
        in_progress_bugs = Bug.query.filter_by(status='in_progress').count()
        
        # Get recent bugs for table
        recent_bugs = Bug.query.order_by(Bug.created_at.desc()).limit(10).all()
        
        return render_template('home.html',
                             total_bugs=total_bugs,
                             open_bugs=open_bugs,
                             resolved_bugs=resolved_bugs,
                             in_progress_bugs=in_progress_bugs,
                             recent_bugs=recent_bugs)
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Login page - replaces PHP login.php"""
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            
            if user and user.check_password(form.password.data):
                login_user(user)
                next_page = request.args.get('next')
                flash(f'Welcome back, {user.username}!', 'success')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                flash('Invalid username or password', 'danger')
        
        return render_template('login.html', form=form)
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """Registration page - replaces PHP register.php"""
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User(
                username=form.username.data,
                email=form.email.data
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html', form=form)
    
    @app.route('/logout')
    @login_required
    def logout():
        """Logout - replaces PHP logout.php"""
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))
    
    @app.route('/report_bug', methods=['GET', 'POST'])
    @login_required
    def report_bug():
        """Report new bug - replaces PHP report_bug.php"""
        form = ReportBugForm()
        
        if form.validate_on_submit():
            bug = Bug(
                title=form.title.data,
                description=form.description.data,
                priority=form.priority.data,
                category=form.category.data,
                created_by=current_user.id,
                status='new'
            )
            
            db.session.add(bug)
            db.session.commit()
            
            flash('Bug reported successfully!', 'success')
            return redirect(url_for('home'))
        
        return render_template('report_bug.html', form=form)
    
    @app.route('/bugs')
    @login_required
    def bugs_list():
        """List all bugs with filtering"""
        page = request.args.get('page', 1, type=int)
        status_filter = request.args.get('status', '')
        priority_filter = request.args.get('priority', '')
        
        query = Bug.query
        
        if status_filter:
            query = query.filter_by(status=status_filter)
        if priority_filter:
            query = query.filter_by(priority=priority_filter)
        
        bugs = query.order_by(Bug.created_at.desc()).paginate(
            page=page, per_page=app.config['BUGS_PER_PAGE'], error_out=False
        )
        
        return render_template('bugs_list.html', bugs=bugs, 
                             status_filter=status_filter, 
                             priority_filter=priority_filter)
    
    @app.route('/bug/<int:bug_id>')
    @login_required
    def bug_detail(bug_id):
        """View bug details"""
        bug = Bug.query.get_or_404(bug_id)
        comments = BugComment.query.filter_by(bug_id=bug_id).order_by(BugComment.created_at.asc()).all()
        comment_form = CommentForm()
        
        return render_template('bug_detail.html', bug=bug, comments=comments, form=comment_form)
    
    @app.route('/bug/<int:bug_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_bug(bug_id):
        """Edit bug - replaces PHP bug form editing"""
        bug = Bug.query.get_or_404(bug_id)
        
        # Only creator or admin can edit
        if bug.created_by != current_user.id and current_user.username != 'admin':
            flash('You can only edit bugs you created.', 'danger')
            return redirect(url_for('bug_detail', bug_id=bug_id))
        
        form = BugForm(obj=bug)
        
        if form.validate_on_submit():
            bug.title = form.title.data
            bug.description = form.description.data
            bug.priority = form.priority.data
            bug.category = form.category.data
            bug.status = form.status.data
            bug.assigned_to = form.assigned_to.data if form.assigned_to.data != 0 else None
            
            # Add comment if provided
            if form.comments.data:
                comment = BugComment(
                    bug_id=bug.id,
                    user_id=current_user.id,
                    comment=form.comments.data
                )
                db.session.add(comment)
            
            db.session.commit()
            flash('Bug updated successfully!', 'success')
            return redirect(url_for('bug_detail', bug_id=bug.id))
        
        return render_template('bug_form.html', form=form, bug=bug)
    
    @app.route('/bug/<int:bug_id>/comment', methods=['POST'])
    @login_required
    def add_comment(bug_id):
        """Add comment to bug"""
        bug = Bug.query.get_or_404(bug_id)
        form = CommentForm()
        
        if form.validate_on_submit():
            comment = BugComment(
                bug_id=bug_id,
                user_id=current_user.id,
                comment=form.comment.data
            )
            db.session.add(comment)
            db.session.commit()
            flash('Comment added successfully!', 'success')
        
        return redirect(url_for('bug_detail', bug_id=bug_id))
    
    @app.route('/api/bugs/stats')
    @login_required
    def api_bug_stats():
        """API endpoint for bug statistics"""
        stats = {
            'total': Bug.query.count(),
            'new': Bug.query.filter_by(status='new').count(),
            'in_progress': Bug.query.filter_by(status='in_progress').count(),
            'resolved': Bug.query.filter_by(status='resolved').count(),
            'closed': Bug.query.filter_by(status='closed').count(),
            'by_priority': {
                'high': Bug.query.filter_by(priority='high').count(),
                'medium': Bug.query.filter_by(priority='medium').count(),
                'low': Bug.query.filter_by(priority='low').count()
            }
        }
        return jsonify(stats)
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500
