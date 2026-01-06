from app.models.session import Session, StudentResponse
from app.models.question import Question
from app.models.student import Student
from app.models.engagement import EngagementMetric
from app.engagement.tracker import EngagementIndicatorTracker
from app.adaptation.engine import AdaptiveEngine
from app import db
from datetime import datetime
import random

class CBTSystem:
    """
    Computer-Based Testing System
    Manages test sessions, question delivery, and response tracking
    """
    
    def __init__(self):
        self.adaptive_engine = AdaptiveEngine()
    
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
        Get the next question for the student.
        Uses difficulty mapping to select from appropriate question pool.
        """
        from app.adaptation.difficulty_mapper import DifficultyMapper
        
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
        
        # Use difficulty mapper to determine question pool
        min_difficulty, max_difficulty, difficulty_label = DifficultyMapper.get_difficulty_range(difficulty)
        
        print(f'[DEBUG] get_next_question: session_difficulty={difficulty}, label={difficulty_label}, range=[{min_difficulty}, {max_difficulty}]')
        
        # Get unanswered questions from the appropriate difficulty range
        questions = Question.query.filter(
            Question.subject == session.subject,
            Question.difficulty >= min_difficulty,
            Question.difficulty <= max_difficulty,
            ~Question.id.in_(answered_ids) if answered_ids else True
        ).all()
        
        if not questions:
            # Fallback: use tighter band around current difficulty
            min_band, max_band, _ = DifficultyMapper.get_difficulty_band(difficulty)
            questions = Question.query.filter(
                Question.subject == session.subject,
                Question.difficulty >= min_band,
                Question.difficulty <= max_band,
                ~Question.id.in_(answered_ids) if answered_ids else True
            ).all()
        
        if not questions:
            # Final fallback: get any unanswered question
            questions = Question.query.filter(
                Question.subject == session.subject,
                ~Question.id.in_(answered_ids) if answered_ids else True
            ).all()
        
        print(f'[DEBUG] Found {len(questions)} questions for difficulty {difficulty_label}')
        if questions:
            q = questions[0]
            print(f'[DEBUG] Sample question: id={q.id}, difficulty={q.difficulty}, text={q.question_text[:50]}...')
        
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
        
        # Return a random question from the available pool
        # This ensures different questions are selected even with same difficulty
        question = random.choice(questions)
        
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
    
    def submit_response(self, session_id, question_id, student_answer, response_time_seconds,
                       initial_option=None, final_option=None, option_change_count=0, 
                       option_change_history=None, navigation_frequency=0,
                       interaction_start_timestamp=None, submission_timestamp=None, 
                       submission_iso_timestamp=None,
                       time_spent_per_question=0, inactivity_duration_ms=0,
                       question_index=0, hesitation_flags=None, navigation_pattern='sequential',
                       facial_metrics=None, hints_used_array=None):
        """
        Record a student's response to a question with comprehensive cognitive and affective tracking
        """
        session = Session.query.get(session_id)
        if not session:
            return {'error': 'Session not found'}, 404
        
        question = Question.query.get(question_id)
        if not question:
            return {'error': 'Question not found'}, 404
        
        # Check if answer is correct
        is_correct = student_answer.upper() == question.correct_option
        
        # CHECK FOR EXISTING RESPONSE - UPDATE IF EXISTS, CREATE IF NEW
        existing_response = StudentResponse.query.filter_by(
            session_id=session_id,
            question_id=question_id
        ).first()
        
        if existing_response:
            # UPDATE EXISTING RESPONSE (revisit/change answer scenario)
            # Track if correctness changed for session stats
            was_correct_before = existing_response.is_correct
            
            # CRITICAL FIX: Accumulate hints instead of replacing them
            # Preserve previous hints and add new ones from revisit
            previous_hints = existing_response.hints_used_array if existing_response.hints_used_array else []
            new_hints = hints_used_array if hints_used_array else []
            
            # Merge hints: keep existing ones, add any new ones not already present
            # (by comparing timestamps to avoid duplicates)
            existing_timestamps = {h.get('timestamp') for h in previous_hints if isinstance(h, dict) and h.get('timestamp')}
            accumulated_hints = list(previous_hints)  # Start with all previous hints
            
            for new_hint in new_hints:
                if isinstance(new_hint, dict) and new_hint.get('timestamp') not in existing_timestamps:
                    accumulated_hints.append(new_hint)
            
            # Update all fields
            existing_response.student_answer = student_answer
            existing_response.is_correct = is_correct
            existing_response.response_time_seconds = response_time_seconds
            existing_response.initial_option = initial_option
            existing_response.final_option = final_option
            existing_response.option_change_count = option_change_count
            existing_response.option_change_history = option_change_history if option_change_history else []
            existing_response.navigation_frequency = navigation_frequency
            existing_response.interaction_start_timestamp = interaction_start_timestamp
            existing_response.submission_timestamp = submission_timestamp
            existing_response.submission_iso_timestamp = submission_iso_timestamp
            existing_response.time_spent_per_question = time_spent_per_question
            existing_response.inactivity_duration_ms = inactivity_duration_ms
            existing_response.question_index = question_index
            existing_response.hesitation_flags = hesitation_flags if hesitation_flags else {}
            existing_response.navigation_pattern = navigation_pattern
            existing_response.facial_metrics = facial_metrics if facial_metrics else {}
            existing_response.hints_used_array = accumulated_hints  # Use accumulated hints
            
            db.session.merge(existing_response)
            
            print(f"[HINTS] Updated response - accumulated hints: {len(accumulated_hints)} total (previous: {len(previous_hints)}, new: {len(new_hints)})", flush=True)
            
            # Update session stats only if correctness changed
            if was_correct_before and not is_correct:
                # Was correct, now wrong - decrease correct count
                session.correct_answers -= 1
            elif not was_correct_before and is_correct:
                # Was wrong, now correct - increase correct count
                session.correct_answers += 1
            # If no change (both correct or both wrong), session.correct_answers stays same
        else:
            # CREATE NEW RESPONSE (first attempt)
            response = StudentResponse(
                session_id=session_id,
                question_id=question_id,
                student_answer=student_answer,
                is_correct=is_correct,
                response_time_seconds=response_time_seconds,
                # Behavioral: Option Changes
                initial_option=initial_option,
                final_option=final_option,
                option_change_count=option_change_count,
                option_change_history=option_change_history if option_change_history else [],
                # Behavioral: Navigation
                navigation_frequency=navigation_frequency,
                # Timestamps
                interaction_start_timestamp=interaction_start_timestamp,
                submission_timestamp=submission_timestamp,
                submission_iso_timestamp=submission_iso_timestamp,
                # Cognitive: Time & Activity
                time_spent_per_question=time_spent_per_question,
                inactivity_duration_ms=inactivity_duration_ms,
                # Cognitive: Context
                question_index=question_index,
                hesitation_flags=hesitation_flags if hesitation_flags else {},
                navigation_pattern=navigation_pattern,
                # Facial & Hint data
                facial_metrics=facial_metrics if facial_metrics else {},
                hints_used_array=hints_used_array if hints_used_array else [],
                # Knowledge gaps (will be populated by engagement tracker)
                knowledge_gaps=[]
            )
            
            db.session.add(response)
            existing_response = response
            
            # Update session stats (only for new responses)
            if is_correct:
                session.correct_answers += 1
        
        # Calculate current score
        if session.total_questions > 0:
            session.score_percentage = (session.correct_answers / session.total_questions) * 100
        
        db.session.commit()
        
        # === CREATE ENGAGEMENT METRICS ===
        # Track behavioral, cognitive, and affective indicators
        engagement_score = 0.5  # Default
        engagement_level = 'medium'  # Default
        
        try:
            tracker = EngagementIndicatorTracker()
            
            # Track indicators
            behavioral = tracker.track_behavioral_indicators(
                session_id,
                {
                    'question_id': question_id,
                    'response_time_seconds': response_time_seconds
                }
            )
            cognitive = tracker.track_cognitive_indicators(session_id)
            affective = tracker.track_affective_indicators(session_id)
            
            # Calculate engagement score
            engagement_score = tracker.calculate_composite_engagement_score(behavioral, cognitive, affective)
            engagement_level = tracker.determine_engagement_level(engagement_score)
            
            # Update response record with knowledge gaps identified
            knowledge_gaps = cognitive.get('knowledge_gaps', [])
            existing_response.knowledge_gaps = knowledge_gaps
            db.session.commit()
            
            # Create and save metric
            metric = EngagementMetric(
                student_id=session.student_id,
                session_id=session_id,
                response_time_seconds=behavioral.get('response_time_seconds'),
                hints_requested=behavioral.get('hints_requested', 0),
                inactivity_duration=behavioral.get('inactivity_duration', 0),
                navigation_frequency=behavioral.get('navigation_frequency', 0),
                completion_rate=behavioral.get('completion_rate', 0),
                accuracy=cognitive.get('accuracy', 0),
                learning_progress=cognitive.get('learning_progress', 0),
                knowledge_gaps=knowledge_gaps,
                confidence_level=affective.get('confidence_level'),
                frustration_level=affective.get('frustration_level'),
                interest_level=affective.get('interest_level'),
                engagement_score=engagement_score,
                engagement_level=engagement_level
            )
            
            db.session.add(metric)
            db.session.commit()
        except Exception as e:
            print(f"[ENGAGEMENT TRACKING ERROR] {str(e)}")
            import traceback
            traceback.print_exc()
        
        # === ADAPTIVE ENGINE - HANDLE DIFFICULTY ADAPTATION ===
        # IMPORTANT: Only adapt every 3 answers, looking at last 3 performance
        # This matches the original behavior which worked well
        try:
            all_responses = StudentResponse.query.filter_by(session_id=session_id).order_by(
                StudentResponse.timestamp.asc()
            ).all()
            
            total_answered = len(all_responses)
            current_difficulty = session.current_difficulty
            
            # Only adapt when we have at least 3 answers AND on multiples of 3
            if total_answered >= 3 and total_answered % 3 == 0:
                # Get the last 3 responses
                last_3 = all_responses[-3:]
                correct_in_last_3 = sum(1 for r in last_3 if r.is_correct)
                
                # Use the engine ONLY for this decision, with recent accuracy
                recent_accuracy = correct_in_last_3 / 3.0
                
                # Create a temporary metric with recent accuracy for the engine
                temp_metric = type('TempMetric', (), {
                    'accuracy': recent_accuracy,
                    'engagement_score': metric.engagement_score if metric else 0.5
                })()
                
                result = self.adaptive_engine.adapt_difficulty(
                    session.student_id,
                    session_id,
                    temp_metric
                )
                
                if result['adapted']:
                    session = Session.query.get(session_id)  # Re-fetch to get updated value
                    print(f"\n[ADAPT Q{total_answered}] Last 3: {correct_in_last_3}/3 ({recent_accuracy:.0%}) | {result['reason']} | {result['old_difficulty']:.2f} → {result['new_difficulty']:.2f}\n", flush=True)
                else:
                    print(f"\n[ADAPT Q{total_answered}] Last 3: {correct_in_last_3}/3 ({recent_accuracy:.0%}) | {result['reason']}\n", flush=True)
                
        except Exception as e:
            import traceback
            print(f"[ADAPT ERROR] {str(e)}")
            traceback.print_exc()

        # Calculate unique answered questions (for progress)
        unique_answered = len(StudentResponse.query.filter_by(session_id=session_id).distinct(
            StudentResponse.question_id
        ).all())

        return {
            'response_id': existing_response.id,
            'is_correct': is_correct,
            'correct_answer': question.correct_option,
            'explanation': question.explanation,
            'current_score': session.score_percentage,
            'correct_count': session.correct_answers,
            'unique_answered': unique_answered,  # Count of unique questions answered
            'total_questions': session.total_questions,
            'current_difficulty': session.current_difficulty,  # Include updated difficulty!
            'engagement_score': engagement_score if 'engagement_score' in locals() else 0.5,
            'engagement_level': engagement_level if 'engagement_level' in locals() else 'medium'
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
