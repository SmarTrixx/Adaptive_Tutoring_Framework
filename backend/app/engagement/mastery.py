"""
Mastery Tracking and Competency Management Module

Tracks student mastery levels across topics using multiple methodologies:
- Accuracy thresholds (0-100%)
- Learning curves (exponential fitting)
- Competency levels (0-5 scale)
- Performance trends
"""

from app.models.session import StudentResponse
from app.models.question import Question
from datetime import datetime, timedelta
import math
from collections import defaultdict

class MasteryTracker:
    """Tracks and calculates student mastery in different topics"""
    
    # Mastery level definitions
    MASTERY_LEVELS = {
        0: {'name': 'No Mastery', 'accuracy_min': 0, 'accuracy_max': 0.2},
        1: {'name': 'Novice', 'accuracy_min': 0.2, 'accuracy_max': 0.4},
        2: {'name': 'Developing', 'accuracy_min': 0.4, 'accuracy_max': 0.65},
        3: {'name': 'Proficient', 'accuracy_min': 0.65, 'accuracy_max': 0.85},
        4: {'name': 'Advanced', 'accuracy_min': 0.85, 'accuracy_max': 0.95},
        5: {'name': 'Expert', 'accuracy_min': 0.95, 'accuracy_max': 1.0}
    }
    
    # Thresholds for competency classification
    COMPETENCY_THRESHOLDS = {
        'emerging': 0.5,      # <50% accuracy
        'developing': 0.65,   # 50-65% accuracy
        'proficient': 0.85,   # 65-85% accuracy
        'advanced': 0.95      # >85% accuracy
    }
    
    def __init__(self):
        pass
    
    def calculate_topic_mastery(self, student_id, topic, session_id=None):
        """
        Calculate mastery level for a specific topic
        
        Returns:
            {
                'topic': str,
                'mastery_level': int (0-5),
                'accuracy': float (0-1),
                'attempts': int,
                'correct': int,
                'total': int,
                'learning_curve': dict,
                'competency': str,
                'readiness_for_advancement': bool
            }
        """
        # Get all responses for this student in this topic
        if session_id:
            responses = StudentResponse.query.join(
                Question, StudentResponse.question_id == Question.id
            ).filter(
                StudentResponse.session_id == session_id,
                Question.topic == topic
            ).order_by(StudentResponse.timestamp).all()
        else:
            responses = StudentResponse.query.join(
                Question, StudentResponse.question_id == Question.id
            ).join(
                app.models.session.Session,
                StudentResponse.session_id == app.models.session.Session.id
            ).filter(
                app.models.session.Session.student_id == student_id,
                Question.topic == topic
            ).order_by(StudentResponse.timestamp).all()
        
        if not responses:
            return {
                'topic': topic,
                'mastery_level': 0,
                'accuracy': 0.0,
                'attempts': 0,
                'correct': 0,
                'total': 0,
                'learning_curve': {'model': 'no_data'},
                'competency': 'no_data',
                'readiness_for_advancement': False,
                'message': 'No data for this topic'
            }
        
        # Calculate basic metrics
        correct = sum(1 for r in responses if r.is_correct)
        total = len(responses)
        accuracy = correct / total if total > 0 else 0.0
        
        # Determine mastery level
        mastery_level = self._get_mastery_level(accuracy)
        
        # Determine competency
        competency = self._get_competency_level(accuracy)
        
        # Calculate learning curve
        learning_curve = self._fit_learning_curve(responses)
        
        # Check readiness for advancement
        readiness = self._check_advancement_readiness(
            responses, accuracy, competency
        )
        
        return {
            'topic': topic,
            'mastery_level': mastery_level,
            'mastery_name': self.MASTERY_LEVELS[mastery_level]['name'],
            'accuracy': accuracy,
            'attempts': total,
            'correct': correct,
            'total': total,
            'learning_curve': learning_curve,
            'competency': competency,
            'readiness_for_advancement': readiness,
            'recent_performance': self._get_recent_performance(responses, window=5)
        }
    
    def calculate_overall_mastery(self, student_id, session_id=None):
        """Calculate overall mastery across all topics"""
        if session_id:
            responses = StudentResponse.query.join(
                Question, StudentResponse.question_id == Question.id
            ).filter(
                StudentResponse.session_id == session_id
            ).all()
        else:
            # Get all responses for student
            from app.models.session import Session
            responses = StudentResponse.query.join(
                Session, StudentResponse.session_id == Session.id
            ).join(
                Question, StudentResponse.question_id == Question.id
            ).filter(
                Session.student_id == student_id
            ).all()
        
        if not responses:
            return {
                'overall_mastery': 0,
                'overall_accuracy': 0.0,
                'total_attempts': 0,
                'topics': {},
                'status': 'no_data'
            }
        
        # Get unique topics
        topics = set(r.question.topic for r in responses)
        
        # Calculate mastery for each topic
        topic_masteries = {}
        topic_accuracies = []
        
        for topic in topics:
            mastery = self.calculate_topic_mastery(student_id, topic, session_id)
            topic_masteries[topic] = mastery
            topic_accuracies.append(mastery['accuracy'])
        
        # Overall metrics
        overall_accuracy = sum(topic_accuracies) / len(topic_accuracies) if topic_accuracies else 0.0
        overall_mastery = self._get_mastery_level(overall_accuracy)
        
        return {
            'overall_mastery': overall_mastery,
            'overall_mastery_name': self.MASTERY_LEVELS[overall_mastery]['name'],
            'overall_accuracy': overall_accuracy,
            'total_attempts': len(responses),
            'total_correct': sum(1 for r in responses if r.is_correct),
            'topics_studied': len(topics),
            'topics': topic_masteries,
            'status': 'calculated'
        }
    
    def get_knowledge_profile(self, student_id, session_id=None):
        """
        Get comprehensive knowledge profile of student
        
        Shows strengths, weaknesses, and growth areas
        """
        overall = self.calculate_overall_mastery(student_id, session_id)
        topics = overall.get('topics', {})
        
        strengths = []
        weaknesses = []
        growth_areas = []
        
        for topic, mastery_data in topics.items():
            level = mastery_data['mastery_level']
            accuracy = mastery_data['accuracy']
            readiness = mastery_data.get('readiness_for_advancement', False)
            learning_curve = mastery_data.get('learning_curve', {})
            trend = learning_curve.get('trend', 'neutral')
            
            if level >= 4:
                strengths.append({'topic': topic, 'mastery': level, 'accuracy': accuracy})
            elif level <= 1:
                weaknesses.append({'topic': topic, 'mastery': level, 'accuracy': accuracy})
            
            if trend == 'improving' or (level >= 3 and readiness):
                growth_areas.append({'topic': topic, 'mastery': level, 'trend': trend})
        
        # Sort by mastery level
        strengths.sort(key=lambda x: x['mastery'], reverse=True)
        weaknesses.sort(key=lambda x: x['accuracy'])
        
        return {
            'overall_mastery': overall['overall_mastery'],
            'overall_accuracy': overall['overall_accuracy'],
            'total_attempts': overall['total_attempts'],
            'strengths': strengths,
            'weaknesses': weaknesses,
            'growth_areas': growth_areas,
            'next_recommended_topics': self._recommend_next_topics(weaknesses, growth_areas),
            'ready_for_advancement': len(weaknesses) == 0 and overall['overall_mastery'] >= 3
        }
    
    # Helper methods
    def _get_mastery_level(self, accuracy):
        """Map accuracy to mastery level (0-5)"""
        for level, spec in self.MASTERY_LEVELS.items():
            if spec['accuracy_min'] <= accuracy <= spec['accuracy_max']:
                return level
        return 0
    
    def _get_competency_level(self, accuracy):
        """Map accuracy to competency level"""
        if accuracy < self.COMPETENCY_THRESHOLDS['emerging']:
            return 'emerging'
        elif accuracy < self.COMPETENCY_THRESHOLDS['developing']:
            return 'developing'
        elif accuracy < self.COMPETENCY_THRESHOLDS['proficient']:
            return 'proficient'
        else:
            return 'advanced'
    
    def _fit_learning_curve(self, responses):
        """
        Fit learning curve to response data
        Uses exponential model: accuracy(t) = 1 - (1 - asymptote) * exp(-rate * t)
        
        Returns: fitted curve parameters and trend
        """
        if len(responses) < 2:
            return {
                'model': 'insufficient_data',
                'trend': 'unknown',
                'points': len(responses)
            }
        
        # Calculate cumulative accuracy at each point
        points = []
        correct_so_far = 0
        for i, response in enumerate(responses):
            if response.is_correct:
                correct_so_far += 1
            accuracy = correct_so_far / (i + 1)
            points.append({'x': i + 1, 'y': accuracy})
        
        # Simple trend detection
        if len(points) >= 2:
            first_half = sum(p['y'] for p in points[:len(points)//2]) / max(1, len(points)//2)
            second_half = sum(p['y'] for p in points[len(points)//2:]) / max(1, len(points) - len(points)//2)
            
            if second_half > first_half + 0.1:
                trend = 'improving'
            elif second_half < first_half - 0.1:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        return {
            'model': 'exponential',
            'trend': trend,
            'points': points,
            'final_accuracy': points[-1]['y'] if points else 0.0
        }
    
    def _check_advancement_readiness(self, responses, accuracy, competency):
        """
        Check if student is ready to advance to next level
        
        Criteria:
        - Accuracy >= 85%
        - Positive trend in recent attempts
        - Minimum number of attempts (at least 5)
        """
        if len(responses) < 5:
            return False
        
        if accuracy < 0.85:
            return False
        
        # Check recent trend (last 5 responses)
        recent = responses[-5:]
        recent_correct = sum(1 for r in recent if r.is_correct)
        recent_accuracy = recent_correct / len(recent)
        
        return recent_accuracy >= 0.8
    
    def _get_recent_performance(self, responses, window=5):
        """Get recent performance in a sliding window"""
        recent = responses[-window:]
        if not recent:
            return {'data': [], 'accuracy': 0.0, 'trend': 'no_data'}
        
        correct = sum(1 for r in recent if r.is_correct)
        accuracy = correct / len(recent)
        
        return {
            'window': window,
            'accuracy': accuracy,
            'correct': correct,
            'total': len(recent),
            'trend': 'improving' if correct >= window * 0.8 else 'needs_practice'
        }
    
    def _recommend_next_topics(self, weaknesses, growth_areas, limit=3):
        """Recommend next topics to focus on"""
        recommendations = []
        
        # First priority: strengthen weak areas
        for weakness in weaknesses[:limit]:
            recommendations.append({
                'topic': weakness['topic'],
                'reason': 'Strengthen weak area',
                'priority': 'high',
                'current_mastery': weakness['mastery']
            })
        
        # Second priority: advance in growth areas
        for growth in growth_areas[:limit-len(recommendations)]:
            recommendations.append({
                'topic': growth['topic'],
                'reason': 'Ready for advancement',
                'priority': 'medium',
                'current_mastery': growth['mastery']
            })
        
        return recommendations
