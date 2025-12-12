import pytest
from app import db
from app.models import Question


class TestQuestionModel:
    """Test Question model."""
    
    def test_question_creation(self, app):
        """Test creating a question."""
        with app.app_context():
            question = Question(
                subject='Mathematics',
                topic='Geometry',
                difficulty=0.5,
                question_text='What is pi?',
                option_a='3.14',
                option_b='3.15',
                option_c='3.16',
                option_d='3.17',
                correct_option='A',
                explanation='Pi is approximately 3.14159',
                hints=['Remember: 3.14']
            )
            db.session.add(question)
            db.session.commit()
            
            assert question.id is not None
            assert question.subject == 'Mathematics'
            assert question.difficulty == 0.5
    
    def test_question_difficulty_validation(self, app):
        """Test question difficulty is between 0 and 1."""
        with app.app_context():
            for diff in [0, 0.5, 1.0]:
                q = Question(
                    subject='Math',
                    topic='Algebra',
                    difficulty=diff,
                    question_text='Test',
                    option_a='A', option_b='B', option_c='C', option_d='D',
                    correct_option='A'
                )
                db.session.add(q)
            db.session.commit()
    
    def test_question_retrieval_by_subject(self, app, sample_questions):
        """Test retrieving questions by subject."""
        with app.app_context():
            math_questions = Question.query.filter_by(subject='Mathematics').all()
            assert len(math_questions) > 0
    
    def test_question_retrieval_by_difficulty(self, app, sample_questions):
        """Test retrieving questions by difficulty range."""
        with app.app_context():
            easy_questions = Question.query.filter(
                Question.difficulty >= 0.1,
                Question.difficulty <= 0.4
            ).all()
            assert len(easy_questions) > 0
