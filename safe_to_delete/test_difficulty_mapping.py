#!/usr/bin/env python3
"""
Test: Question Difficulty Mapping and Pool Selection

Verifies that:
1. Question difficulty labels work correctly
2. System difficulty maps to correct question pools
3. Increasing system difficulty selects harder questions
"""

import sys
sys.path.insert(0, 'backend')

from app import create_app, db
from app.models.question import Question
from app.models.student import Student
from app.models.session import Session
from app.cbt.system import CBTSystem
from app.adaptation.difficulty_mapper import DifficultyMapper, analyze_question_pools


def test_difficulty_mapping():
    """Test the difficulty mapper logic."""
    print("="*70)
    print("TEST 1: Difficulty Mapping Logic")
    print("="*70)
    
    test_cases = [
        (0.0, "easy", "Start - should be easy"),
        (0.2, "easy", "20% - still easy"),
        (0.35, "medium", "Boundary to medium"),
        (0.5, "medium", "Middle - medium"),
        (0.65, "hard", "Boundary to hard"),
        (0.8, "hard", "80% - hard"),
        (1.0, "hard", "Maximum - hard"),
    ]
    
    for system_diff, expected_label, description in test_cases:
        label = DifficultyMapper.get_difficulty_label(system_diff)
        min_d, max_d, label_range = DifficultyMapper.get_difficulty_range(system_diff)
        status = "✓" if label == expected_label else "✗"
        print(f"{status} {system_diff:.2f} → {label:6s} (expected {expected_label:6s}) | Range: {min_d:.2f}-{max_d:.2f} | {description}")


def test_question_pool_distribution():
    """Test question pool distribution across difficulty levels."""
    print("\n" + "="*70)
    print("TEST 2: Question Pool Distribution")
    print("="*70)
    
    app = create_app()
    with app.app_context():
        # Check if we have questions in database
        total_questions = Question.query.count()
        if total_questions == 0:
            print("⚠️  No questions in database. Seeding test questions...")
            _seed_test_questions()
        
        # Count questions by difficulty
        easy_questions = Question.query.filter(
            Question.difficulty < DifficultyMapper.THRESHOLD_LOW_TO_MEDIUM
        ).count()
        
        medium_questions = Question.query.filter(
            Question.difficulty >= DifficultyMapper.THRESHOLD_LOW_TO_MEDIUM,
            Question.difficulty < DifficultyMapper.THRESHOLD_MEDIUM_TO_HARD
        ).count()
        
        hard_questions = Question.query.filter(
            Question.difficulty >= DifficultyMapper.THRESHOLD_MEDIUM_TO_HARD
        ).count()
        
        total = easy_questions + medium_questions + hard_questions
        
        print(f"\n📊 Question Pool Distribution:")
        print(f"  Easy (0.0-0.35):    {easy_questions:3d} questions ({easy_questions/total*100:.1f}%)")
        print(f"  Medium (0.35-0.65): {medium_questions:3d} questions ({medium_questions/total*100:.1f}%)")
        print(f"  Hard (0.65-1.0):    {hard_questions:3d} questions ({hard_questions/total*100:.1f}%)")
        print(f"  {'─'*45}")
        print(f"  Total:              {total:3d} questions")


def test_difficulty_based_selection():
    """Test that system difficulty actually affects question selection."""
    print("\n" + "="*70)
    print("TEST 3: Difficulty-Based Question Selection")
    print("="*70)
    
    app = create_app()
    with app.app_context():
        # Create a test student
        student = Student.query.filter_by(email='difficulty_test@test.com').first()
        if not student:
            student = Student(email='difficulty_test@test.com', name='Difficulty Test')
            db.session.add(student)
            db.session.commit()
        
        # Clean up old sessions
        old_sessions = Session.query.filter_by(student_id=student.id).all()
        for s in old_sessions:
            from app.models.session import StudentResponse
            StudentResponse.query.filter_by(session_id=s.id).delete()
            db.session.delete(s)
        db.session.commit()
        
        # Create sessions at different difficulty levels
        cbt = CBTSystem()
        
        difficulties_to_test = [
            (0.2, "Easy (20%)"),
            (0.5, "Medium (50%)"),
            (0.8, "Hard (80%)")
        ]
        
        print("\n🎯 Testing question selection at different system difficulties:\n")
        
        for target_difficulty, description in difficulties_to_test:
            print(f"\n{description}")
            print(f"{'─'*50}")
            
            # Start session
            session_result = cbt.start_session(student.id, 'Mathematics', 1)
            session = Session.query.get(session_result['session_id'])
            session.current_difficulty = target_difficulty
            db.session.commit()
            
            # Get a question
            q_result = cbt.get_next_question(session_result['session_id'])
            
            if 'error' not in q_result:
                question = Question.query.get(q_result['question_id'])
                label = DifficultyMapper.get_difficulty_label(target_difficulty)
                
                print(f"  System difficulty: {target_difficulty:.2f}")
                print(f"  Target label: {label}")
                print(f"  Question difficulty: {question.difficulty:.2f}")
                print(f"  Question text: {question.question_text[:60]}...")
                
                # Check if question is in expected range
                min_d, max_d, _ = DifficultyMapper.get_difficulty_range(target_difficulty)
                in_range = min_d <= question.difficulty <= max_d
                status = "✓" if in_range else "⚠️"
                print(f"  {status} In expected range [{min_d:.2f}, {max_d:.2f}]")


def test_pool_analysis():
    """Test the pool analysis function."""
    print("\n" + "="*70)
    print("TEST 4: Pool Analysis at Different System Difficulties")
    print("="*70)
    
    app = create_app()
    with app.app_context():
        student = Student.query.filter_by(email='difficulty_test@test.com').first()
        if not student:
            student = Student(email='difficulty_test@test.com', name='Difficulty Test')
            db.session.add(student)
            db.session.commit()
        
        session = Session.query.filter_by(student_id=student.id).first()
        if not session:
            cbt = CBTSystem()
            session_result = cbt.start_session(student.id, 'Mathematics', 10)
            session = Session.query.get(session_result['session_id'])
        
        test_difficulties = [0.2, 0.5, 0.8]
        
        for diff in test_difficulties:
            session.current_difficulty = diff
            db.session.commit()
            
            analysis = analyze_question_pools(session)
            
            print(f"\n🔍 System Difficulty: {diff:.2f}")
            print(f"   Target Label: {analysis['target_label']}")
            print(f"   Target Range: {analysis['target_range'][0]:.2f} - {analysis['target_range'][1]:.2f}")
            print(f"   Available Pools:")
            print(f"     Easy:   {analysis['pools']['easy']:3d} questions")
            print(f"     Medium: {analysis['pools']['medium']:3d} questions")
            print(f"     Hard:   {analysis['pools']['hard']:3d} questions")


def _seed_test_questions():
    """Seed some test questions if database is empty."""
    app = create_app()
    with app.app_context():
        # Create questions across difficulty spectrum
        questions_data = [
            # Easy questions (0.1-0.3)
            ("Math", "Arithmetic", 0.15, "What is 2 + 2?", "4", "5", "3", "6", "A", "Basic addition"),
            ("Math", "Arithmetic", 0.20, "What is 3 × 3?", "9", "6", "12", "15", "A", "Basic multiplication"),
            ("Math", "Arithmetic", 0.25, "What is 10 - 5?", "5", "15", "2", "8", "A", "Basic subtraction"),
            
            # Medium questions (0.4-0.6)
            ("Math", "Algebra", 0.45, "Solve: x + 5 = 12", "7", "17", "2.4", "2", "A", "Linear equation"),
            ("Math", "Algebra", 0.50, "What is √16?", "4", "8", "2", "256", "A", "Square root"),
            ("Math", "Algebra", 0.55, "Solve: 2x = 10", "5", "20", "12", "8", "A", "Linear equation"),
            
            # Hard questions (0.7-0.9)
            ("Math", "Calculus", 0.75, "What is the derivative of x²?", "2x", "x", "2", "x²", "A", "Derivative"),
            ("Math", "Calculus", 0.80, "Integrate: ∫2x dx", "x²", "x", "2x", "x² + C", "A", "Integration"),
            ("Math", "Calculus", 0.85, "What is the limit of 1/x as x→∞?", "0", "1", "∞", "-∞", "A", "Limits"),
        ]
        
        for subject, topic, difficulty, question, opt_a, opt_b, opt_c, opt_d, correct, explanation in questions_data:
            if not Question.query.filter_by(question_text=question).first():
                q = Question(
                    subject=subject,
                    topic=topic,
                    difficulty=difficulty,
                    question_text=question,
                    option_a=opt_a,
                    option_b=opt_b,
                    option_c=opt_c,
                    option_d=opt_d,
                    correct_option=correct,
                    explanation=explanation
                )
                db.session.add(q)
        
        db.session.commit()
        print("✓ Test questions seeded successfully")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("DIFFICULTY MAPPING & QUESTION POOL SELECTION TESTS")
    print("="*70)
    
    test_difficulty_mapping()
    test_question_pool_distribution()
    test_difficulty_based_selection()
    test_pool_analysis()
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETED")
    print("="*70)
