from flask.cli import FlaskGroup
from app import create_app, db
from app.models import User, Program, Exercise, Workout, WorkoutExercise, AthleteProgram, PerformanceLog, FormAnalysis

cli = FlaskGroup(create_app=create_app)

@cli.command("create_db")
def create_db():
    """Creates the database tables."""
    db.create_all()
    print("Database tables created!")

@cli.command("drop_db")
def drop_db():
    """Drops the database tables."""
    if input("Are you sure you want to drop all tables? (y/N): ").lower() == 'y':
        db.drop_all()
        print("Database tables dropped!")
    else:
        print("Operation cancelled.")

@cli.command("seed_db")
def seed_db():
    """Seeds the database with initial data."""
    # Create a coach user
    coach = User(
        email="coach@example.com",
        first_name="John",
        last_name="Coach",
        role="coach"
    )
    coach.password = "password123"  # This will be hashed
    
    # Create an athlete user
    athlete = User(
        email="athlete@example.com",
        first_name="Jane",
        last_name="Athlete",
        role="athlete"
    )
    athlete.password = "password123"  # This will be hashed
    
    # Create some exercises
    exercises = [
        Exercise(
            name="Barbell Back Squat",
            type="strength",
            description="A compound exercise that primarily targets the quadriceps, hamstrings, and glutes.",
            video_url="https://example.com/squat-form"
        ),
        Exercise(
            name="Barbell Bench Press",
            type="strength",
            description="A compound exercise that primarily targets the chest, shoulders, and triceps.",
            video_url="https://example.com/bench-press-form"
        ),
        Exercise(
            name="Barbell Deadlift",
            type="strength",
            description="A compound exercise that targets the entire posterior chain.",
            video_url="https://example.com/deadlift-form"
        )
    ]
    
    # Save all objects
    db.session.add(coach)
    db.session.add(athlete)
    for exercise in exercises:
        db.session.add(exercise)
    
    db.session.commit()
    print("Database seeded!")

if __name__ == "__main__":
    cli()
