# Question Difficulty Mapper
# Maps system difficulty (0.0-1.0) to question difficulty pools (low/medium/high)

class DifficultyMapper:
    """
    Maps system difficulty level to question difficulty labels and pools.
    
    System Difficulty Range (0.0 - 1.0):
    - 0.0 - 0.35: Low difficulty (easy questions)
    - 0.35 - 0.65: Medium difficulty (medium questions)  
    - 0.65 - 1.0: High difficulty (hard questions)
    """
    
    # Question difficulty labels
    QUESTION_EASY = "easy"
    QUESTION_MEDIUM = "medium"
    QUESTION_HARD = "hard"
    
    # System difficulty thresholds
    THRESHOLD_LOW_TO_MEDIUM = 0.35
    THRESHOLD_MEDIUM_TO_HARD = 0.65
    
    @staticmethod
    def get_difficulty_label(system_difficulty):
        """
        Convert system difficulty (0.0-1.0) to label (easy/medium/hard).
        
        Args:
            system_difficulty: Float between 0.0 and 1.0
            
        Returns:
            Difficulty label: "easy", "medium", or "hard"
        """
        if system_difficulty < DifficultyMapper.THRESHOLD_LOW_TO_MEDIUM:
            return DifficultyMapper.QUESTION_EASY
        elif system_difficulty < DifficultyMapper.THRESHOLD_MEDIUM_TO_HARD:
            return DifficultyMapper.QUESTION_MEDIUM
        else:
            return DifficultyMapper.QUESTION_HARD
    
    @staticmethod
    def get_difficulty_range(system_difficulty):
        """
        Get the numeric difficulty range for a given system difficulty.
        
        Returns a tuple (min_difficulty, max_difficulty, label).
        This allows flexible question selection around the target.
        """
        label = DifficultyMapper.get_difficulty_label(system_difficulty)
        
        if label == DifficultyMapper.QUESTION_EASY:
            # Easy questions: 0.1 - 0.4
            return (0.1, 0.4, label)
        elif label == DifficultyMapper.QUESTION_MEDIUM:
            # Medium questions: 0.35 - 0.65
            return (0.35, 0.65, label)
        else:  # HARD
            # Hard questions: 0.6 - 0.95
            return (0.6, 0.95, label)
    
    @staticmethod
    def get_difficulty_band(system_difficulty):
        """
        Get tighter range for more precise targeting (±0.1 around system difficulty).
        """
        min_diff = max(0.0, system_difficulty - 0.1)
        max_diff = min(1.0, system_difficulty + 0.1)
        label = DifficultyMapper.get_difficulty_label(system_difficulty)
        return (min_diff, max_diff, label)


class QuestionPool:
    """
    Represents a pool of questions at a specific difficulty level.
    """
    
    def __init__(self, difficulty_label, question_count=0):
        self.difficulty_label = difficulty_label
        self.question_count = question_count
        self.average_difficulty = self._get_average_difficulty()
    
    def _get_average_difficulty(self):
        """Get the average difficulty value for this label."""
        if self.difficulty_label == DifficultyMapper.QUESTION_EASY:
            return 0.25
        elif self.difficulty_label == DifficultyMapper.QUESTION_MEDIUM:
            return 0.50
        else:  # HARD
            return 0.75
    
    def __repr__(self):
        return f"QuestionPool({self.difficulty_label}, count={self.question_count})"


def analyze_question_pools(session):
    """
    Analyze what question pools are available at current system difficulty.
    Used for debugging and understanding pool selection.
    """
    system_difficulty = session.current_difficulty
    min_diff, max_diff, label = DifficultyMapper.get_difficulty_range(system_difficulty)
    
    from app.models.question import Question
    from app import db
    
    pool_easy = Question.query.filter(
        Question.subject == session.subject,
        Question.difficulty < DifficultyMapper.THRESHOLD_LOW_TO_MEDIUM
    ).count()
    
    pool_medium = Question.query.filter(
        Question.subject == session.subject,
        Question.difficulty >= DifficultyMapper.THRESHOLD_LOW_TO_MEDIUM,
        Question.difficulty < DifficultyMapper.THRESHOLD_MEDIUM_TO_HARD
    ).count()
    
    pool_hard = Question.query.filter(
        Question.subject == session.subject,
        Question.difficulty >= DifficultyMapper.THRESHOLD_MEDIUM_TO_HARD
    ).count()
    
    return {
        'system_difficulty': system_difficulty,
        'target_label': label,
        'pools': {
            'easy': pool_easy,
            'medium': pool_medium,
            'hard': pool_hard
        },
        'target_range': (min_diff, max_diff),
        'probability_distribution': {
            'easy': pool_easy / (pool_easy + pool_medium + pool_hard) if (pool_easy + pool_medium + pool_hard) > 0 else 0,
            'medium': pool_medium / (pool_easy + pool_medium + pool_hard) if (pool_easy + pool_medium + pool_hard) > 0 else 0,
            'hard': pool_hard / (pool_easy + pool_medium + pool_hard) if (pool_easy + pool_medium + pool_hard) > 0 else 0
        }
    }
