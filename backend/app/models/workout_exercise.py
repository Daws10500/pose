from app import db
from .base import BaseModel

class WorkoutExercise(BaseModel):
    """Junction model between workouts and exercises with additional metadata."""
    
    __tablename__ = 'workout_exercises'

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer)
    weight = db.Column(db.Float)  # in lbs/kg
    set_type = db.Column(db.Enum('warmup', 'working', 'dropset', 'failure', 
                                name='set_type'), default='working')
    rest_time = db.Column(db.Integer)  # in seconds
    notes = db.Column(db.Text)
    order_index = db.Column(db.Integer, nullable=True, default=0)

    # Relationships
    performance_logs = db.relationship('PerformanceLog', backref='workout_exercise', 
                                     lazy='dynamic', cascade='all, delete-orphan')
    exercise = db.relationship('Exercise', lazy='joined')

    def log_performance(self, athlete_id, set_number, weight=None, reps=None, 
                       rpe=None, video_url=None, notes=None):
        """Log performance for this exercise."""
        from .performance_log import PerformanceLog
        log = PerformanceLog(
            athlete_id=athlete_id,
            workout_exercise_id=self.id,
            set_number=set_number,
            weight=weight,
            reps=reps,
            rpe=rpe,
            video_url=video_url,
            notes=notes
        )
        log.save()
        return log

    def get_athlete_performance(self, athlete_id):
        """Get all performance logs for this exercise by a specific athlete."""
        return self.performance_logs.filter_by(athlete_id=athlete_id).order_by(
            PerformanceLog.logged_at.desc()
        ).all()

    def to_dict(self, include_exercise=True, include_performance=False, athlete_id=None):
        """Convert workout exercise instance to dictionary."""
        data = {
            'id': self.id,
            'workout_id': self.workout_id,
            'exercise_id': self.exercise_id,
            'sets': self.sets,
            'reps': self.reps,
            'weight': self.weight,
            'set_type': self.set_type,
            'rest_time': self.rest_time,
            'notes': self.notes,
            'order_index': self.order_index,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_exercise:
            data['exercise'] = self.exercise.to_dict()
            
        if include_performance and athlete_id:
            data['performance_logs'] = [
                log.to_dict() for log in self.get_athlete_performance(athlete_id)
            ]
            
        return data
