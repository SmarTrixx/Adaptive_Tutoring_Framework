#!/usr/bin/env python3
"""
Diagnostic script to check adaptation data
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app
from app import db
from app.models.session import Session, StudentResponse

def check_latest_session():
    """Check the latest session and its responses"""
    with app.app_context():
        session = Session.query.order_by(Session.id.desc()).first()
        
        if not session:
            print("No sessions found")
            return
        
        print(f"\nLatest Session: {session.id}")
        print(f"Subject: {session.subject}")
        print(f"Current Difficulty: {session.current_difficulty:.2f}")
        print(f"Score: {session.correct_answers}/{session.total_questions} = {session.score_percentage:.1f}%")
        
        responses = StudentResponse.query.filter_by(session_id=session.id).order_by(
            StudentResponse.timestamp.asc()
        ).all()
        
        print(f"\nResponses ({len(responses)} total):")
        for i, r in enumerate(responses, 1):
            status = "✓" if r.is_correct else "✗"
            timestamp = r.timestamp.strftime("%H:%M:%S") if r.timestamp else "N/A"
            print(f"  Q{i}: {status} ({timestamp})")
        
        # Now simulate what the adaptation algorithm would do
        print(f"\n--- Adaptation Simulation ---")
        total_answered = len(responses)
        print(f"Total answered: {total_answered}")
        
        if total_answered >= 3:
            recent_responses = responses[-5:] if total_answered >= 5 else responses[-3:]
            correct_count = sum(1 for r in recent_responses if r.is_correct)
            total_in_window = len(recent_responses)
            accuracy = correct_count / total_in_window if total_in_window > 0 else 0
            
            recent_str = "".join(["✓" if r.is_correct else "✗" for r in recent_responses])
            print(f"Recent window: {recent_str} ({correct_count}/{total_in_window} = {accuracy:.0%})")
            print(f"Current difficulty: {session.current_difficulty:.2f}")
            
            if accuracy >= 1.0:
                new_diff = min(0.9, session.current_difficulty + 0.05)
                action = "+0.05"
            elif accuracy >= 0.8:
                new_diff = min(0.9, session.current_difficulty + 0.03)
                action = "+0.03"
            elif accuracy >= 0.6:
                new_diff = min(0.9, session.current_difficulty + 0.01)
                action = "+0.01"
            elif accuracy >= 0.4:
                new_diff = session.current_difficulty
                action = "hold"
            elif accuracy >= 0.2:
                new_diff = max(0.1, session.current_difficulty - 0.02)
                action = "-0.02"
            else:
                new_diff = max(0.1, session.current_difficulty - 0.05)
                action = "-0.05"
            
            print(f"Action: {action} → {new_diff:.2f}")

if __name__ == '__main__':
    check_latest_session()
