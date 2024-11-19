from werkzeug.security import generate_password_hash, check_password_hash
from app.database import db
from .base import BaseModel

class User(BaseModel):
    """User model for both coaches and athletes."""
    
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('coach', 'athlete', name='user_role'), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))

    # Relationships
    programs = db.relationship('Program', backref='coach', lazy='dynamic')
    assigned_programs = db.relationship('AthleteProgram', backref='athlete', lazy='dynamic')
    performance_logs = db.relationship('PerformanceLog', backref='athlete', lazy='dynamic')
    form_analyses = db.relationship('FormAnalysis', back_populates='athlete', lazy='dynamic')

    @property
    def password(self):
        """Prevent password from being accessed."""
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """Set password to a hashed password."""
        self.password_hash = generate_password_hash(password)

    def set_password(self, password):
        """Set password to a hashed password."""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """Check if password matches the hashed password."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert user instance to dictionary."""
        return {
            'id': self.id,
            'email': self.email,
            'role': self.role,
            'first_name': self.first_name or '',
            'last_name': self.last_name or '',
            'full_name': self.full_name if (self.first_name or self.last_name) else self.email
        }

    @property
    def full_name(self):
        """Return user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email

    def get_assigned_programs(self):
        """Get all programs assigned to the athlete."""
        if self.role != 'athlete':
            raise ValueError('Only athletes can have assigned programs')
        return self.assigned_programs.all()
