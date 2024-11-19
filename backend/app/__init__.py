from flask import Flask, request, jsonify
from celery import Celery
from flask_cors import CORS
from config import Config
from app.database import db, migrate
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

celery = Celery(__name__)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize Celery
    celery.conf.update(app.config)

    # Configure CORS globally
    CORS(app, 
        origins=["http://localhost:3000"],
        allow_headers=["Content-Type", "Authorization"],
        expose_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        supports_credentials=True,
        max_age=3600
    )

    # Register error handler for CORS preflight
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,PATCH,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Max-Age', '3600')
        return response

    # Register blueprints
    from app.api.v1.auth.routes import auth_bp
    from app.api.v1.exercises.routes import exercises_bp
    from app.api.v1.workouts.routes import workouts_bp
    from app.api.v1.users.routes import users_bp
    from app.api.v1.health.routes import health_bp
    from app.api.v1.performance.routes import performance_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(exercises_bp, url_prefix='/api/v1/exercises')
    app.register_blueprint(workouts_bp, url_prefix='/api/v1/workouts')
    app.register_blueprint(users_bp, url_prefix='/api/v1/users')
    app.register_blueprint(health_bp, url_prefix='/api/v1/health')
    app.register_blueprint(performance_bp, url_prefix='/api/v1/performance')

    return app
