from datetime import datetime
from app import db
from .base import BaseModel
import logging
import mediapipe as mp

logger = logging.getLogger(__name__)

def calculate_angle(a, b, c):
    # Calculate angle between three points
    a = [a['x'], a['y']]
    b = [b['x'], b['y']]
    c = [c['x'], c['y']]
    
    ba = [a[0] - b[0], a[1] - b[1]]
    bc = [c[0] - b[0], c[1] - b[1]]
    
    cosine_angle = (ba[0] * bc[0] + ba[1] * bc[1]) / (abs(ba[0]) * abs(bc[0]) + abs(ba[1]) * abs(bc[1]))
    angle = cosine_angle * 180 / 3.14159265
    
    return angle

class FormAnalysis(db.Model):
    """Model for storing exercise form analysis results."""
    __tablename__ = 'form_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    performance_log_id = db.Column(db.Integer, db.ForeignKey('performance_logs.id'), nullable=False)
    athlete_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    video_url = db.Column(db.String(255))
    pose_data = db.Column(db.JSON)  # Store pose data as JSON
    form_score = db.Column(db.Float)
    feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    athlete = db.relationship('User', backref=db.backref('form_analyses', lazy=True))
    exercise = db.relationship('Exercise', backref=db.backref('form_analyses', lazy=True))
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'performance_log_id': self.performance_log_id,
            'athlete_id': self.athlete_id,
            'exercise_id': self.exercise_id,
            'video_url': self.video_url,
            'pose_data': self.pose_data,
            'form_score': self.form_score,
            'feedback': self.feedback,
            'created_at': self.created_at.isoformat()
        }
    
    def analyze_form(self):
        """Analyze form using pose data."""
        if not self.pose_data:
            return
            
        # Get exercise-specific form criteria
        exercise = Exercise.query.get(self.exercise_id)
        if not exercise:
            return
            
        # Initialize scoring variables
        total_score = 0
        frame_count = len(self.pose_data)
        
        for frame_data in self.pose_data:
            frame_score = self._analyze_frame(frame_data, exercise)
            total_score += frame_score
            
        # Calculate average score
        if frame_count > 0:
            self.form_score = total_score / frame_count
            
        # Generate feedback based on analysis
        self.feedback = self._generate_feedback(exercise)
        
    def _analyze_frame(self, frame_data, exercise):
        """Analyze a single frame of pose data."""
        score = 1.0  # Start with perfect score
        
        # Get key joint positions
        try:
            hip = frame_data[mp.solutions.pose.PoseLandmark.LEFT_HIP.value]
            knee = frame_data[mp.solutions.pose.PoseLandmark.LEFT_KNEE.value]
            ankle = frame_data[mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value]
            
            # Calculate joint angles
            knee_angle = calculate_angle(hip, knee, ankle)
            
            # Apply exercise-specific criteria
            if exercise.name.lower() == 'squat':
                # Check knee angle for proper squat depth
                if knee_angle < 90:  # Too deep
                    score *= 0.8
                elif knee_angle > 120:  # Not deep enough
                    score *= 0.7
                    
                # Check if knees are aligned with toes
                knee_x = knee['x']
                ankle_x = ankle['x']
                if abs(knee_x - ankle_x) > 0.1:  # Knees caving in/out
                    score *= 0.8
                    
            # Add more exercise-specific checks here
            
        except (KeyError, IndexError) as e:
            logger.error(f"Error analyzing frame: {str(e)}")
            return 0.5  # Return middle score for failed analysis
            
        return score
        
    def _generate_feedback(self, exercise):
        """Generate feedback based on form analysis."""
        feedback = []
        
        if not self.form_score:
            return "Unable to analyze form. Please ensure proper video quality and visibility."
            
        if self.form_score >= 0.9:
            feedback.append("Excellent form! Keep up the great work.")
        elif self.form_score >= 0.7:
            feedback.append("Good form with some room for improvement.")
        else:
            feedback.append("Form needs significant improvement. Consider reducing weight and focusing on technique.")
            
        # Add exercise-specific feedback
        if exercise.name.lower() == 'squat':
            avg_knee_angle = self._calculate_average_knee_angle()
            if avg_knee_angle > 120:
                feedback.append("Try to squat deeper - aim for parallel or slightly below.")
            elif avg_knee_angle < 90:
                feedback.append("You're squatting too deep - try to stop at parallel.")
                
        return "\n".join(feedback)
        
    def _calculate_average_knee_angle(self):
        """Calculate average knee angle across all frames."""
        if not self.pose_data:
            return None
            
        total_angle = 0
        valid_frames = 0
        
        for frame_data in self.pose_data:
            try:
                hip = frame_data[mp.solutions.pose.PoseLandmark.LEFT_HIP.value]
                knee = frame_data[mp.solutions.pose.PoseLandmark.LEFT_KNEE.value]
                ankle = frame_data[mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value]
                
                angle = calculate_angle(hip, knee, ankle)
                total_angle += angle
                valid_frames += 1
                
            except (KeyError, IndexError):
                continue
                
        return total_angle / valid_frames if valid_frames > 0 else None
