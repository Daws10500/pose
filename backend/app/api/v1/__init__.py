from flask import Blueprint, jsonify
from .auth.routes import auth_bp
from .workouts.routes import workouts_bp
from .exercises.routes import exercises_bp
from .performance.routes import performance_bp

api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

@api_v1.route('/test', methods=['GET', 'OPTIONS'])
def test():
    """Test endpoint to verify API connectivity."""
    return jsonify({'status': 'ok', 'message': 'API is running'}), 200

api_v1.register_blueprint(auth_bp, url_prefix='/auth')
api_v1.register_blueprint(workouts_bp, url_prefix='/workouts')
api_v1.register_blueprint(exercises_bp, url_prefix='/exercises')
api_v1.register_blueprint(performance_bp, url_prefix='/performance')
