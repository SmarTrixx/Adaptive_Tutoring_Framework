"""
Affective Indicators Module - Facial Expression and Emotional State Analysis

Captures and analyzes student emotional and affective states through:
1. Facial Expression Recognition (via webcam)
2. Gaze Tracking (eye contact and attention)
3. Posture Analysis (engagement indicators)
4. Emotional State Classification
5. Confusion and Frustration Detection
"""

from app.models.engagement import EngagementMetric
from app.models.session import Session, StudentResponse
from datetime import datetime, timedelta
from app import db
import json

class AffectiveIndicatorAnalyzer:
    """
    Analyzes affective (emotional) engagement indicators
    
    Supports two data sources:
    1. Facial emotion recognition (optional, when available)
    2. Behavioral inference (always available)
    
    Falls back gracefully to behavioral inference if facial data unavailable.
    """
    
    # Emotion to engagement mapping
    EMOTION_ENGAGEMENT_MAP = {
        'happy': {'confidence': 0.9, 'frustration': 0.1, 'interest': 0.9},
        'excited': {'confidence': 0.95, 'frustration': 0.0, 'interest': 1.0},
        'confident': {'confidence': 0.85, 'frustration': 0.1, 'interest': 0.8},
        'neutral': {'confidence': 0.5, 'frustration': 0.3, 'interest': 0.5},
        'confused': {'confidence': 0.3, 'frustration': 0.6, 'interest': 0.4},
        'frustrated': {'confidence': 0.2, 'frustration': 0.9, 'interest': 0.3},
        'bored': {'confidence': 0.4, 'frustration': 0.2, 'interest': 0.1},
        'anxious': {'confidence': 0.2, 'frustration': 0.7, 'interest': 0.5},
        'sad': {'confidence': 0.1, 'frustration': 0.8, 'interest': 0.2},
        'angry': {'confidence': 0.1, 'frustration': 1.0, 'interest': 0.1}
    }
    
    # Gaze patterns and their meanings
    GAZE_PATTERNS = {
        'focused': {'attention': 0.9, 'engagement': 0.85},
        'reading': {'attention': 0.85, 'engagement': 0.8},
        'scattered': {'attention': 0.4, 'engagement': 0.3},
        'downward': {'attention': 0.2, 'engagement': 0.1},
        'away': {'attention': 0.1, 'engagement': 0.05}
    }
    
    # Posture analysis
    POSTURE_INDICATORS = {
        'upright_engaged': {'engagement': 0.9, 'confidence': 0.8},
        'leaning_forward': {'engagement': 0.95, 'confidence': 0.85},
        'relaxed': {'engagement': 0.7, 'confidence': 0.7},
        'slumped': {'engagement': 0.3, 'confidence': 0.2},
        'tense': {'engagement': 0.4, 'confidence': 0.2}
    }
    
    def __init__(self):
        pass
    
    def record_facial_expression(self, student_id, session_id, emotion_label, 
                                confidence_score, frame_data=None):
        """
        Record facial expression data from real-time video analysis
        
        Args:
            student_id: Student identifier
            session_id: Current session ID
            emotion_label: Detected emotion (happy, sad, confused, frustrated, etc.)
            confidence_score: Model confidence (0-1)
            frame_data: Optional video frame metadata
        
        Returns:
            AffectiveMetric record
        """
        # Get engagement mapping for this emotion
        engagement_values = self.EMOTION_ENGAGEMENT_MAP.get(
            emotion_label.lower(), 
            {'confidence': 0.5, 'frustration': 0.5, 'interest': 0.5}
        )
        
        # Create metric record
        metric_data = {
            'student_id': student_id,
            'session_id': session_id,
            'timestamp': datetime.utcnow(),
            'detection_type': 'facial_expression',
            'emotion_label': emotion_label,
            'emotion_confidence': confidence_score,
            'inferred_confidence_level': engagement_values['confidence'],
            'inferred_frustration_level': engagement_values['frustration'],
            'inferred_interest_level': engagement_values['interest'],
            'frame_metadata': frame_data or {}
        }
        
        return metric_data
    
    def record_gaze_pattern(self, student_id, session_id, gaze_pattern, 
                           duration_seconds, gaze_metadata=None):
        """
        Record gaze tracking data
        
        Args:
            student_id: Student identifier
            session_id: Current session ID
            gaze_pattern: Type of gaze (focused, scattered, away, etc.)
            duration_seconds: How long this pattern was observed
            gaze_metadata: Detailed gaze information
        """
        pattern_values = self.GAZE_PATTERNS.get(
            gaze_pattern.lower(),
            {'attention': 0.5, 'engagement': 0.5}
        )
        
        metric_data = {
            'student_id': student_id,
            'session_id': session_id,
            'timestamp': datetime.utcnow(),
            'detection_type': 'gaze_tracking',
            'gaze_pattern': gaze_pattern,
            'gaze_duration': duration_seconds,
            'attention_level': pattern_values['attention'],
            'engagement_level': pattern_values['engagement'],
            'gaze_metadata': gaze_metadata or {}
        }
        
        return metric_data
    
    def record_posture(self, student_id, session_id, posture_type, posture_metadata=None):
        """
        Record student posture during learning
        
        Args:
            student_id: Student identifier
            session_id: Current session ID
            posture_type: Body posture classification
            posture_metadata: Detailed posture data
        """
        posture_values = self.POSTURE_INDICATORS.get(
            posture_type.lower(),
            {'engagement': 0.5, 'confidence': 0.5}
        )
        
        metric_data = {
            'student_id': student_id,
            'session_id': session_id,
            'timestamp': datetime.utcnow(),
            'detection_type': 'posture_analysis',
            'posture_type': posture_type,
            'engagement_indicator': posture_values['engagement'],
            'confidence_indicator': posture_values['confidence'],
            'posture_metadata': posture_metadata or {}
        }
        
        return metric_data
    
    def detect_confusion(self, student_id, session_id, facial_data=None, 
                        behavioral_data=None):
        """
        Detect confusion state using multimodal signals
        
        Confusion indicators:
        - Furrowed brow (facial)
        - Slow response time (behavioral)
        - Multiple retries (behavioral)
        - Frequent hint requests (behavioral)
        - Scattered gaze (eye tracking)
        """
        confusion_score = 0.0
        signals = []
        
        # Facial signals
        if facial_data:
            emotion = facial_data.get('emotion', '').lower()
            if emotion in ['confused', 'frustrated', 'anxious']:
                confusion_score += 0.4
                signals.append(f"Facial expression: {emotion}")
        
        # Behavioral signals
        if behavioral_data:
            response_time = behavioral_data.get('response_time', 0)
            attempts = behavioral_data.get('attempts', 1)
            hints = behavioral_data.get('hints_used', 0)
            
            # Slow response (>15 seconds)
            if response_time > 15:
                confusion_score += 0.2
                signals.append(f"Slow response time: {response_time}s")
            
            # Multiple attempts
            if attempts > 2:
                confusion_score += 0.2
                signals.append(f"Multiple attempts: {attempts}")
            
            # Hint requests
            if hints > 1:
                confusion_score += 0.15
                signals.append(f"Multiple hint requests: {hints}")
        
        confusion_score = min(1.0, confusion_score)
        
        return {
            'confusion_detected': confusion_score > 0.5,
            'confusion_score': confusion_score,
            'signals': signals,
            'recommended_action': self._recommend_confusion_response(confusion_score)
        }
    
    def detect_frustration(self, student_id, session_id, facial_data=None,
                          behavioral_data=None):
        """
        Detect frustration state
        
        Frustration indicators:
        - Angry/frustrated facial expression
        - High response time variability
        - Frequent hint requests
        - Multiple wrong attempts
        - Jaw tension
        """
        frustration_score = 0.0
        signals = []
        
        # Facial signals
        if facial_data:
            emotion = facial_data.get('emotion', '').lower()
            if emotion in ['frustrated', 'angry', 'anxious']:
                frustration_score += 0.35
                signals.append(f"Facial expression: {emotion}")
            
            jaw_tension = facial_data.get('jaw_tension', 0)
            if jaw_tension > 0.6:
                frustration_score += 0.2
                signals.append("Jaw tension detected")
        
        # Behavioral signals
        if behavioral_data:
            attempts = behavioral_data.get('attempts', 1)
            hints = behavioral_data.get('hints_used', 0)
            
            if attempts > 3:
                frustration_score += 0.25
                signals.append(f"Many failed attempts: {attempts}")
            
            if hints > 2:
                frustration_score += 0.15
                signals.append(f"Heavy hint usage: {hints}")
        
        frustration_score = min(1.0, frustration_score)
        
        return {
            'frustration_detected': frustration_score > 0.5,
            'frustration_score': frustration_score,
            'signals': signals,
            'recommended_action': self._recommend_frustration_response(frustration_score)
        }
    
    def calculate_affective_engagement_score(self, facial_data=None, gaze_data=None,
                                           posture_data=None):
        """
        Calculate overall affective engagement combining all modalities
        """
        scores = []
        weights = []
        
        if facial_data:
            emotion_score = self._emotion_to_engagement(facial_data.get('emotion', 'neutral'))
            scores.append(emotion_score)
            weights.append(0.4)
        
        if gaze_data:
            attention_score = gaze_data.get('attention_level', 0.5)
            scores.append(attention_score)
            weights.append(0.35)
        
        if posture_data:
            posture_engagement = posture_data.get('engagement_indicator', 0.5)
            scores.append(posture_engagement)
            weights.append(0.25)
        
        if not scores:
            return 0.5  # Default neutral
        
        # Weighted average
        total_weight = sum(weights[:len(scores)])
        if total_weight == 0:
            return 0.5
        
        affective_score = sum(s * w for s, w in zip(scores, weights[:len(scores)])) / total_weight
        return min(1.0, max(0.0, affective_score))
    
    # Helper methods
    def _emotion_to_engagement(self, emotion):
        """Convert emotion to engagement score"""
        emotion_lower = emotion.lower()
        mapping = {
            'excited': 1.0,
            'happy': 0.9,
            'confident': 0.85,
            'neutral': 0.5,
            'confused': 0.3,
            'frustrated': 0.2,
            'bored': 0.15,
            'angry': 0.1
        }
        return mapping.get(emotion_lower, 0.5)
    
    def _recommend_confusion_response(self, confusion_score):
        """Get recommended response to detected confusion"""
        if confusion_score > 0.7:
            return {
                'action': 'provide_hint',
                'urgency': 'high',
                'message': 'Student appears confused. Providing hint automatically.'
            }
        elif confusion_score > 0.5:
            return {
                'action': 'simplify_question',
                'urgency': 'medium',
                'message': 'Breaking down question into simpler components.'
            }
        else:
            return {
                'action': 'monitor',
                'urgency': 'low',
                'message': 'Monitoring student progress.'
            }
    
    def _recommend_frustration_response(self, frustration_score):
        """Get recommended response to detected frustration"""
        if frustration_score > 0.8:
            return {
                'action': 'reduce_difficulty',
                'urgency': 'high',
                'message': 'High frustration detected. Reducing difficulty.'
            }
        elif frustration_score > 0.6:
            return {
                'action': 'encourage_break',
                'urgency': 'medium',
                'message': 'Frustration detected. Consider taking a break.'
            }
        elif frustration_score > 0.4:
            return {
                'action': 'provide_support',
                'urgency': 'low',
                'message': 'Offering additional support and guidance.'
            }
        else:
            return {
                'action': 'continue',
                'urgency': 'none',
                'message': 'Continuing normally.'
            }
    
    def get_affective_summary(self, student_id, session_id, minutes=30):
        """
        Get summary of affective indicators over recent period
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        # This would query affective data from database
        # For now, return structure
        return {
            'period_minutes': minutes,
            'average_confidence': 0.5,  # Would be calculated from data
            'average_frustration': 0.3,
            'average_interest': 0.6,
            'dominant_emotion': 'neutral',
            'emotional_trend': 'stable',
            'affective_engagement': 0.55,
            'recommendations': []
        }

