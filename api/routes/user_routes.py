from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models_mongo import User
from werkzeug.security import generate_password_hash

user_bp = Blueprint('users', __name__)

@user_bp.route('', methods=['GET'])
@jwt_required()
def get_users():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        search = request.args.get('search', '')
        
        # Build query
        query = {}
        if search:
            query['$or'] = [
                {'username': {'$regex': search, '$options': 'i'}},
                {'email': {'$regex': search, '$options': 'i'}}
            ]
        
        # Execute query with pagination
        users = User.objects(**query).order_by('username').paginate(
            page=page, per_page=per_page
        )
        
        # Format response
        users_data = []
        for user in users.items:
            users_data.append({
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
        
        return jsonify({
            'users': users_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': users.total,
                'pages': users.pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch users', 'error': str(e)}), 500

@user_bp.route('/<user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    try:
        user = User.objects(id=user_id).first()
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        user_data = {
            'id': str(user.id),
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'created_at': user.created_at.isoformat() if user.created_at else None
        }
        
        return jsonify(user_data), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch user', 'error': str(e)}), 500

@user_bp.route('/<user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = User.objects(id=current_user_id).first()
        
        if not current_user:
            return jsonify({'message': 'Current user not found'}), 404
        
        # Check if user is updating their own profile or is admin
        if str(current_user.id) != user_id and current_user.role != 'admin':
            return jsonify({'message': 'Permission denied'}), 403
        
        user = User.objects(id=user_id).first()
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'username' in data and data['username'] != user.username:
            # Check if username is already taken
            existing_user = User.objects(username=data['username']).first()
            if existing_user:
                return jsonify({'message': 'Username already exists'}), 400
            user.username = data['username']
        
        if 'email' in data and data['email'] != user.email:
            # Check if email is already taken
            existing_user = User.objects(email=data['email']).first()
            if existing_user:
                return jsonify({'message': 'Email already exists'}), 400
            user.email = data['email']
        
        # Only admin can change roles
        if 'role' in data and current_user.role == 'admin':
            user.role = data['role']
        
        # Handle password change
        if 'password' in data and data['password']:
            if len(data['password']) < 6:
                return jsonify({'message': 'Password must be at least 6 characters'}), 400
            user.password_hash = generate_password_hash(data['password'])
        
        user.save()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to update user', 'error': str(e)}), 500

@user_bp.route('/<user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = User.objects(id=current_user_id).first()
        
        if not current_user or current_user.role != 'admin':
            return jsonify({'message': 'Admin access required'}), 403
        
        user = User.objects(id=user_id).first()
        
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        # Prevent admin from deleting themselves
        if str(current_user.id) == user_id:
            return jsonify({'message': 'Cannot delete your own account'}), 400
        
        user.delete()
        
        return jsonify({'message': 'User deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to delete user', 'error': str(e)}), 500

@user_bp.route('/assignees', methods=['GET'])
@jwt_required()
def get_assignees():
    """Get list of users that can be assigned to bugs"""
    try:
        users = User.objects().only('id', 'username').order_by('username')
        
        assignees = []
        for user in users:
            assignees.append({
                'id': str(user.id),
                'username': user.username
            })
        
        return jsonify({'assignees': assignees}), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to fetch assignees', 'error': str(e)}), 500
