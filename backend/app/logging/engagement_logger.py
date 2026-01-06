# Engagement and Adaptation Logging System
# Records all adaptive decisions and indicators for evaluation and analysis

import csv
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class EngagementLogEntry:
    """
    Single log entry: per-question record of complete adaptive system state.
    """
    
    def __init__(self, session_id: str, question_number: int = 0):
        self.session_id = session_id
        self.question_number = question_number
        self.timestamp = datetime.utcnow().isoformat()
        
        # Question details
        self.question_id = None
        self.question_difficulty = None
        self.response_correctness = None
        self.response_time_seconds = None
        
        # Engagement indicators
        self.indicators = None
        
        # Fused engagement state
        self.fused_engagement = None
        
        # Adaptation decision
        self.adaptation_decision = None
        
        # Resulting difficulty
        self.resulting_difficulty = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON/CSV export."""
        return {
            # Session & timing
            'session_id': self.session_id,
            'question_number': self.question_number,
            'timestamp': self.timestamp,
            
            # Question details
            'question_id': self.question_id,
            'question_difficulty': round(self.question_difficulty, 3) if self.question_difficulty else None,
            'response_correctness': self.response_correctness,
            'response_time_seconds': round(self.response_time_seconds, 2) if self.response_time_seconds else None,
            
            # Engagement indicators
            'behavioral_response_time_deviation': (
                round(self.indicators.response_time_deviation, 4) if self.indicators else None
            ),
            'behavioral_inactivity_duration': (
                round(self.indicators.inactivity_duration, 2) if self.indicators else None
            ),
            'behavioral_hint_usage_count': (
                self.indicators.hint_usage_count if self.indicators else None
            ),
            'behavioral_rapid_guessing_probability': (
                round(self.indicators.rapid_guessing_probability, 4) if self.indicators else None
            ),
            'cognitive_accuracy_trend': (
                round(self.indicators.accuracy_trend, 4) if self.indicators else None
            ),
            'cognitive_consistency_score': (
                round(self.indicators.consistency_score, 4) if self.indicators else None
            ),
            'cognitive_load': (
                round(self.indicators.inferred_cognitive_load, 4) if self.indicators else None
            ),
            'affective_frustration_probability': (
                round(self.indicators.frustration_probability, 4) if self.indicators else None
            ),
            'affective_confusion_probability': (
                round(self.indicators.confusion_probability, 4) if self.indicators else None
            ),
            'affective_boredom_probability': (
                round(self.indicators.boredom_probability, 4) if self.indicators else None
            ),
            
            # Fused engagement
            'engagement_score': (
                round(self.fused_engagement.engagement_score, 4) if self.fused_engagement else None
            ),
            'engagement_categorical_state': (
                self.fused_engagement.categorical_state.value if self.fused_engagement else None
            ),
            'engagement_behavioral_component': (
                round(self.fused_engagement.behavioral_score, 4) if self.fused_engagement else None
            ),
            'engagement_cognitive_component': (
                round(self.fused_engagement.cognitive_score, 4) if self.fused_engagement else None
            ),
            'engagement_affective_component': (
                round(self.fused_engagement.affective_score, 4) if self.fused_engagement else None
            ),
            'engagement_confidence': (
                round(self.fused_engagement.confidence, 4) if self.fused_engagement else None
            ),
            'engagement_primary_driver': (
                self.fused_engagement.primary_driver if self.fused_engagement else None
            ),
            
            # Adaptation decision
            'decision_primary_action': (
                self.adaptation_decision.primary_action.value if self.adaptation_decision else None
            ),
            'decision_secondary_actions': (
                ','.join(a.value for a in self.adaptation_decision.secondary_actions)
                if self.adaptation_decision and self.adaptation_decision.secondary_actions else None
            ),
            'decision_difficulty_delta': (
                round(self.adaptation_decision.difficulty_delta, 3) if self.adaptation_decision else None
            ),
            'decision_rationale': (
                self.adaptation_decision.rationale if self.adaptation_decision else None
            ),
            'decision_engagement_influenced': (
                self.adaptation_decision.engagement_influenced if self.adaptation_decision else None
            ),
            
            # Resulting state
            'resulting_difficulty_level': (
                round(self.resulting_difficulty, 3) if self.resulting_difficulty else None
            )
        }


class WindowLogEntry:
    """
    Summary log entry: per-window aggregate of engagement and performance.
    """
    
    def __init__(self, session_id: str, window_number: int):
        self.session_id = session_id
        self.window_number = window_number
        self.timestamp = datetime.utcnow().isoformat()
        
        # Window performance
        self.window_size = 5
        self.correct_count = 0
        self.incorrect_count = 0
        self.accuracy = 0.0
        self.avg_response_time = 0.0
        
        # Aggregated engagement
        self.avg_engagement_score = 0.0
        self.avg_behavioral_score = 0.0
        self.avg_cognitive_score = 0.0
        self.avg_affective_score = 0.0
        
        # Engagement state summary
        self.dominant_engagement_state = None
        self.primary_driver_summary = None
        
        # Difficulty progression
        self.difficulty_at_start = None
        self.difficulty_at_end = None
        self.total_difficulty_change = None
        
        # Decisions made
        self.decisions_count = 0
        self.increase_count = 0
        self.decrease_count = 0
        self.maintain_count = 0
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON/CSV export."""
        return {
            'session_id': self.session_id,
            'window_number': self.window_number,
            'timestamp': self.timestamp,
            
            # Performance
            'window_size': self.window_size,
            'correct_count': self.correct_count,
            'incorrect_count': self.incorrect_count,
            'accuracy': round(self.accuracy, 4),
            'avg_response_time': round(self.avg_response_time, 2),
            
            # Engagement aggregates
            'avg_engagement_score': round(self.avg_engagement_score, 4),
            'avg_behavioral_score': round(self.avg_behavioral_score, 4),
            'avg_cognitive_score': round(self.avg_cognitive_score, 4),
            'avg_affective_score': round(self.avg_affective_score, 4),
            
            # Dominant state
            'dominant_engagement_state': self.dominant_engagement_state,
            'primary_driver_summary': self.primary_driver_summary,
            
            # Difficulty progression
            'difficulty_at_start': round(self.difficulty_at_start, 3) if self.difficulty_at_start else None,
            'difficulty_at_end': round(self.difficulty_at_end, 3) if self.difficulty_at_end else None,
            'total_difficulty_change': round(self.total_difficulty_change, 3) if self.total_difficulty_change else None,
            
            # Decision summary
            'decisions_count': self.decisions_count,
            'increase_count': self.increase_count,
            'decrease_count': self.decrease_count,
            'maintain_count': self.maintain_count
        }


class EngagementLogger:
    """
    Comprehensive logging system for adaptive tutoring system.
    Records per-question and per-window logs in CSV and JSON formats.
    """
    
    def __init__(self, session_id: str, output_dir: str = None):
        self.session_id = session_id
        self.output_dir = output_dir or "/tmp/engagement_logs"
        
        # Create output directory
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Storage
        self.question_logs: List[EngagementLogEntry] = []
        self.window_logs: List[WindowLogEntry] = []
        
        # Current window tracking
        self.current_window_number = 0
        self.current_window_questions: List[EngagementLogEntry] = []
    
    def log_question(self,
                     question_id: str,
                     question_difficulty: float,
                     response_correctness: bool,
                     response_time_seconds: float,
                     indicators,
                     fused_engagement,
                     adaptation_decision,
                     resulting_difficulty: float):
        """
        Log a single question's complete adaptive system state.
        """
        
        entry = EngagementLogEntry(self.session_id, len(self.question_logs) + 1)
        
        # Fill in all fields
        entry.question_id = question_id
        entry.question_difficulty = question_difficulty
        entry.response_correctness = response_correctness
        entry.response_time_seconds = response_time_seconds
        entry.indicators = indicators
        entry.fused_engagement = fused_engagement
        entry.adaptation_decision = adaptation_decision
        entry.resulting_difficulty = resulting_difficulty
        
        # Store
        self.question_logs.append(entry)
        self.current_window_questions.append(entry)
        
        return entry
    
    def log_window_summary(self,
                          window_number: int,
                          correct_count: int,
                          incorrect_count: int,
                          avg_response_time: float,
                          avg_engagement_score: float,
                          avg_behavioral_score: float,
                          avg_cognitive_score: float,
                          avg_affective_score: float,
                          dominant_engagement_state: str,
                          primary_driver_summary: str,
                          difficulty_at_start: float,
                          difficulty_at_end: float):
        """
        Log window-level summary.
        """
        
        entry = WindowLogEntry(self.session_id, window_number)
        entry.correct_count = correct_count
        entry.incorrect_count = incorrect_count
        entry.accuracy = correct_count / (correct_count + incorrect_count) if (correct_count + incorrect_count) > 0 else 0
        entry.avg_response_time = avg_response_time
        
        entry.avg_engagement_score = avg_engagement_score
        entry.avg_behavioral_score = avg_behavioral_score
        entry.avg_cognitive_score = avg_cognitive_score
        entry.avg_affective_score = avg_affective_score
        
        entry.dominant_engagement_state = dominant_engagement_state
        entry.primary_driver_summary = primary_driver_summary
        
        entry.difficulty_at_start = difficulty_at_start
        entry.difficulty_at_end = difficulty_at_end
        entry.total_difficulty_change = difficulty_at_end - difficulty_at_start
        
        # Count decisions
        entry.decisions_count = len(self.current_window_questions)
        for q_log in self.current_window_questions:
            if q_log.adaptation_decision:
                action = q_log.adaptation_decision.primary_action.value
                if 'increase' in action:
                    entry.increase_count += 1
                elif 'decrease' in action:
                    entry.decrease_count += 1
                elif 'maintain' in action:
                    entry.maintain_count += 1
        
        self.window_logs.append(entry)
        self.current_window_questions = []
        self.current_window_number += 1
    
    def export_to_csv(self, include_questions: bool = True, include_windows: bool = True):
        """
        Export logs to CSV files.
        """
        
        if include_questions and self.question_logs:
            csv_path = os.path.join(
                self.output_dir,
                f"{self.session_id}_questions.csv"
            )
            
            # Get keys from first entry
            keys = sorted(self.question_logs[0].to_dict().keys())
            
            with open(csv_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                for entry in self.question_logs:
                    writer.writerow(entry.to_dict())
            
            print(f"✓ Exported {len(self.question_logs)} question logs to {csv_path}")
        
        if include_windows and self.window_logs:
            csv_path = os.path.join(
                self.output_dir,
                f"{self.session_id}_windows.csv"
            )
            
            keys = sorted(self.window_logs[0].to_dict().keys())
            
            with open(csv_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                for entry in self.window_logs:
                    writer.writerow(entry.to_dict())
            
            print(f"✓ Exported {len(self.window_logs)} window logs to {csv_path}")
    
    def export_to_json(self, include_questions: bool = True, include_windows: bool = True):
        """
        Export logs to JSON files.
        """
        
        if include_questions and self.question_logs:
            json_path = os.path.join(
                self.output_dir,
                f"{self.session_id}_questions.json"
            )
            
            data = {
                'session_id': self.session_id,
                'export_timestamp': datetime.utcnow().isoformat(),
                'total_questions': len(self.question_logs),
                'questions': [entry.to_dict() for entry in self.question_logs]
            }
            
            with open(json_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"✓ Exported {len(self.question_logs)} question logs to {json_path}")
        
        if include_windows and self.window_logs:
            json_path = os.path.join(
                self.output_dir,
                f"{self.session_id}_windows.json"
            )
            
            data = {
                'session_id': self.session_id,
                'export_timestamp': datetime.utcnow().isoformat(),
                'total_windows': len(self.window_logs),
                'windows': [entry.to_dict() for entry in self.window_logs]
            }
            
            with open(json_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"✓ Exported {len(self.window_logs)} window logs to {json_path}")
    
    def export_all(self):
        """Export to both CSV and JSON."""
        self.export_to_csv()
        self.export_to_json()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get aggregate statistics for thesis evaluation.
        """
        
        if not self.question_logs:
            return {}
        
        # Question-level stats
        total_questions = len(self.question_logs)
        correct = sum(1 for q in self.question_logs if q.response_correctness)
        accuracy = correct / total_questions if total_questions > 0 else 0
        
        response_times = [q.response_time_seconds for q in self.question_logs 
                         if q.response_time_seconds]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Engagement stats
        engagement_scores = [q.fused_engagement.engagement_score for q in self.question_logs 
                            if q.fused_engagement]
        avg_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0
        
        # Difficulty stats
        difficulties = [q.resulting_difficulty for q in self.question_logs 
                       if q.resulting_difficulty is not None]
        
        return {
            'total_questions': total_questions,
            'total_windows': len(self.window_logs),
            'accuracy': round(accuracy, 4),
            'avg_response_time': round(avg_response_time, 2),
            'avg_engagement_score': round(avg_engagement, 4),
            'min_difficulty': round(min(difficulties), 3) if difficulties else None,
            'max_difficulty': round(max(difficulties), 3) if difficulties else None,
            'final_difficulty': round(difficulties[-1], 3) if difficulties else None,
            'difficulty_delta': round(difficulties[-1] - difficulties[0], 3) if difficulties else None
        }
    
    def print_summary(self):
        """Print session summary to console."""
        stats = self.get_statistics()
        
        print(f"\n📊 SESSION SUMMARY - {self.session_id}")
        print("="*70)
        print(f"  Questions: {stats.get('total_questions', 0)}")
        print(f"  Windows: {stats.get('total_windows', 0)}")
        print(f"  Accuracy: {stats.get('accuracy', 0):.1%}")
        print(f"  Avg Response Time: {stats.get('avg_response_time', 0):.1f}s")
        print(f"  Avg Engagement: {stats.get('avg_engagement_score', 0):.4f}")
        print(f"\n  Difficulty Progression:")
        print(f"    Start: {stats.get('min_difficulty', 0):.3f}")
        print(f"    End: {stats.get('final_difficulty', 0):.3f}")
        print(f"    Change: {stats.get('difficulty_delta', 0):+.3f}")
        print("="*70 + "\n")
