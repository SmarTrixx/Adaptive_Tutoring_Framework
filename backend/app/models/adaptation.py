from app import db
from datetime import datetime
import uuid

class AdaptationLog(db.Model):
    """Log of system adaptations based on engagement"""
    __tablename__ = 'adaptation_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = db.Column(db.String(36), db.ForeignKey('students.id'), nullable=False, index=True)
    session_id = db.Column(db.String(36), db.ForeignKey('sessions.id'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Trigger information
    trigger_metric = db.Column(db.String(120), nullable=False)  # Which metric triggered adaptation
    trigger_value = db.Column(db.Float, nullable=False)
    
    # Adaptation applied
    adaptation_type = db.Column(db.String(50), nullable=False)  # difficulty, pacing, hint_frequency, etc.
    old_value = db.Column(db.Float, nullable=True)
    new_value = db.Column(db.Float, nullable=True)
    
    # Reason/justification
    reason = db.Column(db.Text, nullable=True)
    
    # Effectiveness tracking
    was_effective = db.Column(db.Boolean, nullable=True)
    effectiveness_notes = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat(),
            'trigger_metric': self.trigger_metric,
            'trigger_value': self.trigger_value,
            'adaptation_type': self.adaptation_type,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'reason': self.reason,
            'was_effective': self.was_effective,
            'effectiveness_notes': self.effectiveness_notes
        }
