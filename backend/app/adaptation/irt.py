"""
Item Response Theory (IRT) Implementation for Adaptive CBT

Uses 3-Parameter Logistic Model (3PL) to:
- Estimate question difficulty (b parameter)
- Calculate question discrimination (a parameter)
- Account for guessing probability (c parameter)
- Estimate student ability (theta)
- Select optimal difficulty questions (CAT algorithm)
"""

import numpy as np
from scipy.optimize import minimize, brentq
from datetime import datetime
from app.models.question import Question
from app.models.session import StudentResponse
from app import db
import json


class IRTModel:
    """3-Parameter Logistic IRT Model Implementation"""
    
    def __init__(self):
        """Initialize IRT model with default parameters"""
        # Item parameters from initial calibration
        self.item_params = {}  # question_id -> {'a': discrimination, 'b': difficulty, 'c': guessing}
        
        # Student abilities cache
        self.student_abilities = {}  # student_id -> ability (theta)
        
        # Calibration data
        self.calibration_data = []
        
        # Default parameters if not yet calibrated
        self.default_params = {
            'a': 1.0,  # Discrimination (steepness of curve)
            'b': 0.0,  # Difficulty (location parameter)
            'c': 0.25  # Guessing (lower asymptote, ~1/4 for 4-choice)
        }
    
    def probability_correct(self, theta, a, b, c):
        """
        Calculate probability of correct response using 3PL model
        
        Args:
            theta: Student ability level
            a: Discrimination parameter (steepness)
            b: Difficulty parameter (location)
            c: Guessing parameter (lower asymptote)
        
        Returns:
            P(correct | theta, a, b, c) - probability between c and 1
        """
        try:
            # Prevent overflow in exponential
            exponent = -1.7 * a * (theta - b)  # 1.7 is scaling constant
            exponent = np.clip(exponent, -100, 100)
            
            exp_val = np.exp(exponent)
            probability = c + (1 - c) / (1 + exp_val)
            return np.clip(probability, c, 1.0)
        except:
            return (1 + c) / 2
    
    def information_function(self, theta, a, b, c):
        """
        Calculate Fisher Information at ability level theta
        Higher information = better for ability estimation at this theta
        
        Args:
            theta: Ability level
            a: Discrimination
            b: Difficulty
            c: Guessing
        
        Returns:
            Information value (>0)
        """
        P = self.probability_correct(theta, a, b, c)
        
        # Prevent division by zero
        if P <= c or P >= 1.0:
            return 0.0
        
        numerator = (a ** 2) * ((P - c) ** 2) * ((1 - P) ** 2)
        denominator = (P * (1 - P)) ** 2
        
        if denominator == 0:
            return 0.0
        
        return 1.7 ** 2 * numerator / denominator
    
    def estimate_ability(self, responses, question_params):
        """
        Estimate student ability (theta) from response pattern
        
        Args:
            responses: List of (correct, question_id) tuples
            question_params: Dict of question_id -> {'a', 'b', 'c'}
        
        Returns:
            theta: Estimated ability level
        """
        if not responses:
            return 0.0
        
        # Use maximum likelihood estimation
        def negative_likelihood(theta):
            """Negative log-likelihood (for minimization)"""
            likelihood = 0.0
            for correct, question_id in responses:
                params = question_params.get(question_id, self.default_params)
                P = self.probability_correct(theta, params['a'], params['b'], params['c'])
                
                # Avoid log(0)
                P = np.clip(P, 1e-10, 1 - 1e-10)
                
                if correct:
                    likelihood -= np.log(P)
                else:
                    likelihood -= np.log(1 - P)
            
            return likelihood
        
        # Find theta that maximizes likelihood (minimizes negative)
        try:
            result = minimize(negative_likelihood, x0=0.0, method='Nelder-Mead')
            theta = np.clip(result.x[0], -4, 4)  # Bound to reasonable range
            return float(theta)
        except:
            # Fallback: simple scoring
            correct_count = sum(1 for c, _ in responses if c)
            return (correct_count / len(responses) - 0.5) * 2  # Scale to -1 to 1
    
    def calibrate_from_responses(self, student_responses):
        """
        Calibrate item parameters from student response data
        Uses method of moments as simple calibration approach
        
        Args:
            student_responses: QueryResult of StudentResponse objects
        """
        question_stats = {}  # question_id -> {'correct': count, 'total': count, 'response_times': []}
        
        # Aggregate response data
        for response in student_responses:
            q_id = response.question_id
            
            if q_id not in question_stats:
                question_stats[q_id] = {
                    'correct': 0,
                    'total': 0,
                    'response_times': [],
                    'attempts': 0
                }
            
            question_stats[q_id]['total'] += 1
            # Use actual response time or skip if None (don't mask with hardcoded 30)
            if response.response_time_seconds is not None and response.response_time_seconds > 0:
                question_stats[q_id]['response_times'].append(response.response_time_seconds)
            # Use actual attempts or default to 1 if None
            attempts = response.attempts if response.attempts is not None else 1
            question_stats[q_id]['attempts'] += attempts
            
            if response.is_correct:
                question_stats[q_id]['correct'] += 1
        
        # Estimate parameters from statistics
        for question_id, stats in question_stats.items():
            if stats['total'] < 3:  # Need minimum samples
                self.item_params[question_id] = self.default_params.copy()
                continue
            
            # Difficulty: easier questions have higher p-values
            p_correct = stats['correct'] / stats['total']
            
            # Use logit transformation: b = -ln((1-p)/p) / 1.7
            if 0.001 < p_correct < 0.999:
                difficulty = -np.log((1 - p_correct) / p_correct) / 1.7
            else:
                difficulty = 0.0
            
            # Discrimination: questions with faster response times and consistent performance
            avg_response_time = np.mean(stats['response_times'])
            response_time_std = np.std(stats['response_times']) if len(stats['response_times']) > 1 else 0
            
            # Higher discrimination for questions with consistent response times and clear p-values
            discrimination = 1.0 + 0.5 * (1 - min(response_time_std / (avg_response_time + 1), 1.0))
            
            # Guessing: for 4-choice questions, expect ~25% random correct
            guessing = 0.25 * (1 - p_correct)  # Lower guessing for high performers
            
            self.item_params[question_id] = {
                'a': np.clip(discrimination, 0.5, 2.5),  # Reasonable discrimination range
                'b': np.clip(difficulty, -4, 4),  # Bound difficulty
                'c': np.clip(guessing, 0.0, 0.4)  # Guessing parameter
            }
    
    def select_optimal_question(self, student_id, available_questions, current_ability=None):
        """
        Select question with maximum information at student's ability level (CAT algorithm)
        
        Args:
            student_id: Student identifier
            available_questions: List of Question objects to choose from
            current_ability: If None, use estimated ability
        
        Returns:
            question_id: ID of optimal question
        """
        if not available_questions:
            return None
        
        # Get student ability
        if current_ability is None:
            current_ability = self.student_abilities.get(student_id, 0.0)
        
        # Calculate information for each question
        max_information = -1
        best_question = None
        
        for question in available_questions:
            params = self.item_params.get(question.id, self.default_params)
            information = self.information_function(current_ability, params['a'], params['b'], params['c'])
            
            if information > max_information:
                max_information = information
                best_question = question
        
        return best_question or available_questions[0]
    
    def update_ability_estimate(self, student_id):
        """
        Update ability estimate for student based on recent responses
        
        Args:
            student_id: Student identifier
        
        Returns:
            Updated theta (ability level)
        """
        # Get student's responses
        responses = StudentResponse.query.filter_by(student_id=student_id).all()
        
        if not responses:
            self.student_abilities[student_id] = 0.0
            return 0.0
        
        # Convert to format for ability estimation
        response_data = []
        for response in responses:
            response_data.append((response.is_correct, response.question_id))
        
        # Estimate ability
        theta = self.estimate_ability(response_data, self.item_params)
        self.student_abilities[student_id] = theta
        
        return theta
    
    def get_question_difficulty_string(self, difficulty):
        """Convert numeric difficulty to descriptive string"""
        if difficulty < -0.5:
            return 'Very Easy'
        elif difficulty < 0.0:
            return 'Easy'
        elif difficulty < 0.5:
            return 'Medium'
        elif difficulty < 1.5:
            return 'Hard'
        else:
            return 'Very Hard'
    
    def get_irt_statistics(self, question_id):
        """Get IRT parameters for a specific question"""
        params = self.item_params.get(question_id, self.default_params)
        return {
            'discrimination': params['a'],
            'difficulty': params['b'],
            'difficulty_label': self.get_question_difficulty_string(params['b']),
            'guessing': params['c'],
            'quality': self._assess_item_quality(params)
        }
    
    def _assess_item_quality(self, params):
        """Assess overall quality of item parameters"""
        a = params['a']
        b = params['b']
        c = params['c']
        
        quality_issues = []
        
        if a < 0.5:
            quality_issues.append('Low discrimination (not distinguishing students)')
        elif a > 2.5:
            quality_issues.append('Very high discrimination (may be too specific)')
        
        if c > 0.4:
            quality_issues.append('High guessing parameter (too easy to guess)')
        
        if abs(b) > 3:
            quality_issues.append('Extreme difficulty (very few students at this level)')
        
        return {
            'issues': quality_issues,
            'score': 3 - len(quality_issues)  # 0-3 scale
        }
    
    def save_calibration(self, filepath):
        """Save calibrated parameters to file"""
        data = {
            'item_params': self.item_params,
            'student_abilities': self.student_abilities,
            'calibrated_at': datetime.utcnow().isoformat()
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_calibration(self, filepath):
        """Load calibrated parameters from file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            self.item_params = data.get('item_params', {})
            self.student_abilities = data.get('student_abilities', {})
        except FileNotFoundError:
            pass


class CATAlgorithm:
    """Computerized Adaptive Testing (CAT) Implementation"""
    
    def __init__(self, irt_model, max_questions=20, stopping_se=0.3):
        """
        Initialize CAT algorithm
        
        Args:
            irt_model: Calibrated IRT model
            max_questions: Maximum questions per session
            stopping_se: Standard error threshold to stop testing
        """
        self.irt_model = irt_model
        self.max_questions = max_questions
        self.stopping_se = stopping_se
    
    def next_question(self, student_id, session_questions, available_questions):
        """
        Select next question using CAT algorithm
        
        Args:
            student_id: Student ID
            session_questions: Questions already administered
            available_questions: Questions available for selection
        
        Returns:
            Next question to administer
        """
        # Update ability estimate
        ability = self.irt_model.update_ability_estimate(student_id)
        
        # Get questions not yet asked
        asked_ids = {q.id for q in session_questions}
        remaining = [q for q in available_questions if q.id not in asked_ids]
        
        if not remaining:
            return None
        
        # Select question with maximum information (most discriminating at student's level)
        return self.irt_model.select_optimal_question(student_id, remaining, ability)
    
    def should_stop_testing(self, session_questions, responses):
        """
        Determine if testing should stop based on convergence criteria
        
        Args:
            session_questions: Questions administered so far
            responses: Student responses
        
        Returns:
            (should_stop: bool, reason: str)
        """
        # Stop if maximum questions reached
        if len(session_questions) >= self.max_questions:
            return True, f"Maximum questions ({self.max_questions}) reached"
        
        # Need minimum questions for reliable estimation
        if len(session_questions) < 3:
            return False, "Insufficient data for reliability"
        
        # For now, use simple stopping rule: continue until max questions
        # In production, would estimate standard error of ability estimate
        return False, "Continue testing"
    
    def estimate_final_ability(self, student_id, responses, question_params):
        """Final ability estimate after testing"""
        response_data = [(r.is_correct, r.question_id) for r in responses]
        return self.irt_model.estimate_ability(response_data, question_params)
