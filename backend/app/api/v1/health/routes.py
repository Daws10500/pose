from flask import Blueprint, jsonify
from app.database import db
from redis import Redis
import os

health_bp = Blueprint('health', __name__)

@health_bp.route('', methods=['GET'])
def health_check():
    """Check the health of all system components."""
    health_status = {
        'status': 'healthy',
        'components': {
            'api': {'status': 'healthy'},
            'database': {'status': 'unknown'},
            'redis': {'status': 'unknown'}
        }
    }
    
    # Check database connection
    try:
        db.session.execute('SELECT 1')
        health_status['components']['database'] = {
            'status': 'healthy',
            'message': 'Connected to TimescaleDB'
        }
    except Exception as e:
        health_status['components']['database'] = {
            'status': 'unhealthy',
            'message': str(e)
        }
        health_status['status'] = 'degraded'
    
    # Check Redis connection
    try:
        redis_client = Redis(
            host='localhost',
            port=6380,
            socket_timeout=2
        )
        redis_client.ping()
        health_status['components']['redis'] = {
            'status': 'healthy',
            'message': 'Connected to Redis'
        }
    except Exception as e:
        health_status['components']['redis'] = {
            'status': 'unhealthy',
            'message': str(e)
        }
        health_status['status'] = 'degraded'
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code
