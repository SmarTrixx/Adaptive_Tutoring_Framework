# Window-Based Performance Evaluator
# Tracks performance over a fixed window of questions (3 or 5 questions)

from datetime import datetime
from app import db
import statistics

class PerformanceWindow:
    """
    Tracks student performance over a fixed window of questions.
    
    Window size: 5 questions (provides better stability than 3)
    Metrics tracked:
    - Number correct
    - Number incorrect
    - Average response time
    - Hint usage
    - Normalized performance score (0.0 - 1.0)
    """
    
    WINDOW_SIZE = 5  # Evaluate every 5 questions
    
    def __init__(self, session_id, student_id):
        self.session_id = session_id
        self.student_id = student_id
        self.responses = []  # Stores StudentResponse objects in window
        self.window_number = 0  # Which window are we in? (0, 1, 2...)
        
    def add_response(self, student_response):
        """Add a response to the current window."""
        self.responses.append(student_response)
    
    def is_window_complete(self):
        """Check if we have a full window of responses."""
        return len(self.responses) >= self.WINDOW_SIZE
    
    def get_window_metrics(self):
        """
        Calculate metrics for the current window.
        
        Returns:
            dict with keys:
            - correct_count: number of correct answers
            - incorrect_count: number of wrong answers
            - accuracy: percentage correct (0.0 - 1.0)
            - avg_response_time: average seconds per question
            - hints_used: total hints requested
            - window_number: which window (0-indexed)
            - is_complete: whether window is full
        """
        if not self.responses:
            return {
                'correct_count': 0,
                'incorrect_count': 0,
                'accuracy': 0.0,
                'avg_response_time': 0.0,
                'hints_used': 0,
                'window_number': self.window_number,
                'is_complete': False
            }
        
        correct_count = sum(1 for r in self.responses if r.is_correct)
        incorrect_count = len(self.responses) - correct_count
        accuracy = correct_count / len(self.responses)
        
        # Response times
        response_times = [r.response_time_seconds for r in self.responses 
                         if r.response_time_seconds and r.response_time_seconds > 0]
        avg_response_time = statistics.mean(response_times) if response_times else 0.0
        
        # Hints
        hints_used = sum(getattr(r, 'hints_used', 0) for r in self.responses)
        
        return {
            'correct_count': correct_count,
            'incorrect_count': incorrect_count,
            'accuracy': accuracy,
            'avg_response_time': avg_response_time,
            'hints_used': hints_used,
            'window_number': self.window_number,
            'is_complete': self.is_window_complete()
        }
    
    def get_performance_score(self):
        """
        Calculate a normalized performance score (0.0 - 1.0) for the window.
        
        This score combines:
        - Accuracy (60% weight): how many questions correct
        - Response time efficiency (25% weight): faster is better (inverse)
        - Hint efficiency (15% weight): fewer hints is better (inverse)
        
        Returns:
            dict with:
            - score: 0.0 - 1.0 performance score
            - components: breakdown of score components
            - feedback: qualitative assessment
        """
        metrics = self.get_window_metrics()
        
        # Component 1: Accuracy (60% weight)
        accuracy_score = metrics['accuracy']  # Already 0.0-1.0
        
        # Component 2: Response Time Efficiency (25% weight)
        # Assume ideal time is 5-15 seconds, penalty for being too slow or too fast
        avg_time = metrics['avg_response_time']
        if avg_time <= 5:
            time_score = 1.0  # Too fast might indicate guessing, but still efficient
        elif avg_time <= 15:
            time_score = 1.0  # Ideal range
        elif avg_time <= 30:
            time_score = 0.7  # Slower but acceptable
        elif avg_time <= 60:
            time_score = 0.4  # Slow
        else:
            time_score = 0.1  # Very slow
        
        # Component 3: Hint Efficiency (15% weight)
        # Assume max 2-3 hints per 5-question window is ideal, more is penalty
        hints = metrics['hints_used']
        if hints == 0:
            hints_score = 1.0  # No hints needed - excellent
        elif hints <= 2:
            hints_score = 0.9  # Minimal hints - very good
        elif hints <= 5:
            hints_score = 0.7  # Some hints - acceptable
        elif hints <= 10:
            hints_score = 0.4  # Many hints - struggling
        else:
            hints_score = 0.1  # Too many hints - major struggles
        
        # Weighted combination
        total_score = (
            (accuracy_score * 0.60) +
            (time_score * 0.25) +
            (hints_score * 0.15)
        )
        
        # Determine feedback level
        if total_score >= 0.85:
            feedback = "excellent"
        elif total_score >= 0.70:
            feedback = "good"
        elif total_score >= 0.50:
            feedback = "fair"
        elif total_score >= 0.30:
            feedback = "poor"
        else:
            feedback = "very_poor"
        
        return {
            'score': round(total_score, 4),
            'components': {
                'accuracy': round(accuracy_score, 4),
                'response_time': round(time_score, 4),
                'hint_efficiency': round(hints_score, 4)
            },
            'weights': {
                'accuracy': 0.60,
                'response_time': 0.25,
                'hint_efficiency': 0.15
            },
            'feedback': feedback,
            'metrics': metrics
        }
    
    def reset_window(self):
        """Reset for next window."""
        self.responses = []
        self.window_number += 1


class WindowPerformanceTracker:
    """
    Manages performance windows for a session.
    """
    
    def __init__(self, session_id, student_id):
        self.session_id = session_id
        self.student_id = student_id
        self.current_window = PerformanceWindow(session_id, student_id)
        self.completed_windows = []  # List of completed window scores
    
    def add_response(self, student_response):
        """
        Add a student response and check if window is complete.
        
        Returns:
            dict with:
            - window_updated: True if response added
            - window_complete: True if window just completed
            - window_score: Score if window just completed, else None
        """
        self.current_window.add_response(student_response)
        
        if self.current_window.is_window_complete():
            score_data = self.current_window.get_performance_score()
            self.completed_windows.append(score_data)
            
            # Reset for next window
            self.current_window.reset_window()
            
            return {
                'window_updated': True,
                'window_complete': True,
                'window_score': score_data,
                'total_windows_completed': len(self.completed_windows)
            }
        else:
            return {
                'window_updated': True,
                'window_complete': False,
                'responses_in_window': len(self.current_window.responses),
                'window_size': PerformanceWindow.WINDOW_SIZE
            }
    
    def get_overall_performance(self):
        """
        Get aggregate performance across all completed windows.
        
        Returns:
            dict with:
            - avg_score: average score across windows
            - best_window: highest scoring window
            - worst_window: lowest scoring window
            - trend: improving, stable, or declining
            - total_windows: number of completed windows
        """
        if not self.completed_windows:
            return {
                'avg_score': 0.0,
                'best_window': None,
                'worst_window': None,
                'trend': 'none',
                'total_windows': 0
            }
        
        scores = [w['score'] for w in self.completed_windows]
        avg_score = statistics.mean(scores)
        best_window = max(self.completed_windows, key=lambda w: w['score'])
        worst_window = min(self.completed_windows, key=lambda w: w['score'])
        
        # Determine trend
        if len(scores) >= 2:
            recent_avg = statistics.mean(scores[-2:])
            older_avg = statistics.mean(scores[:-2]) if len(scores) > 2 else scores[0]
            
            if recent_avg > older_avg + 0.1:
                trend = "improving"
            elif recent_avg < older_avg - 0.1:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "none"
        
        return {
            'avg_score': round(avg_score, 4),
            'best_window': best_window['score'],
            'worst_window': worst_window['score'],
            'trend': trend,
            'total_windows': len(self.completed_windows),
            'all_windows': scores
        }
