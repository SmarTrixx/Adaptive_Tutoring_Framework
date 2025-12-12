from app import db
from datetime import datetime
import uuid
from enum import Enum

class QuestionDifficulty(Enum):
    """Question difficulty levels"""
    EASY = 0.2
    MEDIUM = 0.5
    HARD = 0.8

class Question(db.Model):
    """Question model for CBT system"""
    __tablename__ = 'questions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    subject = db.Column(db.String(120), nullable=False, index=True)
    topic = db.Column(db.String(120), nullable=False)
    difficulty = db.Column(db.Float, nullable=False)  # 0.0 - 1.0
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.Text, nullable=False)
    option_b = db.Column(db.Text, nullable=False)
    option_c = db.Column(db.Text, nullable=False)
    option_d = db.Column(db.Text, nullable=False)
    correct_option = db.Column(db.String(1), nullable=False)  # A, B, C, D
    explanation = db.Column(db.Text, nullable=True)
    hints = db.Column(db.JSON, default=[])  # Array of hint strings
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # IRT Parameters (Item Response Theory)
    irt_discrimination = db.Column(db.Float, default=1.0)  # 'a' parameter - steepness of discrimination
    irt_difficulty = db.Column(db.Float, default=0.0)  # 'b' parameter - location of curve
    irt_guessing = db.Column(db.Float, default=0.25)  # 'c' parameter - lower asymptote (guessing probability)
    irt_calibrated = db.Column(db.Boolean, default=False)  # Whether IRT parameters have been calibrated
    irt_calibration_date = db.Column(db.DateTime, nullable=True)  # When IRT parameters were last updated
    
    # Spaced Repetition Metadata
    times_presented = db.Column(db.Integer, default=0)  # How many times presented to any student
    average_correct_rate = db.Column(db.Float, default=0.0)  # Average accuracy across all students
    
    # Relationships
    responses = db.relationship('StudentResponse', backref='question', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self, include_answer=False, include_irt=False):
        data = {
            'id': self.id,
            'subject': self.subject,
            'topic': self.topic,
            'difficulty': self.difficulty,
            'question_text': self.question_text,
            'options': {
                'A': self.option_a,
                'B': self.option_b,
                'C': self.option_c,
                'D': self.option_d
            },
            'hints': self.hints
        }
        
        if include_answer:
            data['correct_option'] = self.correct_option
            data['explanation'] = self.explanation
        
        if include_irt:
            data['irt'] = {
                'discrimination': self.irt_discrimination,
                'difficulty': self.irt_difficulty,
                'guessing': self.irt_guessing,
                'calibrated': self.irt_calibrated,
                'calibration_date': self.irt_calibration_date.isoformat() if self.irt_calibration_date else None
            }
        
        return data
