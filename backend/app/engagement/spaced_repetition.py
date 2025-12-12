"""
Spaced Repetition Scheduler for Long-term Learning

Implements supermemo2 algorithm with modifications:
- Exponential spacing intervals based on recall quality
- Difficulty adjustment based on performance
- Optimizes review timing for maximum retention
- Tracks learning curve per topic/question
"""

from datetime import datetime, timedelta
from app.models.student import Student
from app.models.session import StudentResponse
from app.models.question import Question
from app import db
import math


class SpacedRepetitionScheduler:
    """Manage spaced repetition scheduling for optimal retention"""
    
    def __init__(self):
        """Initialize scheduler with supermemo2 parameters"""
        # SuperMemo 2 parameters
        self.initial_interval = 1  # First interval in days
        self.easiness_factor_min = 1.3  # Minimum EF (prevents too fast spacing)
        self.easiness_factor_default = 2.5  # Default EF
        
        # Quality grading scale (0-5)
        # 0-1: Incorrect, forget completely
        # 2-3: Difficult but remembered
        # 4-5: Easy, remembered
        self.quality_map = {
            'incorrect': 0,      # Forgot answer
            'difficult': 2,      # Struggled, needs more practice
            'moderate': 3,       # Okay, but not confident
            'good': 4,           # Good recall
            'easy': 5            # Perfect recall
        }
    
    def calculate_quality(self, response):
        """
        Determine recall quality from response data
        
        Args:
            response: StudentResponse object
        
        Returns:
            quality (0-5) for SuperMemo algorithm
        """
        if not response.is_correct:
            return 0  # Incorrect response
        
        # Quality based on confidence and performance
        if response.attempts > 3:
            return 2  # Difficult, took many attempts
        elif response.attempts > 1:
            return 3  # Moderate, needed some attempts
        elif response.response_time_seconds and response.response_time_seconds > 45:
            return 3  # Slow response, less confident
        else:
            # Fast correct response
            if response.response_time_seconds and response.response_time_seconds < 15:
                return 5  # Very easy, quick recall
            else:
                return 4  # Good recall
    
    def calculate_repetition_schedule(self, quality, current_repetition, current_easiness_factor):
        """
        SuperMemo 2 algorithm for calculating next review interval
        
        Args:
            quality: Recall quality (0-5)
            current_repetition: Number of successful repetitions (n)
            current_easiness_factor: Current EF value
        
        Returns:
            {
                'next_interval_days': interval to next review,
                'next_easiness_factor': updated EF,
                'next_repetition': next repetition number
            }
        """
        # Calculate new EF
        new_ef = current_easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        new_ef = max(self.easiness_factor_min, new_ef)  # Minimum EF
        
        # Calculate interval based on repetition number
        if quality < 3:
            # Poor quality: reset repetition counter and restart
            next_repetition = 1
            next_interval = self.initial_interval
        else:
            # Good quality: increase interval
            next_repetition = current_repetition + 1
            
            if next_repetition == 1:
                next_interval = 1
            elif next_repetition == 2:
                next_interval = 3
            else:
                # Exponential growth: I(n) = I(n-1) * EF
                next_interval = round(self._calculate_interval(next_repetition - 1, new_ef))
        
        return {
            'next_interval_days': max(1, next_interval),  # Minimum 1 day
            'next_easiness_factor': new_ef,
            'next_repetition': next_repetition
        }
    
    def _calculate_interval(self, n, ef):
        """Calculate interval using exponential spacing formula"""
        # I(1) = 1, I(2) = 3, I(n) = I(n-1) * EF
        if n == 1:
            return 1
        elif n == 2:
            return 3
        else:
            # Calculate by iteration
            interval = 1
            for i in range(2, n):
                interval = interval * ef
            return interval
    
    def schedule_question_review(self, student_id, question_id, quality=None, response=None):
        """
        Schedule next review of a question for a student
        
        Args:
            student_id: Student ID
            question_id: Question ID
            quality: Recall quality (0-5), or calculate from response
            response: StudentResponse object to calculate quality from
        
        Returns:
            {
                'next_review_date': datetime for next review,
                'interval_days': days until review,
                'quality': quality rating used,
                'status': 'scheduled' | 'due' | 'overdue'
            }
        """
        if quality is None:
            quality = self.calculate_quality(response)
        
        # Get or initialize learning record
        learning_record = self._get_learning_record(student_id, question_id)
        
        # Calculate new schedule
        schedule = self.calculate_repetition_schedule(
            quality,
            learning_record['repetitions'],
            learning_record['easiness_factor']
        )
        
        # Calculate next review date
        next_review_date = datetime.utcnow() + timedelta(days=schedule['next_interval_days'])
        
        # Update learning record
        self._update_learning_record(
            student_id,
            question_id,
            schedule['next_easiness_factor'],
            schedule['next_repetition'],
            next_review_date,
            quality
        )
        
        # Determine status
        today = datetime.utcnow()
        if next_review_date <= today:
            status = 'due'
        elif next_review_date <= today + timedelta(days=1):
            status = 'due_soon'
        else:
            status = 'scheduled'
        
        return {
            'next_review_date': next_review_date.isoformat(),
            'interval_days': schedule['next_interval_days'],
            'quality': quality,
            'status': status,
            'easiness_factor': schedule['next_easiness_factor'],
            'repetition_count': schedule['next_repetition']
        }
    
    def get_due_for_review(self, student_id):
        """
        Get questions due for review for a student
        
        Args:
            student_id: Student ID
        
        Returns:
            List of questions due for review, sorted by urgency
        """
        due_questions = []
        
        # Get all student responses
        responses = StudentResponse.query.filter_by(student_id=student_id).all()
        
        # Check each question's review status
        reviewed_questions = {}
        for response in responses:
            if response.question_id not in reviewed_questions:
                reviewed_questions[response.question_id] = []
            reviewed_questions[response.question_id].append(response)
        
        now = datetime.utcnow()
        
        for question_id, response_list in reviewed_questions.items():
            # Get latest learning record
            record = self._get_learning_record(student_id, question_id)
            
            if record['next_review_date'] and record['next_review_date'] <= now:
                due_questions.append({
                    'question_id': question_id,
                    'days_overdue': (now - record['next_review_date']).days,
                    'interval': record['interval'],
                    'easiness': record['easiness_factor'],
                    'question': Question.query.get(question_id)
                })
        
        # Sort by urgency (most overdue first)
        due_questions.sort(key=lambda x: x['days_overdue'], reverse=True)
        
        return due_questions
    
    def get_learning_statistics(self, student_id):
        """
        Get spaced repetition statistics for student
        
        Args:
            student_id: Student ID
        
        Returns:
            Statistics including questions due, upcoming, mastered
        """
        responses = StudentResponse.query.filter_by(student_id=student_id).all()
        reviewed_questions = set(r.question_id for r in responses)
        
        due_count = 0
        upcoming_count = 0
        mastered_count = 0
        struggling_count = 0
        
        now = datetime.utcnow()
        
        for q_id in reviewed_questions:
            record = self._get_learning_record(student_id, q_id)
            
            if record['easiness_factor'] < self.easiness_factor_min + 0.1:
                struggling_count += 1
            elif record['repetitions'] >= 10:  # Mastered after many successful repetitions
                mastered_count += 1
            elif record['next_review_date'] and record['next_review_date'] <= now:
                due_count += 1
            else:
                upcoming_count += 1
        
        return {
            'total_questions_studied': len(reviewed_questions),
            'due_for_review': due_count,
            'upcoming_reviews': upcoming_count,
            'mastered': mastered_count,
            'struggling': struggling_count,
            'estimated_retention': self._estimate_retention(student_id, reviewed_questions)
        }
    
    def _estimate_retention(self, student_id, question_ids):
        """Estimate retention rate based on easiness factors"""
        if not question_ids:
            return 0.0
        
        total_retention = 0.0
        for q_id in question_ids:
            record = self._get_learning_record(student_id, q_id)
            # Retention inversely proportional to easiness (harder to remember = lower EF)
            # and repetition count (more practice = better retention)
            retention = min(0.95, 0.5 + (record['repetitions'] / 20) * 0.4)
            total_retention += retention
        
        return round(total_retention / len(question_ids), 3)
    
    def _get_learning_record(self, student_id, question_id):
        """Get or create learning record for question"""
        # This would be stored in database in production
        # For now, initialize with default values
        return {
            'student_id': student_id,
            'question_id': question_id,
            'repetitions': 0,
            'easiness_factor': self.easiness_factor_default,
            'next_review_date': None,
            'last_review_date': None,
            'interval': 0,
            'quality_history': []
        }
    
    def _update_learning_record(self, student_id, question_id, ef, reps, next_review, quality):
        """Update learning record (would store in database)"""
        # In production, this would update database record
        pass
    
    def get_review_schedule_for_topic(self, student_id, topic):
        """
        Get spaced repetition schedule for specific topic
        
        Args:
            student_id: Student ID
            topic: Topic name
        
        Returns:
            Schedule organized by review date
        """
        # Get all questions in topic
        topic_questions = Question.query.filter_by(topic=topic).all()
        
        schedule = {
            'due_today': [],
            'due_this_week': [],
            'due_this_month': [],
            'future': []
        }
        
        now = datetime.utcnow()
        
        for question in topic_questions:
            record = self._get_learning_record(student_id, question.id)
            
            if not record['next_review_date']:
                continue
            
            days_until_review = (record['next_review_date'] - now).days
            
            item = {
                'question_id': question.id,
                'question_text': question.question_text[:100],
                'days_until_review': days_until_review,
                'interval': record['interval'],
                'easiness': record['easiness_factor']
            }
            
            if days_until_review <= 0:
                schedule['due_today'].append(item)
            elif days_until_review <= 7:
                schedule['due_this_week'].append(item)
            elif days_until_review <= 30:
                schedule['due_this_month'].append(item)
            else:
                schedule['future'].append(item)
        
        return schedule


class LearningCurveAnalyzer:
    """Analyze learning curves for topics using spaced repetition data"""
    
    @staticmethod
    def get_topic_learning_curve(student_id, topic):
        """
        Get learning curve data for topic
        
        Args:
            student_id: Student ID
            topic: Topic name
        
        Returns:
            List of (attempt_number, accuracy) points showing learning progression
        """
        # Get all responses for questions in topic, chronologically
        topic_questions = Question.query.filter_by(topic=topic).all()
        topic_q_ids = [q.id for q in topic_questions]
        
        responses = StudentResponse.query.filter(
            StudentResponse.student_id == student_id,
            StudentResponse.question_id.in_(topic_q_ids)
        ).order_by(StudentResponse.timestamp).all()
        
        # Calculate cumulative accuracy
        learning_curve = []
        correct_count = 0
        
        for i, response in enumerate(responses, 1):
            if response.is_correct:
                correct_count += 1
            
            accuracy = correct_count / i
            learning_curve.append({
                'attempt': i,
                'accuracy': round(accuracy, 3),
                'cumulative_correct': correct_count,
                'timestamp': response.timestamp.isoformat()
            })
        
        return learning_curve
    
    @staticmethod
    def analyze_mastery_timeline(student_id, topic, mastery_threshold=0.85):
        """
        Estimate when student will reach mastery on topic
        
        Args:
            student_id: Student ID
            topic: Topic name
            mastery_threshold: Accuracy threshold for mastery (default 85%)
        
        Returns:
            {
                'current_accuracy': float,
                'days_to_mastery_estimate': int,
                'mastered': bool,
                'learning_rate': float (accuracy points per day)
            }
        """
        curve = LearningCurveAnalyzer.get_topic_learning_curve(student_id, topic)
        
        if not curve:
            return {
                'current_accuracy': 0.0,
                'days_to_mastery_estimate': 999,
                'mastered': False,
                'learning_rate': 0.0
            }
        
        current_accuracy = curve[-1]['accuracy']
        
        if current_accuracy >= mastery_threshold:
            return {
                'current_accuracy': current_accuracy,
                'days_to_mastery_estimate': 0,
                'mastered': True,
                'learning_rate': 0.0
            }
        
        # Calculate learning rate (linear approximation)
        if len(curve) >= 2:
            first = curve[0]
            last = curve[-1]
            accuracy_gain = last['accuracy'] - first['accuracy']
            attempt_count = last['attempt'] - first['attempt']
            
            # Rough estimate: 1 attempt per day (real session data would be more accurate)
            learning_rate = accuracy_gain / max(1, attempt_count)
            
            if learning_rate > 0:
                attempts_needed = (mastery_threshold - current_accuracy) / learning_rate
                days_to_mastery = max(1, int(attempts_needed))
            else:
                days_to_mastery = 999  # No progress
        else:
            learning_rate = 0.0
            days_to_mastery = 999
        
        return {
            'current_accuracy': round(current_accuracy, 3),
            'days_to_mastery_estimate': days_to_mastery,
            'mastered': False,
            'learning_rate': round(learning_rate, 3)
        }
