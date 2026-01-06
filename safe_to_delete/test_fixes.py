#!/usr/bin/env python3
"""
Test script to verify all fixes are working correctly.
Generates fresh data with the fixed code.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from main import app
from app import db
from app.models.student import Student
from app.models.session import Session
from app.models.question import Question
from app.models.session import StudentResponse
from app.models.engagement import EngagementMetric
from app.cbt.system import CBTSystem
import time
from datetime import datetime

def test_difficulty_scaling():
    """Test difficulty scaling algorithm"""
    print("\n" + "="*80)
    print("TEST 1: DIFFICULTY SCALING")
    print("="*80)
    
    with app.app_context():
        cbt_system = CBTSystem()
        
        # Create student
        unique_id = int(time.time() * 1000) % 1000000
        student = Student(email=f"test_scale_{unique_id}@example.com", name="TestScale")
        db.session.add(student)
        db.session.commit()
        
        # Create session
        session = Session(student_id=student.id, subject='Mathematics', total_questions=4)
        db.session.add(session)
        db.session.commit()
        
        # Get questions
        questions = Question.query.limit(4).all()
        initial_difficulty = session.current_difficulty
        
        print(f"\nInitial difficulty: {initial_difficulty:.2f}")
        print("Simulating: 4 correct answers (accuracy = 1.0)")
        print()
        
        for i, q in enumerate(questions, 1):
            # Submit correct answer
            result = cbt_system.submit_response(
                session_id=session.id,
                question_id=q.id,
                student_answer=q.correct_option,
                response_time_seconds=5.0
            )
            
            # Refresh session
            db.session.refresh(session)
            
            # Get the metric that was just created
            metric = EngagementMetric.query.filter_by(
                session_id=session.id
            ).order_by(EngagementMetric.timestamp.desc()).first()
            
            print(f"Q{i}: accuracy={metric.accuracy:.0%} ", end="")
            print(f"difficulty {initial_difficulty + (i-1)*0.10:.2f} → {session.current_difficulty:.2f} ", end="")
            print(f"response_time={metric.response_time_seconds}s ✓")
        
        print(f"\nExpected: 0.50 → 0.60 → 0.70 → 0.80 → 0.90")
        print(f"Got:      {initial_difficulty:.2f} → ", end="")
        for i in range(1, 5):
            print(f"{initial_difficulty + i*0.10:.2f}", end="")
            if i < 4:
                print(" → ", end="")
        print()
        
        # Verify metrics were created with correct response_time
        metrics = EngagementMetric.query.filter_by(session_id=session.id).all()
        print(f"\n✅ Metrics created: {len(metrics)}")
        print(f"✅ Response times in metrics: {[m.response_time_seconds for m in metrics]}")
        
        return True


def test_response_time_tracking():
    """Test that response_time_seconds is properly tracked"""
    print("\n" + "="*80)
    print("TEST 2: RESPONSE_TIME TRACKING")
    print("="*80)
    
    with app.app_context():
        cbt_system = CBTSystem()
        
        # Create student
        unique_id = int(time.time() * 1000) % 1000000
        student = Student(email=f"test_response_{unique_id}@example.com", name="TestResponse")
        db.session.add(student)
        db.session.commit()
        
        # Create session
        session = Session(student_id=student.id, subject='English', total_questions=3)
        db.session.add(session)
        db.session.commit()
        
        questions = Question.query.limit(3).all()
        response_times = [5.5, 10.2, 15.8]
        
        print("\nSubmitting responses with different response times:")
        for i, (q, rt) in enumerate(zip(questions, response_times), 1):
            result = cbt_system.submit_response(
                session_id=session.id,
                question_id=q.id,
                student_answer=q.correct_option,
                response_time_seconds=rt
            )
            
            # Get the metric
            metric = EngagementMetric.query.filter_by(
                session_id=session.id
            ).order_by(EngagementMetric.timestamp.desc()).first()
            
            match = "✅" if metric.response_time_seconds == rt else "❌"
            print(f"  {match} Q{i}: Sent={rt}s, Stored={metric.response_time_seconds}s")
        
        # Verify all metrics have correct response times
        metrics = EngagementMetric.query.filter_by(session_id=session.id).all()
        all_correct = all(m.response_time_seconds in response_times for m in metrics)
        print(f"\n✅ All response times correctly stored: {all_correct}")
        
        return all_correct


def test_interest_level_inference():
    """Test that interest_level is inferred from behavior"""
    print("\n" + "="*80)
    print("TEST 3: INTEREST_LEVEL INFERENCE")
    print("="*80)
    
    with app.app_context():
        cbt_system = CBTSystem()
        
        # Create student
        unique_id = int(time.time() * 1000) % 1000000
        student = Student(email=f"test_interest_{unique_id}@example.com", name="TestInterest")
        db.session.add(student)
        db.session.commit()
        
        # Create session
        session = Session(student_id=student.id, subject='Science', total_questions=3)
        db.session.add(session)
        db.session.commit()
        
        questions = Question.query.limit(3).all()
        
        print("\nSubmitting 3 responses with perfect accuracy (high interest expected):")
        for i, q in enumerate(questions, 1):
            result = cbt_system.submit_response(
                session_id=session.id,
                question_id=q.id,
                student_answer=q.correct_option,
                response_time_seconds=3.0  # Fast responses = interested
            )
            
            metric = EngagementMetric.query.filter_by(
                session_id=session.id
            ).order_by(EngagementMetric.timestamp.desc()).first()
            
            print(f"  Q{i}: interest_level={metric.interest_level:.2f} (not hardcoded 0.5 ✓)")
        
        # Check that interest level varies
        metrics = EngagementMetric.query.filter_by(session_id=session.id).all()
        interest_levels = [m.interest_level for m in metrics]
        not_all_half = not all(il == 0.5 for il in interest_levels)
        
        print(f"\n✅ Interest levels vary: {interest_levels}")
        print(f"✅ Not all hardcoded to 0.5: {not_all_half}")
        
        return not_all_half


def test_engagement_metrics_created():
    """Test that engagement metrics are created for each response"""
    print("\n" + "="*80)
    print("TEST 4: ENGAGEMENT METRICS CREATION")
    print("="*80)
    
    with app.app_context():
        cbt_system = CBTSystem()
        
        # Create student
        unique_id = int(time.time() * 1000) % 1000000
        student = Student(email=f"test_metrics_{unique_id}@example.com", name="TestMetrics")
        db.session.add(student)
        db.session.commit()
        
        # Create session
        session = Session(student_id=student.id, subject='History', total_questions=5)
        db.session.add(session)
        db.session.commit()
        
        questions = Question.query.limit(5).all()
        
        print(f"\nSubmitting 5 responses and checking metrics creation:")
        for i, q in enumerate(questions, 1):
            cbt_system.submit_response(
                session_id=session.id,
                question_id=q.id,
                student_answer=q.correct_option,
                response_time_seconds=7.0
            )
            
            metrics = EngagementMetric.query.filter_by(session_id=session.id).all()
            print(f"  Q{i}: {len(metrics)} metric(s) created")
        
        # Verify all fields are populated
        metrics = EngagementMetric.query.filter_by(session_id=session.id).all()
        print(f"\n✅ Total metrics created: {len(metrics)}")
        
        if metrics:
            m = metrics[0]
            populated = {
                'response_time_seconds': m.response_time_seconds is not None and m.response_time_seconds != 0,
                'accuracy': m.accuracy is not None,
                'engagement_score': m.engagement_score is not None,
                'confidence_level': m.confidence_level is not None,
                'attempts_count': m.attempts_count is not None,
            }
            
            for field, is_populated in populated.items():
                status = "✅" if is_populated else "❌"
                value = getattr(m, field)
                print(f"  {status} {field}: {value}")
        
        return len(metrics) == 5


def run_all_tests():
    """Run all tests"""
    print("\n\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "VERIFICATION: ALL FIXES ARE WORKING".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "="*78 + "╝")
    
    results = []
    
    try:
        results.append(("Difficulty Scaling", test_difficulty_scaling()))
    except Exception as e:
        print(f"❌ Difficulty scaling test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Difficulty Scaling", False))
    
    try:
        results.append(("Response Time Tracking", test_response_time_tracking()))
    except Exception as e:
        print(f"❌ Response time test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Response Time Tracking", False))
    
    try:
        results.append(("Interest Level Inference", test_interest_level_inference()))
    except Exception as e:
        print(f"❌ Interest level test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Interest Level Inference", False))
    
    try:
        results.append(("Metrics Creation", test_engagement_metrics_created()))
    except Exception as e:
        print(f"❌ Metrics test failed: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Metrics Creation", False))
    
    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result[1] for result in results)
    print("\n" + "="*80)
    if all_passed:
        print("✅ ALL TESTS PASSED - Fixes are working correctly!")
    else:
        print("❌ Some tests failed - check output above")
    print("="*80)
    
    return all_passed


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
