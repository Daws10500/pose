from flask import Blueprint, request, jsonify, current_app
from app.models import User
from app.database import db
from app.utils.auth import create_access_token, jwt_required, get_current_user
from werkzeug.security import check_password_hash
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    """Authenticate a user and return a token."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    try:
        data = request.get_json()
        logger.debug('Login attempt for email: %s', data.get('email'))
        
        # Validate required fields
        if not data or 'email' not in data or 'password' not in data:
            logger.error('Missing email or password in login request')
            return jsonify({'error': 'Email and password are required'}), 400
            
        # Check user credentials
        user = User.query.filter_by(email=data['email']).first()
        if not user or not check_password_hash(user.password_hash, data['password']):
            logger.error('Invalid email or password for login attempt')
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate access token
        token = create_access_token(user.id)
        
        response = jsonify({
            'token': token,
            'user': user.to_dict()
        })
        
        return response, 200
        
    except Exception as e:
        logger.error('Login error: %s', str(e))
        return jsonify({'error': 'An error occurred during login'}), 500

@auth_bp.route('/me', methods=['GET', 'OPTIONS'])
@jwt_required
def get_current_user_info():
    """Get the current user's information."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    try:
        current_user = get_current_user()
        return jsonify(current_user.to_dict()), 200
    except Exception as e:
        logger.error('Error getting current user: %s', str(e))
        return jsonify({'error': 'Error getting current user'}), 500

@auth_bp.route('/register', methods=['POST', 'OPTIONS'])
def register():
    """Register a new user (coach or athlete)."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    try:
        data = request.get_json()
        logger.debug('Registration data received: %s', data)
        
        # Validate required fields
        if not data or 'email' not in data or 'password' not in data or 'role' not in data:
            return jsonify({'error': 'Email, password, and role are required'}), 400
            
        # Check if email already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
            
        # Create new user
        user = User(
            email=data['email'],
            role=data['role']
        )
        user.password = data['password']  # Using the password property instead of set_password
        
        # Add user to database
        db.session.add(user)
        db.session.commit()
        
        logger.info('New user registered: %s', user.email)
        
        # Generate access token for immediate login
        token = create_access_token(user.id)
        
        return jsonify({
            'message': 'Registration successful',
            'token': token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        logger.error('Registration error: %s', str(e), exc_info=True)
        return jsonify({'error': f'Registration error: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['GET', 'OPTIONS'])
@jwt_required
def get_profile():
    """Get the current user's profile."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    current_user = get_current_user()
    return jsonify(current_user.to_dict()), 200

@auth_bp.route('/profile', methods=['PUT', 'OPTIONS'])
@jwt_required
def update_profile():
    """Update the current user's profile."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    current_user = get_current_user()
    data = request.get_json()
    
    allowed_fields = ['first_name', 'last_name', 'email']
    
    try:
        for field in allowed_fields:
            if field in data:
                setattr(current_user, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': current_user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
