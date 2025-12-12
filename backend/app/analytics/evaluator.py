"""
Evaluation Framework for Research Objectives Assessment

Evaluates framework effectiveness for:
1. Sustained Engagement - tracking engagement over time
2. Performance Improvement - measuring learning gains
3. Adaptation Effectiveness - assessing quality of adaptations
4. System Impact - overall framework benefits

Provides statistical analysis and reporting capabilities
"""

from datetime import datetime, timedelta
from app.models.session import Session, StudentResponse
from app.models.engagement import EngagementMetric
from app.models.adaptation import AdaptationLog
from app.models.student import Student
from app import db
import statistics
import json

class ResearchEvaluator:
    """Evaluates framework effectiveness for research objectives"""
    
    def __init__(self):
        self.metrics = {}
    
    # OBJECTIVE IV: Evaluation Framework
    
    def evaluate_sustained_engagement(self, student_id, time_window_days=30):
        """
        Evaluate whether framework supports sustained engagement
        
        Metrics:
        - Session frequency (sessions per week)
        - Average engagement score trend
        - Engagement consistency
        - Session dropout (if any)
        - Time-on-task trend
        
        Returns:
            Comprehensive engagement analysis
        """
        cutoff_date = datetime.utcnow() - timedelta(days=time_window_days)
        
        # Get all sessions in window
        sessions = Session.query.filter(
            Session.student_id == student_id,
            Session.session_start >= cutoff_date
        ).order_by(Session.session_start).all()
        
        if not sessions:
            return {
                'status': 'insufficient_data',
                'message': 'No sessions found in window'
            }
        
        # Session frequency
        session_dates = [s.session_start.date() for s in sessions]
        unique_days = len(set(session_dates))
        weeks_active = max(1, (datetime.utcnow().date() - sessions[0].session_start.date()).days / 7)
        sessions_per_week = len(sessions) / weeks_active
        
        # Engagement trends
        engagement_scores = []
        session_durations = []
        
        for session in sessions:
            metrics = EngagementMetric.query.filter_by(
                session_id=session.id
            ).all()
            
            if metrics:
                avg_score = sum(m.engagement_score for m in metrics) / len(metrics)
                engagement_scores.append(avg_score)
            
            session_durations.append(session.duration_seconds)
        
        # Calculate trends
        if len(engagement_scores) >= 2:
            first_half = engagement_scores[:len(engagement_scores)//2]
            second_half = engagement_scores[len(engagement_scores)//2:]
            
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            
            engagement_trend = 'improving' if second_avg > first_avg else ('declining' if second_avg < first_avg else 'stable')
            trend_magnitude = abs(second_avg - first_avg)
        else:
            engagement_trend = 'insufficient_data'
            trend_magnitude = 0
        
        # Consistency (standard deviation)
        if engagement_scores:
            engagement_consistency = statistics.stdev(engagement_scores) if len(engagement_scores) > 1 else 0
            avg_engagement = statistics.mean(engagement_scores)
        else:
            engagement_consistency = 0
            avg_engagement = 0
        
        return {
            'evaluation_period_days': time_window_days,
            'total_sessions': len(sessions),
            'unique_days_active': unique_days,
            'sessions_per_week': round(sessions_per_week, 2),
            'sustained': sessions_per_week >= 1,  # At least 1 session/week = sustained
            
            'engagement': {
                'average_score': round(avg_engagement, 3),
                'trend': engagement_trend,
                'trend_magnitude': round(trend_magnitude, 3),
                'consistency_sd': round(engagement_consistency, 3),
                'sustained_engagement': engagement_trend != 'declining' and avg_engagement > 0.5
            },
            
            'time_on_task': {
                'average_session_duration': round(statistics.mean(session_durations)) if session_durations else 0,
                'total_time_spent_seconds': sum(session_durations),
                'total_time_spent_hours': round(sum(session_durations) / 3600, 1)
            },
            
            'overall_assessment': {
                'sustained_engagement': sessions_per_week >= 1 and avg_engagement > 0.5,
                'reliability': round(min(1.0, len(sessions) / 10), 2)  # Confidence based on sample size
            }
        }
    
    def evaluate_performance_improvement(self, student_id, include_baseline=True):
        """
        Evaluate performance improvement over time
        
        Metrics:
        - Initial vs. current accuracy
        - Learning gain (improvement)
        - Consistency of improvement
        - Topic-specific improvement
        
        Returns:
            Performance improvement analysis
        """
        # Get all responses ordered by time
        from app.models.session import Session
        responses = StudentResponse.query.join(
            Session, StudentResponse.session_id == Session.id
        ).filter(
            Session.student_id == student_id
        ).order_by(StudentResponse.timestamp).all()
        
        if len(responses) < 5:
            return {
                'status': 'insufficient_data',
                'message': 'Need at least 5 responses for evaluation'
            }
        
        # Calculate baseline (first quartile)
        baseline_size = max(1, len(responses) // 4)
        baseline_responses = responses[:baseline_size]
        baseline_accuracy = sum(1 for r in baseline_responses if r.is_correct) / len(baseline_responses)
        
        # Calculate current performance (last quartile)
        current_responses = responses[-baseline_size:]
        current_accuracy = sum(1 for r in current_responses if r.is_correct) / len(current_responses)
        
        # Learning gain
        learning_gain = current_accuracy - baseline_accuracy
        learning_gain_percent = learning_gain * 100
        
        # Improvement velocity (gain per session)
        sessions = set(r.session_id for r in responses)
        improvement_velocity = learning_gain / len(sessions) if sessions else 0
        
        # Consistency of improvement (reducing variance)
        baseline_correctness = [1 if r.is_correct else 0 for r in baseline_responses]
        current_correctness = [1 if r.is_correct else 0 for r in current_responses]
        
        baseline_variance = statistics.variance(baseline_correctness) if len(baseline_correctness) > 1 else 0
        current_variance = statistics.variance(current_correctness) if len(current_correctness) > 1 else 0
        
        return {
            'performance_analysis': {
                'baseline_accuracy': round(baseline_accuracy, 3),
                'current_accuracy': round(current_accuracy, 3),
                'learning_gain': round(learning_gain, 3),
                'learning_gain_percent': round(learning_gain_percent, 1),
                'improvement': learning_gain > 0.1  # >10% improvement = positive
            },
            
            'improvement_rate': {
                'gain_per_session': round(improvement_velocity, 4),
                'total_sessions': len(sessions),
                'expected_mastery_timeframe': self._estimate_mastery_time(learning_gain, improvement_velocity)
            },
            
            'consistency': {
                'baseline_variance': round(baseline_variance, 3),
                'current_variance': round(current_variance, 3),
                'variance_reduction': round(baseline_variance - current_variance, 3),
                'more_consistent': current_variance < baseline_variance
            },
            
            'overall_assessment': {
                'significant_improvement': learning_gain > 0.15,
                'positive_trend': improvement_velocity > 0,
                'reliable_improvement': current_variance < baseline_variance
            }
        }
    
    def evaluate_adaptation_effectiveness(self, student_id, session_id=None):
        """
        Evaluate how effective the adaptive system's decisions are
        
        Metrics:
        - Adaptation frequency vs. effectiveness
        - Engagement impact of adaptations
        - Performance impact of adaptations
        - Unnecessary adaptations
        
        Returns:
            Adaptation effectiveness analysis
        """
        if session_id:
            logs = AdaptationLog.query.filter_by(
                student_id=student_id,
                session_id=session_id
            ).all()
        else:
            logs = AdaptationLog.query.filter_by(
                student_id=student_id
            ).all()
        
        if not logs:
            return {
                'status': 'no_adaptations',
                'message': 'No adaptations made for this student'
            }
        
        # Analyze each adaptation type
        adaptation_types = {}
        total_effective = 0
        
        for log in logs:
            atype = log.adaptation_type
            
            if atype not in adaptation_types:
                adaptation_types[atype] = {
                    'count': 0,
                    'effective': 0,
                    'reasons': []
                }
            
            adaptation_types[atype]['count'] += 1
            
            if log.was_effective:
                adaptation_types[atype]['effective'] += 1
                total_effective += 1
            
            adaptation_types[atype]['reasons'].append(log.reason)
        
        # Calculate effectiveness percentages
        effectiveness_rates = {}
        for atype, data in adaptation_types.items():
            if data['count'] > 0:
                effectiveness_rates[atype] = round(data['effective'] / data['count'], 3)
        
        overall_effectiveness = round(total_effective / len(logs), 3) if logs else 0
        
        return {
            'total_adaptations': len(logs),
            'adaptation_types': len(adaptation_types),
            
            'effectiveness': {
                'overall_effectiveness_rate': overall_effectiveness,
                'effective_adaptations': total_effective,
                'ineffective_adaptations': len(logs) - total_effective,
                'by_type': effectiveness_rates
            },
            
            'adaptation_summary': {
                atype: {
                    'total': data['count'],
                    'effective': data['effective'],
                    'effectiveness_rate': round(data['effective'] / data['count'], 3),
                    'sample_reasons': list(set(data['reasons']))[:3]
                }
                for atype, data in adaptation_types.items()
            },
            
            'overall_assessment': {
                'effective': overall_effectiveness > 0.6,
                'adaptations_justified': len(logs) <= 10,  # Too many suggests over-adaptation
                'diverse_strategies': len(adaptation_types) >= 2
            }
        }
    
    def evaluate_system_impact(self, student_id=None):
        """
        Evaluate overall system impact on learning outcomes
        
        If student_id provided: individual impact
        If None: aggregate system impact
        
        Returns:
            System impact assessment
        """
        if student_id:
            # Individual impact
            student = Student.query.get(student_id)
            if not student:
                return {'error': 'Student not found'}
            
            # Get metrics
            engagement = self.evaluate_sustained_engagement(student_id)
            performance = self.evaluate_performance_improvement(student_id)
            adaptation = self.evaluate_adaptation_effectiveness(student_id)
            
            return {
                'student_id': student_id,
                'student_name': student.name,
                'engagement_score': engagement.get('engagement', {}).get('average_score', 0),
                'performance_improvement': performance.get('performance_analysis', {}).get('learning_gain_percent', 0),
                'adaptation_effectiveness': adaptation.get('effectiveness', {}).get('overall_effectiveness_rate', 0),
                
                'impact_assessment': {
                    'positive_impact': (
                        engagement.get('sustained', False) and
                        performance.get('overall_assessment', {}).get('significant_improvement', False) and
                        adaptation.get('overall_assessment', {}).get('effective', False)
                    ),
                    'recommended_action': self._recommend_action(engagement, performance, adaptation)
                }
            }
        else:
            # Aggregate impact
            students = Student.query.all()
            
            if not students:
                return {'status': 'no_students'}
            
            metrics = {
                'avg_engagement': [],
                'avg_improvement': [],
                'avg_adaptation_effectiveness': []
            }
            
            for student in students:
                try:
                    engagement = self.evaluate_sustained_engagement(student.id)
                    metrics['avg_engagement'].append(
                        engagement.get('engagement', {}).get('average_score', 0)
                    )
                    
                    performance = self.evaluate_performance_improvement(student.id)
                    if 'performance_analysis' in performance:
                        metrics['avg_improvement'].append(
                            performance['performance_analysis'].get('learning_gain_percent', 0)
                        )
                    
                    adaptation = self.evaluate_adaptation_effectiveness(student.id)
                    if 'effectiveness' in adaptation:
                        metrics['avg_adaptation_effectiveness'].append(
                            adaptation['effectiveness'].get('overall_effectiveness_rate', 0)
                        )
                except:
                    pass
            
            return {
                'total_students': len(students),
                'students_with_data': len(metrics['avg_engagement']),
                
                'system_impact': {
                    'average_engagement': round(
                        statistics.mean(metrics['avg_engagement']),
                        3
                    ) if metrics['avg_engagement'] else 0,
                    'average_improvement_percent': round(
                        statistics.mean(metrics['avg_improvement']),
                        1
                    ) if metrics['avg_improvement'] else 0,
                    'average_adaptation_effectiveness': round(
                        statistics.mean(metrics['avg_adaptation_effectiveness']),
                        3
                    ) if metrics['avg_adaptation_effectiveness'] else 0
                },
                
                'overall_system_effectiveness': self._calculate_system_score(
                    metrics
                )
            }
    
    def generate_research_report(self, student_id=None):
        """Generate comprehensive research evaluation report"""
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'evaluation_type': 'individual' if student_id else 'aggregate'
        }
        
        if student_id:
            report['student_id'] = student_id
            report['sustained_engagement'] = self.evaluate_sustained_engagement(student_id)
            report['performance_improvement'] = self.evaluate_performance_improvement(student_id)
            report['adaptation_effectiveness'] = self.evaluate_adaptation_effectiveness(student_id)
            report['system_impact'] = self.evaluate_system_impact(student_id)
        else:
            report['system_impact'] = self.evaluate_system_impact()
        
        return report
    
    # Helper methods
    def _estimate_mastery_time(self, current_gain, velocity):
        """Estimate time to mastery at current improvement rate"""
        if velocity <= 0:
            return "Not improving"
        
        remaining_gain = 0.85 - (0.5 + current_gain)  # From current to mastery
        if remaining_gain <= 0:
            return "Already at mastery"
        
        sessions_to_mastery = int(remaining_gain / velocity)
        return f"~{sessions_to_mastery} more sessions"
    
    def _recommend_action(self, engagement, performance, adaptation):
        """Recommend action based on evaluations"""
        issues = []
        
        if not engagement.get('sustained', False):
            issues.append("Low engagement - recommend motivational interventions")
        
        if not performance.get('overall_assessment', {}).get('significant_improvement', False):
            issues.append("Low improvement - review adaptation strategy")
        
        if not adaptation.get('overall_assessment', {}).get('effective', False):
            issues.append("Adaptations ineffective - improve algorithm")
        
        if not issues:
            return "Continue with current approach - positive outcomes"
        
        return "; ".join(issues)
    
    def _calculate_system_score(self, metrics):
        """Calculate overall system effectiveness score (0-100)"""
        scores = []
        
        if metrics['avg_engagement']:
            scores.append(statistics.mean(metrics['avg_engagement']) * 100)
        
        if metrics['avg_improvement']:
            # Cap improvement at 50 for this metric (50% = excellent)
            scores.append(min(50, statistics.mean(metrics['avg_improvement'])))
        
        if metrics['avg_adaptation_effectiveness']:
            scores.append(statistics.mean(metrics['avg_adaptation_effectiveness']) * 100)
        
        if not scores:
            return 0
        
        return round(statistics.mean(scores), 1)

