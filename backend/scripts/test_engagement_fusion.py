# Test: Engagement Fusion Layer
# Tests multimodal fusion of behavioral, cognitive, and affective indicators

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime
from app.engagement.indicators import EngagementIndicators
from app.engagement.fusion import (
    EngagementFusionEngine, FusedEngagementState, 
    EngagementState, FusionLogger
)


def create_indicators_scenario(name, behavioral, cognitive, affective, 
                              window_size=5, is_valid=True):
    """Helper: Create EngagementIndicators for a scenario."""
    indicators = EngagementIndicators()
    
    # Set behavioral score-like values
    indicators.response_time_deviation = 0.5 - behavioral * 0.5
    indicators.hint_usage_count = int((1 - behavioral) * 3)
    indicators.rapid_guessing_probability = 1 - behavioral
    indicators.inactivity_duration = (1 - behavioral) * 60
    
    # Set cognitive score-like values
    indicators.accuracy_trend = cognitive - 0.5
    indicators.consistency_score = cognitive
    indicators.inferred_cognitive_load = 1 - cognitive
    
    # Set affective score-like values
    indicators.frustration_probability = 1 - affective
    indicators.confusion_probability = 1 - affective
    indicators.boredom_probability = 1 - affective
    
    indicators.window_size = window_size
    indicators.is_valid = is_valid
    
    return indicators


def test_fusion_basic():
    """Test basic fusion with balanced indicators."""
    print("\n" + "="*70)
    print("TEST 1: Balanced Indicators")
    print("="*70)
    
    # Scenario: Engaged, performing well, good mood
    indicators = create_indicators_scenario(
        name="Engaged",
        behavioral=0.8,   # Consistent, no hints
        cognitive=0.8,    # Improving, good load
        affective=0.8     # Not frustrated, not confused
    )
    
    engine = EngagementFusionEngine()
    fused = engine.fuse(indicators)
    
    print(f"\nInput Indicators:")
    print(f"  Behavioral: 0.8 (engaged, consistent)")
    print(f"  Cognitive: 0.8 (improving, good)")
    print(f"  Affective: 0.8 (positive mood)")
    
    print(f"\nFused Output:")
    print(f"  Engagement Score: {fused.engagement_score:.4f}")
    print(f"  Expected: > 0.75 (highly engaged)")
    print(f"  Status: {'✓' if fused.engagement_score > 0.75 else '✗'}")
    
    print(f"\n  Categorical State: {fused.categorical_state.value}")
    print(f"  Expected: highly_engaged")
    print(f"  Status: {'✓' if fused.categorical_state == EngagementState.HIGHLY_ENGAGED else '✗'}")
    
    print(f"\n  Component Scores:")
    print(f"    Behavioral:  {fused.behavioral_score:.4f}")
    print(f"    Cognitive:   {fused.cognitive_score:.4f}")
    print(f"    Affective:   {fused.affective_score:.4f}")


def test_fusion_struggling():
    """Test fusion with struggling student indicators."""
    print("\n" + "="*70)
    print("TEST 2: Struggling Student")
    print("="*70)
    
    # Scenario: Low performance, high cognitive load, frustration
    indicators = create_indicators_scenario(
        name="Struggling",
        behavioral=0.3,   # Variable, many hints
        cognitive=0.2,    # Declining, overwhelmed
        affective=0.2     # Frustrated, confused
    )
    
    engine = EngagementFusionEngine()
    fused = engine.fuse(indicators)
    
    print(f"\nInput Indicators:")
    print(f"  Behavioral: 0.3 (struggling)")
    print(f"  Cognitive: 0.2 (poor performance)")
    print(f"  Affective: 0.2 (frustrated, confused)")
    
    print(f"\nFused Output:")
    print(f"  Engagement Score: {fused.engagement_score:.4f}")
    print(f"  Expected: < 0.4 (struggling)")
    print(f"  Status: {'✓' if fused.engagement_score < 0.4 else '✗'}")
    
    print(f"\n  Categorical State: {fused.categorical_state.value}")
    print(f"  Expected: struggling")
    print(f"  Status: {'✓' if fused.categorical_state == EngagementState.STRUGGLING else '✗'}")


def test_fusion_weight_balance():
    """Test that weights are balanced (no single modality dominates)."""
    print("\n" + "="*70)
    print("TEST 3: Weight Balance (No Domination)")
    print("="*70)
    
    # Scenario 1: High behavioral + low cognitive/affective
    indicators = create_indicators_scenario(
        name="High_Behavioral",
        behavioral=0.9,   # Excellent behavior
        cognitive=0.2,    # Poor performance
        affective=0.2     # Bad mood
    )
    
    engine = EngagementFusionEngine()
    fused1 = engine.fuse(indicators)
    
    print(f"\nScenario: High Behavioral (0.9), Low Cognitive (0.2), Low Affective (0.2)")
    print(f"  Engagement Score: {fused1.engagement_score:.4f}")
    print(f"  Weight formula: 0.9*0.4 + 0.2*0.4 + 0.2*0.2 = 0.44")
    print(f"  Expected: ~0.44 (balanced, not dominated by behavioral)")
    print(f"  Status: {'✓' if 0.40 < fused1.engagement_score < 0.48 else '✗'}")
    
    # Scenario 2: All equal (should give ~0.5)
    indicators = create_indicators_scenario(
        name="Equal",
        behavioral=0.5,
        cognitive=0.5,
        affective=0.5
    )
    
    fused2 = engine.fuse(indicators)
    
    print(f"\nScenario: All Equal (0.5, 0.5, 0.5)")
    print(f"  Engagement Score: {fused2.engagement_score:.4f}")
    print(f"  Expected: 0.5")
    print(f"  Status: {'✓' if abs(fused2.engagement_score - 0.5) < 0.01 else '✗'}")


def test_driver_identification():
    """Test that drivers are correctly identified."""
    print("\n" + "="*70)
    print("TEST 4: Driver Identification")
    print("="*70)
    
    # Scenario: Frustrated student
    indicators = create_indicators_scenario(
        name="Frustrated",
        behavioral=0.2,   # Many hints
        cognitive=0.3,    # Declining
        affective=0.2     # High frustration
    )
    
    engine = EngagementFusionEngine()
    fused = engine.fuse(indicators)
    
    print(f"\nScenario: Struggling student (few hints, declining accuracy)")
    print(f"  Primary Driver: {fused.primary_driver}")
    print(f"  Secondary Driver: {fused.secondary_driver}")
    print(f"  Status: {'✓' if 'frustration' in fused.primary_driver.lower() or 'struggling' in fused.primary_driver.lower() else '✗'}")


def test_confidence():
    """Test confidence calculation based on window size."""
    print("\n" + "="*70)
    print("TEST 5: Confidence Based on Data")
    print("="*70)
    
    engine = EngagementFusionEngine()
    
    # Small window
    indicators = create_indicators_scenario("Small", 0.5, 0.5, 0.5, window_size=2)
    fused_small = engine.fuse(indicators)
    
    print(f"\nSmall window (2 responses):")
    print(f"  Confidence: {fused_small.confidence:.2f}")
    print(f"  Expected: 0.30 (low)")
    print(f"  Status: {'✓' if fused_small.confidence < 0.4 else '✗'}")
    
    # Medium window
    indicators = create_indicators_scenario("Medium", 0.5, 0.5, 0.5, window_size=5)
    fused_medium = engine.fuse(indicators)
    
    print(f"\nMedium window (5 responses):")
    print(f"  Confidence: {fused_medium.confidence:.2f}")
    print(f"  Expected: 0.60-0.70")
    print(f"  Status: {'✓' if 0.5 < fused_medium.confidence < 0.8 else '✗'}")
    
    # Large window
    indicators = create_indicators_scenario("Large", 0.5, 0.5, 0.5, window_size=15)
    fused_large = engine.fuse(indicators)
    
    print(f"\nLarge window (15 responses):")
    print(f"  Confidence: {fused_large.confidence:.2f}")
    print(f"  Expected: 0.85-1.0")
    print(f"  Status: {'✓' if fused_large.confidence >= 0.85 else '✗'}")


def test_engagement_mapping():
    """Test score-to-category mapping."""
    print("\n" + "="*70)
    print("TEST 6: Score-to-Category Mapping")
    print("="*70)
    
    engine = EngagementFusionEngine()
    
    test_cases = [
        (0.9, EngagementState.HIGHLY_ENGAGED, "Excellent engagement"),
        (0.7, EngagementState.ENGAGED, "Good engagement"),
        (0.5, EngagementState.NEUTRAL, "Neutral engagement"),
        (0.3, EngagementState.STRUGGLING, "Struggling"),
        (0.1, EngagementState.DISENGAGED, "Disengaged"),
    ]
    
    for score, expected_state, description in test_cases:
        state = engine._score_to_category(score)
        status = "✓" if state == expected_state else "✗"
        print(f"  Score {score:.1f} → {state.value:20s} {status} ({description})")


def test_integrated_fusion():
    """Test full fusion pipeline with logging."""
    print("\n" + "="*70)
    print("TEST 7: Integrated Fusion with Logging")
    print("="*70)
    
    # Create realistic indicators
    indicators = create_indicators_scenario(
        name="Realistic",
        behavioral=0.65,   # Decent behavior, some hints
        cognitive=0.70,    # Good performance, stable
        affective=0.60     # Some frustration, mostly okay
    )
    
    engine = EngagementFusionEngine()
    fused = engine.fuse(indicators)
    
    FusionLogger.log_fusion('test_session', fused)
    
    # Verify output structure
    output_dict = fused.to_dict()
    print(f"Output structure verified: {bool(output_dict)}")
    print(f"  Contains engagement_score: {'✓' if 'engagement_score' in output_dict else '✗'}")
    print(f"  Contains component_scores: {'✓' if 'component_scores' in output_dict else '✗'}")
    print(f"  Contains drivers: {'✓' if 'drivers' in output_dict else '✗'}")


if __name__ == '__main__':
    print("\n" + "█"*70)
    print("ENGAGEMENT FUSION LAYER TESTS")
    print("█"*70)
    
    test_fusion_basic()
    test_fusion_struggling()
    test_fusion_weight_balance()
    test_driver_identification()
    test_confidence()
    test_engagement_mapping()
    test_integrated_fusion()
    
    print("\n" + "█"*70)
    print("ALL TESTS COMPLETED")
    print("█"*70 + "\n")
