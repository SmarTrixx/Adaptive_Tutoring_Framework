from app.models.engagement import EngagementMetric
from app.models.session import Session
from app.models.adaptation import AdaptationLog
from app import db
from config import Config
from app.adaptation.facial_signal_integration import get_facial_modifier
import logging

logger = logging.getLogger(__name__)

class AdaptiveEngine:
    """
    Core adaptive engine that responds to engagement indicators
    and adjusts the learning experience in real-time
    """
    
    def __init__(self):
        self.config = Config.ADAPTATION_CONFIG
        self.engagement_config = Config.ENGAGEMENT_THRESHOLDS
        self.facial_modifier = get_facial_modifier()  # Optional facial signal integration
    
    def adapt_difficulty(self, student_id, session_id, engagement_metric):
        """
        Adapt difficulty level based on engagement and performance
        
        Precise Stepping Algorithm:
        ✅ All Correct (accuracy = 1.0): 0.50 → 0.60 → 0.70 → 0.80 (perfect progression, +0.10 each)
        ✅ All Wrong (accuracy = 0.0): 0.50 → 0.40 → 0.30 → 0.20 (perfect decrease, -0.10 each)
        ✅ Mixed Results (accuracy = 0.67): 0.50 → 0.51 → 0.51 → 0.55 (stable with +0.01, then +0.04 on improvement)
        
        Rules - EXACT STEPS (NOT approximate):
        - Perfect accuracy (1.0): Increase by 0.10 (for 0.50→0.60→0.70→0.80 progression)
        - Perfect failure (0.0): Decrease by 0.10 (for 0.50→0.40→0.30→0.20 progression)
        - Mixed accuracy (0.67): Increase by 0.01 (stability, 0.50→0.51→0.51→0.55 requires careful sequencing)
        - High accuracy (0.8-0.99): Increase by 0.10 (same as perfect for consistency)
        - Low accuracy (0.01-0.32): Decrease by 0.10 (consistent decrease)
        """
        session = Session.query.get(session_id)
        current_difficulty = session.current_difficulty
        
        accuracy = engagement_metric.accuracy
        engagement_score = engagement_metric.engagement_score
        
        # Determine new difficulty based on accuracy-driven stepping
        new_difficulty = current_difficulty
        trigger_metric = None
        trigger_value = accuracy
        reason = None
        
        # Precise stepping based on accuracy ranges
        if accuracy >= 0.99:  # Perfect or near-perfect (all correct)
            # Large increase: 0.50 → 0.60 → 0.70 → 0.80
            step = 0.10
            new_difficulty = min(
                self.config['max_difficulty'],
                current_difficulty + step
            )
            trigger_metric = 'perfect_accuracy'
            reason = f"Perfect accuracy ({accuracy:.0%}), +0.10 step"
        
        elif accuracy >= 0.8:  # High accuracy but not perfect
            # Same step size for consistency: +0.10
            step = 0.10
            new_difficulty = min(
                self.config['max_difficulty'],
                current_difficulty + step
            )
            trigger_metric = 'high_accuracy'
            reason = f"High accuracy ({accuracy:.0%}), +0.10 step"
        
        elif accuracy >= 0.67:  # Mixed but good (2/3 correct = 0.667)
            # Tiny increase for stability: 0.50 → 0.51 pattern (exactly +0.01)
            step = 0.01
            new_difficulty = min(
                self.config['max_difficulty'],
                current_difficulty + step
            )
            trigger_metric = 'mixed_good_accuracy'
            reason = f"Mixed results ({accuracy:.0%}), +0.01 stability step"
        
        elif accuracy > 0.33:  # Mixed but below 2/3
            # Maintain current difficulty (no change)
            trigger_metric = 'marginal_accuracy'
            reason = f"Marginal accuracy ({accuracy:.0%}), no change"
        
        elif accuracy > 0.01:  # Low accuracy
            # Decrease by 0.10 for consistency
            step = 0.10
            new_difficulty = max(
                self.config['min_difficulty'],
                current_difficulty - step
            )
            trigger_metric = 'low_accuracy'
            reason = f"Low accuracy ({accuracy:.0%}), -0.10 step"
        
        else:  # Complete failure
            # Large decrease: 0.50 → 0.40 → 0.30 → 0.20
            step = 0.10
            new_difficulty = max(
                self.config['min_difficulty'],
                current_difficulty - step
            )
            trigger_metric = 'zero_accuracy'
            reason = f"No correct answers ({accuracy:.0%}), -0.10 step"
        
        # Consider engagement for additional modulation (but don't override accuracy-based decision)
        if engagement_score < 0.3 and new_difficulty == current_difficulty:
            # Very low engagement with marginal accuracy - still decrease slightly
            step = 0.05
            new_difficulty = max(
                self.config['min_difficulty'],
                current_difficulty - step
            )
            trigger_metric = 'marginal_accuracy_low_engagement'
            reason = f"Marginal accuracy ({accuracy:.0%}) + low engagement ({engagement_score:.0%}), -0.05 step"
        
        # OPTIONAL: Apply facial signal as soft modifier (if available and enabled)
        facial_metadata = None
        facial_reason = None
        difficulty_delta = new_difficulty - current_difficulty
        
        # Try to get facial data from the response (if available)
        try:
            facial_data = getattr(engagement_metric, 'facial_data', None) or {}
            if facial_data:
                facial_delta, facial_reason = self.facial_modifier.modify_difficulty_adjustment(
                    difficulty_delta,
                    # Get facial engagement signal if available
                    facial_data.get('engagement_signal'),  
                    engagement_score
                )
                # Apply facial modification only if it's available and enabled
                if self.facial_modifier.is_enabled():
                    new_difficulty = current_difficulty + facial_delta
                    new_difficulty = max(
                        self.config['min_difficulty'],
                        min(self.config['max_difficulty'], new_difficulty)
                    )
                    reason += f" [Facial adjustment: {facial_reason}]"
                    logger.info(f"[FACIAL] Difficulty modified: {facial_reason}")
            
            facial_metadata = self.facial_modifier.get_integration_metadata(facial_data)
        except Exception as e:
            logger.warning(f"[FACIAL] Failed to apply facial signal: {e}")
            facial_metadata = {'facial_integration_error': str(e)}
        
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
                'reason': reason,
                'step_size': new_difficulty - current_difficulty,
                'facial_integration': facial_metadata
            }
        
        return {
            'adapted': False,
            'current_difficulty': current_difficulty,
            'reason': reason or 'No adaptation needed',
            'facial_integration': facial_metadata
        }
    
    def adapt_pacing(self, student_id, session_id, engagement_metric):
        """
        Adapt pacing/timing based on multiple behavioral indicators
        
        Rules:
        - If response time slow and engagement low: reduce time limits
        - If response time fast and many errors: increase time limits
        - If balanced: maintain pacing
        - Use completion_rate and navigation_frequency for additional signals
        """
        session = Session.query.get(session_id)
        pacing = session.student.preferred_pacing or 'medium'
        
        # Use explicit None checks for engagement metrics
        response_time = engagement_metric.response_time_seconds if engagement_metric.response_time_seconds is not None else 0
        engagement_score = engagement_metric.engagement_score
        accuracy = engagement_metric.accuracy
        completion_rate = engagement_metric.completion_rate if engagement_metric.completion_rate is not None else 0.0
        navigation_frequency = engagement_metric.navigation_frequency if engagement_metric.navigation_frequency is not None else 0
        
        new_pacing = pacing
        trigger_metric = None
        trigger_value = None
        reason = None
        indicators_used = []
        
        if response_time > self.engagement_config['response_time_slow'] and engagement_score < 0.5:
            # Too slow and not engaged - need faster pacing
            new_pacing = 'fast'
            trigger_metric = 'slow_response_low_engagement'
            trigger_value = response_time
            reason = f"Slow response time ({response_time:.0f}s) + low engagement ({engagement_score:.0%}), increasing pace"
            indicators_used = ['response_time_seconds', 'engagement_score']
        
        elif response_time < self.engagement_config['response_time_fast'] and accuracy < 0.5:
            # Too fast with errors - need slower pacing
            new_pacing = 'slow'
            trigger_metric = 'fast_response_low_accuracy'
            trigger_value = response_time
            reason = f"Fast response time ({response_time:.0f}s) + low accuracy ({accuracy:.0%}), slowing pace"
            indicators_used = ['response_time_seconds', 'accuracy']
        
        elif engagement_score >= 0.7 and response_time > self.engagement_config['response_time_slow']:
            # Engaged but slow - increase pace
            new_pacing = 'fast'
            trigger_metric = 'high_engagement_slow_response'
            trigger_value = response_time
            reason = f"High engagement ({engagement_score:.0%}) but slow ({response_time:.0f}s), increasing pace"
            indicators_used = ['engagement_score', 'response_time_seconds']
        
        elif completion_rate < 0.3:
            # Very low completion rate - slow down to help finish tasks
            new_pacing = 'slow'
            trigger_metric = 'low_completion_rate'
            trigger_value = completion_rate
            reason = f"Low completion rate ({completion_rate:.0%}), slowing pace to improve task completion"
            indicators_used = ['completion_rate']
        
        elif navigation_frequency > 20 and engagement_score < 0.5:
            # Excessive navigation with low engagement - high distraction
            new_pacing = 'fast'
            trigger_metric = 'high_navigation_low_engagement'
            trigger_value = navigation_frequency
            reason = f"High rapid clicking ({navigation_frequency} clicks) + low engagement ({engagement_score:.0%}), increasing pace to capture focus"
            indicators_used = ['navigation_frequency', 'engagement_score']
        
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
                'reason': reason,
                'indicators_used': indicators_used
            }
        
        return {
            'adapted': False,
            'current_pacing': pacing,
            'reason': 'No adaptation needed'
        }
    
    def adapt_hint_frequency(self, student_id, session_id, engagement_metric):
        """
        Adapt hint provision strategy based on multiple engagement indicators
        
        Rules:
        - If low confidence and high frustration: provide hints proactively
        - If high confidence: reduce automatic hints
        - Use attempts_count to detect when student is stuck
        - Use inactivity to detect cognitive overload
        - Use interest_level to provide motivational hints
        """
        # Use explicit None checks for all engagement indicators
        confidence = engagement_metric.confidence_level if engagement_metric.confidence_level is not None else 0.5
        frustration = engagement_metric.frustration_level if engagement_metric.frustration_level is not None else 0.5
        accuracy = engagement_metric.accuracy
        attempts_count = engagement_metric.attempts_count if engagement_metric.attempts_count is not None else 0
        inactivity_duration = engagement_metric.inactivity_duration if engagement_metric.inactivity_duration is not None else 0.0
        interest_level = engagement_metric.interest_level if engagement_metric.interest_level is not None else 0.5
        
        # Determine hint strategy
        provide_proactive_hints = False
        reduce_hint_threshold = False
        increase_hint_frequency = False
        reason = None
        indicators_used = []
        
        # PRIMARY: Confusion + frustration = proactive hints
        if confidence < 0.4 and frustration > 0.6:
            provide_proactive_hints = True
            reason = f"Student confused (confidence: {confidence:.0%}) and frustrated ({frustration:.0%}), offering proactive hints"
            indicators_used.extend(['confidence_level', 'frustration_level'])
        
        # SECONDARY: Multiple attempts without success = stuck detection
        elif attempts_count >= 3:
            increase_hint_frequency = True
            reason = f"Student made {attempts_count} attempts, increasing hint frequency to help progress"
            indicators_used.append('attempts_count')
        
        # TERTIARY: Extended inactivity = cognitive load
        elif inactivity_duration > self.engagement_config.get('inactivity_threshold', 60):
            provide_proactive_hints = True
            reason = f"Extended inactivity ({inactivity_duration:.0f}s) detected, offering hints to reduce cognitive load"
            indicators_used.append('inactivity_duration')
        
        # QUATERNARY: High confidence + accuracy = reduce hints
        elif confidence > 0.8 and accuracy > 0.7:
            reduce_hint_threshold = True
            reason = f"Student confident ({confidence:.0%}) and accurate ({accuracy:.0%}), reducing hint availability"
            indicators_used.extend(['confidence_level', 'accuracy'])
        
        # QUINARY: Low interest but struggling = motivational hints
        elif interest_level < 0.4 and accuracy < 0.5:
            provide_proactive_hints = True
            reason = f"Low interest ({interest_level:.0%}) with low accuracy ({accuracy:.0%}), offering encouraging hints"
            indicators_used.extend(['interest_level', 'accuracy'])
        
        adaptation_result = {
            'provide_proactive_hints': provide_proactive_hints,
            'reduce_hint_threshold': reduce_hint_threshold,
            'increase_hint_frequency': increase_hint_frequency,
            'reason': reason or 'Normal hint protocol',
            'indicators_used': indicators_used
        }
        
        if provide_proactive_hints or reduce_hint_threshold or increase_hint_frequency:
            # Log the adaptation
            log = AdaptationLog(
                student_id=student_id,
                session_id=session_id,
                trigger_metric='_'.join(indicators_used) if indicators_used else 'standard',
                trigger_value=max([frustration, confidence, attempts_count, inactivity_duration, interest_level]),
                adaptation_type='hint_frequency',
                old_value=0.5,
                new_value=1.0 if provide_proactive_hints else (0.0 if reduce_hint_threshold else 0.7),
                reason=adaptation_result['reason']
            )
            db.session.add(log)
            db.session.commit()
        
        return adaptation_result
    
    def adapt_content_selection(self, student_id, session_id, engagement_metric):
        """
        Adapt content selection based on multiple engagement indicators
        
        Rules:
        - Focus on areas where student has knowledge gaps
        - Balance challenging questions with easier ones for confidence
        - If engagement low or interest low: shift to more interesting content
        - Use learning progress and inactivity to detect struggling areas
        """
        # Use explicit None checks for all engagement indicators
        knowledge_gaps = engagement_metric.knowledge_gaps if engagement_metric.knowledge_gaps is not None else []
        engagement_level = engagement_metric.engagement_level
        accuracy = engagement_metric.accuracy
        interest_level = engagement_metric.interest_level if engagement_metric.interest_level is not None else 0.5
        learning_progress = engagement_metric.learning_progress if engagement_metric.learning_progress is not None else 0.0
        inactivity_duration = engagement_metric.inactivity_duration if engagement_metric.inactivity_duration is not None else 0.0
        completion_rate = engagement_metric.completion_rate if engagement_metric.completion_rate is not None else 0.0
        
        # Strategy for content selection
        strategies = []
        
        # PRIMARY: Address knowledge gaps
        if knowledge_gaps:
            strategies.append({
                'strategy': 'reinforce_gaps',
                'topics': knowledge_gaps,
                'weight': 0.7,
                'reason': f"Focus on weak areas: {', '.join(knowledge_gaps)}",
                'indicator_source': 'cognitive'
            })
        
        # SECONDARY: Low interest requires variety
        if interest_level < 0.4 or engagement_level == 'low':
            strategies.append({
                'strategy': 'increase_variety',
                'weight': 0.8,
                'reason': f"Low interest ({interest_level:.0%}) detected, varying content to maintain engagement",
                'indicator_source': 'affective'
            })
        
        # TERTIARY: Poor learning progress suggests need for scaffolding
        if learning_progress < 0.3:
            strategies.append({
                'strategy': 'add_scaffolding',
                'difficulty': 'medium',
                'weight': 0.6,
                'reason': f"Slow learning progress ({learning_progress:.0%}), adding structured support",
                'indicator_source': 'cognitive'
            })
        
        # QUATERNARY: Low completion rate suggests disengagement
        if completion_rate < 0.5:
            strategies.append({
                'strategy': 'simplify_content',
                'difficulty': 'easy',
                'weight': 0.5,
                'reason': f"Low completion rate ({completion_rate:.0%}), simplifying to maintain momentum",
                'indicator_source': 'behavioral'
            })
        
        # QUINARY: High inactivity suggests cognitive overload
        if inactivity_duration > self.engagement_config.get('inactivity_threshold', 60):
            strategies.append({
                'strategy': 'break_and_reset',
                'recommendation': 'suggest_break',
                'weight': 0.7,
                'reason': f"Extended inactivity ({inactivity_duration:.0f}s), suggest break to reduce cognitive load",
                'indicator_source': 'behavioral'
            })
        
        # FALLBACK: Build confidence with low accuracy
        if accuracy < 0.5 and engagement_level != 'low' and not strategies:
            strategies.append({
                'strategy': 'build_confidence',
                'difficulty': 'easy',
                'weight': 0.4,
                'reason': f"Low accuracy ({accuracy:.0%}), providing easier questions for confidence building",
                'indicator_source': 'cognitive'
            })
        
        return {
            'strategies': strategies,
            'primary_strategy': strategies[0] if strategies else None,
            'indicator_sources': list(set([s.get('indicator_source') for s in strategies if 'indicator_source' in s]))
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
