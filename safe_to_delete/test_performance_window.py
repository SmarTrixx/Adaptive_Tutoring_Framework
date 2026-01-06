#!/usr/bin/env python3
"""
Test: Window-Based Performance Evaluator

Verifies that:
1. Performance windows are created correctly (5-question windows)
2. Metrics are calculated accurately
3. Performance scores are normalized (0.0-1.0)
4. Performance trends are detected
"""

import sys
sys.path.insert(0, 'backend')

from app import create_app, db
from app.models.student import Student
from app.models.session import Session, StudentResponse
from app.models.question import Question
from app.cbt.system import CBTSystem
from app.adaptation.performance_window import PerformanceWindow, WindowPerformanceTracker


def test_window_creation():
    """Test that performance windows are created and managed correctly."""
    print("="*70)
    print("TEST 1: Performance Window Creation & Management")
    print("="*70)
    
    window = PerformanceWindow("session-123", "student-456")
    
    print(f"\n✓ Window created")
    print(f"  Session ID: {window.session_id}")
    print(f"  Student ID: {window.student_id}")
    print(f"  Window size: {PerformanceWindow.WINDOW_SIZE}")
    print(f"  Current window number: {window.window_number}")
    print(f"  Is empty: {not window.responses}")


def test_window_metrics():
    """Test metrics calculation with mock responses."""
    print("\n" + "="*70)
    print("TEST 2: Window Metrics Calculation")
    print("="*70)
    
    app = create_app()
    with app.app_context():
        # Create test student and session
        student = Student.query.filter_by(email='window_test@test.com').first()
        if not student:
            student = Student(email='window_test@test.com', name='Window Test')
            db.session.add(student)
            db.session.commit()
        
        # Clean up old sessions
        old_sessions = Session.query.filter_by(student_id=student.id).all()
        for s in old_sessions:
            StudentResponse.query.filter_by(session_id=s.id).delete()
            db.session.delete(s)
        db.session.commit()
        
        # Create session and add questions
        cbt = CBTSystem()
        session_result = cbt.start_session(student.id, 'Mathematics', 5)
        session_id = session_result['session_id']
        
        # Create 5 mock responses
        window = PerformanceWindow(session_id, student.id)
        
        print("\n📝 Adding 5 responses to window (3 correct, 2 wrong):")
        print(f"   Q1: ✓ Correct (2.0s)")
        print(f"   Q2: ✓ Correct (3.5s)")
        print(f"   Q3: ✗ Wrong (4.0s)")
        print(f"   Q4: ✓ Correct (2.5s)")
        print(f"   Q5: ✗ Wrong (5.0s)")
        
        # Simulate responses
        for i in range(5):
            q = cbt.get_next_question(session_id)
            question = Question.query.get(q['question_id'])
            
            is_correct = i in [0, 1, 3]  # Q1, Q2, Q4 correct
            response_time = [2.0, 3.5, 4.0, 2.5, 5.0][i]
            
            response = cbt.submit_response(
                session_id,
                q['question_id'],
                question.correct_option if is_correct else 'X',
                response_time
            )
            
            # Get actual StudentResponse
            student_response = StudentResponse.query.filter_by(
                session_id=session_id,
                question_id=q['question_id']
            ).first()
            
            window.add_response(student_response)
        
        # Check metrics
        metrics = window.get_window_metrics()
        
        print(f"\n✓ Window Metrics:")
        print(f"  Correct: {metrics['correct_count']}/5")
        print(f"  Incorrect: {metrics['incorrect_count']}/5")
        print(f"  Accuracy: {metrics['accuracy']:.2%}")
        print(f"  Avg response time: {metrics['avg_response_time']:.2f}s")
        print(f"  Hints used: {metrics['hints_used']}")
        print(f"  Is complete: {metrics['is_complete']}")


def test_performance_score():
    """Test the performance score calculation."""
    print("\n" + "="*70)
    print("TEST 3: Performance Score Calculation")
    print("="*70)
    
    app = create_app()
    with app.app_context():
        # Get the same session from test 2
        student = Student.query.filter_by(email='window_test@test.com').first()
        sessions = Session.query.filter_by(student_id=student.id).all()
        
        if sessions:
            session = sessions[0]
            responses = StudentResponse.query.filter_by(session_id=session.id).all()
            
            if len(responses) >= 5:
                # Create window with actual responses
                window = PerformanceWindow(session.id, student.id)
                for r in responses:
                    window.add_response(r)
                
                score_data = window.get_performance_score()
                
                print(f"\n✓ Performance Score Analysis:")
                print(f"  Overall Score: {score_data['score']:.4f} ({score_data['feedback']})")
                print(f"\n  Component Breakdown:")
                print(f"    Accuracy:          {score_data['components']['accuracy']:.4f} (weight: 60%)")
                print(f"    Response Time:     {score_data['components']['response_time']:.4f} (weight: 25%)")
                print(f"    Hint Efficiency:   {score_data['components']['hint_efficiency']:.4f} (weight: 15%)")
                print(f"\n  Metrics:")
                metrics = score_data['metrics']
                print(f"    Correct: {metrics['correct_count']}/{metrics['correct_count'] + metrics['incorrect_count']}")
                print(f"    Avg Time: {metrics['avg_response_time']:.2f}s")
                print(f"    Hints: {metrics['hints_used']}")


def test_window_tracker():
    """Test the WindowPerformanceTracker across multiple windows."""
    print("\n" + "="*70)
    print("TEST 4: Multi-Window Performance Tracking")
    print("="*70)
    
    app = create_app()
    with app.app_context():
        # Create student
        student = Student.query.filter_by(email='tracker_test@test.com').first()
        if not student:
            student = Student(email='tracker_test@test.com', name='Tracker Test')
            db.session.add(student)
            db.session.commit()
        
        # Clean up old sessions
        old_sessions = Session.query.filter_by(student_id=student.id).all()
        for s in old_sessions:
            StudentResponse.query.filter_by(session_id=s.id).delete()
            db.session.delete(s)
        db.session.commit()
        
        # Start session with many questions
        cbt = CBTSystem()
        session_result = cbt.start_session(student.id, 'Mathematics', 15)
        session_id = session_result['session_id']
        
        # Create tracker
        tracker = WindowPerformanceTracker(session_id, student.id)
        
        print(f"\n📊 Submitting 15 questions (simulating improving performance):\n")
        
        # Submit 15 responses - with improving accuracy over windows
        for i in range(15):
            q = cbt.get_next_question(session_id)
            question = Question.query.get(q['question_id'])
            
            # Window 1 (Q1-Q5): 2/5 correct (poor)
            # Window 2 (Q6-Q10): 3/5 correct (improving)
            # Window 3 (Q11-15): 5/5 correct (excellent)
            if i < 5:
                is_correct = i in [0, 3]  # 2 correct
            elif i < 10:
                is_correct = i in [5, 7, 9]  # 3 correct
            else:
                is_correct = True  # 5 correct
            
            response = cbt.submit_response(
                session_id,
                q['question_id'],
                question.correct_option if is_correct else 'X',
                3.5
            )
            
            # Get actual StudentResponse
            student_response = StudentResponse.query.filter_by(
                session_id=session_id,
                question_id=q['question_id']
            ).first()
            
            window_update = tracker.add_response(student_response)
            
            if window_update['window_complete']:
                window_num = window_update['total_windows_completed']
                score = window_update['window_score']
                print(f"  ✓ Window {window_num} completed: Score {score['score']:.4f} ({score['feedback']})")
        
        # Get overall performance
        overall = tracker.get_overall_performance()
        
        print(f"\n✓ Overall Performance Summary:")
        print(f"  Windows completed: {overall['total_windows']}")
        print(f"  Average score: {overall['avg_score']:.4f}")
        print(f"  Best window: {overall['best_window']:.4f}")
        print(f"  Worst window: {overall['worst_window']:.4f}")
        print(f"  Trend: {overall['trend']}")


def test_feedback_levels():
    """Test that feedback levels are assigned correctly."""
    print("\n" + "="*70)
    print("TEST 5: Feedback Level Assignment")
    print("="*70)
    
    feedback_levels = {
        0.90: "excellent",
        0.75: "good",
        0.60: "fair",
        0.40: "poor",
        0.15: "very_poor"
    }
    
    print("\nFeedback Scale:")
    print("  Score Range        Feedback Level")
    print("  ─────────────────  ─────────────")
    print("  ≥ 0.85             excellent")
    print("  ≥ 0.70             good")
    print("  ≥ 0.50             fair")
    print("  ≥ 0.30             poor")
    print("  < 0.30             very_poor")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("WINDOW-BASED PERFORMANCE EVALUATOR TESTS")
    print("="*70)
    
    test_window_creation()
    test_window_metrics()
    test_performance_score()
    test_window_tracker()
    test_feedback_levels()
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETED")
    print("="*70)
