from app import db
from .base import BaseModel

class Exercise(BaseModel):
    """Exercise model for individual exercises."""
    
    __tablename__ = 'exercises'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.Enum('strength', 'cardio', 'flexibility', 'other', 
                            name='exercise_type'), nullable=False)
    description = db.Column(db.Text)
    video_url = db.Column(db.String(255))

    # Relationships
    workout_exercises = db.relationship('WorkoutExercise', back_populates='exercise', lazy='dynamic',
                                      cascade='all, delete-orphan')
    form_analyses = db.relationship('FormAnalysis', back_populates='exercise', lazy='dynamic')

    @classmethod
    def get_by_type(cls, exercise_type):
        """Get all exercises of a specific type."""
        return cls.query.filter_by(type=exercise_type).all()

    @classmethod
    def search(cls, query):
        """Search exercises by name or description."""
        search = f"%{query}%"
        return cls.query.filter(
            db.or_(
                cls.name.ilike(search),
                cls.description.ilike(search)
            )
        ).all()

    def get_performance_history(self, athlete_id):
        """Get performance history for this exercise by a specific athlete."""
        from .performance_log import PerformanceLog
        return PerformanceLog.query.join(
            'workout_exercise'
        ).filter(
            PerformanceLog.athlete_id == athlete_id,
            WorkoutExercise.exercise_id == self.id
        ).order_by(
            PerformanceLog.logged_at.desc()
        ).all()

    def to_dict(self, include_performance=False, athlete_id=None):
        """Convert exercise instance to dictionary."""
        data = {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'description': self.description,
            'video_url': self.video_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_performance and athlete_id:
            data['performance_history'] = [
                log.to_dict() for log in self.get_performance_history(athlete_id)
            ]
        return data
