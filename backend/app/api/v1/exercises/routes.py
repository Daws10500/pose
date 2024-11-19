from flask import Blueprint, request, jsonify
from app.models import Exercise
from app.database import db
from app.utils.auth import jwt_required, coach_required
from sqlalchemy.exc import SQLAlchemyError

exercises_bp = Blueprint('exercises', __name__)

@exercises_bp.route('', methods=['GET', 'OPTIONS'])
@jwt_required
def get_exercises():
    """Get all exercises."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    try:
        exercises = Exercise.query.all()
        return jsonify({
            'exercises': [exercise.to_dict() for exercise in exercises]
        }), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@exercises_bp.route('/<int:exercise_id>', methods=['GET', 'OPTIONS'])
@jwt_required
def get_exercise(exercise_id):
    """Get a specific exercise."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    try:
        exercise = Exercise.query.get_or_404(exercise_id)
        return jsonify(exercise.to_dict()), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@exercises_bp.route('', methods=['POST', 'OPTIONS'])
@coach_required
def create_exercise():
    """Create a new exercise."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    data = request.get_json()
    required_fields = ['name', 'type']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        exercise = Exercise(
            name=data['name'],
            type=data['type'],
            description=data.get('description'),
            video_url=data.get('video_url')
        )
        exercise.save()
        
        return jsonify({
            'message': 'Exercise created successfully',
            'exercise': exercise.to_dict()
        }), 201
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@exercises_bp.route('/<int:exercise_id>', methods=['PUT', 'OPTIONS'])
@coach_required
def update_exercise(exercise_id):
    """Update an exercise."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    exercise = Exercise.query.get_or_404(exercise_id)
    data = request.get_json()
    
    try:
        # Update fields if provided
        if 'name' in data:
            exercise.name = data['name']
        if 'type' in data:
            exercise.type = data['type']
        if 'description' in data:
            exercise.description = data['description']
        if 'video_url' in data:
            exercise.video_url = data['video_url']
        if 'equipment' in data:
            exercise.equipment = data['equipment']
        if 'muscles_worked' in data:
            exercise.muscles_worked = data['muscles_worked']
        
        exercise.save()
        return jsonify({
            'message': 'Exercise updated successfully',
            'exercise': exercise.to_dict()
        }), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@exercises_bp.route('/search', methods=['GET', 'OPTIONS'])
@jwt_required
def search_exercises():
    """Search exercises by name, type, or muscles worked."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    query = request.args.get('q', '').lower()
    type = request.args.get('type')
    muscle = request.args.get('muscle')
    
    try:
        exercises = Exercise.query
        
        if query:
            exercises = exercises.filter(Exercise.name.ilike(f'%{query}%'))
        if type:
            exercises = exercises.filter(Exercise.type == type)
        if muscle:
            exercises = exercises.filter(Exercise.muscles_worked.contains(muscle))
        
        results = exercises.all()
        return jsonify({
            'exercises': [exercise.to_dict() for exercise in results]
        }), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500
