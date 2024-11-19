from app import db
from .base import BaseModel

class Workout(BaseModel):
    """Workout model for individual workout sessions within a program."""
    
    __tablename__ = 'workouts'

    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    day_number = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text)

    # Relationships
    exercises = db.relationship('WorkoutExercise', backref='workout', lazy='dynamic',
                              cascade='all, delete-orphan', order_by='WorkoutExercise.order_index')

    def add_exercise(self, exercise_id, sets, reps=None, set_type='working', 
                    rest_time=None, notes=None, order_index=None):
        """Add an exercise to the workout."""
        from .workout_exercise import WorkoutExercise
        
        if order_index is None:
            # Get the next available order index
            last_exercise = self.exercises.order_by(
                WorkoutExercise.order_index.desc()
            ).first()
            order_index = (last_exercise.order_index + 1) if last_exercise else 0

        exercise = WorkoutExercise(
            workout_id=self.id,
            exercise_id=exercise_id,
            sets=sets,
            reps=reps,
            set_type=set_type,
            rest_time=rest_time,
            notes=notes,
            order_index=order_index
        )
        exercise.save()
        return exercise

    def reorder_exercises(self, exercise_order):
        """Reorder exercises in the workout.
        
        Args:
            exercise_order (list): List of tuples (exercise_id, new_order_index)
        """
        for exercise_id, new_index in exercise_order:
            exercise = self.exercises.filter_by(id=exercise_id).first()
            if exercise:
                exercise.order_index = new_index
                exercise.save()

    def get_performance_logs(self, athlete_id):
        """Get all performance logs for this workout by a specific athlete."""
        from .performance_log import PerformanceLog
        return PerformanceLog.query.join(
            'workout_exercise'
        ).filter(
            PerformanceLog.athlete_id == athlete_id,
            WorkoutExercise.workout_id == self.id
        ).order_by(
            WorkoutExercise.order_index,
            PerformanceLog.set_number
        ).all()

    def to_dict(self, include_exercises=True):
        """Convert workout instance to dictionary."""
        data = {
            'id': self.id,
            'name': self.name,
            'program_id': self.program_id,
            'description': self.description,
            'day_number': self.day_number,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_exercises:
            data['exercises'] = [
                exercise.to_dict() for exercise in self.exercises.order_by(
                    WorkoutExercise.order_index
                ).all()
            ]
        return data
