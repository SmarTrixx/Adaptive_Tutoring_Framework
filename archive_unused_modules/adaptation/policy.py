# Adaptive Decision Policy
# RL-inspired policy that determines tutoring actions based on engagement + performance + difficulty

from enum import Enum
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from app.engagement.fusion import FusedEngagementState, EngagementState
from app.adaptation.performance_window import WindowPerformanceTracker
from app.engagement.indicators import EngagementIndicators


class TutoringAction(Enum):
    """Available tutoring actions."""
    INCREASE_DIFFICULTY = "increase_difficulty"
    DECREASE_DIFFICULTY = "decrease_difficulty"
    MAINTAIN_DIFFICULTY = "maintain_difficulty"
    PROVIDE_HINT = "provide_hint"
    GIVE_MOTIVATIONAL_FEEDBACK = "give_motivational_feedback"
    SUGGEST_SHORT_BREAK = "suggest_short_break"


@dataclass
class AdaptiveDecision:
    """
    Decision output from adaptive policy.
    """
    primary_action: TutoringAction
    secondary_actions: List[TutoringAction]
    
    difficulty_delta: float  # Change to apply to system difficulty (-0.15 to +0.15)
    
    # Reasoning and logging
    rationale: str
    engagement_influenced: bool  # Was engagement a factor?
    
    timestamp: datetime
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'primary_action': self.primary_action.value,
            'secondary_actions': [a.value for a in self.secondary_actions],
            'difficulty_delta': round(self.difficulty_delta, 3),
            'rationale': self.rationale,
            'engagement_influenced': self.engagement_influenced,
            'timestamp': self.timestamp.isoformat()
        }


class AdaptivePolicyEngine:
    """
    Window-based deterministic policy for adaptive difficulty.
    
    Core principle: Make difficulty adjustments every 5 questions based on:
    1. Window accuracy (performance)
    2. Fused engagement state
    3. Response time behavior
    
    Ensures stability and interpretability.
    """
    
    # Window-based constants
    WINDOW_SIZE = 5  # Decisions every 5 questions
    
    # Difficulty adjustment (per 5-question window)
    LARGE_STEP = 0.10      # Strong evidence: +0.10 or -0.10
    SMALL_STEP = 0.05      # Moderate evidence: +0.05 or -0.05
    TINY_STEP = 0.025      # Weak evidence: +0.025 or -0.025
    
    # Performance thresholds (accuracy-based)
    EXCELLENT_PERFORMANCE = 0.85    # 4-5 correct per window
    GOOD_PERFORMANCE = 0.70         # 3-4 correct per window
    FAIR_PERFORMANCE = 0.50         # 2-3 correct per window
    POOR_PERFORMANCE = 0.30         # 1-2 correct per window
    
    # Engagement thresholds
    HIGH_ENGAGEMENT = 0.70
    MODERATE_ENGAGEMENT = 0.50
    LOW_ENGAGEMENT = 0.25
    
    # Anti-oscillation: track last 3 window decisions
    OSCILLATION_WINDOW = 3
    
    def __init__(self):
        """Initialize policy engine."""
        self.recent_decisions: List[AdaptiveDecision] = []
        self.break_suggestions_made = 0
        self.last_break_time = None
    
    
    def decide(self, 
               engagement_state: FusedEngagementState,
               window_performance: float,
               current_difficulty: float,
               window_sample_size: int = 5) -> AdaptiveDecision:
        """
        Decide tutoring actions based on current state.
        
        Args:
            engagement_state: FusedEngagementState from fusion engine
            window_performance: Performance score from window evaluator (0.0-1.0)
            current_difficulty: Current system difficulty (0.0-1.0)
            window_sample_size: Number of questions in window
            
        Returns:
            AdaptiveDecision: Action(s) to take
        """
        
        decision = AdaptiveDecision(
            primary_action=TutoringAction.MAINTAIN_DIFFICULTY,
            secondary_actions=[],
            difficulty_delta=0.0,
            rationale="",
            engagement_influenced=False,
            timestamp=datetime.utcnow()
        )
        
        # Validate inputs
        if not engagement_state or engagement_state.engagement_score < 0:
            decision.rationale = "Invalid engagement state"
            return decision
        
        # STEP 1: Determine difficulty adjustment based on performance + engagement
        difficulty_delta, difficulty_rationale = self._adjust_difficulty(
            engagement_state, window_performance, current_difficulty
        )
        
        if abs(difficulty_delta) > 0.001:  # Meaningful change
            decision.difficulty_delta = difficulty_delta
            decision.engagement_influenced = True
            
            if difficulty_delta > 0:
                decision.primary_action = TutoringAction.INCREASE_DIFFICULTY
                decision.rationale = f"Increase difficulty (+{difficulty_delta:.3f}). {difficulty_rationale}"
            else:
                decision.primary_action = TutoringAction.DECREASE_DIFFICULTY
                decision.rationale = f"Decrease difficulty ({difficulty_delta:.3f}). {difficulty_rationale}"
        else:
            decision.primary_action = TutoringAction.MAINTAIN_DIFFICULTY
            decision.rationale = f"Maintain difficulty. {difficulty_rationale}"
        
        # STEP 2: Determine secondary supportive actions
        secondary = self._suggest_secondary_actions(
            engagement_state, window_performance
        )
        decision.secondary_actions = secondary
        
        # STEP 3: Add to recent decisions for oscillation detection
        self.recent_decisions.append(decision)
        if len(self.recent_decisions) > self.OSCILLATION_WINDOW:
            self.recent_decisions.pop(0)
        
        return decision
    
    
    def _adjust_difficulty(self, 
                          engagement_state: FusedEngagementState,
                          window_performance: float,
                          current_difficulty: float) -> Tuple[float, str]:
        """
        Determine difficulty adjustment based on WINDOW performance and engagement.
        
        Decision matrix:
        - Performance (accuracy): main signal
        - Engagement: modulates aggressiveness
        - Response time: detects rushing/struggling
        
        Returns:
            (difficulty_delta, rationale)
        """
        
        engagement = engagement_state.engagement_score
        response_behavior = engagement_state.behavioral_score  # Low = struggling
        
        # RUSHING DETECTION: Very fast responses (< 2 seconds average)
        # when accuracy is high suggests potential guessing without effort
        # We detect this through rapid_guessing_probability in indicators,
        # or infer it from very low response times with high accuracy
        rushing_suspected = response_behavior > 0.95  # Suspiciously perfect behavior
        
        # DECISION MATRIX: Performance × Engagement
        
        # EXCELLENT PERFORMANCE (≥85% accuracy)
        if window_performance >= self.EXCELLENT_PERFORMANCE:
            if engagement >= self.HIGH_ENGAGEMENT:
                # Excellent + engaged: push hard
                delta = self.LARGE_STEP
                reason = "Excellent accuracy (≥85%) + engaged → +0.10 increase"
            elif engagement >= self.MODERATE_ENGAGEMENT:
                # Excellent + moderate engagement: push moderately
                if rushing_suspected:
                    # But if behavior seems too perfect (potential rushing), be cautious
                    delta = self.TINY_STEP
                    reason = "Excellent accuracy + moderate engagement, but suspiciously perfect behavior → +0.025 (cautious)"
                else:
                    delta = self.SMALL_STEP
                    reason = "Excellent accuracy (≥85%) + moderate engagement → +0.05 increase"
            else:
                # Excellent + low engagement: still increase but cautiously
                delta = self.SMALL_STEP
                reason = "Excellent accuracy (≥85%) despite low engagement → +0.05 (monitor engagement)"
        
        # GOOD PERFORMANCE (70-84% accuracy)
        elif window_performance >= self.GOOD_PERFORMANCE:
            if engagement >= self.HIGH_ENGAGEMENT:
                # Good + engaged: increase moderately
                delta = self.SMALL_STEP
                reason = "Good accuracy (70-84%) + engaged → +0.05 increase"
            elif engagement >= self.MODERATE_ENGAGEMENT:
                # Good + moderate: maintain (safe)
                if rushing_suspected:
                    # But if behavior is suspiciously perfect, stay cautious
                    delta = -self.TINY_STEP
                    reason = "Good accuracy but suspiciously perfect behavior → -0.025 (monitor engagement)"
                else:
                    delta = 0.0
                    reason = "Good accuracy (70-84%) + moderate engagement → maintain"
            else:
                # Good + low: slight decrease to re-engage
                delta = -self.TINY_STEP
                reason = "Good accuracy but disengaged → -0.025 (re-engage)"
        
        # FAIR PERFORMANCE (50-69% accuracy)
        elif window_performance >= self.FAIR_PERFORMANCE:
            if engagement >= self.HIGH_ENGAGEMENT:
                # Fair but engaged: maintain (let engagement help)
                delta = 0.0
                reason = "Fair accuracy (50-69%) but engaged → maintain"
            elif engagement >= self.MODERATE_ENGAGEMENT:
                # Fair + moderate: slight decrease (getting harder)
                delta = -self.TINY_STEP
                reason = "Fair accuracy (50-69%) + moderate engagement → -0.025 (slight decrease)"
            else:
                # Fair + low: decrease to reduce cognitive load
                delta = -self.SMALL_STEP
                reason = "Fair accuracy + low engagement → -0.05 (reduce load)"
        
        # POOR PERFORMANCE (<50% accuracy)
        else:
            if engagement >= self.MODERATE_ENGAGEMENT:
                # Poor but engaged: decrease (too hard, try with easier content)
                delta = -self.SMALL_STEP
                reason = "Poor accuracy (<50%) despite engagement → -0.05 (too hard)"
            else:
                # Poor + low: decrease significantly (struggling)
                delta = -self.LARGE_STEP
                reason = "Poor accuracy (<50%) + low engagement → -0.10 (struggling)"
        
        # OSCILLATION DAMPING: Prevent flip-flopping
        if len(self.recent_decisions) >= 2:
            last_deltas = [d.difficulty_delta for d in self.recent_decisions[-2:]]
            # If last 2 were opposite direction (one increase, one decrease), dampen
            if len(last_deltas) == 2 and last_deltas[0] * last_deltas[1] < -0.001:
                delta = delta * 0.5
                reason += " [Oscillation damped to ×0.5]"
        
        # MOMENTUM: If trending up, encourage continuation (but not too aggressively)
        if len(self.recent_decisions) >= 3:
            last_three = [d.difficulty_delta for d in self.recent_decisions[-3:]]
            # If all three were increases, we have momentum
            if all(d > 0.001 for d in last_three):
                # Allow larger step, but not unlimited
                if delta > 0:
                    delta = min(delta * 1.1, self.LARGE_STEP)
                    reason += " [Momentum boost applied]"
            # If all three were decreases, we have downward momentum
            elif all(d < -0.001 for d in last_three):
                # Already decreasing, don't accelerate too much
                if delta < 0:
                    delta = max(delta * 1.05, -self.LARGE_STEP)
        
        # BOUNDS CHECKING: Ensure valid difficulty range
        new_difficulty = current_difficulty + delta
        
        if new_difficulty < 0.0:
            delta = -current_difficulty
            reason += " [Clamped to min: 0.0]"
        elif new_difficulty > 1.0:
            delta = 1.0 - current_difficulty
            reason += " [Clamped to max: 1.0]"
        
        return delta, reason
    
    
    def _suggest_secondary_actions(self,
                                  engagement_state: FusedEngagementState,
                                  window_performance: float) -> List[TutoringAction]:
        """
        Suggest secondary supportive actions.
        """
        actions = []
        
        # Rule 1: Frustration → Hint
        if engagement_state.affective_score < 0.3:  # High frustration signal
            actions.append(TutoringAction.PROVIDE_HINT)
        
        # Rule 2: Disengagement → Motivational feedback
        if engagement_state.categorical_state == EngagementState.DISENGAGED:
            actions.append(TutoringAction.GIVE_MOTIVATIONAL_FEEDBACK)
        
        # Rule 3: Struggling with low engagement → Suggest break
        if (engagement_state.categorical_state in 
            [EngagementState.STRUGGLING, EngagementState.DISENGAGED] and
            window_performance < self.FAIR_PERFORMANCE):
            
            # Don't suggest breaks too frequently (max once per session)
            if self.break_suggestions_made < 1:
                actions.append(TutoringAction.SUGGEST_SHORT_BREAK)
                self.break_suggestions_made += 1
                self.last_break_time = datetime.utcnow()
        
        # Rule 4: Recovery after break → Resume with encouragement
        if (self.last_break_time and 
            (datetime.utcnow() - self.last_break_time).total_seconds() > 300):  # 5 min passed
            if engagement_state.engagement_score > self.MODERATE_ENGAGEMENT:
                actions.append(TutoringAction.GIVE_MOTIVATIONAL_FEEDBACK)
        
        # Rule 5: Consistent improvement → Positive reinforcement
        if engagement_state.cognitive_score > 0.8:  # Improving accuracy
            if TutoringAction.GIVE_MOTIVATIONAL_FEEDBACK not in actions:
                actions.append(TutoringAction.GIVE_MOTIVATIONAL_FEEDBACK)
        
        return actions
    
    
    def reset_session(self):
        """Reset for new session."""
        self.recent_decisions = []
        self.break_suggestions_made = 0
        self.last_break_time = None


class PolicyLogger:
    """Logs policy decisions for debugging/analysis."""
    
    @staticmethod
    def log_decision(session_id: str, decision: AdaptiveDecision, 
                    current_difficulty: float):
        """Log adaptive policy decision."""
        print(f"\n🎓 ADAPTIVE POLICY DECISION - Session {session_id}")
        print("="*70)
        
        print(f"\n📍 PRIMARY ACTION: {decision.primary_action.value.upper()}")
        if decision.difficulty_delta != 0:
            new_diff = current_difficulty + decision.difficulty_delta
            print(f"   Difficulty: {current_difficulty:.3f} → {new_diff:.3f} ({decision.difficulty_delta:+.3f})")
        
        if decision.secondary_actions:
            print(f"\n🤝 SECONDARY ACTIONS:")
            for action in decision.secondary_actions:
                print(f"   • {action.value}")
        
        print(f"\n💡 RATIONALE:")
        print(f"   {decision.rationale}")
        
        print(f"\n📊 ENGAGEMENT INFLUENCE: {'Yes' if decision.engagement_influenced else 'No'}")
        
        print("="*70 + "\n")
