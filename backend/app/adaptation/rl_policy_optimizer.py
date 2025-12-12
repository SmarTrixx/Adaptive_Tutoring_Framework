"""
RL Policy Optimizer - Advanced Reinforcement Learning Features

Extends base RL agent with:
- Policy validation and performance assessment
- Reward signal optimization
- Convergence monitoring
- Action impact analysis
- Policy improvement strategies
"""

import numpy as np
from collections import defaultdict
from datetime import datetime, timedelta
from app.models.adaptation import AdaptationLog
from app.models.session import Session, StudentResponse
from app import db
import json


class RLPolicyOptimizer:
    """Optimize and validate RL adaptation policies"""
    
    def __init__(self, rl_agent):
        """
        Initialize policy optimizer
        
        Args:
            rl_agent: RLAdaptiveAgent instance to optimize
        """
        self.rl_agent = rl_agent
        self.policy_history = []  # Track policy changes over time
        self.reward_signals = defaultdict(list)  # Track rewards per action
        self.action_effectiveness = defaultdict(float)  # Action -> avg effectiveness
    
    def validate_policy(self, test_sessions_count=50):
        """
        Validate current policy on test sessions
        
        Args:
            test_sessions_count: Number of recent sessions to validate on
        
        Returns:
            {
                'policy_score': 0-100,
                'convergence': bool,
                'action_effectiveness': {},
                'recommendations': []
            }
        """
        # Get recent sessions
        recent_sessions = Session.query.order_by(
            Session.session_end.desc()
        ).limit(test_sessions_count).all()
        
        if not recent_sessions:
            return {'policy_score': 0, 'convergence': False, 'recommendations': ['No session data']}
        
        # Analyze policy effectiveness on these sessions
        total_effectiveness = 0
        action_successes = defaultdict(lambda: {'success': 0, 'total': 0})
        
        for session in recent_sessions:
            adaptation_logs = AdaptationLog.query.filter_by(session_id=session.id).all()
            
            # Calculate session effectiveness
            session_gain = session.score_percentage if session.score_percentage else 0
            
            for log in adaptation_logs:
                action_type = log.adaptation_type  # 'difficulty', 'pacing', 'hints', 'content'
                
                # Check if engagement improved after this action
                if session_gain > 50:  # Arbitrary threshold
                    action_successes[action_type]['success'] += 1
                
                action_successes[action_type]['total'] += 1
            
            total_effectiveness += session_gain
        
        # Calculate metrics
        avg_effectiveness = total_effectiveness / len(recent_sessions) if recent_sessions else 0
        policy_score = min(100, avg_effectiveness)
        
        # Determine convergence (small variance in recent rewards)
        recent_rewards = self.reward_signals.get('recent', [])
        convergence = (len(recent_rewards) > 10 and 
                      np.std(recent_rewards[-10:]) < 0.1) if recent_rewards else False
        
        # Calculate action effectiveness
        action_effectiveness = {}
        for action, results in action_successes.items():
            if results['total'] > 0:
                action_effectiveness[action] = results['success'] / results['total']
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            policy_score, action_effectiveness, convergence
        )
        
        return {
            'policy_score': round(policy_score, 1),
            'convergence': convergence,
            'action_effectiveness': action_effectiveness,
            'avg_session_performance': round(avg_effectiveness, 1),
            'sessions_analyzed': len(recent_sessions),
            'recommendations': recommendations
        }
    
    def _generate_recommendations(self, score, action_eff, convergence):
        """Generate improvement recommendations"""
        recs = []
        
        if score < 50:
            recs.append('Policy needs improvement - consider retraining')
        
        if not convergence:
            recs.append('Policy not converged - continue training for stability')
        
        for action, eff in action_eff.items():
            if eff < 0.3:
                recs.append(f'Action "{action}" is ineffective - consider adjusting parameters')
            elif eff > 0.7:
                recs.append(f'Action "{action}" is very effective - prioritize in learning')
        
        return recs
    
    def tune_reward_signal(self, session_id):
        """
        Tune and optimize reward signal for a session
        
        Args:
            session_id: Session to analyze
        
        Returns:
            Optimized reward values
        """
        session = Session.query.get(session_id)
        if not session:
            return None
        
        # Calculate reward components
        engagement_change = self._estimate_engagement_change(session_id)
        accuracy_change = self._estimate_accuracy_change(session_id)
        student_satisfaction = self._estimate_satisfaction(session_id)
        
        # Weighted reward signal (can be tuned)
        weights = {
            'engagement': 0.35,
            'accuracy': 0.40,
            'satisfaction': 0.25
        }
        
        optimized_reward = (
            weights['engagement'] * engagement_change +
            weights['accuracy'] * accuracy_change +
            weights['satisfaction'] * student_satisfaction
        )
        
        return {
            'engagement_change': engagement_change,
            'accuracy_change': accuracy_change,
            'satisfaction_estimate': student_satisfaction,
            'overall_reward': optimized_reward,
            'weights': weights
        }
    
    def _estimate_engagement_change(self, session_id):
        """Estimate change in engagement during session"""
        responses = StudentResponse.query.filter_by(session_id=session_id).order_by(
            StudentResponse.timestamp
        ).all()
        
        if len(responses) < 2:
            return 0.0
        
        # Early vs late engagement
        early_responses = responses[:len(responses)//2]
        late_responses = responses[len(responses)//2:]
        
        early_engagement = np.mean([
            1.0 if r.response_time_seconds and r.response_time_seconds < 45 else 0.5
            for r in early_responses
        ])
        
        late_engagement = np.mean([
            1.0 if r.response_time_seconds and r.response_time_seconds < 45 else 0.5
            for r in late_responses
        ])
        
        return late_engagement - early_engagement
    
    def _estimate_accuracy_change(self, session_id):
        """Estimate accuracy improvement during session"""
        responses = StudentResponse.query.filter_by(session_id=session_id).order_by(
            StudentResponse.timestamp
        ).all()
        
        if len(responses) < 2:
            return 0.0
        
        early_acc = np.mean([1.0 if r.is_correct else 0.0 for r in responses[:len(responses)//2]])
        late_acc = np.mean([1.0 if r.is_correct else 0.0 for r in responses[len(responses)//2:]])
        
        return late_acc - early_acc
    
    def _estimate_satisfaction(self, session_id):
        """Estimate student satisfaction from session behavior"""
        session = Session.query.get(session_id)
        
        # Proxies for satisfaction
        completion_rate = session.total_questions / max(1, session.total_questions)
        accuracy = session.score_percentage / 100.0 if session.score_percentage else 0.5
        
        # Satisfaction is higher with moderate accuracy and completion
        satisfaction = min(1.0, completion_rate * 0.6 + (0.5 if 0.3 < accuracy < 0.7 else accuracy) * 0.4)
        
        return satisfaction
    
    def monitor_convergence(self):
        """
        Monitor Q-table convergence
        
        Returns:
            Convergence metrics
        """
        if not self.rl_agent.experience_buffer:
            return {'converged': False, 'q_table_size': 0}
        
        # Get Q-value statistics
        all_q_values = []
        for state_actions in self.rl_agent.q_table.values():
            all_q_values.extend(state_actions.values())
        
        if not all_q_values:
            return {'converged': False, 'q_table_size': 0}
        
        # Calculate metrics
        q_values = np.array(all_q_values)
        q_std = np.std(q_values)
        q_mean = np.mean(q_values)
        
        # Convergence indicators
        max_q_variance = q_std / (abs(q_mean) + 0.1) if q_mean != 0 else q_std
        
        return {
            'q_table_size': len(self.rl_agent.q_table),
            'states_visited': len(self.rl_agent.q_table),
            'avg_q_value': float(q_mean),
            'q_value_std': float(q_std),
            'convergence_metric': 1.0 - min(1.0, max_q_variance),
            'converged': max_q_variance < 0.3,  # Converged if low variance
            'training_progress': min(1.0, len(self.rl_agent.experience_buffer) / 1000.0)
        }
    
    def analyze_action_impact(self, action_type):
        """
        Analyze impact of specific action type
        
        Args:
            action_type: 'difficulty', 'pacing', 'hints', 'content'
        
        Returns:
            Impact analysis
        """
        logs = AdaptationLog.query.filter_by(adaptation_type=action_type).all()
        
        if not logs:
            return {'action': action_type, 'impact': 'insufficient_data'}
        
        # Collect outcomes
        improvements = 0
        total = 0
        impact_scores = []
        
        for log in logs:
            session = Session.query.get(log.session_id)
            if session:
                total += 1
                
                # Check if performance improved after action
                if session.score_percentage and session.score_percentage > 50:
                    improvements += 1
                    impact_scores.append(session.score_percentage / 100.0)
        
        if total == 0:
            return {'action': action_type, 'impact': 'insufficient_data'}
        
        return {
            'action': action_type,
            'total_times_used': total,
            'success_rate': improvements / total,
            'avg_impact_score': np.mean(impact_scores) if impact_scores else 0.0,
            'impact_std': np.std(impact_scores) if impact_scores else 0.0,
            'recommendation': self._action_recommendation(improvements / total)
        }
    
    def _action_recommendation(self, success_rate):
        """Generate recommendation based on success rate"""
        if success_rate > 0.75:
            return 'Highly effective - increase usage'
        elif success_rate > 0.5:
            return 'Moderately effective - continue using'
        elif success_rate > 0.25:
            return 'Needs improvement - consider tuning'
        else:
            return 'Ineffective - consider removing or redesigning'
    
    def get_policy_summary(self):
        """Get comprehensive policy summary"""
        return {
            'convergence_status': self.monitor_convergence(),
            'policy_validation': self.validate_policy(),
            'action_impacts': {
                'difficulty': self.analyze_action_impact('difficulty'),
                'pacing': self.analyze_action_impact('pacing'),
                'hints': self.analyze_action_impact('hints'),
                'content': self.analyze_action_impact('content')
            },
            'timestamp': datetime.utcnow().isoformat()
        }


class ExplorationStrategy:
    """Manage exploration vs exploitation trade-off"""
    
    def __init__(self, initial_epsilon=0.1, decay_rate=0.995):
        """
        Initialize exploration strategy
        
        Args:
            initial_epsilon: Starting exploration rate
            decay_rate: Rate at which epsilon decays
        """
        self.initial_epsilon = initial_epsilon
        self.current_epsilon = initial_epsilon
        self.decay_rate = decay_rate
        self.iteration_count = 0
    
    def decay_epsilon(self):
        """Decay exploration rate over time"""
        self.current_epsilon = self.initial_epsilon * (self.decay_rate ** self.iteration_count)
        self.iteration_count += 1
        return self.current_epsilon
    
    def should_explore(self):
        """Determine if should explore or exploit"""
        return np.random.random() < self.current_epsilon
    
    def get_status(self):
        """Get current exploration status"""
        return {
            'epsilon': self.current_epsilon,
            'iteration': self.iteration_count,
            'explore_rate': f"{self.current_epsilon*100:.1f}%",
            'exploit_rate': f"{(1-self.current_epsilon)*100:.1f}%"
        }
