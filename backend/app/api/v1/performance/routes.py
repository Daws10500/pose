from flask import jsonify, request
from app.models.performance_log import PerformanceLog
from app.models.workout_exercise import WorkoutExercise
from app.utils.auth import login_required, get_current_user
from . import performance_bp

@performance_bp.route('/', methods=['GET'])
@login_required
def get_performance_logs():
    """Get performance logs for the current user."""
    user = get_current_user()
    logs = PerformanceLog.query.filter_by(athlete_id=user.id).order_by(
        PerformanceLog.logged_at.desc()
    ).all()
    return jsonify([log.to_dict() for log in logs]), 200

@performance_bp.route('/exercise/<int:exercise_id>', methods=['GET'])
@login_required
def get_exercise_performance(exercise_id):
    """Get performance logs for a specific exercise."""
    user = get_current_user()
    logs = PerformanceLog.query.join(
        WorkoutExercise
    ).filter(
        PerformanceLog.athlete_id == user.id,
        WorkoutExercise.exercise_id == exercise_id
    ).order_by(
        PerformanceLog.logged_at.desc()
    ).all()
    return jsonify([log.to_dict() for log in logs]), 200

@performance_bp.route('/workout/<int:workout_id>', methods=['GET'])
@login_required
def get_workout_performance(workout_id):
    """Get performance logs for a specific workout."""
    user = get_current_user()
    logs = PerformanceLog.query.join(
        WorkoutExercise
    ).filter(
        PerformanceLog.athlete_id == user.id,
        WorkoutExercise.workout_id == workout_id
    ).order_by(
        PerformanceLog.logged_at.desc()
    ).all()
    return jsonify([log.to_dict() for log in logs]), 200
