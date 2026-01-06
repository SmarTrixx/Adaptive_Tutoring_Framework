# Test: Engagement Indicators Extraction
# Tests behavioral, cognitive, and affective indicator computation

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime, timedelta
from app.engagement.indicators import EngagementIndicatorExtractor, IndicatorLogger

# Mock StudentResponse for testing
class StudentResponse:
    def __init__(self, session_id, question_id, selected_option, is_correct,
                 response_time_seconds, hints_used, timestamp):
        self.session_id = session_id
        self.question_id = question_id
        self.selected_option = selected_option
        self.is_correct = is_correct
        self.response_time_seconds = response_time_seconds
        self.hints_used = hints_used
        self.timestamp = timestamp


def create_test_responses(session_id, count=10, accuracy=0.6, 
                         avg_response_time=5.0, hints_per_5=1):
    """Helper: Create test StudentResponse objects."""
    responses = []
    
    for i in range(count):
        # Alternate correct/incorrect based on accuracy
        is_correct = i % (1 / accuracy) == 0
        
        # Variable response times around average
        if i % 3 == 0:
            response_time = avg_response_time * 0.5
        elif i % 3 == 1:
            response_time = avg_response_time
        else:
            response_time = avg_response_time * 1.5
        
        response = StudentResponse(
            session_id=session_id,
            question_id=i,
            selected_option='A',
            is_correct=is_correct,
            response_time_seconds=response_time,
            hints_used=1 if i < hints_per_5 else 0,
            timestamp=datetime.utcnow() - timedelta(seconds=count*response_time - i*response_time)
        )
        responses.append(response)
    
    return responses


def test_behavioral_indicators():
    """Test behavioral indicator computation."""
    print("\n" + "="*70)
    print("TEST 1: Behavioral Indicators")
    print("="*70)
    
    # Scenario 1: Consistent, engaged student
    print("\nScenario 1: Consistent, engaged student")
    responses = create_test_responses('test1', count=5, accuracy=0.8, 
                                    avg_response_time=5.0, hints_per_5=0)
    
    extractor = EngagementIndicatorExtractor()
    indicators = extractor.extract_from_responses(responses)
    
    print(f"  Response Time Deviation: {indicators.response_time_deviation:.4f}")
    print(f"    Expected: < 0.5 (consistent)")
    print(f"    Status: {'✓' if indicators.response_time_deviation < 0.5 else '✗'}")
    
    print(f"  Hint Usage Count: {indicators.hint_usage_count}")
    print(f"    Expected: 0 (none needed)")
    print(f"    Status: {'✓' if indicators.hint_usage_count == 0 else '✗'}")
    
    print(f"  Rapid Guessing Probability: {indicators.rapid_guessing_probability:.4f}")
    print(f"    Expected: 0.0 (no guessing)")
    print(f"    Status: {'✓' if indicators.rapid_guessing_probability == 0.0 else '✗'}")
    
    # Scenario 2: Struggling student (slow, many hints, wrong answers)
    print("\nScenario 2: Struggling student")
    responses = create_test_responses('test2', count=5, accuracy=0.4, 
                                    avg_response_time=15.0, hints_per_5=3)
    
    indicators = extractor.extract_from_responses(responses)
    
    print(f"  Hint Usage Count: {indicators.hint_usage_count}")
    print(f"    Expected: 3 (many hints)")
    print(f"    Status: {'✓' if indicators.hint_usage_count == 3 else '✗'}")
    
    print(f"  Rapid Guessing Probability: {indicators.rapid_guessing_probability:.4f}")
    print(f"    Expected: > 0.5 (likely guessing from wrong answers)")
    # Note: depends on response times, so just print
    
    # Scenario 3: Very fast responses (possible guessing)
    print("\nScenario 3: Very fast responses (possible guessing)")
    responses = []
    for i in range(5):
        response = StudentResponse(
            session_id='test3',
            question_id=i,
            selected_option='A',
            is_correct=(i % 2 == 0),  # 50% correct
            response_time_seconds=0.5,  # Very fast
            hints_used=0,
            timestamp=datetime.utcnow() - timedelta(seconds=5-i)
        )
        responses.append(response)
    
    indicators = extractor.extract_from_responses(responses)
    
    print(f"  Rapid Guessing Probability: {indicators.rapid_guessing_probability:.4f}")
    print(f"    Expected: 0.5 (fast + 50% correct)")
    print(f"    Status: {'✓' if abs(indicators.rapid_guessing_probability - 0.5) < 0.1 else '✗'}")


def test_cognitive_indicators():
    """Test cognitive indicator computation."""
    print("\n" + "="*70)
    print("TEST 2: Cognitive Indicators")
    print("="*70)
    
    # Scenario 1: Improving performance
    print("\nScenario 1: Improving performance")
    responses = []
    for i in range(6):
        # First half: 33% correct, second half: 67% correct
        is_correct = i < 2 or i >= 4
        response = StudentResponse(
            session_id='test4',
            question_id=i,
            selected_option='A',
            is_correct=is_correct,
            response_time_seconds=5.0,
            hints_used=0,
            timestamp=datetime.utcnow() - timedelta(seconds=6-i)
        )
        responses.append(response)
    
    extractor = EngagementIndicatorExtractor()
    indicators = extractor.extract_from_responses(responses)
    
    print(f"  Accuracy Trend: {indicators.accuracy_trend:.4f}")
    print(f"    Expected: > 0 (improving)")
    print(f"    Status: {'✓' if indicators.accuracy_trend > 0 else '✗'}")
    
    # Scenario 2: Declining performance
    print("\nScenario 2: Declining performance")
    responses = []
    for i in range(6):
        # First half: 67% correct, second half: 33% correct
        is_correct = i < 4
        response = StudentResponse(
            session_id='test5',
            question_id=i,
            selected_option='A',
            is_correct=is_correct,
            response_time_seconds=5.0,
            hints_used=0,
            timestamp=datetime.utcnow() - timedelta(seconds=6-i)
        )
        responses.append(response)
    
    indicators = extractor.extract_from_responses(responses)
    
    print(f"  Accuracy Trend: {indicators.accuracy_trend:.4f}")
    print(f"    Expected: < 0 (declining)")
    print(f"    Status: {'✓' if indicators.accuracy_trend < 0 else '✗'}")
    
    # Scenario 3: Cognitive load assessment
    print("\nScenario 3: Cognitive load (low accuracy + slow + hints)")
    responses = create_test_responses('test6', count=5, accuracy=0.2, 
                                    avg_response_time=20.0, hints_per_5=3)
    
    indicators = extractor.extract_from_responses(responses)
    
    print(f"  Inferred Cognitive Load: {indicators.inferred_cognitive_load:.4f}")
    print(f"    Expected: > 0.6 (high load)")
    print(f"    Status: {'✓' if indicators.inferred_cognitive_load > 0.6 else '✗'}")


def test_affective_indicators():
    """Test affective (probabilistic) indicator computation."""
    print("\n" + "="*70)
    print("TEST 3: Affective Indicators (Simulated)")
    print("="*70)
    
    # Scenario 1: Frustrated student (low accuracy, many hints, slow)
    print("\nScenario 1: Frustrated student")
    responses = create_test_responses('test7', count=5, accuracy=0.2, 
                                    avg_response_time=20.0, hints_per_5=3)
    
    extractor = EngagementIndicatorExtractor()
    indicators = extractor.extract_from_responses(responses)
    
    print(f"  Frustration Probability: {indicators.frustration_probability:.4f}")
    print(f"    Expected: > 0.5 (high)")
    print(f"    Status: {'✓' if indicators.frustration_probability > 0.5 else '✗'}")
    
    print(f"  Confusion Probability: {indicators.confusion_probability:.4f}")
    print(f"    Expected: > 0.5 (inconsistent + high load)")
    print(f"    Status: {'✓' if indicators.confusion_probability > 0.5 else '✗'}")
    
    # Scenario 2: Bored student (very fast, perfect accuracy, no hints)
    print("\nScenario 2: Bored student")
    responses = []
    for i in range(5):
        response = StudentResponse(
            session_id='test8',
            question_id=i,
            selected_option='A',
            is_correct=True,
            response_time_seconds=0.8,  # Very fast
            hints_used=0,
            timestamp=datetime.utcnow() - timedelta(seconds=5-i)
        )
        responses.append(response)
    
    indicators = extractor.extract_from_responses(responses)
    
    print(f"  Boredom Probability: {indicators.boredom_probability:.4f}")
    print(f"    Expected: > 0.5 (too easy, very fast)")
    print(f"    Status: {'✓' if indicators.boredom_probability > 0.5 else '✗'}")
    
    print(f"  Frustration Probability: {indicators.frustration_probability:.4f}")
    print(f"    Expected: 0.0 (perfect accuracy)")
    print(f"    Status: {'✓' if indicators.frustration_probability == 0.0 else '✗'}")


def test_integrated_extraction():
    """Test all indicators together."""
    print("\n" + "="*70)
    print("TEST 4: Integrated Indicator Extraction")
    print("="*70)
    
    # Real-world scenario: struggling student with mixed signals
    print("\nScenario: Mixed signals (improving but still struggling)")
    responses = []
    
    # First 3: low accuracy, slow
    for i in range(3):
        response = StudentResponse(
            session_id='test9',
            question_id=i,
            selected_option='A',
            is_correct=False,
            response_time_seconds=18.0,
            hints_used=1,
            timestamp=datetime.utcnow() - timedelta(seconds=10-i)
        )
        responses.append(response)
    
    # Last 2: improving accuracy, still slow
    for i in range(3, 5):
        response = StudentResponse(
            session_id='test9',
            question_id=i,
            selected_option='A',
            is_correct=True,
            response_time_seconds=12.0,
            hints_used=0,
            timestamp=datetime.utcnow() - timedelta(seconds=10-i)
        )
        responses.append(response)
    
    extractor = EngagementIndicatorExtractor()
    indicators = extractor.extract_from_responses(responses)
    
    IndicatorLogger.log_indicators('test9', indicators)
    
    # Verify all indicators computed
    print(f"Window Size: {indicators.window_size}")
    print(f"Valid: {indicators.is_valid}")
    print(f"Status: {'✓' if indicators.is_valid and indicators.window_size == 5 else '✗'}")


if __name__ == '__main__':
    print("\n" + "█"*70)
    print("ENGAGEMENT INDICATORS EXTRACTION TESTS")
    print("█"*70)
    
    test_behavioral_indicators()
    test_cognitive_indicators()
    test_affective_indicators()
    test_integrated_extraction()
    
    print("\n" + "█"*70)
    print("ALL TESTS COMPLETED")
    print("█"*70 + "\n")
