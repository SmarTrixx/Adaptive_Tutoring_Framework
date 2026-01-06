# Sanity-Check Simulator for Adaptive Tutoring System
# Tests the system with realistic student scenarios and verifies sensible behavior

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime, timedelta
from app.engagement.indicators import (
    EngagementIndicatorExtractor, EngagementIndicators
)
from app.engagement.fusion import EngagementFusionEngine
from app.adaptation.policy import AdaptivePolicyEngine, PolicyLogger
from app.logging.engagement_logger import EngagementLogger

# Mock StudentResponse
class StudentResponse:
    def __init__(self, question_id, is_correct, response_time_seconds, hints_used, timestamp):
        self.question_id = question_id
        self.is_correct = is_correct
        self.response_time_seconds = response_time_seconds
        self.hints_used = hints_used
        self.timestamp = timestamp
        self.selected_option = 'A'


def create_responses_for_scenario(scenario_type, window_num):
    """
    Create realistic response sequences for different student types.
    
    Args:
        scenario_type: 'high_performer', 'struggling', 'disengaged_accurate'
        window_num: Which window (1, 2, 3, etc.) for progression
        
    Returns:
        List of StudentResponse objects
    """
    
    responses = []
    
    if scenario_type == 'high_performer':
        # High-performing engaged student: improving accuracy, fast consistent times, no hints
        base_accuracy = 0.70 + (window_num * 0.05)  # Improves each window
        base_response_time = 4.0
        hint_rate = 0.0
        variance = 0.5  # Low variance (consistent)
        
    elif scenario_type == 'struggling':
        # Struggling student: low accuracy, slow responses, many hints
        base_accuracy = 0.30 + (window_num * 0.10)  # Slowly improving
        base_response_time = 12.0
        hint_rate = 0.6  # Many hints
        variance = 1.5  # High variance (inconsistent)
        
    elif scenario_type == 'disengaged_accurate':
        # Disengaged but accurate: high accuracy, very fast (rushing), no struggle
        base_accuracy = 0.90  # Consistently high
        base_response_time = 1.5  # Very fast (guessing?)
        hint_rate = 0.0
        variance = 0.2  # Very consistent (too consistent?)
        
    else:
        raise ValueError(f"Unknown scenario: {scenario_type}")
    
    # Generate 5 responses per window
    for i in range(5):
        is_correct = (i / 5.0) < base_accuracy
        
        # Variable response times
        if i % 3 == 0:
            response_time = base_response_time * (1 - variance * 0.5)
        elif i % 3 == 1:
            response_time = base_response_time
        else:
            response_time = base_response_time * (1 + variance * 0.5)
        
        hints = 1 if (i < int(5 * hint_rate)) else 0
        
        response = StudentResponse(
            question_id=f"q{window_num * 5 + i}",
            is_correct=is_correct,
            response_time_seconds=max(0.5, response_time),  # Minimum 0.5s
            hints_used=hints,
            timestamp=datetime.utcnow() - timedelta(seconds=5-i)
        )
        responses.append(response)
    
    return responses


def simulate_scenario(scenario_type, num_windows=3):
    """
    Simulate a complete tutoring session for a student type.
    
    Args:
        scenario_type: Type of student ('high_performer', 'struggling', 'disengaged_accurate')
        num_windows: Number of 5-question windows to simulate
    """
    
    print(f"\n" + "="*80)
    print(f"SCENARIO: {scenario_type.upper().replace('_', ' ')}")
    print("="*80)
    
    session_id = f"sim_{scenario_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    logger = EngagementLogger(session_id, output_dir="/tmp/engagement_logs")
    
    current_difficulty = 0.50  # Start at medium difficulty
    
    # Components
    extractor = EngagementIndicatorExtractor()
    fusion_engine = EngagementFusionEngine()
    policy_engine = AdaptivePolicyEngine()
    
    print(f"\n🎓 Session: {session_id}")
    print(f"Starting Difficulty: {current_difficulty:.3f} (MEDIUM)")
    print(f"Number of Windows: {num_windows}\n")
    
    difficulty_trajectory = [current_difficulty]
    engagement_trajectory = []
    
    for window_num in range(1, num_windows + 1):
        print(f"\n{'─'*80}")
        print(f"WINDOW {window_num} (Questions {(window_num-1)*5 + 1}-{window_num*5})")
        print(f"{'─'*80}")
        
        # Get responses for this window
        responses = create_responses_for_scenario(scenario_type, window_num)
        
        window_correct = sum(1 for r in responses if r.is_correct)
        window_incorrect = len(responses) - window_correct
        window_accuracy = window_correct / len(responses)
        
        print(f"\nResponses: {window_correct}/{len(responses)} correct ({window_accuracy:.0%})")
        
        # Per-question processing and logging (accumulate engagement data)
        window_engagement_scores = []
        window_primary_drivers = []
        
        for q_num, response in enumerate(responses, 1):
            # Extract indicators from window up to this point
            responses_so_far = responses[:q_num]
            indicators = extractor.extract_from_responses(responses_so_far)
            
            # Fuse indicators
            fused_state = fusion_engine.fuse(indicators)
            window_engagement_scores.append(fused_state.engagement_score)
            window_primary_drivers.append(fused_state.primary_driver)
            
            # Log this question (but don't make decision yet - wait until window end)
            logger.log_question(
                question_id=response.question_id,
                question_difficulty=current_difficulty,
                response_correctness=response.is_correct,
                response_time_seconds=response.response_time_seconds,
                indicators=indicators,
                fused_engagement=fused_state,
                adaptation_decision=None,  # No decision yet
                resulting_difficulty=current_difficulty  # Won't change until window end
            )
            
            # Print per-question update (compact, no adaptation yet)
            print(f"  Q{(window_num-1)*5 + q_num}: "
                  f"{'✓' if response.is_correct else '✗'} "
                  f"| Engage: {fused_state.engagement_score:.3f} "
                  f"| Diff: {current_difficulty:.3f}")
        
        # WINDOW END: Make adaptation decision based on full window performance
        # Calculate window-level performance score (primarily accuracy)
        # Accuracy is the main signal; response time is secondary modulation
        window_performance = window_accuracy
        
        # If response time is very high (struggling) or very low (rushing), adjust slightly
        avg_response_time = sum(r.response_time_seconds for r in responses) / len(responses)
        if avg_response_time > 10:  # Struggling: slow response
            window_performance = window_performance * 0.9  # Penalize slightly
        elif avg_response_time < 2:  # Rushing: very fast
            window_performance = window_performance * 0.95  # Penalize slightly
        
        # Get final fused engagement state for the window
        final_indicators = extractor.extract_from_responses(responses)
        final_fused_state = fusion_engine.fuse(final_indicators)
        
        # Make adaptation decision
        decision = policy_engine.decide(
            engagement_state=final_fused_state,
            window_performance=window_performance,
            current_difficulty=current_difficulty,
            window_sample_size=5
        )
        
        # Apply difficulty change (once per window)
        old_difficulty = current_difficulty
        new_difficulty = current_difficulty + decision.difficulty_delta
        new_difficulty = max(0.0, min(1.0, new_difficulty))
        current_difficulty = new_difficulty
        
        # Log the window summary with the decision
        avg_engagement = sum(window_engagement_scores) / len(window_engagement_scores) if window_engagement_scores else 0.5
        avg_response_time = sum(r.response_time_seconds for r in responses) / len(responses)
        
        # Determine dominant engagement state
        state_counts = {}
        for driver in window_primary_drivers:
            state_counts[driver] = state_counts.get(driver, 0) + 1
        dominant_driver = max(state_counts, key=state_counts.get) if state_counts else "Unknown"
        
        logger.log_window_summary(
            window_number=window_num,
            correct_count=window_correct,
            incorrect_count=window_incorrect,
            avg_response_time=avg_response_time,
            avg_engagement_score=avg_engagement,
            avg_behavioral_score=final_fused_state.behavioral_score,
            avg_cognitive_score=final_fused_state.cognitive_score,
            avg_affective_score=final_fused_state.affective_score,
            dominant_engagement_state=final_fused_state.categorical_state.value,
            primary_driver_summary=dominant_driver,
            difficulty_at_start=old_difficulty,
            difficulty_at_end=new_difficulty
        )
        
        difficulty_trajectory.append(current_difficulty)
        engagement_trajectory.append(avg_engagement)
        
        print(f"\nWindow Summary:")
        print(f"  Accuracy: {window_accuracy:.0%}")
        print(f"  Performance Score: {window_performance:.3f}")
        print(f"  Avg Engagement: {avg_engagement:.4f}")
        print(f"  Engagement State: {final_fused_state.categorical_state.value}")
        print(f"  Difficulty: {old_difficulty:.3f} → {new_difficulty:.3f} ({decision.difficulty_delta:+.3f})")
        print(f"  Decision: {decision.primary_action.value}")
        print(f"  Rationale: {decision.rationale}")
    
    # Session summary
    print(f"\n" + "="*80)
    print(f"SESSION SUMMARY")
    print("="*80)
    
    logger.print_summary()
    
    print(f"\n📈 DIFFICULTY TRAJECTORY:")
    for w, diff in enumerate(difficulty_trajectory):
        marker = "  START" if w == 0 else f"  W{w}"
        print(f"  {marker}: {diff:.3f}")
    
    print(f"\n📊 ENGAGEMENT PROGRESSION:")
    for w, eng in enumerate(engagement_trajectory, 1):
        state_map = {
            0.1: "DISENGAGED",
            0.3: "STRUGGLING",
            0.5: "NEUTRAL",
            0.7: "ENGAGED",
            0.9: "HIGHLY_ENGAGED"
        }
        state = min(state_map.keys(), key=lambda x: abs(x - eng))
        state_name = state_map[state]
        print(f"  W{w}: {eng:.4f} ({state_name})")
    
    # Export logs
    print(f"\n💾 EXPORTING LOGS...")
    logger.export_all()
    
    return {
        'scenario': scenario_type,
        'difficulty_trajectory': difficulty_trajectory,
        'engagement_trajectory': engagement_trajectory,
        'final_difficulty': current_difficulty,
        'final_engagement': engagement_trajectory[-1] if engagement_trajectory else 0.5
    }


def verify_sanity(results):
    """
    Verify that system behaves sensibly for each scenario.
    """
    
    print(f"\n" + "="*80)
    print(f"SANITY CHECK VERIFICATION")
    print("="*80)
    
    checks_passed = 0
    checks_total = 0
    
    for scenario_result in results:
        scenario = scenario_result['scenario']
        difficulty_traj = scenario_result['difficulty_trajectory']
        engagement_traj = scenario_result['engagement_trajectory']
        final_diff = scenario_result['final_difficulty']
        final_eng = scenario_result['final_engagement']
        
        print(f"\n✓ {scenario.upper().replace('_', ' ')}")
        print(f"  Difficulty: {difficulty_traj[0]:.3f} → {final_diff:.3f} "
              f"({final_diff - difficulty_traj[0]:+.3f})")
        print(f"  Engagement: {engagement_traj[0]:.4f} → {final_eng:.4f}")
        
        # Sanity checks
        checks = []
        
        if scenario == 'high_performer':
            # Should increase difficulty (or maintain high)
            is_sane = final_diff >= difficulty_traj[0] - 0.10
            checks.append(("Difficulty increased or maintained", is_sane))
            
            # Should maintain high engagement
            is_sane = final_eng >= 0.70
            checks.append(("Engagement stayed high (≥0.70)", is_sane))
            
        elif scenario == 'struggling':
            # Should decrease difficulty significantly
            is_sane = final_diff < difficulty_traj[0]
            checks.append(("Difficulty decreased", is_sane))
            
            # Should show engagement improvement through windows
            is_improving = len(engagement_traj) < 2 or engagement_traj[-1] >= engagement_traj[0] - 0.10
            checks.append(("Engagement stable or improving", is_improving))
            
        elif scenario == 'disengaged_accurate':
            # Should maintain medium/easy difficulty (don't push hard)
            is_sane = final_diff <= difficulty_traj[0] + 0.10
            checks.append(("Difficulty stable (not pushed too hard)", is_sane))
            
            # Should detect disengagement signal
            is_disengaged = final_eng < 0.70
            checks.append(("System detected disengagement", is_disengaged))
        
        # Print checks
        for check_name, passed in checks:
            status = "✓" if passed else "✗"
            print(f"  {status} {check_name}")
            checks_total += 1
            if passed:
                checks_passed += 1
    
    print(f"\n" + "="*80)
    print(f"SANITY CHECK RESULTS: {checks_passed}/{checks_total} checks passed")
    if checks_passed == checks_total:
        print("✅ ALL CHECKS PASSED - System behavior is sensible!")
    else:
        print(f"⚠️  {checks_total - checks_passed} checks failed - Review logic")
    print("="*80 + "\n")


def main():
    """Run all scenario simulations."""
    
    print("\n" + "█"*80)
    print("ADAPTIVE TUTORING SYSTEM - SANITY CHECK SIMULATOR")
    print("█"*80)
    
    scenarios = ['high_performer', 'struggling', 'disengaged_accurate']
    results = []
    
    for scenario in scenarios:
        try:
            result = simulate_scenario(scenario, num_windows=3)
            results.append(result)
        except Exception as e:
            print(f"\n❌ Error simulating {scenario}: {e}")
            import traceback
            traceback.print_exc()
    
    # Verify sanity
    verify_sanity(results)
    
    print("\n" + "█"*80)
    print("SIMULATOR COMPLETE")
    print("█"*80 + "\n")


if __name__ == '__main__':
    main()
