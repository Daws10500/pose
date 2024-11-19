from flask import Blueprint, request, jsonify, current_app
from app.models import Exercise, WorkoutExercise, FormAnalysis
from app.utils.auth import jwt_required, get_current_user
from app.utils.video import process_video_form, save_uploaded_video
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename
import os
from celery import chain

video_bp = Blueprint('videos', __name__)

@video_bp.route('/upload', methods=['POST'])
@jwt_required
def upload_video():
    """Upload a video for form analysis."""
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    video_file = request.files['video']
    if not video_file.filename:
        return jsonify({'error': 'No video file selected'}), 400
    
    # Validate exercise_id
    exercise_id = request.form.get('exercise_id')
    if not exercise_id:
        return jsonify({'error': 'exercise_id is required'}), 400
    
    try:
        exercise = Exercise.query.get_or_404(exercise_id)
        
        # Save video file
        filename = secure_filename(video_file.filename)
        video_path = save_uploaded_video(video_file, filename)
        
        # Create form analysis record
        analysis = FormAnalysis(
            user_id=get_current_user().id,
            exercise_id=exercise.id,
            video_path=video_path,
            status='processing'
        )
        analysis.save()
        
        # Queue video processing task
        process_video_form.delay(analysis.id)
        
        return jsonify({
            'message': 'Video uploaded successfully and queued for processing',
            'analysis_id': analysis.id
        }), 202
        
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@video_bp.route('/analysis/<int:analysis_id>', methods=['GET'])
@jwt_required
def get_analysis(analysis_id):
    """Get the results of a form analysis."""
    try:
        analysis = FormAnalysis.query.get_or_404(analysis_id)
        
        # Check if user has access to this analysis
        if analysis.user_id != get_current_user().id:
            return jsonify({'error': 'Not authorized to view this analysis'}), 403
        
        return jsonify(analysis.to_dict()), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@video_bp.route('/exercises/<int:exercise_id>/analyses', methods=['GET'])
@jwt_required
def get_exercise_analyses(exercise_id):
    """Get all form analyses for a specific exercise."""
    try:
        analyses = FormAnalysis.query.filter_by(
            user_id=get_current_user().id,
            exercise_id=exercise_id
        ).order_by(FormAnalysis.created_at.desc()).all()
        
        return jsonify({
            'analyses': [analysis.to_dict() for analysis in analyses]
        }), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@video_bp.route('/analysis/<int:analysis_id>/feedback', methods=['POST'])
@jwt_required
def add_feedback(analysis_id):
    """Add coach feedback to a form analysis."""
    analysis = FormAnalysis.query.get_or_404(analysis_id)
    
    # Only coaches can add feedback
    if get_current_user().role != 'coach':
        return jsonify({'error': 'Only coaches can add feedback'}), 403
    
    data = request.get_json()
    if not data or 'feedback' not in data:
        return jsonify({'error': 'Feedback is required'}), 400
    
    try:
        analysis.coach_feedback = data['feedback']
        analysis.coach_id = get_current_user().id
        analysis.save()
        
        return jsonify({
            'message': 'Feedback added successfully',
            'analysis': analysis.to_dict()
        }), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500
