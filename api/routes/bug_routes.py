from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models_mongo import Bug, User, BugComment
from datetime import datetime
from bson import ObjectId
from flask_caching import Cache
from app import cache

bug_bp = Blueprint('bugs', __name__)

@bug_bp.route('', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60)  # Cache for 1 minute
def get_bugs():
    try:
        # Get query parameters for filtering
        status = request.args.get('status', 'all')
        priority = request.args.get('priority', 'all')
        assignee = request.args.get('assignee', 'all')
        search = request.args.get('search', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Build query
        query = {}
        
        if status != 'all':
            query['status'] = status
        
        if priority != 'all':
            query['priority'] = priority
        
        if assignee == 'unassigned':
            query['assignee'] = None
        elif assignee != 'all':
            assignee_user = User.objects(username=assignee).first()
            if assignee_user:
                query['assignee'] = assignee_user.id
        
        if search:
            query['$or'] = [
                {'title': {'$regex': search, '$options': 'i'}},
                {'description': {'$regex': search, '$options': 'i'}}
            ]
        
        # Execute query with pagination
        bugs = Bug.objects(**query).order_by('-created_at').paginate(
            page=page, per_page=per_page
        )
        
        # Format response
        bugs_data = []
        for bug in bugs.items:
            bugs_data.append({
                'id': str(bug.id),
                'title': bug.title,
                'description': bug.description,
                'priority': bug.priority,
                'status': bug.status,
                'reporter': {
                    'id': str(bug.reporter.id),
                    'username': bug.reporter.username
                } if bug.reporter else None,
                'assignee': {
                    'id': str(bug.assignee.id),
                    'username': bug.assignee.username
                } if bug.assignee else None,
                'tags': bug.tags,
                'created_at': bug.created_at.isoformat() if bug.created_at else None,
                'updated_at': bug.updated_at.isoformat() if bug.updated_at else None
            })
        
        return jsonify({
            'bugs': bugs_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': bugs.total,
                'pages': bugs.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch bugs', 'error': str(e)}), 500

@bug_bp.route('/<bug_id>', methods=['GET'])
@jwt_required()
def get_bug(bug_id):
    try:
        bug = Bug.objects(id=bug_id).first()
        
        if not bug:
            return jsonify({'message': 'Bug not found'}), 404
        
        # Get comments
        comments_data = []
        for comment in bug.comments:
            comments_data.append({
                'id': str(comment.id) if hasattr(comment, 'id') else None,
                'content': comment.content,
                'author': {
                    'id': str(comment.author.id),
                    'username': comment.author.username
                } if comment.author else None,
                'created_at': comment.created_at.isoformat() if comment.created_at else None
            })
        
        bug_data = {
            'id': str(bug.id),
            'title': bug.title,
            'description': bug.description,
            'priority': bug.priority,
            'status': bug.status,
            'reporter': {
                'id': str(bug.reporter.id),
                'username': bug.reporter.username
            } if bug.reporter else None,
            'assignee': {
                'id': str(bug.assignee.id),
                'username': bug.assignee.username
            } if bug.assignee else None,
            'tags': bug.tags,
            'steps_to_reproduce': bug.steps_to_reproduce,
            'expected_behavior': bug.expected_behavior,
            'environment': bug.environment,
            'comments': comments_data,
            'created_at': bug.created_at.isoformat() if bug.created_at else None,
            'updated_at': bug.updated_at.isoformat() if bug.updated_at else None
        }
        
        return jsonify(bug_data), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch bug', 'error': str(e)}), 500

@bug_bp.route('', methods=['POST'])
@jwt_required()
def create_bug():
    try:
        user_id = get_jwt_identity()
        user = User.objects(id=user_id).first()
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('title') or not data.get('description'):
            return jsonify({'message': 'Title and description are required'}), 400
        
        # Handle assignee
        assignee = None
        if data.get('assignee'):
            assignee = User.objects(username=data['assignee']).first()
        
        # Create bug
        bug = Bug(
            title=data['title'],
            description=data['description'],
            priority=data.get('priority', 'medium'),
            status=data.get('status', 'open'),
            reporter=user,
            assignee=assignee,
            tags=data.get('tags', []),
            steps_to_reproduce=data.get('steps_to_reproduce', ''),
            expected_behavior=data.get('expected_behavior', ''),
            environment=data.get('environment', ''),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        bug.save()
        
        # Invalidate related caches
        cache.delete('bugtracker_bugs_list')
        cache.delete('bugtracker_bug_stats')
        
        return jsonify({
            'message': 'Bug created successfully',
            'bug': {
                'id': str(bug.id),
                'title': bug.title,
                'description': bug.description,
                'priority': bug.priority,
                'status': bug.status,
                'reporter': {
                    'id': str(bug.reporter.id),
                    'username': bug.reporter.username
                },
                'assignee': {
                    'id': str(bug.assignee.id),
                    'username': bug.assignee.username
                } if bug.assignee else None,
                'tags': bug.tags,
                'created_at': bug.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        return jsonify({'message': 'Failed to create bug', 'error': str(e)}), 500

@bug_bp.route('/<bug_id>', methods=['PUT'])
@jwt_required()
def update_bug(bug_id):
    try:
        bug = Bug.objects(id=bug_id).first()
        
        if not bug:
            return jsonify({'message': 'Bug not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'title' in data:
            bug.title = data['title']
        if 'description' in data:
            bug.description = data['description']
        if 'priority' in data:
            bug.priority = data['priority']
        if 'status' in data:
            bug.status = data['status']
        if 'tags' in data:
            bug.tags = data['tags']
        if 'steps_to_reproduce' in data:
            bug.steps_to_reproduce = data['steps_to_reproduce']
        if 'expected_behavior' in data:
            bug.expected_behavior = data['expected_behavior']
        if 'environment' in data:
            bug.environment = data['environment']
        
        # Handle assignee
        if 'assignee' in data:
            if data['assignee']:
                assignee = User.objects(username=data['assignee']).first()
                bug.assignee = assignee
            else:
                bug.assignee = None
        
        bug.updated_at = datetime.utcnow()
        bug.save()
        
        # Invalidate related caches
        cache.delete(f'bugtracker_bug_{bug_id}')
        cache.delete('bugtracker_bugs_list')
        cache.delete('bugtracker_bug_stats')
        
        return jsonify({
            'message': 'Bug updated successfully',
            'bug': {
                'id': str(bug.id),
                'title': bug.title,
                'status': bug.status,
                'priority': bug.priority
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to update bug', 'error': str(e)}), 500

@bug_bp.route('/<bug_id>', methods=['DELETE'])
@jwt_required()
def delete_bug(bug_id):
    try:
        bug = Bug.objects(id=bug_id).first()
        
        if not bug:
            return jsonify({'message': 'Bug not found'}), 404
        
        bug.delete()
        
        # Invalidate related caches
        cache.delete(f'bugtracker_bug_{bug_id}')
        cache.delete('bugtracker_bugs_list')
        cache.delete('bugtracker_bug_stats')
        
        return jsonify({'message': 'Bug deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to delete bug', 'error': str(e)}), 500

@bug_bp.route('/<bug_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(bug_id):
    try:
        user_id = get_jwt_identity()
        user = User.objects(id=user_id).first()
        bug = Bug.objects(id=bug_id).first()
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        if not bug:
            return jsonify({'message': 'Bug not found'}), 404
        
        data = request.get_json()
        
        if not data.get('content'):
            return jsonify({'message': 'Comment content is required'}), 400
        
        # Create comment
        comment = BugComment(
            content=data['content'],
            author=user,
            created_at=datetime.utcnow()
        )
        
        # Add comment to bug
        bug.comments.append(comment)
        bug.updated_at = datetime.utcnow()
        bug.save()
        
        # Invalidate related caches
        cache.delete(f'bugtracker_bug_{bug_id}')
        cache.delete('bugtracker_bugs_list')
        
        return jsonify({
            'message': 'Comment added successfully',
            'comment': {
                'content': comment.content,
                'author': {
                    'id': str(comment.author.id),
                    'username': comment.author.username
                },
                'created_at': comment.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        return jsonify({'message': 'Failed to add comment', 'error': str(e)}), 500

@bug_bp.route('/stats', methods=['GET'])
@jwt_required()
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_bug_stats():
    try:
        # Get status counts
        status_counts = {
            'open': Bug.objects(status='open').count(),
            'inProgress': Bug.objects(status='in_progress').count(),
            'resolved': Bug.objects(status='resolved').count(),
            'closed': Bug.objects(status='closed').count()
        }
        
        # Get priority counts
        priority_counts = {
            'low': Bug.objects(priority='low').count(),
            'medium': Bug.objects(priority='medium').count(),
            'high': Bug.objects(priority='high').count(),
            'critical': Bug.objects(priority='critical').count()
        }
        
        total_bugs = Bug.objects.count()
        
        return jsonify({
            'totalBugs': total_bugs,
            'statusCounts': status_counts,
            'priorityCounts': priority_counts
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get stats', 'error': str(e)}), 500
