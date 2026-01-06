# Engagement Indicators Extractor
# Computes behavioral, cognitive, and affective indicators from CBT interaction data

from datetime import datetime, timedelta
from statistics import mean, stdev
from typing import Dict, List, Tuple, Optional
from app.models.session import StudentResponse
from app import db


class EngagementIndicators:
    """
    Structured data container for engagement indicators.
    All indicators normalized to 0.0-1.0 unless otherwise specified.
    """
    
    def __init__(self):
        # Behavioral indicators
        self.response_time_deviation = 0.0  # How much response time varies (0=consistent, 1=highly variable)
        self.inactivity_duration = 0.0      # Seconds of inactivity (raw value, not normalized)
        self.hint_usage_count = 0           # Number of hints requested (raw count)
        self.rapid_guessing_probability = 0.0  # Likelihood of guessing (0=confident, 1=guessing)
        
        # Cognitive indicators
        self.accuracy_trend = 0.0           # Performance direction (-1=declining, 0=stable, 1=improving)
        self.consistency_score = 0.0        # 1.0=consistent performance, 0.0=random/guessing
        self.inferred_cognitive_load = 0.0  # 0=easy, 1=very hard
        
        # Affective indicators (probabilistic)
        self.frustration_probability = 0.0  # P(student frustrated)
        self.confusion_probability = 0.0    # P(student confused)
        self.boredom_probability = 0.0      # P(student bored)
        
        # Metadata
        self.timestamp = datetime.utcnow()
        self.window_size = 0                # How many questions analyzed
        self.is_valid = False               # Whether indicators are meaningful
    
    def to_dict(self):
        """Convert to dictionary for logging/serialization."""
        return {
            'behavioral': {
                'response_time_deviation': round(self.response_time_deviation, 4),
                'inactivity_duration': round(self.inactivity_duration, 2),
                'hint_usage_count': self.hint_usage_count,
                'rapid_guessing_probability': round(self.rapid_guessing_probability, 4)
            },
            'cognitive': {
                'accuracy_trend': round(self.accuracy_trend, 4),
                'consistency_score': round(self.consistency_score, 4),
                'inferred_cognitive_load': round(self.inferred_cognitive_load, 4)
            },
            'affective': {
                'frustration_probability': round(self.frustration_probability, 4),
                'confusion_probability': round(self.confusion_probability, 4),
                'boredom_probability': round(self.boredom_probability, 4)
            },
            'metadata': {
                'timestamp': self.timestamp.isoformat(),
                'window_size': self.window_size,
                'is_valid': self.is_valid
            }
        }


class EngagementIndicatorExtractor:
    """
    Extracts and computes engagement indicators from student response data.
    """
    
    # Constants for indicator thresholds
    RESPONSE_TIME_MIN = 1.0      # Seconds (too fast = guessing)
    RESPONSE_TIME_MAX = 60.0     # Seconds (too slow = struggle/confusion)
    RESPONSE_TIME_IDEAL = 5.0    # Seconds (sweet spot)
    
    INACTIVITY_THRESHOLD = 30.0  # Seconds (indicates disengagement)
    
    HINT_OVERUSE_THRESHOLD = 3   # Hints per 5 questions (>= indicates struggling)
    
    def extract_from_responses(self, responses: List[StudentResponse]) -> EngagementIndicators:
        """
        Extract engagement indicators from a list of student responses.
        
        Args:
            responses: List of StudentResponse objects
            
        Returns:
            EngagementIndicators: Computed indicators
        """
        indicators = EngagementIndicators()
        
        if not responses or len(responses) < 2:
            # Not enough data to compute meaningful indicators
            return indicators
        
        indicators.window_size = len(responses)
        
        # Compute behavioral indicators
        self._compute_behavioral_indicators(responses, indicators)
        
        # Compute cognitive indicators
        self._compute_cognitive_indicators(responses, indicators)
        
        # Compute affective indicators (simulated)
        self._compute_affective_indicators(responses, indicators)
        
        indicators.is_valid = True
        return indicators
    
    def _compute_behavioral_indicators(self, responses: List[StudentResponse], 
                                      indicators: EngagementIndicators):
        """Compute behavioral indicators from response data."""
        
        # 1. Response Time Deviation
        response_times = [r.response_time_seconds for r in responses 
                         if r.response_time_seconds and r.response_time_seconds > 0]
        
        if response_times and len(response_times) >= 2:
            mean_time = mean(response_times)
            if len(response_times) > 1:
                std_dev = stdev(response_times) if len(response_times) > 1 else 0
                # Normalize: 0=consistent, 1=highly variable
                # Coefficient of variation (std/mean)
                cv = (std_dev / mean_time) if mean_time > 0 else 0
                indicators.response_time_deviation = min(1.0, cv)  # Cap at 1.0
            else:
                indicators.response_time_deviation = 0.0
        
        # 2. Inactivity Duration
        # Sum of gaps between consecutive responses
        total_inactivity = 0.0
        if len(responses) >= 2:
            for i in range(1, len(responses)):
                if hasattr(responses[i], 'timestamp') and hasattr(responses[i-1], 'timestamp'):
                    gap = (responses[i].timestamp - responses[i-1].timestamp).total_seconds()
                    total_inactivity += gap
        
        indicators.inactivity_duration = total_inactivity
        
        # 3. Hint Usage Count
        hint_count = sum(1 for r in responses if getattr(r, 'hints_used', 0) > 0)
        indicators.hint_usage_count = hint_count
        
        # 4. Rapid Guessing Detection
        # Fast responses + wrong answers = likely guessing
        rapid_responses = [r for r in responses 
                          if r.response_time_seconds and r.response_time_seconds < self.RESPONSE_TIME_MIN]
        
        if rapid_responses:
            wrong_rapid = sum(1 for r in rapid_responses if not r.is_correct)
            guessing_rate = wrong_rapid / len(rapid_responses)
            indicators.rapid_guessing_probability = guessing_rate
        
    
    def _compute_cognitive_indicators(self, responses: List[StudentResponse], 
                                     indicators: EngagementIndicators):
        """Compute cognitive indicators from response data."""
        
        correct_answers = [r.is_correct for r in responses]
        
        # 1. Accuracy Trend
        # Compare first half vs second half
        if len(responses) >= 4:
            mid = len(responses) // 2
            first_half_correct = sum(correct_answers[:mid])
            second_half_correct = sum(correct_answers[mid:])
            
            first_half_acc = first_half_correct / mid if mid > 0 else 0
            second_half_acc = second_half_correct / (len(responses) - mid) if (len(responses) - mid) > 0 else 0
            
            # -1 = declining, 0 = stable, 1 = improving
            trend = second_half_acc - first_half_acc
            indicators.accuracy_trend = max(-1.0, min(1.0, trend))
        else:
            indicators.accuracy_trend = 0.0
        
        # 2. Consistency Score
        # How consistent is performance? All correct/all wrong = 1.0, random = 0.0
        if len(responses) >= 3:
            accuracy = sum(correct_answers) / len(responses)
            # Entropy-based: consistent performance = high entropy separation
            # If accuracy close to 0 or 1, more consistent
            consistency = 1.0 - abs(accuracy - 0.5) * 2  # Maps to [0, 1]
            
            # But also check for run patterns (consecutive correct/wrong)
            runs = self._count_runs(correct_answers)
            max_runs = len(responses) // 2 + 1  # Max possible alternations
            run_ratio = runs / max_runs if max_runs > 0 else 0
            
            # Average consistency from accuracy pattern and run pattern
            indicators.consistency_score = (consistency + (1 - run_ratio)) / 2
        
        # 3. Inferred Cognitive Load
        # Based on: accuracy, response time, hints needed
        cognitive_load = 0.0
        
        # Low accuracy = high load
        accuracy = sum(correct_answers) / len(responses) if responses else 0
        load_from_accuracy = 1.0 - accuracy
        
        # Slow/variable responses = high load
        response_times = [r.response_time_seconds for r in responses 
                         if r.response_time_seconds and r.response_time_seconds > 0]
        if response_times:
            avg_time = mean(response_times)
            # Normalize: 5s = 0 load, >30s = 1.0 load
            load_from_time = max(0.0, min(1.0, (avg_time - self.RESPONSE_TIME_IDEAL) / 25.0))
        else:
            load_from_time = 0.0
        
        # Many hints = high load
        load_from_hints = min(1.0, indicators.hint_usage_count / self.HINT_OVERUSE_THRESHOLD)
        
        # Combine (equally weighted)
        cognitive_load = (load_from_accuracy + load_from_time + load_from_hints) / 3
        indicators.inferred_cognitive_load = cognitive_load
    
    
    def _compute_affective_indicators(self, responses: List[StudentResponse], 
                                     indicators: EngagementIndicators):
        """Compute affective indicators (simulated/probabilistic)."""
        
        # Use behavioral and cognitive indicators to infer affective state
        
        # 1. Frustration Probability
        # Frustration: wrong answers, slow responses, many hints, declining accuracy
        frustration_signals = []
        
        accuracy = sum(1 for r in responses if r.is_correct) / len(responses)
        frustration_signals.append(1.0 - accuracy)  # Low accuracy = frustrated
        
        if indicators.inactivity_duration > self.INACTIVITY_THRESHOLD:
            frustration_signals.append(0.7)  # Long inactivity = frustrated
        
        if indicators.accuracy_trend < -0.2:
            frustration_signals.append(0.8)  # Declining performance = frustrated
        
        if indicators.hint_usage_count > self.HINT_OVERUSE_THRESHOLD:
            frustration_signals.append(0.6)  # Many hints = frustrated
        
        if frustration_signals:
            indicators.frustration_probability = mean(frustration_signals)
        
        # 2. Confusion Probability
        # Confusion: inconsistent performance, wrong answers, slow with hints
        confusion_signals = []
        
        confusion_signals.append(1.0 - indicators.consistency_score)  # Inconsistent = confused
        
        if indicators.inferred_cognitive_load > 0.7:
            confusion_signals.append(0.8)  # High cognitive load = confused
        
        if indicators.inactivity_duration > 10:  # Moderate inactivity
            confusion_signals.append(0.5)  # Pausing = thinking/confused
        
        if confusion_signals:
            indicators.confusion_probability = mean(confusion_signals)
        
        # 3. Boredom Probability
        # Boredom: very fast responses, perfect accuracy, no hints needed, no inactivity
        boredom_signals = []
        
        response_times = [r.response_time_seconds for r in responses 
                         if r.response_time_seconds and r.response_time_seconds > 0]
        if response_times:
            avg_time = mean(response_times)
            if avg_time < self.RESPONSE_TIME_MIN:
                boredom_signals.append(0.9)  # Very fast = bored/not engaged
        
        if accuracy == 1.0:
            boredom_signals.append(0.7)  # Perfect = too easy/bored
        
        if indicators.hint_usage_count == 0 and accuracy > 0.8:
            boredom_signals.append(0.6)  # No help needed, high accuracy = bored
        
        if indicators.inactivity_duration == 0:
            boredom_signals.append(0.4)  # No pausing = rushed/bored
        
        if boredom_signals:
            indicators.boredom_probability = mean(boredom_signals)
    
    
    def _count_runs(self, sequence: List[bool]) -> int:
        """Count number of runs in a boolean sequence (transitions between True/False)."""
        if not sequence or len(sequence) < 2:
            return len(sequence)
        
        runs = 1
        for i in range(1, len(sequence)):
            if sequence[i] != sequence[i-1]:
                runs += 1
        
        return runs


class IndicatorLogger:
    """Logs engagement indicators for debugging/analysis."""
    
    @staticmethod
    def log_indicators(session_id: str, indicators: EngagementIndicators):
        """Log indicators to database or file."""
        print(f"\n📊 ENGAGEMENT INDICATORS - Session {session_id}")
        print("="*70)
        
        print("\n🎯 BEHAVIORAL:")
        print(f"  Response Time Deviation: {indicators.response_time_deviation:.4f}")
        print(f"    (0=consistent, 1=highly variable)")
        print(f"  Inactivity Duration: {indicators.inactivity_duration:.2f}s")
        print(f"  Hint Usage Count: {indicators.hint_usage_count}")
        print(f"  Rapid Guessing Probability: {indicators.rapid_guessing_probability:.4f}")
        
        print("\n🧠 COGNITIVE:")
        print(f"  Accuracy Trend: {indicators.accuracy_trend:.4f}")
        print(f"    (-1=declining, 0=stable, 1=improving)")
        print(f"  Consistency Score: {indicators.consistency_score:.4f}")
        print(f"    (0=random, 1=very consistent)")
        print(f"  Inferred Cognitive Load: {indicators.inferred_cognitive_load:.4f}")
        print(f"    (0=easy, 1=very hard)")
        
        print("\n❤️  AFFECTIVE (Simulated):")
        print(f"  Frustration Probability: {indicators.frustration_probability:.4f}")
        print(f"  Confusion Probability: {indicators.confusion_probability:.4f}")
        print(f"  Boredom Probability: {indicators.boredom_probability:.4f}")
        
        print("\n📋 METADATA:")
        print(f"  Window Size: {indicators.window_size} responses")
        print(f"  Valid: {indicators.is_valid}")
        print(f"  Timestamp: {indicators.timestamp.isoformat()}")
        print("="*70 + "\n")
