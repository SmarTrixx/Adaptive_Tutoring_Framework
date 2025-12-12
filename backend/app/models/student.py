from app import db
from datetime import datetime
import uuid

class Student(db.Model):
    """Student model to track learner information"""
    __tablename__ = 'students'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, nullable=True)
    
    # Learning preferences
    preferred_difficulty = db.Column(db.Float, default=0.5)
    preferred_pacing = db.Column(db.String(20), default='medium')  # slow, medium, fast
    
    # Relationships
    sessions = db.relationship('Session', backref='student', lazy=True, cascade='all, delete-orphan')
    engagement_metrics = db.relationship('EngagementMetric', backref='student', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'preferred_difficulty': self.preferred_difficulty,
            'preferred_pacing': self.preferred_pacing
        }
