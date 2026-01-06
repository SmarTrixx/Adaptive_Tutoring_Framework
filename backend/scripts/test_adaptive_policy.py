# Test: Adaptive Decision Policy
# Tests RL-inspired policy decisions based on engagement + performance + difficulty

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime
from app.engagement.indicators import EngagementIndicators
from app.engagement.fusion import (
    EngagementFusionEngine, FusedEngagementState, EngagementState
)
from app.adaptation.policy import (
    AdaptivePolicyEngine, TutoringAction, PolicyLogger
)


def create_indicators_scenario(behavioral, cognitive, affective, window_size=5):
    """Helper: Create EngagementIndicators."""
    indicators = EngagementIndicators()
    
    indicators.response_time_deviation = 0.5 - behavioral * 0.5
    indicators.hint_usage_count = int((1 - behavioral) * 3)
    indicators.rapid_guessing_probability = 1 - behavioral
    indicators.inactivity_duration = (1 - behavioral) * 60
    
    indicators.accuracy_trend = cognitive - 0.5
    indicators.consistency_score = cognitive
    indicators.inferred_cognitive_load = 1 - cognitive
    
    indicators.frustration_probability = 1 - affective
    indicators.confusion_probability = 1 - affective
    indicators.boredom_probability = 1 - affective
    
    indicators.window_size = window_size
    indicators.is_valid = True
    
    return indicators


def create_fused_state(behavioral, cognitive, affective):
    """Helper: Create FusedEngagementState from indicators."""
    indicators = create_indicators_scenario(behavioral, cognitive, affective)
    engine = EngagementFusionEngine()
    return engine.fuse(indicators)


def test_excellent_performance_high_engagement():
    """Test: Excellent performance + high engagement → increase difficulty."""
    print("\n" + "="*70)
    print("TEST 1: Excellent Performance + High Engagement")
    print("="*70)
    
    # Scenario: Student doing very well and engaged
    fused = create_fused_state(
        behavioral=0.85,  # Consistent, confident
        cognitive=0.85,   # Improving, good load
        affective=0.85    # Happy, not frustrated
    )
    
    policy = AdaptivePolicyEngine()
    decision = policy.decide(
        engagement_state=fused,
        window_performance=0.90,  # Excellent
        current_difficulty=0.50,
        window_sample_size=5
    )
    
    print(f"\nEngagement Score: {fused.engagement_score:.4f}")
    print(f"Window Performance: 0.90 (Excellent)")
    print(f"Current Difficulty: 0.50")
    
    print(f"\nDecision:")
    print(f"  Primary Action: {decision.primary_action.value}")
    print(f"  Expected: increase_difficulty")
    print(f"  Status: {'✓' if decision.primary_action == TutoringAction.INCREASE_DIFFICULTY else '✗'}")
    
    print(f"  Difficulty Delta: {decision.difficulty_delta:.3f}")
    print(f"  Expected: > 0.10 (substantial increase)")
    print(f"  Status: {'✓' if decision.difficulty_delta > 0.10 else '✗'}")
    
    print(f"  Engagement Influenced: {decision.engagement_influenced}")
    print(f"  Status: {'✓' if decision.engagement_influenced else '✗'}")


def test_poor_performance_low_engagement():
    """Test: Poor performance + low engagement → decrease difficulty + support."""
    print("\n" + "="*70)
    print("TEST 2: Poor Performance + Low Engagement")
    print("="*70)
    
    # Scenario: Student struggling and disengaged
    fused = create_fused_state(
        behavioral=0.25,  # Variable, many hints
        cognitive=0.20,   # Declining, overwhelmed
        affective=0.20    # Frustrated
    )
    
    policy = AdaptivePolicyEngine()
    decision = policy.decide(
        engagement_state=fused,
        window_performance=0.25,  # Poor
        current_difficulty=0.70,
        window_sample_size=5
    )
    
    print(f"\nEngagement Score: {fused.engagement_score:.4f}")
    print(f"Window Performance: 0.25 (Poor)")
    print(f"Current Difficulty: 0.70")
    
    print(f"\nDecision:")
    print(f"  Primary Action: {decision.primary_action.value}")
    print(f"  Expected: decrease_difficulty")
    print(f"  Status: {'✓' if decision.primary_action == TutoringAction.DECREASE_DIFFICULTY else '✗'}")
    
    print(f"  Difficulty Delta: {decision.difficulty_delta:.3f}")
    print(f"  Expected: < -0.05 (decrease)")
    print(f"  Status: {'✓' if decision.difficulty_delta < -0.05 else '✗'}")
    
    print(f"\nSecondary Actions:")
    for action in decision.secondary_actions:
        print(f"  • {action.value}")
    
    print(f"  Expected: hint or motivational feedback")
    expected_actions = [TutoringAction.PROVIDE_HINT, TutoringAction.GIVE_MOTIVATIONAL_FEEDBACK]
    found = any(action in expected_actions for action in decision.secondary_actions)
    print(f"  Status: {'✓' if found else '✗'}")


def test_engagement_modulates_difficulty():
    """Test: Engagement modulates difficulty adjustment magnitude."""
    print("\n" + "="*70)
    print("TEST 3: Engagement Modulates Difficulty")
    print("="*70)
    
    # Same performance, different engagement
    high_eng = create_fused_state(0.80, 0.80, 0.80)
    low_eng = create_fused_state(0.30, 0.80, 0.30)
    
    policy = AdaptivePolicyEngine()
    
    # Both at excellent performance
    decision_high = policy.decide(high_eng, 0.85, 0.50, 5)
    policy = AdaptivePolicyEngine()  # Reset
    decision_low = policy.decide(low_eng, 0.85, 0.50, 5)
    
    print(f"\nBoth at Excellent Performance (0.85)")
    print(f"\nHigh Engagement (0.80):")
    print(f"  Action: {decision_high.primary_action.value}")
    print(f"  Delta: {decision_high.difficulty_delta:.3f}")
    print(f"  Expected: INCREASE_DIFFICULTY with larger delta")
    
    print(f"\nLow Engagement (0.30):")
    print(f"  Action: {decision_low.primary_action.value}")
    print(f"  Delta: {decision_low.difficulty_delta:.3f}")
    print(f"  Expected: MAINTAIN_DIFFICULTY (engagement-first)")
    
    print(f"\nStatus: {'✓' if decision_high.difficulty_delta > decision_low.difficulty_delta else '✗'}")
    print(f"  (High engagement should increase more than low)")


def test_anti_oscillation():
    """Test: Policy avoids oscillating difficulty up and down."""
    print("\n" + "="*70)
    print("TEST 4: Anti-Oscillation Protection")
    print("="*70)
    
    # Create state that causes difficulty changes
    moderate = create_fused_state(0.50, 0.50, 0.50)
    
    policy = AdaptivePolicyEngine()
    
    # Decision 1: Increase
    decision1 = policy.decide(moderate, 0.80, 0.50, 5)
    print(f"\nDecision 1 (good performance):")
    print(f"  Action: {decision1.primary_action.value}")
    print(f"  Delta: {decision1.difficulty_delta:.3f}")
    
    # Decision 2: Immediately after, poor performance
    decision2 = policy.decide(moderate, 0.20, 0.60, 5)
    print(f"\nDecision 2 (poor performance after increase):")
    print(f"  Action: {decision2.primary_action.value}")
    print(f"  Delta: {decision2.difficulty_delta:.3f}")
    print(f"  Raw Delta would be: -0.05, Damped to: {decision2.difficulty_delta:.3f}")
    print(f"  Expected: Damped (less aggressive decrease to avoid ping-ponging)")
    
    # Check if oscillation was detected
    if len(policy.recent_decisions) >= 2:
        last_deltas = [d.difficulty_delta for d in policy.recent_decisions[-2:]]
        is_oscillating = last_deltas[0] * last_deltas[1] < 0
        print(f"\nOscillation Detected: {is_oscillating}")
        print(f"Status: {'✓' if is_oscillating else '✗'} (should detect opposite directions)")


def test_boundary_clamping():
    """Test: Difficulty changes respect [0, 1] bounds."""
    print("\n" + "="*70)
    print("TEST 5: Boundary Clamping")
    print("="*70)
    
    excellent = create_fused_state(0.90, 0.90, 0.90)
    terrible = create_fused_state(0.10, 0.10, 0.10)
    
    policy = AdaptivePolicyEngine()
    
    # Try to increase from already high difficulty
    decision_high = policy.decide(excellent, 0.95, 0.95, 5)
    print(f"\nAt difficulty 0.95, trying to increase:")
    print(f"  Delta: {decision_high.difficulty_delta:.3f}")
    print(f"  New difficulty would be: {0.95 + decision_high.difficulty_delta:.3f}")
    print(f"  Expected: Clamped to 1.0, Delta = 0.05")
    print(f"  Status: {'✓' if abs((0.95 + decision_high.difficulty_delta) - 1.0) < 0.001 else '✗'}")
    
    # Try to decrease from already low difficulty
    policy = AdaptivePolicyEngine()
    decision_low = policy.decide(terrible, 0.10, 0.05, 5)
    print(f"\nAt difficulty 0.05, trying to decrease:")
    print(f"  Delta: {decision_low.difficulty_delta:.3f}")
    print(f"  New difficulty would be: {0.05 + decision_low.difficulty_delta:.3f}")
    print(f"  Expected: Clamped to 0.0, Delta = -0.05")
    print(f"  Status: {'✓' if abs((0.05 + decision_low.difficulty_delta) - 0.0) < 0.001 else '✗'}")


def test_fair_performance_consistency():
    """Test: Fair performance with engagement → maintain."""
    print("\n" + "="*70)
    print("TEST 6: Fair Performance + Engagement → Maintain")
    print("="*70)
    
    # Scenario: Fair performance but student is engaged
    fused = create_fused_state(0.70, 0.65, 0.70)
    
    policy = AdaptivePolicyEngine()
    decision = policy.decide(
        engagement_state=fused,
        window_performance=0.60,  # Fair
        current_difficulty=0.50,
        window_sample_size=5
    )
    
    print(f"\nEngagement Score: {fused.engagement_score:.4f}")
    print(f"Window Performance: 0.60 (Fair)")
    print(f"Current Difficulty: 0.50")
    
    print(f"\nDecision:")
    print(f"  Primary Action: {decision.primary_action.value}")
    print(f"  Difficulty Delta: {decision.difficulty_delta:.3f}")
    print(f"  Expected: MAINTAIN_DIFFICULTY (δ ≈ 0.0)")
    print(f"  Status: {'✓' if abs(decision.difficulty_delta) < 0.02 else '✗'}")


def test_hint_suggestion():
    """Test: Frustration leads to hint suggestion."""
    print("\n" + "="*70)
    print("TEST 7: Frustration Detection → Hint Suggestion")
    print("="*70)
    
    # Scenario: Low performance, hints not helping
    fused = create_fused_state(0.25, 0.30, 0.25)
    
    policy = AdaptivePolicyEngine()
    decision = policy.decide(fused, 0.25, 0.50, 5)
    
    print(f"\nEngagement: {fused.engagement_score:.4f}")
    print(f"Affective Score: {fused.affective_score:.4f}")
    print(f"Performance: 0.25 (Poor)")
    
    print(f"\nSecondary Actions:")
    for action in decision.secondary_actions:
        print(f"  • {action.value}")
    
    has_hint = TutoringAction.PROVIDE_HINT in decision.secondary_actions
    has_feedback = TutoringAction.GIVE_MOTIVATIONAL_FEEDBACK in decision.secondary_actions
    
    print(f"\nExpected: PROVIDE_HINT and/or GIVE_MOTIVATIONAL_FEEDBACK")
    print(f"Status: {'✓' if (has_hint or has_feedback) else '✗'}")


def test_full_scenario():
    """Test: Full adaptive session scenario."""
    print("\n" + "="*70)
    print("TEST 8: Full Adaptive Scenario (5 decisions)")
    print("="*70)
    
    policy = AdaptivePolicyEngine()
    current_difficulty = 0.50
    
    scenarios = [
        # (name, behavioral, cognitive, affective, performance, description)
        ("Initial", 0.60, 0.60, 0.60, 0.60, "Starting out"),
        ("Improving", 0.70, 0.70, 0.70, 0.75, "Getting better"),
        ("Excellent", 0.80, 0.80, 0.80, 0.85, "Excelling"),
        ("Fatigue", 0.50, 0.55, 0.50, 0.65, "Some fatigue"),
        ("Recovery", 0.65, 0.70, 0.65, 0.70, "Recovered"),
    ]
    
    for i, (name, beh, cog, aff, perf, desc) in enumerate(scenarios, 1):
        fused = create_fused_state(beh, cog, aff)
        decision = policy.decide(fused, perf, current_difficulty, 5)
        
        new_difficulty = current_difficulty + decision.difficulty_delta
        
        print(f"\nDecision {i}: {name}")
        print(f"  Engagement: {fused.engagement_score:.2f}, Performance: {perf:.2f}")
        print(f"  Action: {decision.primary_action.value}")
        print(f"  Difficulty: {current_difficulty:.3f} → {new_difficulty:.3f}")
        
        current_difficulty = new_difficulty


if __name__ == '__main__':
    print("\n" + "█"*70)
    print("ADAPTIVE DECISION POLICY TESTS")
    print("█"*70)
    
    test_excellent_performance_high_engagement()
    test_poor_performance_low_engagement()
    test_engagement_modulates_difficulty()
    test_anti_oscillation()
    test_boundary_clamping()
    test_fair_performance_consistency()
    test_hint_suggestion()
    test_full_scenario()
    
    print("\n" + "█"*70)
    print("ALL TESTS COMPLETED")
    print("█"*70 + "\n")
