from functools import wraps
from flask import request, jsonify, current_app, g
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.models import User

def create_access_token(user_id, expires_delta=None):
    """Create a new access token for a user."""
    if expires_delta is None:
        expires_delta = timedelta(days=1)  # Default to 1 day
        
    expire = datetime.utcnow() + expires_delta
    
    to_encode = {
        'exp': expire,
        'user_id': str(user_id)
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    
    return encoded_jwt

def decode_token(token):
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        return payload
    except JWTError:
        return None

def get_current_user():
    """Get the current authenticated user."""
    return g.current_user if hasattr(g, 'current_user') else None

def jwt_required(f):
    """Decorator to require JWT authentication for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip authentication for OPTIONS requests
        if request.method == 'OPTIONS':
            return current_app.make_default_options_response()

        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'Missing authorization header'}), 401
        
        try:
            # Extract token from "Bearer <token>"
            token_type, token = auth_header.split()
            if token_type.lower() != 'bearer':
                return jsonify({'error': 'Invalid token type'}), 401
        except ValueError:
            return jsonify({'error': 'Invalid authorization header'}), 401
        
        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        user = User.query.get(int(payload['user_id']))
        if not user:
            return jsonify({'error': 'User not found'}), 401
        
        # Store user in flask.g for the current request
        g.current_user = user
        
        return f(*args, **kwargs)
    
    return decorated_function

# Alias jwt_required as login_required for consistency
login_required = jwt_required

def coach_required(f):
    """Decorator to require coach role for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip authentication for OPTIONS requests
        if request.method == 'OPTIONS':
            return current_app.make_default_options_response()

        if not g.current_user or g.current_user.role != 'coach':
            return jsonify({'error': 'Coach access required'}), 403
        return f(*args, **kwargs)
    return jwt_required(decorated_function)

def athlete_required(f):
    """Decorator to require athlete role for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip authentication for OPTIONS requests
        if request.method == 'OPTIONS':
            return current_app.make_default_options_response()

        if not g.current_user or g.current_user.role != 'athlete':
            return jsonify({'error': 'Athlete access required'}), 403
        return f(*args, **kwargs)
    return jwt_required(decorated_function)
