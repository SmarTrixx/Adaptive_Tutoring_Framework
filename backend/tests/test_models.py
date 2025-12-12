import pytest
from app import db
from app.models import Student


class TestStudentModel:
    """Test Student model."""
    
    def test_student_creation(self, app):
        """Test creating a student."""
        with app.app_context():
            student = Student(email='newtest@example.com', name='New Student')
            db.session.add(student)
            db.session.commit()
            
            assert student.id is not None
            assert student.email == 'newtest@example.com'
            assert student.name == 'New Student'
    
    def test_student_retrieval(self, app, sample_student):
        """Test retrieving a student."""
        with app.app_context():
            student = Student.query.get(sample_student)
            assert student is not None
            assert student.email == 'test@example.com'
    
    def test_student_unique_email(self, app):
        """Test that student emails are unique."""
        with app.app_context():
            s1 = Student(email='unique@test.com', name='Student 1')
            db.session.add(s1)
            db.session.commit()
            
            s2 = Student(email='unique@test.com', name='Student 2')
            db.session.add(s2)
            
            with pytest.raises(Exception):  # IntegrityError
                db.session.commit()
