from flask import Blueprint, request, jsonify
from app.models import User
from app.database import db
from app.utils.auth import jwt_required, coach_required
from sqlalchemy.exc import SQLAlchemyError

users_bp = Blueprint('users', __name__)

@users_bp.route('', methods=['GET'])
@jwt_required
def get_users():
    """Get all users."""
    try:
        users = User.query.all()
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required
def get_user(user_id):
    """Get a specific user."""
    try:
        user = User.query.get_or_404(user_id)
        return jsonify(user.to_dict()), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/me', methods=['GET'])
@jwt_required
def get_current_user():
    """Get the current user's profile."""
    try:
        # The current user is already attached to the request by the jwt_required decorator
        return jsonify(request.user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/me', methods=['PUT'])
@jwt_required
def update_current_user():
    """Update the current user's profile."""
    try:
        data = request.get_json()
        user = request.user
        
        # Update allowed fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'email' in data:
            user.email = data['email']
            
        user.save()
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
