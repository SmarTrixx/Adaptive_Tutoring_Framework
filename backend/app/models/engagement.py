from app import db
from datetime import datetime
import uuid

class EngagementMetric(db.Model):
    """Engagement metrics for real-time adaptation"""
    __tablename__ = 'engagement_metrics'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = db.Column(db.String(36), db.ForeignKey('students.id'), nullable=False, index=True)
    session_id = db.Column(db.String(36), db.ForeignKey('sessions.id'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Behavioral Indicators
    response_time_seconds = db.Column(db.Float, nullable=True)
    attempts_count = db.Column(db.Integer, default=0)
    hints_requested = db.Column(db.Integer, default=0)
    inactivity_duration = db.Column(db.Float, default=0.0)  # seconds
    navigation_frequency = db.Column(db.Integer, default=0)  # rapid clicking count
    completion_rate = db.Column(db.Float, default=0.0)  # 0-1
    
    # Cognitive Indicators (inferred)
    accuracy = db.Column(db.Float, default=0.0)  # 0-1
    learning_progress = db.Column(db.Float, default=0.0)  # 0-1
    knowledge_gaps = db.Column(db.JSON, default=[])  # List of weak areas
    
    # Affective Indicators (self-reported)
    confidence_level = db.Column(db.Float, nullable=True)  # 0-1
    frustration_level = db.Column(db.Float, nullable=True)  # 0-1
    interest_level = db.Column(db.Float, nullable=True)  # 0-1
    
    # Composite engagement score
    engagement_score = db.Column(db.Float, default=0.5)  # 0-1
    engagement_level = db.Column(db.String(20), default='medium')  # low, medium, high
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat(),
            'behavioral': {
                'response_time_seconds': self.response_time_seconds,
                'attempts_count': self.attempts_count,
                'hints_requested': self.hints_requested,
                'inactivity_duration': self.inactivity_duration,
                'navigation_frequency': self.navigation_frequency,
                'completion_rate': self.completion_rate
            },
            'cognitive': {
                'accuracy': self.accuracy,
                'learning_progress': self.learning_progress,
                'knowledge_gaps': self.knowledge_gaps
            },
            'affective': {
                'confidence_level': self.confidence_level,
                'frustration_level': self.frustration_level,
                'interest_level': self.interest_level
            },
            'engagement_score': self.engagement_score,
            'engagement_level': self.engagement_level
        }
