from app import db
from .base import BaseModel
from datetime import datetime

class PerformanceLog(BaseModel):
    """Model for tracking athlete performance on exercises."""
    
    __tablename__ = 'performance_logs'

    id = db.Column(db.Integer, primary_key=True)
    athlete_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    workout_exercise_id = db.Column(db.Integer, db.ForeignKey('workout_exercises.id'), nullable=False)
    set_number = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Numeric(10, 2))
    reps = db.Column(db.Integer)
    rpe = db.Column(db.Numeric(3, 1))
    video_url = db.Column(db.String(255))
    notes = db.Column(db.Text)
    logged_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    pose_data = db.Column(db.JSON)  # Store pose data as JSON
    form_score = db.Column(db.Float)

    # Relationships
    form_analyses = db.relationship('FormAnalysis', back_populates='performance_log', cascade='all, delete-orphan')

    @classmethod
    def get_athlete_history(cls, athlete_id, exercise_id=None, days=30):
        """Get performance history for an athlete.
        
        Args:
            athlete_id (int): ID of the athlete
            exercise_id (int, optional): Filter by specific exercise
            days (int, optional): Number of days to look back
        """
        from datetime import datetime, timedelta
        from .workout_exercise import WorkoutExercise
        
        query = cls.query.join(
            WorkoutExercise
        ).filter(
            cls.athlete_id == athlete_id,
            cls.logged_at >= datetime.utcnow() - timedelta(days=days)
        )
        
        if exercise_id:
            query = query.filter(WorkoutExercise.exercise_id == exercise_id)
            
        return query.order_by(cls.logged_at.desc()).all()

    @classmethod
    def get_exercise_stats(cls, athlete_id, exercise_id):
        """Get statistics for a specific exercise.
        
        Returns:
            dict: Contains max weight, max reps, average RPE, etc.
        """
        from .workout_exercise import WorkoutExercise
        from sqlalchemy import func
        
        stats = db.session.query(
            func.max(cls.weight).label('max_weight'),
            func.max(cls.reps).label('max_reps'),
            func.avg(cls.rpe).label('avg_rpe'),
            func.count(cls.id).label('total_sets')
        ).join(
            WorkoutExercise
        ).filter(
            cls.athlete_id == athlete_id,
            WorkoutExercise.exercise_id == exercise_id
        ).first()
        
        return {
            'max_weight': float(stats.max_weight) if stats.max_weight else 0,
            'max_reps': stats.max_reps or 0,
            'avg_rpe': float(stats.avg_rpe) if stats.avg_rpe else 0,
            'total_sets': stats.total_sets
        }

    def calculate_volume(self):
        """Calculate volume (weight * reps) for this set."""
        return float(self.weight) * self.reps if self.weight and self.reps else 0

    def calculate_intensity(self, one_rep_max):
        """Calculate intensity percentage based on one rep max."""
        return (float(self.weight) / one_rep_max * 100) if self.weight and one_rep_max else 0

    def to_dict(self, include_exercise=False):
        """Convert performance log instance to dictionary."""
        data = super().to_dict()
        data['volume'] = self.calculate_volume()
        data['pose_data'] = self.pose_data
        data['form_score'] = self.form_score
        
        if include_exercise:
            data['exercise'] = self.workout_exercise.exercise.to_dict()
            
        return data
