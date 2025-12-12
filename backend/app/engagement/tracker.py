from app.models.engagement import EngagementMetric
from app.models.session import StudentResponse
from app import db
from datetime import datetime, timedelta
from config import Config

class EngagementIndicatorTracker:
    """
    Tracks behavioral, cognitive, and affective engagement indicators
    """
    
    def __init__(self):
        self.config = Config.ENGAGEMENT_THRESHOLDS
    
    def track_behavioral_indicators(self, session_id, response_data):
        """
        Track behavioral indicators:
        - Response time patterns
        - Frequency of attempts/retries
        - Navigation habits
        - Duration of activity
        - Completion rates
        - Hint requests
        - Inactivity periods
        """
        # Handle different response_data formats
        if not response_data or not isinstance(response_data, dict):
            return {
                'response_time_seconds': 0,
                'attempts_count': 0,
                'hints_requested': 0,
                'navigation_frequency': 0,
                'completion_rate': 0,
                'inactivity_duration': 0
            }
        
        # Get question_id from response_data
        question_id = response_data.get('question_id')
        if not question_id:
            # Fallback: return empty tracking data
            return {
                'response_time_seconds': response_data.get('response_time_seconds', 0),
                'attempts_count': response_data.get('attempts', 1),
                'hints_requested': 0,
                'navigation_frequency': self._calculate_navigation_frequency(session_id),
                'completion_rate': self._calculate_completion_rate(session_id),
                'inactivity_duration': self._calculate_inactivity(session_id)
            }
        
        response = StudentResponse.query.filter_by(
            session_id=session_id,
            question_id=question_id
        ).order_by(StudentResponse.timestamp.desc()).first()
        
        if not response:
            return {
                'response_time_seconds': response_data.get('response_time_seconds', 0),
                'attempts_count': 1,
                'hints_requested': 0,
                'navigation_frequency': 0,
                'completion_rate': 0,
                'inactivity_duration': 0
            }
        
        behavioral_data = {
            'response_time_seconds': response.response_time_seconds,
            'attempts_count': response.attempts,
            'hints_requested': response.hints_used,
            'navigation_frequency': self._calculate_navigation_frequency(session_id),
            'completion_rate': self._calculate_completion_rate(session_id),
            'inactivity_duration': self._calculate_inactivity(session_id)
        }
        
        return behavioral_data
    
    def track_cognitive_indicators(self, session_id):
        """
        Track cognitive indicators:
        - Accuracy/correctness
        - Learning progress
        - Knowledge gaps
        - Mastery level
        """
        responses = StudentResponse.query.filter_by(session_id=session_id).all()
        
        if not responses:
            return {
                'accuracy': 0.0,
                'learning_progress': 0.0,
                'knowledge_gaps': []
            }
        
        correct_count = sum(1 for r in responses if r.is_correct)
        accuracy = correct_count / len(responses) if responses else 0.0
        
        # Calculate learning progress (trend over time)
        recent_responses = responses[-5:]  # Last 5 responses
        recent_correct = sum(1 for r in recent_responses if r.is_correct)
        recent_accuracy = recent_correct / len(recent_responses) if recent_responses else 0.0
        
        # Identify knowledge gaps
        knowledge_gaps = self._identify_knowledge_gaps(responses)
        
        cognitive_data = {
            'accuracy': accuracy,
            'learning_progress': recent_accuracy,
            'knowledge_gaps': knowledge_gaps
        }
        
        return cognitive_data
    
    def track_affective_indicators(self, session_id, affective_feedback=None):
        """
        Track affective indicators:
        - Confidence level
        - Frustration level
        - Interest level
        - Motivation
        
        These can be self-reported or inferred from behavior
        """
        if affective_feedback is None:
            affective_feedback = {}
        
        # Infer confidence from accuracy
        responses = StudentResponse.query.filter_by(session_id=session_id).all()
        recent_responses = responses[-5:] if responses else []
        recent_correct = sum(1 for r in recent_responses if r.is_correct)
        confidence = recent_correct / len(recent_responses) if recent_responses else 0.0
        
        # Infer frustration from response time and retry patterns
        frustration = self._infer_frustration(session_id, responses)
        
        affective_data = {
            'confidence_level': affective_feedback.get('confidence', confidence),
            'frustration_level': affective_feedback.get('frustration', frustration),
            'interest_level': affective_feedback.get('interest', 0.5)
        }
        
        return affective_data
    
    def calculate_composite_engagement_score(self, behavioral, cognitive, affective):
        """
        Calculate a composite engagement score (0-1)
        Combines all three engagement dimensions
        """
        # Normalize behavioral indicators
        behavioral_score = (
            self._normalize_response_time(behavioral.get('response_time_seconds', 0)) * 0.25 +
            self._normalize_attempts(behavioral.get('attempts_count', 0)) * 0.15 +
            (1 - behavioral.get('inactivity_duration', 0) / 100) * 0.2 +
            behavioral.get('completion_rate', 0) * 0.2 +
            self._normalize_hints(behavioral.get('hints_requested', 0)) * 0.2
        )
        
        # Cognitive score
        cognitive_score = (
            cognitive.get('accuracy', 0) * 0.5 +
            cognitive.get('learning_progress', 0) * 0.5
        )
        
        # Affective score
        affective_score = (
            cognitive.get('confidence_level', 0.5) * 0.4 +
            (1 - cognitive.get('frustration_level', 0)) * 0.4 +
            cognitive.get('interest_level', 0.5) * 0.2
        )
        
        # Weighted composite score
        composite = (
            behavioral_score * 0.35 +
            cognitive_score * 0.40 +
            affective_score * 0.25
        )
        
        return max(0, min(1, composite))  # Clamp between 0-1
    
    def determine_engagement_level(self, engagement_score):
        """Classify engagement level as low, medium, or high"""
        if engagement_score < self.config['low_engagement_score']:
            return 'low'
        elif engagement_score > self.config['high_engagement_score']:
            return 'high'
        else:
            return 'medium'
    
    # Helper methods
    def _calculate_navigation_frequency(self, session_id):
        """Count rapid page/question switches"""
        responses = StudentResponse.query.filter_by(session_id=session_id).all()
        if len(responses) < 2:
            return 0
        
        # Count switches within 2 seconds
        rapid_switches = 0
        for i in range(1, len(responses)):
            time_diff = (responses[i].timestamp - responses[i-1].timestamp).total_seconds()
            if time_diff < 2:
                rapid_switches += 1
        
        return rapid_switches
    
    def _calculate_completion_rate(self, session_id):
        """Calculate percentage of questions answered"""
        from app.models.session import Session
        session = Session.query.get(session_id)
        if session.total_questions == 0:
            return 0.0
        return min(1.0, len(StudentResponse.query.filter_by(session_id=session_id).all()) / session.total_questions)
    
    def _calculate_inactivity(self, session_id):
        """Calculate period of inactivity"""
        responses = StudentResponse.query.filter_by(session_id=session_id).order_by(StudentResponse.timestamp.desc()).all()
        if not responses:
            return 0.0
        
        last_activity = responses[0].timestamp
        inactivity = (datetime.utcnow() - last_activity).total_seconds()
        return inactivity
    
    def _identify_knowledge_gaps(self, responses):
        """Identify topic/subject areas where student struggles"""
        gaps = {}
        for response in responses:
            if not response.is_correct:
                topic = response.question.topic
                gaps[topic] = gaps.get(topic, 0) + 1
        
        # Return topics with highest error rates
        return list(gaps.keys()) if gaps else []
    
    def _infer_frustration(self, session_id, responses):
        """Infer frustration from response patterns"""
        if not responses:
            return 0.5
        
        # High frustration indicators:
        # - Slow response times
        # - Multiple retries
        # - Frequent hint requests
        
        slow_responses = sum(1 for r in responses if r.response_time_seconds > self.config['response_time_slow'])
        high_retries = sum(1 for r in responses if r.attempts > 2)
        many_hints = sum(1 for r in responses if r.hints_used > 1)
        
        frustration = (slow_responses * 0.3 + high_retries * 0.4 + many_hints * 0.3) / len(responses) if responses else 0.0
        return min(1.0, frustration)
    
    def _normalize_response_time(self, response_time):
        """Normalize response time to 0-1 scale (too fast or too slow = low engagement)"""
        if response_time < self.config['response_time_fast']:
            return 0.3  # Too fast, might not be thinking
        elif response_time > self.config['response_time_slow']:
            return 0.4  # Too slow, might be frustrated
        else:
            return 0.9  # Good pace
    
    def _normalize_attempts(self, attempts):
        """Normalize attempt count (1 = best, >3 = worse)"""
        if attempts == 1:
            return 1.0
        elif attempts == 2:
            return 0.7
        elif attempts == 3:
            return 0.4
        else:
            return 0.2
    
    def _normalize_hints(self, hints):
        """Normalize hint requests (more hints = lower engagement)"""
        return max(0, 1.0 - (hints * 0.3))
