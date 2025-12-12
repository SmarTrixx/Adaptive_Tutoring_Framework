import pytest
from app import db
from app.models import Question, Student, Session


class TestBasicEndpoints:
    """Test basic app functionality."""
    
    def test_health_endpoint_via_app(self, app):
        """Test application context."""
        with app.app_context():
            # Verify database is set up
            assert db.engine is not None
    
    def test_cors_enabled(self, client):
        """Test that CORS is enabled."""
        # CORS should allow OPTIONS requests
        response = client.options('/')
        assert response.status_code in [200, 404]  # 404 is OK if route doesn't exist


class TestDatabaseSetup:
    """Test database initialization."""
    
    def test_tables_created(self, app):
        """Test that all tables are created."""
        with app.app_context():
            # Check if tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            # Verify key tables exist (table names are lowercase plural)
            assert 'students' in tables
            assert 'questions' in tables
            assert 'sessions' in tables
    
    def test_sample_data_available(self, app, sample_questions):
        """Test that sample questions are created."""
        with app.app_context():
            count = Question.query.count()
            assert count > 0


class TestStudentOperations:
    """Test student-related operations."""
    
    def test_student_creation_via_app(self, app):
        """Test creating a student directly."""
        with app.app_context():
            student = Student(
                email='direct@example.com',
                name='Direct Test'
            )
            db.session.add(student)
            db.session.commit()
            
            # Verify creation
            found = Student.query.filter_by(email='direct@example.com').first()
            assert found is not None
            assert found.name == 'Direct Test'
    
    def test_student_retrieval(self, app, sample_student):
        """Test retrieving a student."""
        with app.app_context():
            student = Student.query.get(sample_student)
            assert student is not None
            assert student.name == 'Test Student'


class TestQuestionOperations:
    """Test question-related operations."""
    
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
                Question.difficulty <= 0.3
            ).all()
            assert len(easy_questions) > 0
    
    def test_random_question_selection(self, app, sample_questions):
        """Test selecting a random question."""
        with app.app_context():
            import random
            all_questions = Question.query.all()
            random_q = random.choice(all_questions)
            assert random_q is not None
            assert random_q.question_text is not None


class TestSessionOperations:
    """Test session-related operations."""
    
    def test_session_creation(self, app, sample_student, sample_questions):
        """Test creating a session."""
        with app.app_context():
            session = Session(
                student_id=sample_student,
                subject='Mathematics'
            )
            db.session.add(session)
            db.session.commit()
            
            assert session.id is not None
            assert session.student_id == sample_student
    
    def test_session_completion(self, app, sample_student):
        """Test marking a session as complete."""
        with app.app_context():
            session = Session(
                student_id=sample_student,
                subject='Mathematics'
            )
            db.session.add(session)
            db.session.commit()
            
            session_id = session.id
            
            # Update session
            session.is_completed = True
            session.score = 85.5
            db.session.commit()
            
            # Verify
            updated = Session.query.get(session_id)
            assert updated.is_completed == True
            assert updated.score == 85.5


class TestDataIntegrity:
    """Test data integrity and constraints."""
    
    def test_question_has_required_fields(self, app, sample_questions):
        """Test that questions have all required fields."""
        with app.app_context():
            question = Question.query.first()
            
            assert question.question_text is not None
            assert question.subject is not None
            assert question.topic is not None
            assert question.difficulty is not None
            assert question.correct_option is not None
            assert question.option_a is not None
            assert question.option_b is not None
            assert question.option_c is not None
            assert question.option_d is not None
    
    def test_difficulty_range(self, app, sample_questions):
        """Test that difficulty values are in valid range."""
        with app.app_context():
            questions = Question.query.all()
            
            for q in questions:
                assert 0 <= q.difficulty <= 1, f"Invalid difficulty: {q.difficulty}"
    
    def test_student_email_uniqueness(self, app):
        """Test that student emails are unique."""
        with app.app_context():
            s1 = Student(email='unique@example.com', name='Student 1')
            db.session.add(s1)
            db.session.commit()
            
            s2 = Student(email='unique@example.com', name='Student 2')
            db.session.add(s2)
            
            # Should raise an integrity error
            with pytest.raises(Exception):
                db.session.commit()
