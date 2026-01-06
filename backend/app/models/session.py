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
    hints_used = db.Column(db.Integer, default=0)  # Legacy: count of hints used
    hints_used_array = db.Column(db.JSON, default=[])  # Array of hint usage objects with timestamps
    attempts = db.Column(db.Integer, default=1)
    
    # Option selection tracking (Behavioral)
    initial_option = db.Column(db.String(1), nullable=True)  # First option selected
    final_option = db.Column(db.String(1), nullable=True)    # Last option before submit
    option_change_count = db.Column(db.Integer, default=0)   # Number of times user changed option
    option_change_history = db.Column(db.JSON, default=[])   # List of changes: [{from, to, timestamp}, ...]
    
    # Navigation tracking (Behavioral)
    navigation_frequency = db.Column(db.Integer, default=0)  # Count of navigation events
    
    # Timestamps for tracking (Behavioral)
    interaction_start_timestamp = db.Column(db.Integer, nullable=True)  # milliseconds since epoch
    submission_timestamp = db.Column(db.Integer, nullable=True)         # milliseconds since epoch
    submission_iso_timestamp = db.Column(db.String(50), nullable=True)  # ISO format timestamp
    
    # Knowledge gaps (Cognitive)
    knowledge_gaps = db.Column(db.JSON, default=[])  # Empty list or list of gap areas
    
    # Cognitive & Affective Indicators
    time_spent_per_question = db.Column(db.Integer, default=0)  # Seconds spent on this question
    inactivity_duration_ms = db.Column(db.Integer, default=0)  # Milliseconds of inactivity
    question_index = db.Column(db.Integer, default=0)  # Index of question in session
    hesitation_flags = db.Column(db.JSON, default={})  # {rapidClicking, longHesitation, frequentSwitching}
    navigation_pattern = db.Column(db.String(50), default='sequential')  # sequential, revisit, backtrack
    
    # Facial Monitoring Data
    facial_metrics = db.Column(db.JSON, default={})  # {camera_enabled, face_detected_count, face_lost_count, attention_score, emotions_detected, face_presence_duration_seconds}
    
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
            'hints_used_array': self.hints_used_array if self.hints_used_array else [],
            'attempts': self.attempts,
            'initial_option': self.initial_option,
            'final_option': self.final_option,
            'option_change_count': self.option_change_count,
            'option_change_history': self.option_change_history,
            'navigation_frequency': self.navigation_frequency,
            'interaction_start_timestamp': self.interaction_start_timestamp,
            'submission_timestamp': self.submission_timestamp,
            'submission_iso_timestamp': self.submission_iso_timestamp,
            'knowledge_gaps': self.knowledge_gaps if self.knowledge_gaps else [],
            'time_spent_per_question': self.time_spent_per_question,
            'inactivity_duration_ms': self.inactivity_duration_ms,
            'question_index': self.question_index,
            'hesitation_flags': self.hesitation_flags if self.hesitation_flags else {},
            'navigation_pattern': self.navigation_pattern,
            'facial_metrics': self.facial_metrics if self.facial_metrics else {}
        }

