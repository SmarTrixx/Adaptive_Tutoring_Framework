#!/usr/bin/env python3
"""
Diagnostic script to understand the scaling/adaptation issue

The problem:
1. Scaling adapts on EVERY question (should be every 3)
2. Difficulty gets stuck at 0.90 even with wrong answers
3. Response time showing 30 (default value)

Root cause analysis:
- Old system: Checked "last 3 answers" every 3 questions
- New engine: Uses "cumulative accuracy from entire session"

This explains:
- Every answer changes cumulative accuracy → every answer adapts
- At 90% with 6/10 answers: If you get 2 wrong (8/10 = 80%), cumulative still high
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import create_app, db
from app.models.session import Session, StudentResponse
from app.engagement.tracker import EngagementIndicatorTracker

def analyze_session_scaling():
    """Analyze how scaling works in a session"""
    print("\n" + "="*80)
    print("SCALING BEHAVIOR ANALYSIS")
    print("="*80)
    
    app = create_app()
    with app.app_context():
        # Get the latest session
        session = Session.query.order_by(Session.session_start.desc()).first()
        
        if not session:
            print("❌ No sessions found")
            return
        
        responses = StudentResponse.query.filter_by(session_id=session.id).order_by(
            StudentResponse.timestamp
        ).all()
        
        print(f"\nSession: {session.id}")
        print(f"Total responses: {len(responses)}")
        print(f"Total correct: {session.correct_answers}")
        print(f"Final difficulty: {session.current_difficulty}")
        
        print("\n" + "-"*80)
        print("SCALING BEHAVIOR - ANALYZING ACCURACY CALCULATION")
        print("-"*80)
        
        cumulative_correct = 0
        for i, response in enumerate(responses, 1):
            cumulative_correct += (1 if response.is_correct else 0)
            cumulative_accuracy = cumulative_correct / i
            
            # What the engine would calculate
            tracker = EngagementIndicatorTracker()
            cognitive = tracker.track_cognitive_indicators(session.id)
            engine_accuracy = cognitive['accuracy']
            
            print(f"\nQ{i}: {'✓' if response.is_correct else '✗'}")
            print(f"  Cumulative: {cumulative_correct}/{i} = {cumulative_accuracy:.0%}")
            print(f"  Engine sees: {engine_accuracy:.0%}")
            print(f"  Step decision:")
            
            if engine_accuracy >= 0.99:
                print(f"    → Perfect (≥0.99): +0.10 step")
            elif engine_accuracy >= 0.8:
                print(f"    → High (≥0.80): +0.10 step")
            elif engine_accuracy >= 0.67:
                print(f"    → Mixed (≥0.67): +0.01 step")
            elif engine_accuracy > 0.33:
                print(f"    → Marginal (>0.33): NO CHANGE")
            elif engine_accuracy > 0.01:
                print(f"    → Low (>0.01): -0.10 step")
            else:
                print(f"    → Zero (0.0): -0.10 step")
        
        print("\n" + "="*80)
        print("KEY FINDINGS")
        print("="*80)
        
        print("""
❌ PROBLEM 1: Adapts on EVERY question
   OLD SYSTEM: Checked every 3 answers (3, 6, 9...)
   NEW SYSTEM: Checks cumulative accuracy every question
   
   Example: 6 correct, 0 wrong
   - Q1: 1/1 = 100% → +0.10
   - Q2: 2/2 = 100% → +0.10
   - Q3: 3/3 = 100% → +0.10
   ...adapts every time!

❌ PROBLEM 2: Stuck at 0.90 with wrong answers
   Cumulative stays high because:
   - With 6 correct out of 10: 60%
   - With 6 correct out of 10: 60% (still High >0.8? NO, 60% < 80%)
   
   Wait... let me recalculate. If 6 correct and 4 wrong:
   - Accuracy = 6/10 = 60% 
   - 60% is > 0.33 but < 0.67 → MARGINAL, NO CHANGE
   
   So it SHOULD decrease... unless the data export shows cumulative differently.

❌ PROBLEM 3: Response time showing 30
   This is a hardcoded default, not from actual StudentResponse time tracking.
""")

def compare_old_vs_new():
    """Compare old simple system vs new engine"""
    print("\n" + "="*80)
    print("OLD vs NEW ADAPTATION LOGIC")
    print("="*80)
    
    print("""
OLD SYSTEM (Simple Adaptation):
  Called: Every 3 answers
  Logic:
    if last_3_correct == 3: difficulty += 0.05  # ❌ 0.05
    elif last_3_correct == 2: difficulty += 0.01
    elif last_3_correct == 1: no change
    else: difficulty -= 0.05  # ❌ 0.05

  Result: 0.50 → 0.55 → 0.60 → 0.65 (increments of 0.05)
  Behavior: Uses WINDOWING (last 3 answers)

NEW ENGINE:
  Called: Every question
  Logic:
    if cumulative_accuracy >= 0.99: difficulty += 0.10
    elif cumulative_accuracy >= 0.8: difficulty += 0.10  ✓ Fixed step
    elif cumulative_accuracy >= 0.67: difficulty += 0.01
    elif cumulative_accuracy > 0.33: no change
    else: difficulty -= 0.10  ✓ Fixed step

  Result: 0.50 → 0.60 → 0.70 → 0.80 (increments of 0.10)
  Behavior: Uses CUMULATIVE accuracy across entire session
  
MISMATCH: 
  Engine uses cumulative accuracy, which:
  - Changes on EVERY question (not every 3)
  - Makes decisions based on TOTAL session, not recent performance
  - Can get "stuck" when overall accuracy hits a boundary
""")

if __name__ == '__main__':
    analyze_session_scaling()
    compare_old_vs_new()
    
    print("\n" + "="*80)
    print("SOLUTION NEEDED")
    print("="*80)
    print("""
The engine was designed with cumulative accuracy, but the behavior
suggests it should use WINDOWING (last 3 answers) like the old system.

Two options:

OPTION 1: Use windowing (like old system)
  - Keep engine, modify tracker to return recent_accuracy
  - Or modify engine to use last 3 answers instead of cumulative

OPTION 2: Keep cumulative but change strategy
  - Reduce adaptation frequency (don't call engine every question)
  - Use larger thresholds to avoid frequent changes
  
RECOMMENDATION: Use OPTION 1 with WINDOWING
  - This matches the old "working" behavior
  - Users expect adaptation every 3 questions
  - Better stability and predictability
""")
