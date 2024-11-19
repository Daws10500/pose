from flask import Blueprint, request, jsonify
from app.models import Workout, Exercise, WorkoutExercise, PerformanceLog, FormAnalysis
from app.database import db
from app.utils.auth import jwt_required, coach_required
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

workouts_bp = Blueprint('workouts', __name__)

class WorkoutError(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code

@workouts_bp.errorhandler(WorkoutError)
def handle_workout_error(error):
    response = jsonify({'error': error.message})
    response.status_code = error.status_code
    return response

@workouts_bp.route('', methods=['GET', 'OPTIONS'])
@jwt_required
def get_workouts():
    """Get all workouts with optional filtering."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    try:
        # Get query parameters
        athlete_id = request.args.get('athlete_id', type=int)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        # Build query
        query = Workout.query
        
        if athlete_id:
            query = query.filter(Workout.athlete_id == athlete_id)
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d')
                query = query.filter(Workout.created_at >= date_from)
            except ValueError:
                raise WorkoutError('Invalid date_from format. Use YYYY-MM-DD')
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d')
                query = query.filter(Workout.created_at <= date_to)
            except ValueError:
                raise WorkoutError('Invalid date_to format. Use YYYY-MM-DD')
        
        workouts = query.all()
        return jsonify({
            'workouts': [workout.to_dict() for workout in workouts],
            'count': len(workouts)
        }), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_workouts: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        logger.error(f"Unexpected error in get_workouts: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@workouts_bp.route('/<int:workout_id>', methods=['GET', 'OPTIONS'])
@jwt_required
def get_workout(workout_id):
    """Get a specific workout with detailed exercise information."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    try:
        workout = Workout.query.get(workout_id)
        if not workout:
            raise WorkoutError(f'Workout with id {workout_id} not found', 404)
            
        return jsonify(workout.to_dict()), 200
    except WorkoutError as e:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_workout: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        logger.error(f"Unexpected error in get_workout: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@workouts_bp.route('/exercise/<int:exercise_id>', methods=['GET', 'OPTIONS'])
@jwt_required
def get_exercise_workouts(exercise_id):
    """Get workout history for a specific exercise."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    try:
        workouts = Workout.query.join(WorkoutExercise).filter(
            WorkoutExercise.exercise_id == exercise_id
        ).order_by(Workout.created_at.desc()).all()
        
        return jsonify({
            'workouts': [workout.to_dict() for workout in workouts],
            'count': len(workouts)
        }), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_exercise_workouts: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        logger.error(f"Unexpected error in get_exercise_workouts: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@workouts_bp.route('/exercise/<int:exercise_id>/records', methods=['GET', 'OPTIONS'])
@jwt_required
def get_exercise_records(exercise_id):
    """Get personal records for a specific exercise."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    try:
        # Get the exercise to ensure it exists
        exercise = Exercise.query.get(exercise_id)
        if not exercise:
            return jsonify({'error': f'Exercise with id {exercise_id} not found'}), 404

        # Get all workouts for this exercise
        workout_exercises = WorkoutExercise.query.filter_by(exercise_id=exercise_id).all()
        
        # Calculate records
        records = {
            'max_weight': max([we.weight for we in workout_exercises if we.weight is not None], default=0),
            'max_reps': max([we.reps for we in workout_exercises if we.reps is not None], default=0),
            'total_sets': len(workout_exercises)
        }
        
        return jsonify(records), 200
        
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_exercise_records: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        logger.error(f"Unexpected error in get_exercise_records: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@workouts_bp.route('/exercise/<int:exercise_id>/set', methods=['POST'])
@jwt_required
def log_exercise_set(exercise_id):
    """Log a set for an exercise with pose data."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    try:
        data = request.get_json()
        required_fields = ['weight', 'reps', 'rpe']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Create performance log
        log = PerformanceLog(
            athlete_id=get_current_user().id,
            exercise_id=exercise_id,
            weight=data['weight'],
            reps=data['reps'],
            rpe=data['rpe'],
            notes=data.get('notes'),
            video_url=data.get('videoUrl'),
            pose_data=data.get('poseData'),  # Store pose data
            form_score=data.get('formScore')
        )
        log.save()
        
        # If video and pose data are present, create form analysis
        if data.get('videoUrl') and data.get('poseData'):
            analysis = FormAnalysis(
                performance_log_id=log.id,
                athlete_id=get_current_user().id,
                exercise_id=exercise_id,
                video_url=data['videoUrl'],
                pose_data=data['poseData'],
                form_score=data.get('formScore', 0),
                feedback=generate_form_feedback(data['poseData'], exercise_id)
            )
            analysis.save()
            
        return jsonify({
            'message': 'Set logged successfully',
            'log': log.to_dict()
        }), 201
        
    except SQLAlchemyError as e:
        logger.error(f"Database error in log_exercise_set: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        logger.error(f"Unexpected error in log_exercise_set: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@workouts_bp.route('', methods=['POST', 'OPTIONS'])
@coach_required
def create_workout():
    """Create a new workout with exercises."""
    if request.method == 'OPTIONS':
        return jsonify({}), 200
        
    try:
        data = request.get_json()
        logger.info(f"Creating workout with data: {data}")
        
        # Validate required fields
        required_fields = ['name', 'exercises']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise WorkoutError(f"Missing required fields: {', '.join(missing_fields)}")
            
        # Validate exercises format
        if not isinstance(data['exercises'], list):
            raise WorkoutError("Exercises must be a list")
        if not data['exercises']:
            raise WorkoutError("At least one exercise is required")
            
        # Create workout
        workout = Workout(
            name=data['name'],
            description=data.get('description', ''),
            athlete_id=data.get('athlete_id'),
            coach_id=data.get('coach_id')
        )
        logger.info(f"Created workout object")
        db.session.add(workout)
        
        # Add exercises
        for i, ex_data in enumerate(data['exercises']):
            if not isinstance(ex_data, dict):
                raise WorkoutError("Each exercise must be an object")
            if 'exercise_id' not in ex_data:
                raise WorkoutError("exercise_id is required for each exercise")
                
            exercise = Exercise.query.get(ex_data['exercise_id'])
            if not exercise:
                raise WorkoutError(f"Exercise with id {ex_data['exercise_id']} not found")
                
            logger.info(f"Creating workout exercise with data: {ex_data}")
            workout_exercise = WorkoutExercise(
                workout_id=workout.id,
                exercise_id=exercise.id,
                sets=ex_data.get('sets', 3),
                reps=ex_data.get('reps', 10),
                weight=ex_data.get('weight', 0),
                rest_time=ex_data.get('rest_time', 60),
                notes=ex_data.get('notes', ''),
                order_index=i,  # Set order_index based on position in list
                pose_data=ex_data.get('poseData')  # Store pose data
            )
            logger.info(f"Created workout exercise object")
            db.session.add(workout_exercise)
        
        # Commit all changes at once
        db.session.commit()
        logger.info("Successfully committed workout and exercises")
        
        # Reload the workout to ensure all relationships are properly loaded
        workout = Workout.query.get(workout.id)
        return jsonify(workout.to_dict()), 201
        
    except WorkoutError as e:
        db.session.rollback()
        logger.error(f"Workout error: {str(e)}")
        raise
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Integrity error in create_workout: {str(e)}")
        return jsonify({'error': 'Database integrity error'}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in create_workout: {str(e)}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error in create_workout: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500
