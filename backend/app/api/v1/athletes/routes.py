from flask import Blueprint, request, jsonify
from app.models import AthleteProgram, WorkoutExercise, PerformanceLog
from app.utils.auth import athlete_required, get_current_user
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

athlete_bp = Blueprint('athletes', __name__)

@athlete_bp.route('/programs', methods=['GET'])
@athlete_required
def get_assigned_programs():
    """Get all programs assigned to the athlete."""
    try:
        programs = get_current_user().get_assigned_programs()
        return jsonify({
            'programs': [program.to_dict(include_workouts=True) 
                        for program in programs]
        }), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@athlete_bp.route('/programs/active', methods=['GET'])
@athlete_required
def get_active_program():
    """Get the athlete's currently active program."""
    try:
        program = get_current_user().get_active_program()
        if not program:
            return jsonify({'message': 'No active program found'}), 404
        
        return jsonify(program.to_dict(include_workouts=True)), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@athlete_bp.route('/programs/<int:program_id>/workouts/today', methods=['GET'])
@athlete_required
def get_todays_workout(program_id):
    """Get today's workout from the program."""
    try:
        assignment = AthleteProgram.query.filter_by(
            athlete_id=get_current_user().id,
            program_id=program_id,
            is_active=True
        ).first_or_404()
        
        workout = assignment.get_workout_for_date(datetime.utcnow().date())
        if not workout:
            return jsonify({'message': 'No workout scheduled for today'}), 404
        
        return jsonify(workout.to_dict(include_exercises=True)), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@athlete_bp.route('/exercises/<int:exercise_id>/log', methods=['POST'])
@athlete_required
def log_performance(exercise_id):
    """Log performance for a workout exercise."""
    workout_exercise = WorkoutExercise.query.get_or_404(exercise_id)
    
    # Verify the exercise belongs to the athlete's program
    assignment = AthleteProgram.query.filter_by(
        athlete_id=get_current_user().id,
        program_id=workout_exercise.workout.program_id,
        is_active=True
    ).first()
    
    if not assignment:
        return jsonify({'error': 'Not authorized to log performance for this exercise'}), 403
    
    data = request.get_json()
    required_fields = ['set_number', 'weight', 'reps']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        log = PerformanceLog(
            athlete_id=get_current_user().id,
            workout_exercise_id=exercise_id,
            set_number=data['set_number'],
            weight=data['weight'],
            reps=data['reps'],
            rpe=data.get('rpe'),
            notes=data.get('notes')
        )
        log.save()
        
        return jsonify({
            'message': 'Performance logged successfully',
            'log': log.to_dict()
        }), 201
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@athlete_bp.route('/exercises/<int:exercise_id>/logs', methods=['GET'])
@athlete_required
def get_performance_logs(exercise_id):
    """Get performance logs for a specific exercise."""
    try:
        logs = PerformanceLog.query.filter_by(
            athlete_id=get_current_user().id,
            workout_exercise_id=exercise_id
        ).order_by(PerformanceLog.created_at.desc()).all()
        
        return jsonify({
            'logs': [log.to_dict() for log in logs]
        }), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@athlete_bp.route('/progress', methods=['GET'])
@athlete_required
def get_progress():
    """Get the athlete's progress over time for all exercises."""
    try:
        # Get all performance logs grouped by exercise
        logs = PerformanceLog.query.filter_by(
            athlete_id=get_current_user().id
        ).order_by(
            PerformanceLog.workout_exercise_id,
            PerformanceLog.created_at
        ).all()
        
        # Group logs by exercise
        exercise_progress = {}
        for log in logs:
            exercise_id = log.workout_exercise.exercise_id
            if exercise_id not in exercise_progress:
                exercise_progress[exercise_id] = []
            exercise_progress[exercise_id].append(log.to_dict())
        
        return jsonify({
            'progress': exercise_progress
        }), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500
