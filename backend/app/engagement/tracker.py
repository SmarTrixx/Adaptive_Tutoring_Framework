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
            response_data = {}
        
        # Get the LATEST StudentResponse for this session (most recent answer)
        latest_response = StudentResponse.query.filter_by(
            session_id=session_id
        ).order_by(StudentResponse.timestamp.desc()).first()
        
        if latest_response:
            # Get data from the latest response - use explicit None checks
            response_time_seconds = latest_response.response_time_seconds if latest_response.response_time_seconds is not None else 0
            if response_time_seconds == 0 and latest_response.response_time_seconds is None:
                print(f"WARNING: response_time_seconds is None for session {session_id}")
            
            attempts_count = latest_response.attempts if latest_response.attempts is not None else 1
            if attempts_count == 1 and latest_response.attempts is None:
                print(f"WARNING: attempts is None for session {session_id}")
            
            # FIX: Use hints_used_array (new field) instead of hints_used (legacy)
            # hints_used_array is an array of hint objects with timestamps
            hints_used_array = latest_response.hints_used_array if latest_response.hints_used_array else []
            hints_requested = len(hints_used_array) if isinstance(hints_used_array, list) else (latest_response.hints_used if latest_response.hints_used is not None else 0)
        else:
            # Fallback to response_data or defaults
            response_time_seconds = response_data.get('response_time_seconds', 0)
            attempts_count = response_data.get('attempts', 1)
            hints_requested = response_data.get('hints_requested', 0)
        
        behavioral_data = {
            'response_time_seconds': response_time_seconds,
            'attempts_count': attempts_count,
            'hints_requested': hints_requested,
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
        
        # Dynamically infer affective indicators from actual behavior
        responses = StudentResponse.query.filter_by(session_id=session_id).all()
        
        # Confidence: based on recent accuracy and decision-making decisiveness
        confidence = self._infer_confidence(session_id, responses)
        
        # Frustration: based on slow responses, option changes, and error streaks
        frustration = self._infer_frustration(session_id, responses)
        
        # Interest level: based on engagement patterns
        interest = self._infer_interest_level(session_id, responses, affective_feedback)
        
        affective_data = {
            'confidence_level': affective_feedback.get('confidence', confidence),
            'frustration_level': affective_feedback.get('frustration', frustration),
            'interest_level': affective_feedback.get('interest', interest)
        }
        
        return affective_data
    
    def _infer_interest_level(self, session_id, responses, affective_feedback):
        """Infer interest level from engagement patterns"""
        # If explicitly provided, use that
        if 'interest' in affective_feedback:
            return affective_feedback['interest']
        
        if not responses:
            return 0.5  # Default neutral
        
        # Factors that indicate interest:
        # 1. Fast response times (engaged, not procrastinating)
        # 2. Consistent performance (engaged, not bored/careless)
        # 3. Attempting questions rather than skipping
        
        # IMPORTANT: Use actual response times from database
        # If response_time_seconds is None, something went wrong in logging
        response_times = [r.response_time_seconds for r in responses if r.response_time_seconds is not None]
        
        if not response_times:
            # No valid response times recorded - default to neutral
            avg_response_time = 30
            print(f"[WARNING] No valid response times in {len(responses)} responses")
        else:
            avg_response_time = sum(response_times) / len(response_times)
        
        # Low response time = interested (fast = engaged)
        # High response time = less interested or struggling
        response_time_interest = max(0, 1 - (avg_response_time / 60))  # 0-1 scale
        
        # Low variance in performance = interested (consistent engagement)
        recent = responses[-5:] if len(responses) >= 5 else responses
        if len(recent) > 1:
            accuracies = [1.0 if r.is_correct else 0.0 for r in recent]
            avg_accuracy = sum(accuracies) / len(accuracies)
            variance = sum((a - avg_accuracy) ** 2 for a in accuracies) / len(accuracies)
            consistency_interest = max(0, 1 - (variance * 2))  # Low variance = high interest
        else:
            consistency_interest = 0.5
        
        # Combine factors
        inferred_interest = (response_time_interest * 0.4) + (consistency_interest * 0.6)
        return max(0, min(1, inferred_interest))
    
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
        """
        Infer frustration dynamically from recent behavior patterns.
        Frustration increases with:
        - Response time deviation (much slower than normal)
        - Multiple option changes (indecision)
        - Incorrect streaks (repeated failures)
        - High inactivity before submission
        """
        if not responses:
            return 0.0
        
        # Get the latest response for dynamic computation
        latest = responses[-1] if responses else None
        if not latest:
            return 0.0
        
        frustration_factors = []
        
        # Factor 1: Response time (very slow = frustration)
        response_time = latest.response_time_seconds if latest.response_time_seconds else 0
        if response_time > self.config['response_time_slow']:
            # Normalize: slow response indicates frustration
            time_factor = min(1.0, (response_time - self.config['response_time_slow']) / 30.0)
            frustration_factors.append(time_factor * 0.3)
        
        # Factor 2: Option changes (indecision = confusion/frustration)
        option_changes = latest.option_change_count if latest.option_change_count else 0
        if option_changes > 2:
            change_factor = min(1.0, option_changes / 5.0)
            frustration_factors.append(change_factor * 0.3)
        
        # Factor 3: Incorrect streak (recent failures)
        recent_incorrect = sum(1 for r in responses[-3:] if not r.is_correct)
        if recent_incorrect >= 2:
            streak_factor = recent_incorrect / 3.0
            frustration_factors.append(streak_factor * 0.4)
        
        frustration = sum(frustration_factors)
        return min(1.0, max(0.0, frustration))
    
    def _infer_confidence(self, session_id, responses):
        """
        Infer confidence from recent performance and option decisiveness.
        Confidence increases with:
        - Correct answers
        - Fast response times (decisive)
        - Few option changes
        - High accuracy streak
        """
        if not responses:
            return 0.5
        
        latest = responses[-1] if responses else None
        if not latest:
            return 0.5
        
        confidence_factors = []
        
        # Factor 1: Recent accuracy (correct answers boost confidence)
        recent_correct = sum(1 for r in responses[-3:] if r.is_correct)
        accuracy_factor = recent_correct / 3.0
        confidence_factors.append(accuracy_factor * 0.4)
        
        # Factor 2: Decisiveness (few option changes = confident)
        option_changes = latest.option_change_count if latest.option_change_count else 0
        decisiveness_factor = max(0, 1.0 - (option_changes / 5.0))
        confidence_factors.append(decisiveness_factor * 0.3)
        
        # Factor 3: Response time (moderate speed = confident, not rushed or stuck)
        response_time = latest.response_time_seconds if latest.response_time_seconds else 0
        if self.config['response_time_fast'] < response_time < self.config['response_time_slow']:
            time_factor = 1.0
        else:
            time_factor = 0.6
        confidence_factors.append(time_factor * 0.3)
        
        confidence = sum(confidence_factors)
        return min(1.0, max(0.0, confidence))

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
