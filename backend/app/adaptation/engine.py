from app.models.engagement import EngagementMetric
from app.models.session import Session
from app.models.adaptation import AdaptationLog
from app import db
from config import Config

class AdaptiveEngine:
    """
    Core adaptive engine that responds to engagement indicators
    and adjusts the learning experience in real-time
    """
    
    def __init__(self):
        self.config = Config.ADAPTATION_CONFIG
        self.engagement_config = Config.ENGAGEMENT_THRESHOLDS
    
    def adapt_difficulty(self, student_id, session_id, engagement_metric):
        """
        Adapt difficulty level based on engagement and performance
        
        Rules:
        - If accuracy high and engagement high: increase difficulty
        - If accuracy low or engagement low: decrease difficulty
        - If engagement medium: maintain current difficulty
        """
        session = Session.query.get(session_id)
        current_difficulty = session.current_difficulty
        
        accuracy = engagement_metric.accuracy
        engagement_score = engagement_metric.engagement_score
        
        # Determine new difficulty
        new_difficulty = current_difficulty
        trigger_metric = None
        trigger_value = None
        reason = None
        
        if accuracy >= 0.8 and engagement_score >= 0.7:
            # Strong performance - increase difficulty
            new_difficulty = min(
                self.config['max_difficulty'],
                current_difficulty + self.config['difficulty_step']
            )
            trigger_metric = 'high_accuracy_high_engagement'
            trigger_value = accuracy
            reason = f"Student performing well (accuracy: {accuracy:.2%}), increased difficulty"
        
        elif accuracy <= 0.4 or engagement_score <= 0.3:
            # Poor performance or low engagement - decrease difficulty
            new_difficulty = max(
                self.config['min_difficulty'],
                current_difficulty - self.config['difficulty_step']
            )
            trigger_metric = 'low_accuracy_or_engagement'
            trigger_value = min(accuracy, engagement_score)
            reason = f"Student struggling (accuracy: {accuracy:.2%}, engagement: {engagement_score:.2%}), decreased difficulty"
        
        # Apply the adaptation
        if new_difficulty != current_difficulty:
            session.current_difficulty = new_difficulty
            db.session.commit()
            
            # Log the adaptation
            log = AdaptationLog(
                student_id=student_id,
                session_id=session_id,
                trigger_metric=trigger_metric,
                trigger_value=trigger_value,
                adaptation_type='difficulty',
                old_value=current_difficulty,
                new_value=new_difficulty,
                reason=reason
            )
            db.session.add(log)
            db.session.commit()
            
            return {
                'adapted': True,
                'old_difficulty': current_difficulty,
                'new_difficulty': new_difficulty,
                'reason': reason
            }
        
        return {
            'adapted': False,
            'current_difficulty': current_difficulty,
            'reason': 'No adaptation needed'
        }
    
    def adapt_pacing(self, student_id, session_id, engagement_metric):
        """
        Adapt pacing/timing based on engagement
        
        Rules:
        - If response time slow and engagement low: reduce time limits
        - If response time fast and many errors: increase time limits
        - If balanced: maintain pacing
        """
        session = Session.query.get(session_id)
        pacing = session.student.preferred_pacing or 'medium'
        
        response_time = engagement_metric.response_time_seconds or 0
        engagement_score = engagement_metric.engagement_score
        accuracy = engagement_metric.accuracy
        
        new_pacing = pacing
        trigger_metric = None
        trigger_value = None
        reason = None
        
        if response_time > self.engagement_config['response_time_slow'] and engagement_score < 0.5:
            # Too slow and not engaged - need faster pacing
            new_pacing = 'fast'
            trigger_metric = 'slow_response_low_engagement'
            trigger_value = response_time
            reason = "Student responding slowly, increasing pace to maintain engagement"
        
        elif response_time < self.engagement_config['response_time_fast'] and accuracy < 0.5:
            # Too fast with errors - need slower pacing
            new_pacing = 'slow'
            trigger_metric = 'fast_response_low_accuracy'
            trigger_value = response_time
            reason = "Student rushing through questions, slowing pace"
        
        elif engagement_score >= 0.7 and response_time > self.engagement_config['response_time_slow']:
            # Engaged but slow - increase pace
            new_pacing = 'fast'
            trigger_metric = 'high_engagement_slow_response'
            trigger_value = response_time
            reason = "Student engaged but slow, increasing pace"
        
        # Apply the adaptation
        if new_pacing != pacing:
            session.student.preferred_pacing = new_pacing
            db.session.commit()
            
            # Log the adaptation
            log = AdaptationLog(
                student_id=student_id,
                session_id=session_id,
                trigger_metric=trigger_metric,
                trigger_value=trigger_value,
                adaptation_type='pacing',
                old_value=self._pacing_to_float(pacing),
                new_value=self._pacing_to_float(new_pacing),
                reason=reason
            )
            db.session.add(log)
            db.session.commit()
            
            return {
                'adapted': True,
                'old_pacing': pacing,
                'new_pacing': new_pacing,
                'reason': reason
            }
        
        return {
            'adapted': False,
            'current_pacing': pacing,
            'reason': 'No adaptation needed'
        }
    
    def adapt_hint_frequency(self, student_id, session_id, engagement_metric):
        """
        Adapt hint provision strategy based on engagement
        
        Rules:
        - If low confidence and high frustration: provide hints proactively
        - If high confidence: reduce automatic hints
        - If moderate: follow normal hint protocol
        """
        confidence = engagement_metric.confidence_level or 0.5
        frustration = engagement_metric.frustration_level or 0.5
        accuracy = engagement_metric.accuracy
        
        # Determine hint strategy
        provide_proactive_hints = False
        reduce_hint_threshold = False
        reason = None
        
        if confidence < 0.4 and frustration > 0.6:
            provide_proactive_hints = True
            reason = "Student confused and frustrated, offering proactive hints"
        elif confidence > 0.8 and accuracy > 0.7:
            reduce_hint_threshold = True
            reason = "Student confident and accurate, reducing hint availability"
        
        adaptation_result = {
            'provide_proactive_hints': provide_proactive_hints,
            'reduce_hint_threshold': reduce_hint_threshold,
            'reason': reason or 'Normal hint protocol'
        }
        
        if provide_proactive_hints or reduce_hint_threshold:
            # Log the adaptation
            log = AdaptationLog(
                student_id=student_id,
                session_id=session_id,
                trigger_metric='confidence_frustration',
                trigger_value=frustration,
                adaptation_type='hint_frequency',
                old_value=0.5,
                new_value=1.0 if provide_proactive_hints else 0.0,
                reason=adaptation_result['reason']
            )
            db.session.add(log)
            db.session.commit()
        
        return adaptation_result
    
    def adapt_content_selection(self, student_id, session_id, engagement_metric):
        """
        Adapt content selection based on knowledge gaps and engagement
        
        Rules:
        - Focus on areas where student has knowledge gaps
        - Balance challenging questions with easier ones for confidence
        - If engagement low: shift to more interesting content
        """
        knowledge_gaps = engagement_metric.knowledge_gaps or []
        engagement_level = engagement_metric.engagement_level
        accuracy = engagement_metric.accuracy
        
        # Strategy for content selection
        strategies = []
        
        if knowledge_gaps:
            strategies.append({
                'strategy': 'reinforce_gaps',
                'topics': knowledge_gaps,
                'weight': 0.6,
                'reason': f"Focus on weak areas: {', '.join(knowledge_gaps)}"
            })
        
        if engagement_level == 'low':
            strategies.append({
                'strategy': 'increase_variety',
                'weight': 0.7,
                'reason': "Low engagement detected, varying content to maintain interest"
            })
        
        if accuracy < 0.5 and engagement_level != 'low':
            strategies.append({
                'strategy': 'build_confidence',
                'difficulty': 'easy',
                'weight': 0.4,
                'reason': "Low accuracy detected, providing easier questions for confidence building"
            })
        
        return {
            'strategies': strategies,
            'primary_strategy': strategies[0] if strategies else None
        }
    
    def get_adaptation_recommendations(self, student_id, session_id):
        """
        Get all adaptation recommendations for a student's current session
        """
        session = Session.query.get(session_id)
        if not session:
            return {'error': 'Session not found'}, 404
        
        # Get latest engagement metric
        metric = EngagementMetric.query.filter_by(
            session_id=session_id
        ).order_by(EngagementMetric.timestamp.desc()).first()
        
        if not metric:
            return {'error': 'No engagement metrics found'}, 404
        
        recommendations = {
            'difficulty': self.adapt_difficulty(student_id, session_id, metric),
            'pacing': self.adapt_pacing(student_id, session_id, metric),
            'hints': self.adapt_hint_frequency(student_id, session_id, metric),
            'content': self.adapt_content_selection(student_id, session_id, metric)
        }
        
        return recommendations
    
    def _pacing_to_float(self, pacing):
        """Convert pacing string to float value"""
        pacing_map = {'slow': 0.3, 'medium': 0.5, 'fast': 0.7}
        return pacing_map.get(pacing, 0.5)
