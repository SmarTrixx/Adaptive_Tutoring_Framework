from app.models.session import Session, StudentResponse
from app.models.question import Question
from app.models.student import Student
from app import db
from datetime import datetime

class CBTSystem:
    """
    Computer-Based Testing System
    Manages test sessions, question delivery, and response tracking
    """
    
    def __init__(self):
        pass
    
    def start_session(self, student_id, subject, num_questions=10):
        """
        Start a new CBT session
        """
        student = Student.query.get(student_id)
        if not student:
            return {'error': 'Student not found'}, 404
        
        session = Session(
            student_id=student_id,
            subject=subject,
            status='active',
            total_questions=num_questions,
            current_difficulty=student.preferred_difficulty or 0.5
        )
        
        db.session.add(session)
        db.session.commit()
        
        # Update student's last activity
        student.last_activity = datetime.utcnow()
        db.session.commit()
        
        return {
            'session_id': session.id,
            'student_id': student_id,
            'subject': subject,
            'total_questions': num_questions,
            'current_difficulty': session.current_difficulty,
            'status': 'active'
        }
    
    def get_next_question(self, session_id, current_difficulty=None):
        """
        Get the next question for the student
        Uses adaptive difficulty if provided
        """
        session = Session.query.get(session_id)
        if not session:
            return {'error': 'Session not found'}, 404
        
        # Check if we've reached the target number of questions
        answered_count = len(StudentResponse.query.filter_by(session_id=session_id).all())
        if answered_count >= session.total_questions:
            # Test is complete - auto-end the session
            if session.status != 'completed':
                session.status = 'completed'
                session.session_end = datetime.utcnow()
                db.session.commit()
            
            return {
                'status': 'completed',
                'message': 'Test completed successfully!',
                'final_score': session.score_percentage,
                'correct_answers': session.correct_answers,
                'total_questions': session.total_questions
            }
        
        # Allow both 'active' and 'paused' status to continue (more lenient)
        if session.status not in ['active', 'paused']:
            # If session was marked completed but we haven't reached question limit yet, reset it
            if session.status == 'completed' and answered_count < session.total_questions:
                session.status = 'active'
                db.session.commit()
            else:
                return {'error': f'Session is not active (status: {session.status})'}, 400
        
        # Use provided difficulty or session's current difficulty
        difficulty = current_difficulty or session.current_difficulty
        
        # Get questions already answered in this session
        answered_questions = StudentResponse.query.filter_by(
            session_id=session_id
        ).with_entities(StudentResponse.question_id).all()
        answered_ids = [q[0] for q in answered_questions]
        
        # Find unanswered questions near the target difficulty
        difficulty_range = 0.15  # ±15% of target difficulty
        questions = Question.query.filter(
            Question.subject == session.subject,
            Question.difficulty >= (difficulty - difficulty_range),
            Question.difficulty <= (difficulty + difficulty_range),
            ~Question.id.in_(answered_ids) if answered_ids else True
        ).all()
        
        if not questions:
            # Fallback: get any unanswered question
            questions = Question.query.filter(
                Question.subject == session.subject,
                ~Question.id.in_(answered_ids) if answered_ids else True
            ).all()
        
        if not questions:
            # No more questions available - end session
            session.status = 'completed'
            session.session_end = datetime.utcnow()
            db.session.commit()
            
            return {
                'status': 'completed',
                'message': 'Test completed! No more questions available.',
                'final_score': session.score_percentage,
                'correct_answers': session.correct_answers,
                'total_questions': session.total_questions
            }
        
        # Return first available question (can implement smarter selection later)
        question = questions[0]
        
        return {
            'question_id': question.id,
            'question_text': question.question_text,
            'options': {
                'A': question.option_a,
                'B': question.option_b,
                'C': question.option_c,
                'D': question.option_d
            },
            'difficulty': question.difficulty,
            'hints_available': len(question.hints)
        }
    
    def submit_response(self, session_id, question_id, student_answer, response_time_seconds):
        """
        Record a student's response to a question
        """
        session = Session.query.get(session_id)
        if not session:
            return {'error': 'Session not found'}, 404
        
        question = Question.query.get(question_id)
        if not question:
            return {'error': 'Question not found'}, 404
        
        # Check if answer is correct
        is_correct = student_answer.upper() == question.correct_option
        
        # Create response record
        response = StudentResponse(
            session_id=session_id,
            question_id=question_id,
            student_answer=student_answer,
            is_correct=is_correct,
            response_time_seconds=response_time_seconds,
            attempts=1
        )
        
        db.session.add(response)
        
        # Update session stats
        # Don't modify total_questions - it was set at session start
        if is_correct:
            session.correct_answers += 1
        
        # Calculate current score
        if session.total_questions > 0:
            session.score_percentage = (session.correct_answers / session.total_questions) * 100
        
        db.session.commit()
        
        # Adapt difficulty based on correctness
        # Simple adaptation: increase difficulty on correct answers, decrease on wrong
        total_answered = len(StudentResponse.query.filter_by(session_id=session_id).all())
        if total_answered >= 2:  # Adapt after at least 2 answers
            accuracy = session.correct_answers / total_answered
            current_difficulty = session.current_difficulty
            
            # Increase difficulty if accuracy is high (>= 80%)
            if accuracy >= 0.8:
                new_difficulty = min(0.9, current_difficulty + 0.1)  # Increase by 0.1, max 0.9
                session.current_difficulty = new_difficulty
                db.session.commit()
            # Decrease difficulty if accuracy is low (< 40%)
            elif accuracy < 0.4:
                new_difficulty = max(0.1, current_difficulty - 0.1)  # Decrease by 0.1, min 0.1
                session.current_difficulty = new_difficulty
                db.session.commit()
        
        return {
            'response_id': response.id,
            'is_correct': is_correct,
            'correct_answer': question.correct_option,
            'explanation': question.explanation,
            'current_score': session.score_percentage,
            'correct_count': session.correct_answers,
            'total_answered': len(StudentResponse.query.filter_by(session_id=session_id).all())
        }
    
    def get_hint(self, session_id, question_id, hint_index=0):
        """
        Get a hint for a question
        """
        question = Question.query.get(question_id)
        if not question:
            return {'error': 'Question not found'}, 404
        
        if not question.hints or hint_index >= len(question.hints):
            return {'error': 'No more hints available'}, 400
        
        # Update response to record hint usage
        response = StudentResponse.query.filter_by(
            session_id=session_id,
            question_id=question_id
        ).first()
        
        if response:
            response.hints_used += 1
            db.session.commit()
        
        return {
            'hint': question.hints[hint_index],
            'hint_number': hint_index + 1,
            'total_hints': len(question.hints)
        }
    
    def end_session(self, session_id):
        """
        End a test session and calculate final score
        """
        session = Session.query.get(session_id)
        if not session:
            return {'error': 'Session not found'}, 404
        
        session.status = 'completed'
        session.session_end = datetime.utcnow()
        
        db.session.commit()
        
        return {
            'session_id': session.id,
            'status': 'completed',
            'final_score': session.score_percentage,
            'correct_answers': session.correct_answers,
            'total_questions': session.total_questions,
            'duration_seconds': session.duration_seconds
        }
    
    def get_session_summary(self, session_id):
        """
        Get detailed summary of a session
        """
        session = Session.query.get(session_id)
        if not session:
            return {'error': 'Session not found'}, 404
        
        responses = StudentResponse.query.filter_by(session_id=session_id).all()
        
        # Calculate detailed stats
        total_hints = sum(r.hints_used for r in responses)
        avg_response_time = sum(r.response_time_seconds for r in responses) / len(responses) if responses else 0
        total_attempts = sum(r.attempts for r in responses)
        
        return {
            'session': session.to_dict(),
            'statistics': {
                'total_questions_answered': len(responses),
                'correct_answers': session.correct_answers,
                'incorrect_answers': len(responses) - session.correct_answers,
                'final_score_percentage': session.score_percentage,
                'total_hints_used': total_hints,
                'average_response_time': avg_response_time,
                'total_attempts': total_attempts
            },
            'responses': [r.to_dict() for r in responses]
        }
