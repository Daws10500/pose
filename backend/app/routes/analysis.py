from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from app import db
from app.models.form_analysis import FormAnalysis
import logging

logger = logging.getLogger(__name__)
analysis_bp = Blueprint('analysis', __name__)

UPLOAD_FOLDER = 'uploads/videos'
ALLOWED_EXTENSIONS = {'webm', 'mp4'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@analysis_bp.route('/upload', methods=['POST'])
def upload_video():
    """Handle video upload and store pose data."""
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
            
        video_file = request.files['video']
        if video_file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if not allowed_file(video_file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
            
        # Create upload directory if it doesn't exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Save video file
        filename = secure_filename(video_file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        video_file.save(filepath)
        
        # Return video URL
        video_url = f'/uploads/videos/{filename}'
        return jsonify({'videoUrl': video_url}), 200
        
    except Exception as e:
        logger.error(f"Error uploading video: {str(e)}")
        return jsonify({'error': 'Failed to upload video'}), 500

@analysis_bp.route('/form', methods=['POST'])
def analyze_form():
    """Analyze exercise form using pose data."""
    try:
        data = request.get_json()
        if not data or 'videoUrl' not in data:
            return jsonify({'error': 'No video URL provided'}), 400
            
        # Create form analysis record
        analysis = FormAnalysis(
            video_url=data['videoUrl'],
            pose_data=data.get('poseData', []),
            athlete_id=request.user_id,  # Assuming user authentication
            exercise_id=data.get('exerciseId'),
            performance_log_id=data.get('performanceLogId')
        )
        
        # Analyze form
        analysis.analyze_form()
        
        # Save to database
        db.session.add(analysis)
        db.session.commit()
        
        return jsonify({
            'score': analysis.form_score,
            'feedback': analysis.feedback
        }), 200
        
    except Exception as e:
        logger.error(f"Error analyzing form: {str(e)}")
        return jsonify({'error': 'Failed to analyze form'}), 500
