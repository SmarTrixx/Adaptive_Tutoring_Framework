import pytest
from app import db
from app.models import Student, Session


class TestSessionModel:
    """Test Session model."""
    
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
    
    def test_session_retrieval(self, app, sample_student):
        """Test retrieving a session."""
        with app.app_context():
            session = Session(
                student_id=sample_student,
                subject='Science'
            )
            db.session.add(session)
            db.session.commit()
            
            retrieved = Session.query.filter_by(student_id=sample_student).first()
            assert retrieved is not None
            assert retrieved.subject == 'Science'
