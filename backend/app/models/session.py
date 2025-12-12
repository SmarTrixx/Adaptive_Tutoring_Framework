from app import db
from datetime import datetime
import uuid

class Session(db.Model):
    """Study session model"""
    __tablename__ = 'sessions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = db.Column(db.String(36), db.ForeignKey('students.id'), nullable=False, index=True)
    session_start = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    session_end = db.Column(db.DateTime, nullable=True)
    subject = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), default='active')  # active, paused, completed
    
    # Performance metrics
    total_questions = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    score_percentage = db.Column(db.Float, default=0.0)
    
    # Current difficulty level
    current_difficulty = db.Column(db.Float, default=0.5)
    
    # Relationships
    responses = db.relationship('StudentResponse', backref='session', lazy=True, cascade='all, delete-orphan')
    
    @property
    def duration_seconds(self):
        """Calculate session duration in seconds"""
        end_time = self.session_end or datetime.utcnow()
        delta = end_time - self.session_start
        return int(delta.total_seconds())
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'session_start': self.session_start.isoformat(),
            'session_end': self.session_end.isoformat() if self.session_end else None,
            'subject': self.subject,
            'status': self.status,
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'score_percentage': self.score_percentage,
            'current_difficulty': self.current_difficulty,
            'duration_seconds': self.duration_seconds
        }

class StudentResponse(db.Model):
    """Student response to a question"""
    __tablename__ = 'student_responses'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = db.Column(db.String(36), db.ForeignKey('sessions.id'), nullable=False, index=True)
    question_id = db.Column(db.String(36), db.ForeignKey('questions.id'), nullable=False, index=True)
    student_answer = db.Column(db.String(1), nullable=False)  # A, B, C, D
    is_correct = db.Column(db.Boolean, nullable=False)
    response_time_seconds = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Engagement data
    hints_used = db.Column(db.Integer, default=0)
    attempts = db.Column(db.Integer, default=1)
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'question_id': self.question_id,
            'student_answer': self.student_answer,
            'is_correct': self.is_correct,
            'response_time_seconds': self.response_time_seconds,
            'timestamp': self.timestamp.isoformat(),
            'hints_used': self.hints_used,
            'attempts': self.attempts
        }
