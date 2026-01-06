#!/usr/bin/env python3
"""
Test script to verify frontend fixes:
1. Difficulty values show 0.10 step progression (not 0.05)
2. Engagement metrics are created with real values
3. Dashboard receives correct data

Run after starting backend: python3 test_frontend_fixes.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import create_app, db
from app.models.student import Student
from app.models.session import Session
from app.models.question import Question
from app.models.engagement import EngagementMetric
from app.cbt.system import CBTSystem
from app.analytics.routes import get_dashboard
from datetime import datetime

def setup_test_data():
    """Create test student and questions"""
    print("\n" + "="*80)
    print("SETUP: Creating test data...")
    print("="*80)
    
    # Create test student
    student = Student.query.filter_by(email='frontend_test@test.com').first()
    if not student:
        student = Student(email='frontend_test@test.com', name='Frontend Tester')
        db.session.add(student)
        db.session.commit()
    print(f"✅ Student created: {student.id}")
    
    # Create test questions if they don't exist
    questions = Question.query.filter_by(subject='Mathematics').limit(20).all()
    if len(questions) < 20:
        print("⚠️  Need at least 20 Mathematics questions. Creating test questions...")
        for i in range(1, 21):
            if not Question.query.filter_by(subject='Mathematics', question_text=f'Test Q{i}').first():
                q = Question(
                    subject='Mathematics',
                    question_text=f'Test Q{i}: What is {i}+{i}?',
                    option_a=str(2*i),
                    option_b=str(2*i + 1),
                    option_c=str(2*i - 1),
                    option_d=str(2*i + 2),
                    correct_option='A',
                    difficulty=0.5,
                    explanation=f'The answer is {2*i}',
                    hints=[f'Hint 1: {i}+{i}={2*i}', f'Hint 2: Double the number']
                )
                db.session.add(q)
        db.session.commit()
        print("✅ Test questions created")
    
    return student

def test_difficulty_progression_frontend():
    """Test 1: Verify difficulty shows 0.10 step progression"""
    print("\n" + "="*80)
    print("TEST 1: DIFFICULTY PROGRESSION (Frontend View)")
    print("="*80)
    
    student = Student.query.filter_by(email='frontend_test@test.com').first()
    cbt = CBTSystem()
    
    # Start session
    session_result = cbt.start_session(student.id, 'Mathematics', 10)
    session_id = session_result['session_id']
    print(f"✅ Session started: {session_id}")
    print(f"   Initial difficulty: {session_result['current_difficulty']}")
    
    difficulties = [session_result['current_difficulty']]
    
    # Submit 4 CORRECT answers
    print("\n   Submitting 4 CORRECT answers...")
    for i in range(4):
        # Get question
        q_result = cbt.get_next_question(session_id)
        question_id = q_result['question_id']
        
        # Submit correct answer
        response = cbt.submit_response(session_id, question_id, 'A', 5.0)
        
        if response.get('is_correct'):
            new_difficulty = response['current_difficulty']
            difficulties.append(new_difficulty)
            print(f"   Q{i+1}: ✓ Correct | Difficulty now: {new_difficulty:.2f}")
        else:
            print(f"   Q{i+1}: ✗ Wrong (unexpected!)")
    
    # Verify progression
    print("\n   📊 Difficulty Progression:")
    for i, d in enumerate(difficulties):
        print(f"      Step {i}: {d:.2f}")
    
    # Check if using 0.10 steps (NEW) or 0.05 steps (OLD)
    deltas = [difficulties[i+1] - difficulties[i] for i in range(len(difficulties)-1)]
    print(f"\n   Step sizes: {[f'{d:.2f}' for d in deltas]}")
    
    if deltas[0] >= 0.09 and deltas[0] <= 0.11:
        print(f"\n✅ TEST 1 PASSED: Using 0.10 step sizes (FIXED)")
        return True
    elif deltas[0] >= 0.04 and deltas[0] <= 0.06:
        print(f"\n❌ TEST 1 FAILED: Still using 0.05 step sizes (OLD)")
        return False
    else:
        print(f"\n❓ TEST 1 UNCLEAR: Using {deltas[0]:.2f} step sizes")
        return False

def test_engagement_metrics_creation():
    """Test 2: Verify engagement metrics are created with real values"""
    print("\n" + "="*80)
    print("TEST 2: ENGAGEMENT METRICS CREATION")
    print("="*80)
    
    student = Student.query.filter_by(email='frontend_test@test.com').first()
    cbt = CBTSystem()
    
    # Start fresh session
    session_result = cbt.start_session(student.id, 'Mathematics', 5)
    session_id = session_result['session_id']
    print(f"✅ Session started: {session_id}")
    
    # Clear old metrics for this session
    EngagementMetric.query.filter_by(session_id=session_id).delete()
    db.session.commit()
    
    # Submit 3 responses
    print("\n   Submitting 3 responses...")
    for i in range(3):
        q_result = cbt.get_next_question(session_id)
        response = cbt.submit_response(session_id, q_result['question_id'], 'A', 5.0 + i)
        print(f"   Q{i+1}: Response submitted (time: {5.0+i}s)")
    
    # Check metrics created
    metrics = EngagementMetric.query.filter_by(session_id=session_id).order_by(
        EngagementMetric.timestamp
    ).all()
    
    print(f"\n   📊 Metrics Created: {len(metrics)}")
    
    if len(metrics) < 3:
        print(f"❌ TEST 2 FAILED: Only {len(metrics)} metrics created, expected 3")
        return False
    
    # Check metric fields
    print("\n   Checking metric field values:")
    all_good = True
    
    for i, metric in enumerate(metrics):
        print(f"\n   Metric {i+1}:")
        print(f"      response_time_seconds: {metric.response_time_seconds}")
        print(f"      interest_level: {metric.interest_level}")
        print(f"      engagement_score: {metric.engagement_score}")
        print(f"      attempts_count: {metric.attempts_count}")
        
        # Check if values are real (not hardcoded)
        if metric.response_time_seconds == 0:
            print(f"      ❌ response_time is 0 (should be >0)")
            all_good = False
        
        if metric.interest_level == 0.5:
            print(f"      ❌ interest_level is 0.5 (hardcoded, should vary)")
            all_good = False
        
        if metric.engagement_score is None or metric.engagement_score == 0:
            print(f"      ❌ engagement_score is None or 0")
            all_good = False
    
    if all_good and len(metrics) == 3:
        print(f"\n✅ TEST 2 PASSED: Metrics created with real values")
        return True
    else:
        print(f"\n❌ TEST 2 FAILED: Some metrics have hardcoded/missing values")
        return False

def test_dashboard_data():
    """Test 3: Verify dashboard receives correct engagement data"""
    print("\n" + "="*80)
    print("TEST 3: DASHBOARD DATA (Frontend Receives)")
    print("="*80)
    
    student = Student.query.filter_by(email='frontend_test@test.com').first()
    
    # Simulate getting dashboard
    from flask import Flask
    from app.analytics.routes import analytics_bp
    
    app = create_app()
    with app.app_context():
        print(f"✅ Checking dashboard data for student {student.id}")
        
        # Get all engagement metrics for this student
        metrics = EngagementMetric.query.filter_by(student_id=student.id).all()
        print(f"\n   Total metrics for student: {len(metrics)}")
        
        if len(metrics) == 0:
            print("❌ TEST 3 FAILED: No metrics found for student")
            return False
        
        # Get latest metric (what dashboard will show)
        latest = metrics[-1]
        print(f"\n   Latest Engagement Metric:")
        print(f"      engagement_score: {latest.engagement_score}")
        print(f"      engagement_level: {latest.engagement_level}")
        print(f"      response_time_seconds: {latest.response_time_seconds}")
        print(f"      interest_level: {latest.interest_level}")
        
        # Dashboard stats
        print(f"\n   Dashboard Statistics (would show):")
        sessions = Session.query.filter_by(student_id=student.id).all()
        total_questions = sum(len(s.responses) for s in sessions)
        correct = sum(s.correct_answers for s in sessions)
        accuracy = (correct / total_questions * 100) if total_questions > 0 else 0
        
        print(f"      Total Sessions: {len(sessions)}")
        print(f"      Total Questions: {total_questions}")
        print(f"      Accuracy: {accuracy:.1f}%")
        print(f"      Latest Engagement: {latest.engagement_score*100:.0f}% (from metric)")
        
        # Verify values are not hardcoded
        if latest.engagement_score and latest.engagement_score > 0:
            print(f"\n✅ TEST 3 PASSED: Dashboard will show real engagement data")
            return True
        else:
            print(f"\n❌ TEST 3 FAILED: Dashboard engagement_score is 0 or None")
            return False

def main():
    """Run all tests"""
    print("\n" + "█"*80)
    print("█" + " "*78 + "█")
    print("█" + "  FRONTEND FIXES VERIFICATION TEST".center(78) + "█")
    print("█" + " "*78 + "█")
    print("█"*80)
    
    app = create_app()
    with app.app_context():
        # Setup
        student = setup_test_data()
        
        # Run tests
        results = {
            'difficulty_progression': test_difficulty_progression_frontend(),
            'engagement_metrics': test_engagement_metrics_creation(),
            'dashboard_data': test_dashboard_data()
        }
        
        # Summary
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        total = len(results)
        passed = sum(1 for v in results.values() if v)
        
        for test_name, passed_test in results.items():
            status = "✅ PASS" if passed_test else "❌ FAIL"
            print(f"{status} - {test_name.replace('_', ' ').title()}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n" + "🎉 "*40)
            print("ALL TESTS PASSED - FRONTEND FIXES WORKING!")
            print("🎉 "*40)
            return 0
        else:
            print("\n⚠️  Some tests failed - see details above")
            return 1

if __name__ == '__main__':
    sys.exit(main())
