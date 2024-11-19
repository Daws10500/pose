from app import db
from .base import BaseModel

class AthleteProgram(BaseModel):
    """Junction model between athletes and programs with assignment metadata."""
    
    __tablename__ = 'athlete_programs'

    id = db.Column(db.Integer, primary_key=True)
    athlete_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(50), default='active')

    def complete_program(self):
        """Mark the program as completed."""
        from datetime import date
        self.status = 'completed'
        self.end_date = date.today()
        self.save()

    def pause_program(self):
        """Pause the program."""
        self.status = 'paused'
        self.save()

    def resume_program(self):
        """Resume the paused program."""
        if self.status == 'paused':
            self.status = 'active'
            self.save()
        else:
            raise ValueError('Can only resume paused programs')

    def get_progress(self):
        """Calculate program completion progress."""
        from .performance_log import PerformanceLog
        from .workout_exercise import WorkoutExercise
        
        # Get total number of exercises in the program
        total_exercises = WorkoutExercise.query.join(
            'workout'
        ).filter(
            Workout.program_id == self.program_id
        ).count()

        # Get number of completed exercises
        completed_exercises = PerformanceLog.query.join(
            'workout_exercise', 'workout'
        ).filter(
            PerformanceLog.athlete_id == self.athlete_id,
            Workout.program_id == self.program_id
        ).distinct(
            WorkoutExercise.id
        ).count()

        return {
            'total_exercises': total_exercises,
            'completed_exercises': completed_exercises,
            'completion_percentage': (completed_exercises / total_exercises * 100) if total_exercises > 0 else 0
        }

    def to_dict(self, include_program=False, include_progress=False):
        """Convert athlete program instance to dictionary."""
        data = super().to_dict()
        
        if include_program:
            data['program'] = self.program.to_dict()
            
        if include_progress:
            data['progress'] = self.get_progress()
            
        return data
