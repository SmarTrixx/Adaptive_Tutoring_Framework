import pytest
import os
import tempfile
from app import create_app, db
from app.models import Student, Question, Session


@pytest.fixture
def app():
    """Create and configure a test app."""
    db_fd, db_path = tempfile.mkstemp()
    app = create_app('testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's CLI commands."""
    return app.test_cli_runner()


@pytest.fixture
def sample_student(app):
    """Create a sample student for testing."""
    with app.app_context():
        student = Student(
            email='test@example.com',
            name='Test Student'
        )
        db.session.add(student)
        db.session.commit()
        # Return ID instead of object to avoid DetachedInstanceError
        return student.id


@pytest.fixture
def sample_questions(app):
    """Create sample questions for testing."""
    with app.app_context():
        questions = [
            Question(
                subject='Mathematics',
                topic='Algebra',
                difficulty=0.2,
                question_text='What is 2 + 2?',
                option_a='3',
                option_b='4',
                option_c='5',
                option_d='6',
                correct_option='B',
                explanation='2 plus 2 equals 4',
                hints=['Count: 1,2,3,4']
            ),
            Question(
                subject='Mathematics',
                topic='Algebra',
                difficulty=0.5,
                question_text='Solve: x + 5 = 12',
                option_a='x = 7',
                option_b='x = 17',
                option_c='x = -7',
                option_d='x = 2',
                correct_option='A',
                explanation='Subtract 5 from both sides: x = 7',
                hints=['Move 5 to the other side']
            ),
            Question(
                subject='Science',
                topic='Physics',
                difficulty=0.3,
                question_text='What is the SI unit of force?',
                option_a='Joule',
                option_b='Newton',
                option_c='Watt',
                option_d='Pascal',
                correct_option='B',
                explanation='The Newton (N) is the SI unit of force',
                hints=['F = ma']
            )
        ]
        for q in questions:
            db.session.add(q)
        db.session.commit()
        return questions
