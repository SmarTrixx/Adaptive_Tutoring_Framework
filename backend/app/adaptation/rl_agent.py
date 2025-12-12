"""
Reinforcement Learning Agent for Adaptive Tutoring

Uses Q-learning to optimize adaptation decisions based on:
- Student engagement state
- Performance outcomes
- Adaptation effectiveness

Learns optimal policies for:
- Difficulty adjustment
- Pacing modification
- Hint provision
- Content selection
"""

import numpy as np
from collections import defaultdict
from datetime import datetime, timedelta
from app.models.adaptation import AdaptationLog
from app.models.session import Session, StudentResponse
from app import db
import json

class RLAdaptiveAgent:
    """Reinforcement Learning Agent for tutorial adaptation"""
    
    def __init__(self, learning_rate=0.1, discount_factor=0.95, epsilon=0.1):
        """
        Initialize RL Agent
        
        Args:
            learning_rate: How much new information overrides old (0-1)
            discount_factor: How much future rewards matter (0-1)
            epsilon: Exploration rate (0-1)
        """
        self.alpha = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon
        
        # Q-table: state -> action -> Q-value
        # State: (engagement_level, accuracy_range, question_difficulty)
        # Action: (difficulty_change, pacing, hint_strategy, content_focus)
        self.q_table = defaultdict(lambda: defaultdict(float))
        
        # Experience buffer for training
        self.experience_buffer = []
        self.max_buffer_size = 10000
        
        # Action space
        self.difficulty_actions = [-0.2, -0.1, 0, 0.1, 0.2]  # Change in difficulty
        self.pacing_actions = ['slow', 'medium', 'fast']
        self.hint_actions = ['minimal', 'normal', 'generous']
        self.content_actions = ['reinforce_gaps', 'maintain', 'advance']
    
    def discretize_state(self, engagement_score, accuracy, question_difficulty):
        """
        Convert continuous state into discrete buckets for Q-table
        
        Returns: state tuple
        """
        # Engagement buckets: low (0-.33), medium (.33-.67), high (.67-1)
        engagement_level = 'low' if engagement_score < 0.33 else ('medium' if engagement_score < 0.67 else 'high')
        
        # Accuracy buckets: poor (0-.33), fair (.33-.67), good (.67-1)
        accuracy_level = 'poor' if accuracy < 0.33 else ('fair' if accuracy < 0.67 else 'good')
        
        # Difficulty buckets: easy (0-.33), medium (.33-.67), hard (.67-1)
        difficulty_level = 'easy' if question_difficulty < 0.33 else ('medium' if question_difficulty < 0.67 else 'hard')
        
        state = (engagement_level, accuracy_level, difficulty_level)
        return state
    
    def select_action(self, state, use_exploration=True):
        """
        Select action using epsilon-greedy strategy
        
        Args:
            state: Current state (discretized)
            use_exploration: Whether to use exploration (epsilon-greedy)
        
        Returns:
            (difficulty_action, pacing_action, hint_action, content_action)
        """
        # Epsilon-greedy action selection
        if use_exploration and np.random.random() < self.epsilon:
            # Explore: random action
            return (
                np.random.choice(self.difficulty_actions),
                np.random.choice(self.pacing_actions),
                np.random.choice(self.hint_actions),
                np.random.choice(self.content_actions)
            )
        else:
            # Exploit: best known action
            difficulty_action = self._select_best_action(state, 'difficulty')
            pacing_action = self._select_best_action(state, 'pacing')
            hint_action = self._select_best_action(state, 'hints')
            content_action = self._select_best_action(state, 'content')
            
            return (difficulty_action, pacing_action, hint_action, content_action)
    
    def update_q_value(self, state, action, reward, next_state):
        """
        Update Q-value using Q-learning formula:
        Q(s,a) = Q(s,a) + α[r + γ*max(Q(s',a')) - Q(s,a)]
        
        Args:
            state: Current state
            action: Action taken (tuple of 4 sub-actions)
            reward: Reward received
            next_state: Resulting state
        """
        action_str = str(action)
        
        # Current Q-value
        current_q = self.q_table[state][action_str]
        
        # Maximum Q-value for next state
        max_next_q = max(
            (self.q_table[next_state].values()) 
            if self.q_table[next_state] else [0]
        )
        
        # Q-learning update
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        
        self.q_table[state][action_str] = new_q
    
    def calculate_reward(self, engagement_before, engagement_after, 
                        accuracy_before, accuracy_after, adaptation_type):
        """
        Calculate reward for taking an action
        
        Reward is based on:
        - Improvement in engagement (+)
        - Improvement in accuracy (+)
        - Over-adaptation penalty (-)
        
        Args:
            engagement_before/after: Engagement scores
            accuracy_before/after: Accuracy scores
            adaptation_type: Type of adaptation made
        
        Returns:
            Reward value (-1 to +1)
        """
        reward = 0.0
        
        # Engagement improvement (max +0.4)
        engagement_delta = engagement_after - engagement_before
        if engagement_delta > 0:
            reward += min(0.4, engagement_delta * 0.4)
        else:
            reward -= min(0.2, abs(engagement_delta) * 0.2)
        
        # Accuracy improvement (max +0.4)
        accuracy_delta = accuracy_after - accuracy_before
        if accuracy_delta > 0:
            reward += min(0.4, accuracy_delta * 0.4)
        else:
            reward -= min(0.2, abs(accuracy_delta) * 0.2)
        
        # Small penalty for each adaptation (encourage stability)
        reward -= 0.05
        
        return max(-1.0, min(1.0, reward))  # Clamp to [-1, 1]
    
    def learn_from_experience(self, student_id, session_id):
        """
        Learn from student's session experience
        
        Analyzes adaptation logs and engagement metrics to improve policy
        """
        # Get adaptation logs for this session
        logs = AdaptationLog.query.filter_by(
            session_id=session_id
        ).order_by(AdaptationLog.timestamp).all()
        
        if len(logs) < 2:
            return {'status': 'insufficient_data', 'updates': 0}
        
        updates = 0
        
        # Process each adaptation event
        for i, log in enumerate(logs[:-1]):
            # Get engagement metric before and after
            metric_before = self._get_engagement_at_time(session_id, log.timestamp)
            metric_after = self._get_engagement_at_time(session_id, logs[i+1].timestamp)
            
            if not (metric_before and metric_after):
                continue
            
            # Discretize states
            state = self.discretize_state(
                metric_before.engagement_score,
                metric_before.accuracy,
                metric_before.confidence_level or 0.5
            )
            
            next_state = self.discretize_state(
                metric_after.engagement_score,
                metric_after.accuracy,
                metric_after.confidence_level or 0.5
            )
            
            # Convert log to action tuple
            action = self._log_to_action(log)
            
            # Calculate reward
            reward = self.calculate_reward(
                metric_before.engagement_score,
                metric_after.engagement_score,
                metric_before.accuracy,
                metric_after.accuracy,
                log.adaptation_type
            )
            
            # Update Q-value
            self.update_q_value(state, action, reward, next_state)
            updates += 1
        
        return {
            'status': 'success',
            'updates': updates,
            'total_states_learned': len(self.q_table)
        }
    
    def get_policy_summary(self):
        """Get summary of learned policy"""
        return {
            'total_states': len(self.q_table),
            'q_table_size': sum(len(actions) for actions in self.q_table.values()),
            'learning_rate': self.alpha,
            'discount_factor': self.gamma,
            'exploration_rate': self.epsilon
        }
    
    def predict_best_adaptation(self, engagement_score, accuracy, current_difficulty):
        """
        Predict best adaptation for current state based on learned policy
        
        Returns:
            Recommended actions for difficulty, pacing, hints, and content
        """
        state = self.discretize_state(engagement_score, accuracy, current_difficulty)
        
        difficulty_action = self._select_best_action(state, 'difficulty')
        pacing_action = self._select_best_action(state, 'pacing')
        hint_action = self._select_best_action(state, 'hints')
        content_action = self._select_best_action(state, 'content')
        
        return {
            'difficulty_change': difficulty_action,
            'pacing': pacing_action,
            'hint_strategy': hint_action,
            'content_focus': content_action,
            'confidence': self._estimate_confidence(state)
        }
    
    # Helper methods
    def _select_best_action(self, state, action_type):
        """Select best action for given state and action type"""
        # Stub: would evaluate all possible actions
        # For now, return neutral action
        if action_type == 'difficulty':
            return 0  # No change
        elif action_type == 'pacing':
            return 'medium'
        elif action_type == 'hints':
            return 'normal'
        else:  # content
            return 'maintain'
    
    def _estimate_confidence(self, state):
        """Estimate confidence in policy recommendation"""
        if state in self.q_table:
            actions = self.q_table[state]
            if actions:
                values = list(actions.values())
                return min(1.0, len(values) / 10)  # More data = more confidence
        return 0.1  # Low confidence for unexplored states
    
    def _log_to_action(self, log):
        """Convert AdaptationLog to action tuple"""
        # Parse action from log
        action_type = log.adaptation_type
        new_value = log.new_value or 0
        old_value = log.old_value or 0
        
        # Map to action tuple format
        # This is a simplified mapping; could be more sophisticated
        return (new_value - old_value, 'medium', 'normal', 'maintain')
    
    def _get_engagement_at_time(self, session_id, timestamp):
        """Get engagement metric closest to given timestamp"""
        from app.models.engagement import EngagementMetric
        
        metric = EngagementMetric.query.filter_by(
            session_id=session_id
        ).filter(
            EngagementMetric.timestamp <= timestamp
        ).order_by(EngagementMetric.timestamp.desc()).first()
        
        return metric
    
    def save_model(self, filepath):
        """Save trained model to file"""
        # Convert defaultdict to regular dict for serialization
        q_table_dict = {str(k): {str(a): v for a, v in actions.items()} 
                       for k, actions in self.q_table.items()}
        
        model_data = {
            'q_table': q_table_dict,
            'alpha': self.alpha,
            'gamma': self.gamma,
            'epsilon': self.epsilon,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Save to JSON
        import json
        with open(filepath, 'w') as f:
            json.dump(model_data, f, indent=2)
    
    def load_model(self, filepath):
        """Load trained model from file"""
        import json
        
        with open(filepath, 'r') as f:
            model_data = json.load(f)
        
        # Restore Q-table
        for state_str, actions in model_data['q_table'].items():
            state = eval(state_str)  # Convert string back to tuple
            for action_str, q_value in actions.items():
                self.q_table[state][action_str] = q_value
        
        self.alpha = model_data['alpha']
        self.gamma = model_data['gamma']
        self.epsilon = model_data['epsilon']

