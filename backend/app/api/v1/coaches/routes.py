from flask import Blueprint, request, jsonify
from app.models import Program, User, Workout, Exercise, WorkoutExercise
from app.utils.auth import coach_required, get_current_user
from sqlalchemy.exc import SQLAlchemyError

coach_bp = Blueprint('coaches', __name__)

@coach_bp.route('/programs', methods=['POST'])
@coach_required
def create_program():
    """Create a new workout program."""
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Program name is required'}), 400
    
    program = Program(
        coach_id=get_current_user().id,
        name=data['name'],
        description=data.get('description')
    )
    
    try:
        program.save()
        return jsonify({
            'message': 'Program created successfully',
            'program': program.to_dict()
        }), 201
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@coach_bp.route('/programs', methods=['GET'])
@coach_required
def get_programs():
    """Get all programs created by the coach."""
    try:
        programs = get_current_user().get_coached_programs()
        return jsonify({
            'programs': [program.to_dict(include_workouts=True) 
                        for program in programs]
        }), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@coach_bp.route('/programs/<int:program_id>', methods=['GET'])
@coach_required
def get_program(program_id):
    """Get a specific program's details."""
    program = Program.query.get_or_404(program_id)
    
    if program.coach_id != get_current_user().id:
        return jsonify({'error': 'Not authorized to view this program'}), 403
    
    return jsonify(program.to_dict(include_workouts=True)), 200

@coach_bp.route('/programs/<int:program_id>', methods=['PUT'])
@coach_required
def update_program(program_id):
    """Update a program's details."""
    program = Program.query.get_or_404(program_id)
    
    if program.coach_id != get_current_user().id:
        return jsonify({'error': 'Not authorized to modify this program'}), 403
    
    data = request.get_json()
    if 'name' in data:
        program.name = data['name']
    if 'description' in data:
        program.description = data['description']
    
    try:
        program.save()
        return jsonify({
            'message': 'Program updated successfully',
            'program': program.to_dict(include_workouts=True)
        }), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@coach_bp.route('/programs/<int:program_id>/workouts', methods=['POST'])
@coach_required
def add_workout(program_id):
    """Add a workout to a program."""
    program = Program.query.get_or_404(program_id)
    
    if program.coach_id != get_current_user().id:
        return jsonify({'error': 'Not authorized to modify this program'}), 403
    
    data = request.get_json()
    required_fields = ['name', 'day_number']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        workout = program.add_workout(
            name=data['name'],
            day_number=data['day_number'],
            notes=data.get('notes')
        )
        return jsonify({
            'message': 'Workout added successfully',
            'workout': workout.to_dict(include_exercises=True)
        }), 201
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@coach_bp.route('/workouts/<int:workout_id>/exercises', methods=['POST'])
@coach_required
def add_exercise_to_workout(workout_id):
    """Add an exercise to a workout."""
    workout = Workout.query.get_or_404(workout_id)
    
    if workout.program.coach_id != get_current_user().id:
        return jsonify({'error': 'Not authorized to modify this workout'}), 403
    
    data = request.get_json()
    required_fields = ['exercise_id', 'sets']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        exercise = workout.add_exercise(
            exercise_id=data['exercise_id'],
            sets=data['sets'],
            reps=data.get('reps'),
            set_type=data.get('set_type', 'working'),
            rest_time=data.get('rest_time'),
            notes=data.get('notes')
        )
        return jsonify({
            'message': 'Exercise added successfully',
            'exercise': exercise.to_dict(include_exercise=True)
        }), 201
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@coach_bp.route('/programs/<int:program_id>/assign', methods=['POST'])
@coach_required
def assign_program(program_id):
    """Assign a program to an athlete."""
    program = Program.query.get_or_404(program_id)
    
    if program.coach_id != get_current_user().id:
        return jsonify({'error': 'Not authorized to assign this program'}), 403
    
    data = request.get_json()
    required_fields = ['athlete_id', 'start_date']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    athlete = User.query.get_or_404(data['athlete_id'])
    if athlete.role != 'athlete':
        return jsonify({'error': 'User is not an athlete'}), 400
    
    try:
        assignment = program.assign_to_athlete(
            athlete_id=athlete.id,
            start_date=data['start_date'],
            end_date=data.get('end_date')
        )
        return jsonify({
            'message': 'Program assigned successfully',
            'assignment': assignment.to_dict(include_program=True)
        }), 201
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500
