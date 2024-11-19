from app import db
from .base import BaseModel

class Program(BaseModel):
    """Program model for workout programs created by coaches."""
    
    __tablename__ = 'programs'

    id = db.Column(db.Integer, primary_key=True)
    coach_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    # Relationships
    workouts = db.relationship('Workout', backref='program', lazy='dynamic',
                             cascade='all, delete-orphan')
    athlete_assignments = db.relationship('AthleteProgram', backref='program', lazy='dynamic',
                                        cascade='all, delete-orphan')

    def get_active_athletes(self):
        """Get all athletes currently assigned to this program."""
        return [assignment.athlete for assignment in 
                self.athlete_assignments.filter_by(status='active').all()]

    def add_workout(self, name, day_number, notes=None):
        """Add a new workout to the program."""
        from .workout import Workout
        workout = Workout(
            program_id=self.id,
            name=name,
            day_number=day_number,
            notes=notes
        )
        workout.save()
        return workout

    def assign_to_athlete(self, athlete_id, start_date, end_date=None):
        """Assign this program to an athlete."""
        from .athlete_program import AthleteProgram
        assignment = AthleteProgram(
            athlete_id=athlete_id,
            program_id=self.id,
            start_date=start_date,
            end_date=end_date
        )
        assignment.save()
        return assignment

    def to_dict(self, include_workouts=False):
        """Convert program instance to dictionary."""
        data = super().to_dict()
        if include_workouts:
            data['workouts'] = [workout.to_dict() for workout in self.workouts.all()]
        return data
