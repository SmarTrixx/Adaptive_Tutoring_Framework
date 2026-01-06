#!/usr/bin/env python3
"""
Comprehensive adaptation testing script.
Simulates 3 test scenarios and shows detailed logs.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app
from app import db
from app.models.student import Student
from app.models.session import Session
from app.models.question import Question
from app.models.session import StudentResponse
from app.cbt.system import CBTSystem
import time

def test_scenario_1():
    """Test 1: All answers correct"""
    print("\n" + "="*70)
    print("TEST 1: ALL ANSWERS CORRECT")
    print("="*70)
    
    with app.app_context():
        cbt_system = CBTSystem()
        
        # Create student with unique email
        unique_id = int(time.time() * 1000) % 1000000
        student = Student(email=f"test1_{unique_id}@example.com", name="Test1")
        db.session.add(student)
        db.session.commit()
        
        # Create session
        session = Session(student_id=student.id, subject='Mathematics', total_questions=10)
        db.session.add(session)
        db.session.commit()
        
        # Get questions
        questions = Question.query.limit(10).all()
        
        print(f"\nSession: {session.id}")
        print(f"Initial difficulty: {session.current_difficulty:.2f}")
        
        # Simulate 10 correct answers using the actual submit_response function
        for i, q in enumerate(questions[:10], 1):
            result = cbt_system.submit_response(
                session_id=session.id,
                question_id=q.id,
                student_answer=q.correct_option,  # Always correct
                response_time_seconds=5.0
            )
            
            # Refresh session to get updated difficulty
            db.session.refresh(session)
            
            is_correct = "✓" if result.get('is_correct') else "✗"
            print(f"  Q{i}: {is_correct} | Difficulty: {session.current_difficulty:.2f}")
        
        print(f"\nFinal difficulty: {session.current_difficulty:.2f}")
        print(f"Expected: 0.50 → 0.55 (Q3) → 0.60 (Q6) → 0.65 (Q9)")
        
        return session.id, session.current_difficulty

def test_scenario_2():
    """Test 2: All answers wrong"""
    print("\n" + "="*70)
    print("TEST 2: ALL ANSWERS WRONG")
    print("="*70)
    
    with app.app_context():
        cbt_system = CBTSystem()
        
        # Create student with unique email
        unique_id = int(time.time() * 1000) % 1000000
        student = Student(email=f"test2_{unique_id}@example.com", name="Test2")
        db.session.add(student)
        db.session.commit()
        
        # Create session
        session = Session(student_id=student.id, subject='Science', total_questions=10)
        db.session.add(session)
        db.session.commit()
        
        # Get questions
        questions = Question.query.limit(10).all()
        
        print(f"\nSession: {session.id}")
        print(f"Initial difficulty: {session.current_difficulty:.2f}")
        
        # Simulate 10 wrong answers using the actual submit_response function
        for i, q in enumerate(questions[:10], 1):
            # Choose a wrong answer
            wrong_answer = 'A' if q.correct_option != 'A' else 'B'
            result = cbt_system.submit_response(
                session_id=session.id,
                question_id=q.id,
                student_answer=wrong_answer,  # Always wrong
                response_time_seconds=5.0
            )
            
            # Refresh session to get updated difficulty
            db.session.refresh(session)
            
            is_correct = "✓" if result.get('is_correct') else "✗"
            print(f"  Q{i}: {is_correct} | Difficulty: {session.current_difficulty:.2f}")
        
        print(f"\nFinal difficulty: {session.current_difficulty:.2f}")
        print(f"Expected: 0.50 → 0.45 (Q3) → 0.40 (Q6) → 0.35 (Q9)")
        
        return session.id, session.current_difficulty

def test_scenario_3():
    """Test 3: Mixed answers"""
    print("\n" + "="*70)
    print("TEST 3: MIXED ANSWERS (Alternating correct/wrong)")
    print("="*70)
    
    with app.app_context():
        cbt_system = CBTSystem()
        
        # Create student with unique email
        unique_id = int(time.time() * 1000) % 1000000
        student = Student(email=f"test3_{unique_id}@example.com", name="Test3")
        db.session.add(student)
        db.session.commit()
        
        # Create session
        session = Session(student_id=student.id, subject='History', total_questions=10)
        db.session.add(session)
        db.session.commit()
        
        # Get questions
        questions = Question.query.limit(10).all()
        
        print(f"\nSession: {session.id}")
        print(f"Initial difficulty: {session.current_difficulty:.2f}")
        
        # Simulate alternating: ✓✗✓✗✓✗✓✗✓✗ using the actual submit_response function
        for i, q in enumerate(questions[:10], 1):
            is_correct = (i % 2 == 1)  # Odd questions correct, even wrong
            student_answer = q.correct_option if is_correct else ('A' if q.correct_option != 'A' else 'B')
            
            result = cbt_system.submit_response(
                session_id=session.id,
                question_id=q.id,
                student_answer=student_answer,
                response_time_seconds=5.0
            )
            
            # Refresh session to get updated difficulty
            db.session.refresh(session)
            
            mark = "✓" if result.get('is_correct') else "✗"
            print(f"  Q{i}: {mark} | Difficulty: {session.current_difficulty:.2f}")
        
        print(f"\nFinal difficulty: {session.current_difficulty:.2f}")
        print(f"Expected: 0.50 → 0.50 (Q3: 2/3) → 0.50 (Q6: 2/3) → 0.50 (Q9: 2/3)")
        
        return session.id, session.current_difficulty


def analyze_sessions():
    """Analyze all sessions"""
    print("\n" + "="*70)
    print("DETAILED SESSION ANALYSIS")
    print("="*70)
    
    with app.app_context():
        sessions = Session.query.order_by(Session.session_start.desc()).limit(3).all()
        
        for session in reversed(sessions):
            responses = StudentResponse.query.filter_by(session_id=session.id).order_by(
                StudentResponse.timestamp.asc()
            ).all()
            
            print(f"\nSession: {session.id[:8]}...")
            print(f"  Subject: {session.subject}")
            print(f"  Final Difficulty: {session.current_difficulty:.2f}")
            print(f"  Score: {session.correct_answers}/{session.total_questions}")
            
            print(f"\n  Responses:")
            for i, r in enumerate(responses, 1):
                status = "✓" if r.is_correct else "✗"
                timestamp = r.timestamp.strftime("%H:%M:%S") if r.timestamp else "N/A"
                print(f"    Q{i}: {status} ({timestamp})")
            
            # Check adaptation points
            print(f"\n  Adaptation Points:")
            if len(responses) >= 3:
                last3 = responses[-3:] if len(responses) >= 3 else responses
                correct3 = sum(1 for r in last3 if r.is_correct)
                print(f"    Last 3 (Q{len(responses)-2} to Q{len(responses)}): {correct3}/3")
            
            if len(responses) >= 6:
                last6_last3 = responses[3:6]
                correct6 = sum(1 for r in last6_last3 if r.is_correct)
                print(f"    Q4-Q6: {correct6}/3")
            
            if len(responses) >= 9:
                last9_last3 = responses[6:9]
                correct9 = sum(1 for r in last9_last3 if r.is_correct)
                print(f"    Q7-Q9: {correct9}/3")

if __name__ == '__main__':
    print("\n\n")
    print("█" * 70)
    print("COMPREHENSIVE ADAPTATION TESTING SUITE")
    print("█" * 70)
    
    session1_id, diff1 = test_scenario_1()
    session2_id, diff2 = test_scenario_2()
    session3_id, diff3 = test_scenario_3()
    
    analyze_sessions()
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\nTest 1 (All Correct):")
    print(f"  Final Difficulty: {diff1:.2f} (Expected: ~0.65)")
    print(f"  ✓ PASS" if diff1 >= 0.60 else f"  ✗ FAIL")
    
    print(f"\nTest 2 (All Wrong):")
    print(f"  Final Difficulty: {diff2:.2f} (Expected: ~0.35)")
    print(f"  ✓ PASS" if diff2 <= 0.40 else f"  ✗ FAIL")
    
    print(f"\nTest 3 (Mixed):")
    print(f"  Final Difficulty: {diff3:.2f} (Expected: ~0.50)")
    print(f"  ✓ PASS" if abs(diff3 - 0.50) <= 0.05 else f"  ✗ FAIL")
    
    print("\n" + "="*70)
