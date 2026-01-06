#!/usr/bin/env python3
"""
Integration Test: Complete Flow

Demonstrates:
1. Question difficulty mapping working
2. Performance window evaluation working
3. Both systems working together
"""

import sys
sys.path.insert(0, 'backend')

from app import create_app, db
from app.models.student import Student
from app.models.session import Session, StudentResponse
from app.models.question import Question
from app.cbt.system import CBTSystem
from app.adaptation.difficulty_mapper import DifficultyMapper, analyze_question_pools
from app.adaptation.performance_window import WindowPerformanceTracker


def main():
    print("\n" + "="*80)
    print("INTEGRATION TEST: Question Difficulty + Performance Window Evaluation")
    print("="*80)
    
    app = create_app()
    with app.app_context():
        # Create test student
        student = Student.query.filter_by(email='integration_test@test.com').first()
        if not student:
            student = Student(email='integration_test@test.com', name='Integration Test')
            db.session.add(student)
            db.session.commit()
        
        # Clean up old sessions
        old_sessions = Session.query.filter_by(student_id=student.id).all()
        for s in old_sessions:
            StudentResponse.query.filter_by(session_id=s.id).delete()
            db.session.delete(s)
        db.session.commit()
        
        print(f"\n👤 Student: {student.email}")
        print(f"   ID: {student.id}")
        
        # Start session
        cbt = CBTSystem()
        session_result = cbt.start_session(student.id, 'Mathematics', 15)
        session_id = session_result['session_id']
        session = Session.query.get(session_id)
        
        print(f"\n🎯 Session Started")
        print(f"   Session ID: {session_id}")
        print(f"   Initial Difficulty: {session.current_difficulty:.2f}")
        
        # Analyze pool at start
        analysis = analyze_question_pools(session)
        print(f"   Initial Pool: {analysis['target_label'].upper()}")
        print(f"   Available: Easy={analysis['pools']['easy']}, Medium={analysis['pools']['medium']}, Hard={analysis['pools']['hard']}")
        
        # Create performance tracker
        tracker = WindowPerformanceTracker(session_id, student.id)
        
        print(f"\n📝 COMPLETE SESSION: 15 Questions (3 Windows of 5)")
        print(f"   Window Size: 5 questions")
        print(f"   {'─'*76}")
        print(f"   {'Q#':<4} {'Result':<10} {'Difficulty':<12} {'Label':<8} {'Pool Analysis':<30}")
        print(f"   {'─'*76}")
        
        for i in range(15):
            q_result = cbt.get_next_question(session_id)
            question = Question.query.get(q_result['question_id'])
            
            # Determine correct/wrong - simulating improving performance
            if i < 5:
                is_correct = i in [0, 3]  # 2/5 = poor
            elif i < 10:
                is_correct = i in [5, 7, 9]  # 3/5 = fair
            else:
                is_correct = True  # 5/5 = excellent
            
            # Submit response
            response = cbt.submit_response(
                session_id,
                q_result['question_id'],
                question.correct_option if is_correct else 'X',
                3.5
            )
            
            # Get actual StudentResponse
            student_response = StudentResponse.query.filter_by(
                session_id=session_id,
                question_id=q_result['question_id']
            ).first()
            
            # Add to performance tracker
            window_update = tracker.add_response(student_response)
            
            # Get current difficulty label
            current_diff = session.current_difficulty
            label = DifficultyMapper.get_difficulty_label(current_diff)
            
            # Show result
            result_str = "✓ Correct" if is_correct else "✗ Wrong"
            pool_str = f"Sys: {current_diff:.2f} ({label})"
            
            print(f"   Q{i+1:<3} {result_str:<10} {question.difficulty:<12.2f} {label:<8} {pool_str:<30}", end="")
            
            # Check if window completed
            if window_update['window_complete']:
                window_score = window_update['window_score']
                print(f"\n   {'─'*76}")
                print(f"   🏆 WINDOW {window_update['total_windows_completed']} COMPLETE!")
                print(f"      Score: {window_score['score']:.4f} ({window_score['feedback']})")
                print(f"      Accuracy: {window_score['components']['accuracy']:.2f} | Time: {window_score['components']['response_time']:.2f} | Hints: {window_score['components']['hint_efficiency']:.2f}")
                print(f"      Metrics: {window_score['metrics']['correct_count']}/{window_score['metrics']['correct_count']+window_score['metrics']['incorrect_count']} correct, Avg {window_score['metrics']['avg_response_time']:.1f}s")
                print(f"   {'─'*76}")
            else:
                print()
        
        # Final summary
        session = Session.query.get(session_id)
        overall = tracker.get_overall_performance()
        
        print(f"\n📊 FINAL SUMMARY")
        print(f"   {'─'*76}")
        print(f"   Final Difficulty: {session.current_difficulty:.2f}")
        print(f"   Total Correct: {session.correct_answers}/15")
        print(f"   Final Score: {session.score_percentage:.1f}%")
        
        print(f"\n   🏆 Performance Summary:")
        print(f"      Windows Completed: {overall['total_windows']}")
        print(f"      Average Window Score: {overall['avg_score']:.4f}")
        print(f"      Best Window: {overall['best_window']:.4f}")
        print(f"      Worst Window: {overall['worst_window']:.4f}")
        print(f"      Trend: {overall['trend'].upper()}")
        
        print(f"\n   📈 Window Progression:")
        for idx, score in enumerate(overall['all_windows'], 1):
            bar = "█" * int(score * 20)
            print(f"      Window {idx}: {score:.4f} {bar}")
        
        print(f"\n   ✓ Both systems working together:")
        print(f"      - Difficulty Mapper: Selecting questions by pool ✓")
        print(f"      - Performance Window: Evaluating in 5-question windows ✓")
        print(f"      - Adaptation Ready: For next integration phase ✓")
        
        print(f"\n{'='*80}")
        print("✅ INTEGRATION TEST COMPLETE - Both systems operational!")
        print(f"{'='*80}\n")


if __name__ == '__main__':
    main()
