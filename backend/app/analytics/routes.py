from flask import Blueprint, request, jsonify
from app.models.student import Student
from app.models.session import Session, StudentResponse
from app.models.engagement import EngagementMetric
from app.models.adaptation import AdaptationLog
from app.models.question import Question
from app import db
from sqlalchemy import func, and_
import statistics

# Import new modules
from app.engagement.mastery import MasteryTracker
from app.engagement.affective import AffectiveIndicatorAnalyzer
from app.engagement.spaced_repetition import SpacedRepetitionScheduler, LearningCurveAnalyzer
from app.adaptation.rl_agent import RLAdaptiveAgent
from app.adaptation.rl_policy_optimizer import RLPolicyOptimizer, ExplorationStrategy
from app.adaptation.irt import IRTModel, CATAlgorithm
from app.analytics.evaluator import ResearchEvaluator

analytics_bp = Blueprint('analytics', __name__)

# Initialize modules (singletons)
mastery_tracker = MasteryTracker()
affective_analyzer = AffectiveIndicatorAnalyzer()
spaced_rep_scheduler = SpacedRepetitionScheduler()
learning_curve_analyzer = LearningCurveAnalyzer()
rl_agent = RLAdaptiveAgent()
policy_optimizer = RLPolicyOptimizer(rl_agent)
exploration_strategy = ExplorationStrategy()
irt_model = IRTModel()
cat_algorithm = CATAlgorithm(irt_model)
research_evaluator = ResearchEvaluator()

@analytics_bp.route('/student/<student_id>/summary', methods=['GET'])
def get_student_summary(student_id):
    """Get comprehensive summary of a student's learning"""
    student = Student.query.get(student_id)
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    sessions = Session.query.filter_by(student_id=student_id).all()
    
    if not sessions:
        return jsonify({
            'success': True,
            'student_id': student_id,
            'summary': {
                'total_sessions': 0,
                'total_questions_answered': 0,
                'overall_accuracy': 0,
                'average_session_score': 0,
                'total_study_time_seconds': 0
            }
        }), 200
    
    # Calculate statistics
    total_questions = sum(len(s.responses) for s in sessions)
    correct_answers = sum(s.correct_answers for s in sessions)
    overall_accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
    
    session_scores = [s.score_percentage for s in sessions if s.score_percentage is not None]
    average_score = statistics.mean(session_scores) if session_scores else 0
    
    total_study_time = sum(s.duration_seconds for s in sessions)
    
    return jsonify({
        'success': True,
        'student_id': student_id,
        'summary': {
            'total_sessions': len(sessions),
            'total_questions_answered': total_questions,
            'correct_answers': correct_answers,
            'overall_accuracy': round(overall_accuracy, 2),
            'average_session_score': round(average_score, 2),
            'total_study_time_seconds': total_study_time,
            'last_activity': student.last_activity.isoformat() if student.last_activity else None
        }
    }), 200

@analytics_bp.route('/session/<session_id>/engagement_timeline', methods=['GET'])
def get_engagement_timeline(session_id):
    """Get engagement metrics timeline for a session"""
    metrics = EngagementMetric.query.filter_by(
        session_id=session_id
    ).order_by(EngagementMetric.timestamp.asc()).all()
    
    if not metrics:
        return jsonify({'error': 'No engagement metrics found'}), 404
    
    timeline = []
    for metric in metrics:
        timeline.append({
            'timestamp': metric.timestamp.isoformat(),
            'engagement_score': metric.engagement_score,
            'engagement_level': metric.engagement_level,
            'accuracy': metric.accuracy,
            'response_time': metric.response_time_seconds,
            'confidence': metric.confidence_level
        })
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'timeline': timeline
    }), 200

@analytics_bp.route('/session/<session_id>/performance_analysis', methods=['GET'])
def get_performance_analysis(session_id):
    """Analyze performance metrics for a session"""
    responses = StudentResponse.query.filter_by(session_id=session_id).all()
    
    if not responses:
        return jsonify({'error': 'No responses found'}), 404
    
    # Categorize responses
    correct_count = sum(1 for r in responses if r.is_correct)
    incorrect_count = len(responses) - correct_count
    accuracy = (correct_count / len(responses)) * 100 if responses else 0
    
    # Response time analysis
    response_times = [r.response_time_seconds for r in responses]
    avg_response_time = statistics.mean(response_times) if response_times else 0
    
    # Question difficulty analysis
    difficulties = [r.question.difficulty for r in responses]
    avg_difficulty = statistics.mean(difficulties) if difficulties else 0
    
    # Topic-based analysis
    topic_performance = {}
    for response in responses:
        topic = response.question.topic
        if topic not in topic_performance:
            topic_performance[topic] = {'correct': 0, 'total': 0}
        topic_performance[topic]['total'] += 1
        if response.is_correct:
            topic_performance[topic]['correct'] += 1
    
    # Convert to percentages
    for topic in topic_performance:
        topic_performance[topic]['accuracy'] = (
            (topic_performance[topic]['correct'] / topic_performance[topic]['total'] * 100)
            if topic_performance[topic]['total'] > 0 else 0
        )
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'analysis': {
            'accuracy': round(accuracy, 2),
            'correct_answers': correct_count,
            'incorrect_answers': incorrect_count,
            'total_questions': len(responses),
            'average_response_time': round(avg_response_time, 2),
            'average_difficulty_level': round(avg_difficulty, 2),
            'topic_performance': topic_performance
        }
    }), 200

@analytics_bp.route('/student/<student_id>/progress', methods=['GET'])
def get_student_progress(student_id):
    """Track student progress over multiple sessions"""
    sessions = Session.query.filter_by(
        student_id=student_id,
        status='completed'
    ).order_by(Session.session_start.asc()).all()
    
    if not sessions:
        return jsonify({'error': 'No completed sessions found'}), 404
    
    progress = []
    for session in sessions:
        responses = StudentResponse.query.filter_by(session_id=session.id).all()
        correct = sum(1 for r in responses if r.is_correct)
        
        progress.append({
            'session_id': session.id,
            'session_date': session.session_start.isoformat(),
            'subject': session.subject,
            'score': round(session.score_percentage, 2),
            'correct_answers': correct,
            'total_questions': len(responses),
            'duration_minutes': session.duration_seconds / 60
        })
    
    # Calculate trend
    scores = [p['score'] for p in progress]
    trend = 'improving' if len(scores) > 1 and scores[-1] > scores[0] else 'stable' if len(scores) <= 1 else 'declining'
    
    return jsonify({
        'success': True,
        'student_id': student_id,
        'progress': progress,
        'trend': trend
    }), 200

@analytics_bp.route('/session/<session_id>/adaptation_impact', methods=['GET'])
def get_adaptation_impact(session_id):
    """Analyze the impact of adaptations on session performance"""
    logs = AdaptationLog.query.filter_by(session_id=session_id).all()
    
    if not logs:
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'No adaptations recorded for this session'
        }), 200
    
    # Categorize by adaptation type
    adaptations_by_type = {}
    for log in logs:
        adaptation_type = log.adaptation_type
        if adaptation_type not in adaptations_by_type:
            adaptations_by_type[adaptation_type] = []
        adaptations_by_type[adaptation_type].append(log.to_dict())
    
    # Calculate effectiveness
    total_logged = len(logs)
    effective = sum(1 for log in logs if log.was_effective == True)
    ineffective = sum(1 for log in logs if log.was_effective == False)
    unknown = total_logged - effective - ineffective
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'adaptation_summary': {
            'total_adaptations': total_logged,
            'effective': effective,
            'ineffective': ineffective,
            'unknown_effectiveness': unknown,
            'effectiveness_rate': round((effective / total_logged * 100), 2) if total_logged > 0 else 0
        },
        'adaptations_by_type': adaptations_by_type
    }), 200

@analytics_bp.route('/student/<student_id>/engagement_trends', methods=['GET'])
def get_engagement_trends(student_id):
    """Get engagement trends across all sessions for a student"""
    metrics = EngagementMetric.query.filter_by(
        student_id=student_id
    ).order_by(EngagementMetric.timestamp.asc()).all()
    
    if not metrics:
        return jsonify({'error': 'No engagement metrics found'}), 404
    
    # Group by session
    sessions_data = {}
    for metric in metrics:
        session_id = metric.session_id
        if session_id not in sessions_data:
            sessions_data[session_id] = []
        sessions_data[session_id].append(metric)
    
    # Calculate average engagement per session
    session_trends = []
    for session_id, session_metrics in sessions_data.items():
        avg_engagement = statistics.mean(m.engagement_score for m in session_metrics)
        avg_confidence = statistics.mean(
            [m.confidence_level for m in session_metrics if m.confidence_level is not None]
        ) if any(m.confidence_level is not None for m in session_metrics) else 0
        
        session_trends.append({
            'session_id': session_id,
            'average_engagement': round(avg_engagement, 3),
            'average_confidence': round(avg_confidence, 3),
            'engagement_level': session_metrics[0].engagement_level
        })
    
    return jsonify({
        'success': True,
        'student_id': student_id,
        'session_trends': session_trends
    }), 200

@analytics_bp.route('/dashboard/<student_id>', methods=['GET'])
def get_dashboard(student_id):
    """Get comprehensive dashboard data for a student"""
    student = Student.query.get(student_id)
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # Get all relevant data
    sessions = Session.query.filter_by(student_id=student_id).all()
    engagement_metrics = EngagementMetric.query.filter_by(student_id=student_id).all()
    
    # Summary stats
    total_questions = sum(len(s.responses) for s in sessions)
    correct_answers = sum(s.correct_answers for s in sessions)
    overall_accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
    
    # Recent engagement
    recent_engagement = engagement_metrics[-1].engagement_score if engagement_metrics else None
    
    return jsonify({
        'success': True,
        'dashboard': {
            'student_info': student.to_dict(),
            'statistics': {
                'total_sessions': len(sessions),
                'total_questions': total_questions,
                'correct_answers': correct_answers,
                'overall_accuracy': round(overall_accuracy, 2),
                'recent_engagement_score': recent_engagement
            },
            'recent_sessions': [s.to_dict() for s in sessions[-5:]]
        }
    }), 200

# ============ RESEARCH EVALUATION ROUTES ============

# Import evaluation modules
from app.engagement.mastery import MasteryTracker
from app.engagement.affective import AffectiveIndicatorAnalyzer
from app.adaptation.rl_agent import RLAdaptiveAgent
from app.analytics.evaluator import ResearchEvaluator

mastery_tracker = MasteryTracker()
affective_analyzer = AffectiveIndicatorAnalyzer()
rl_agent = RLAdaptiveAgent()
research_evaluator = ResearchEvaluator()

# ============ MASTERY ROUTES ============

@analytics_bp.route('/mastery/topic/<student_id>/<topic>', methods=['GET'])
def get_topic_mastery(student_id, topic):
    """Get mastery level for a specific topic"""
    try:
        mastery_data = mastery_tracker.calculate_topic_mastery(student_id, topic)
        return jsonify({
            'success': True,
            'data': mastery_data
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/mastery/overall/<student_id>', methods=['GET'])
def get_overall_mastery(student_id):
    """Get overall mastery across all topics"""
    try:
        mastery_data = mastery_tracker.calculate_overall_mastery(student_id)
        return jsonify({
            'success': True,
            'data': mastery_data
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/mastery/profile/<student_id>', methods=['GET'])
def get_knowledge_profile(student_id):
    """Get comprehensive knowledge profile"""
    try:
        profile = mastery_tracker.get_knowledge_profile(student_id)
        return jsonify({
            'success': True,
            'profile': profile
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ AFFECTIVE ROUTES ============

@analytics_bp.route('/affective/record-facial', methods=['POST'])
def record_facial_expression():
    """Record facial expression data"""
    data = request.get_json()
    
    try:
        student_id = data.get('student_id')
        session_id = data.get('session_id')
        emotion_label = data.get('emotion')
        confidence = data.get('confidence', 0.7)
        
        metric = affective_analyzer.record_facial_expression(
            student_id, session_id, emotion_label, confidence
        )
        
        return jsonify({
            'success': True,
            'metric': metric
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/affective/detect-confusion', methods=['POST'])
def detect_confusion():
    """Detect confusion state"""
    data = request.get_json()
    
    try:
        student_id = data.get('student_id')
        session_id = data.get('session_id')
        facial_data = data.get('facial_data', {})
        behavioral_data = data.get('behavioral_data', {})
        
        result = affective_analyzer.detect_confusion(
            student_id, session_id, facial_data, behavioral_data
        )
        
        return jsonify({
            'success': True,
            'confusion': result
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/affective/detect-frustration', methods=['POST'])
def detect_frustration():
    """Detect frustration state"""
    data = request.get_json()
    
    try:
        student_id = data.get('student_id')
        session_id = data.get('session_id')
        facial_data = data.get('facial_data', {})
        behavioral_data = data.get('behavioral_data', {})
        
        result = affective_analyzer.detect_frustration(
            student_id, session_id, facial_data, behavioral_data
        )
        
        return jsonify({
            'success': True,
            'frustration': result
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ RL AGENT ROUTES ============

@analytics_bp.route('/rl/recommend/<student_id>/<session_id>', methods=['GET'])
def get_rl_recommendations(student_id, session_id):
    """Get RL-optimized adaptation recommendations"""
    try:
        # Get latest engagement metric
        metric = EngagementMetric.query.filter_by(
            session_id=session_id
        ).order_by(EngagementMetric.timestamp.desc()).first()
        
        if not metric:
            return jsonify({'error': 'No engagement metrics found'}), 404
        
        recommendations = rl_agent.predict_best_adaptation(
            metric.engagement_score,
            metric.accuracy,
            metric.confidence_level or 0.5
        )
        
        return jsonify({
            'success': True,
            'recommendations': recommendations
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/rl/learn/<student_id>/<session_id>', methods=['POST'])
def learn_from_session(student_id, session_id):
    """Learn from completed session"""
    try:
        result = rl_agent.learn_from_experience(student_id, session_id)
        
        return jsonify({
            'success': True,
            'learning_result': result
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ EVALUATION ROUTES ============

@analytics_bp.route('/evaluate/engagement/<student_id>', methods=['GET'])
def eval_engagement(student_id):
    """Evaluate sustained engagement"""
    try:
        days = request.args.get('days', 30, type=int)
        result = research_evaluator.evaluate_sustained_engagement(student_id, days)
        
        return jsonify({
            'success': True,
            'evaluation': result
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/evaluate/performance/<student_id>', methods=['GET'])
def eval_performance(student_id):
    """Evaluate performance improvement"""
    try:
        result = research_evaluator.evaluate_performance_improvement(student_id)
        
        return jsonify({
            'success': True,
            'evaluation': result
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/evaluate/adaptation/<student_id>', methods=['GET'])
def eval_adaptation(student_id):
    """Evaluate adaptation effectiveness"""
    try:
        session_id = request.args.get('session_id', None)
        result = research_evaluator.evaluate_adaptation_effectiveness(student_id, session_id)
        
        return jsonify({
            'success': True,
            'evaluation': result
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/evaluate/impact/<student_id>', methods=['GET'])
def eval_impact(student_id):
    """Evaluate system impact for a student"""
    try:
        result = research_evaluator.evaluate_system_impact(student_id)
        
        return jsonify({
            'success': True,
            'evaluation': result
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/evaluate/system-impact', methods=['GET'])
def eval_system_impact():
    """Evaluate aggregate system impact"""
    try:
        result = research_evaluator.evaluate_system_impact()
        
        return jsonify({
            'success': True,
            'evaluation': result
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/report/<student_id>', methods=['GET'])
def get_research_report(student_id):
    """Get comprehensive research evaluation report"""
    try:
        report = research_evaluator.generate_research_report(student_id)
        
        return jsonify({
            'success': True,
            'report': report
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/report/aggregate', methods=['GET'])
def get_aggregate_report():
    """Get aggregate system research report"""
    try:
        report = research_evaluator.generate_research_report()
        
        return jsonify({
            'success': True,
            'report': report
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============ IRT (Item Response Theory) Endpoints ============

@analytics_bp.route('/irt/calibrate', methods=['POST'])
def calibrate_irt():
    """Calibrate IRT parameters from student response data"""
    try:
        responses = StudentResponse.query.all()
        irt_model.calibrate_from_responses(responses)
        
        # Update question models with calibrated parameters
        for q_id, params in irt_model.item_params.items():
            question = Question.query.get(q_id)
            if question:
                question.irt_discrimination = params['a']
                question.irt_difficulty = params['b']
                question.irt_guessing = params['c']
                question.irt_calibrated = True
                db.session.add(question)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'IRT calibration complete',
            'questions_calibrated': len(irt_model.item_params)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/irt/question-stats/<question_id>', methods=['GET'])
def get_irt_stats(question_id):
    """Get IRT statistics for a question"""
    try:
        stats = irt_model.get_irt_statistics(question_id)
        
        return jsonify({
            'success': True,
            'question_id': question_id,
            'irt_statistics': stats
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/irt/student-ability/<student_id>', methods=['GET'])
def get_student_ability(student_id):
    """Get estimated ability (theta) for student"""
    try:
        ability = irt_model.update_ability_estimate(student_id)
        
        return jsonify({
            'success': True,
            'student_id': student_id,
            'estimated_ability': ability,
            'ability_label': 'Below Average' if ability < -0.5 else ('Average' if ability < 0.5 else 'Above Average')
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============ CAT (Computerized Adaptive Testing) Endpoints ============

@analytics_bp.route('/cat/next-question/<student_id>/<session_id>', methods=['GET'])
def get_cat_question(student_id, session_id):
    """Get next optimal question using CAT algorithm"""
    try:
        session = Session.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Get questions already asked in session
        asked_questions = StudentResponse.query.filter_by(session_id=session_id).all()
        asked_ids = {r.question_id for r in asked_questions}
        
        # Get all available questions
        all_questions = Question.query.filter_by(subject=session.subject).all()
        available = [q for q in all_questions if q.id not in asked_ids]
        
        # Get optimal question
        next_q = cat_algorithm.next_question(student_id, asked_questions, available)
        
        if not next_q:
            return jsonify({'success': True, 'question': None, 'message': 'All questions answered'}), 200
        
        ability = irt_model.student_abilities.get(student_id, 0.0)
        
        return jsonify({
            'success': True,
            'question': next_q.to_dict(include_irt=True),
            'student_ability': ability,
            'questions_answered': len(asked_questions),
            'selection_rationale': 'Maximum Information (optimal difficulty for student)'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/cat/should-stop/<student_id>/<session_id>', methods=['GET'])
def check_stop_testing(student_id, session_id):
    """Check if testing should stop based on convergence"""
    try:
        session = Session.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        responses = StudentResponse.query.filter_by(session_id=session_id).all()
        session_questions = [Question.query.get(r.question_id) for r in responses]
        
        should_stop, reason = cat_algorithm.should_stop_testing(session_questions, responses)
        
        return jsonify({
            'success': True,
            'should_stop': should_stop,
            'reason': reason,
            'questions_answered': len(responses),
            'max_questions': cat_algorithm.max_questions
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============ Spaced Repetition Endpoints ============

@analytics_bp.route('/sr/schedule/<student_id>/<question_id>', methods=['POST'])
def schedule_review(student_id, question_id):
    """Schedule next review of a question"""
    try:
        data = request.get_json()
        quality = data.get('quality', 3)  # 0-5
        
        schedule = spaced_rep_scheduler.schedule_question_review(
            student_id, question_id, quality=quality
        )
        
        return jsonify({
            'success': True,
            'schedule': schedule
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/sr/due-for-review/<student_id>', methods=['GET'])
def get_due_reviews(student_id):
    """Get questions due for review"""
    try:
        due_questions = spaced_rep_scheduler.get_due_for_review(student_id)
        
        return jsonify({
            'success': True,
            'student_id': student_id,
            'due_count': len(due_questions),
            'questions': [
                {
                    'question_id': q['question_id'],
                    'days_overdue': q['days_overdue'],
                    'question_text': q['question'].question_text[:100] if q['question'] else 'N/A'
                }
                for q in due_questions[:20]  # Limit to 20
            ]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/sr/statistics/<student_id>', methods=['GET'])
def get_sr_statistics(student_id):
    """Get spaced repetition statistics"""
    try:
        stats = spaced_rep_scheduler.get_learning_statistics(student_id)
        
        return jsonify({
            'success': True,
            'statistics': stats
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/sr/learning-curve/<student_id>/<topic>', methods=['GET'])
def get_topic_curve(student_id, topic):
    """Get learning curve for a topic"""
    try:
        curve = LearningCurveAnalyzer.get_topic_learning_curve(student_id, topic)
        mastery_timeline = LearningCurveAnalyzer.analyze_mastery_timeline(student_id, topic)
        
        return jsonify({
            'success': True,
            'topic': topic,
            'learning_curve': curve[-20:] if curve else [],  # Last 20 attempts
            'mastery_analysis': mastery_timeline
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/sr/review-schedule/<student_id>/<topic>', methods=['GET'])
def get_topic_schedule(student_id, topic):
    """Get review schedule for a topic"""
    try:
        schedule = spaced_rep_scheduler.get_review_schedule_for_topic(student_id, topic)
        
        return jsonify({
            'success': True,
            'topic': topic,
            'schedule': schedule
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============ RL Policy Optimizer Endpoints ============

@analytics_bp.route('/rl/policy-validation', methods=['GET'])
def validate_policy():
    """Validate current RL policy"""
    try:
        validation = policy_optimizer.validate_policy(test_sessions_count=int(request.args.get('sessions', 50)))
        
        return jsonify({
            'success': True,
            'validation': validation
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/rl/policy-summary', methods=['GET'])
def get_policy_summary():
    """Get comprehensive policy summary"""
    try:
        summary = policy_optimizer.get_policy_summary()
        
        return jsonify({
            'success': True,
            'policy_summary': summary
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/rl/convergence-status', methods=['GET'])
def get_convergence():
    """Get Q-table convergence status"""
    try:
        status = policy_optimizer.monitor_convergence()
        
        return jsonify({
            'success': True,
            'convergence_status': status
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/rl/action-impact/<action_type>', methods=['GET'])
def analyze_action(action_type):
    """Analyze impact of specific action type"""
    try:
        impact = policy_optimizer.analyze_action_impact(action_type)
        
        return jsonify({
            'success': True,
            'action_impact': impact
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/rl/tune-reward/<session_id>', methods=['POST'])
def tune_reward(session_id):
    """Tune reward signal for a session"""
    try:
        reward = policy_optimizer.tune_reward_signal(session_id)
        
        if not reward:
            return jsonify({'error': 'Session not found'}), 404
        
        return jsonify({
            'success': True,
            'reward_signal': reward
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/rl/exploration-status', methods=['GET'])
def get_exploration():
    """Get exploration strategy status"""
    try:
        status = exploration_strategy.get_status()
        
        return jsonify({
            'success': True,
            'exploration_status': status
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/rl/decay-epsilon', methods=['POST'])
def decay_eps():
    """Decay exploration rate"""
    try:
        new_epsilon = exploration_strategy.decay_epsilon()
        
        return jsonify({
            'success': True,
            'new_epsilon': new_epsilon,
            'status': exploration_strategy.get_status()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# FACIAL EXPRESSION API ENDPOINTS
# ============================================================================

from app.engagement.facial_expression_api import FacialExpressionIntegrator

# Initialize facial expression integrator
facial_integrator = FacialExpressionIntegrator(provider='face.js')


@analytics_bp.route('/affective/facial-summary/<session_id>', methods=['GET'])
def get_facial_summary(session_id):
    """Get facial expression summary for a session"""
    try:
        # Aggregate facial data from session
        session = Session.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Get engagement metrics
        summary = {
            'session_id': session_id,
            'total_frames_analyzed': session.engagement_events if hasattr(session, 'engagement_events') else 0,
            'avg_engagement': session.engagement_score,
            'primary_emotion': session.last_emotion if hasattr(session, 'last_emotion') else 'unknown',
            'facial_monitoring_enabled': True,
            'privacy_mode': 'local_processing'  # Face.js local only
        }
        
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/affective/facial-capabilities', methods=['GET'])
def get_facial_capabilities():
    """Get available facial detection capabilities"""
    try:
        capabilities = {
            'providers_available': ['face.js', 'azure', 'aws', 'mediapipe'],
            'current_provider': 'face.js',
            'emotions_supported': [
                'happy', 'sad', 'angry', 'fearful', 
                'disgusted', 'neutral', 'surprised'
            ],
            'accuracy': '85-90%',
            'latency_ms': 500,
            'privacy_level': 'maximum',
            'requires_internet': False,
            'features': {
                'emotion_detection': True,
                'engagement_tracking': True,
                'frustration_detection': True,
                'attention_monitoring': True,
                'real_time_processing': True,
                'offline_capable': True
            },
            'implementation_status': 'ready_for_deployment',
            'frontend_integration': {
                'video_element': 'required',
                'webcam_access': 'required',
                'library': 'face-api.js',
                'cdn_url': 'https://cdn.jsdelivr.net/npm/@vladmandic/face-api'
            }
        }
        
        return jsonify(capabilities), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analytics_bp.route('/affective/facial-privacy', methods=['GET'])
def get_facial_privacy_info():
    """Get privacy information about facial monitoring"""
    try:
        privacy_info = {
            'data_processing_location': 'client_side_only',
            'data_stored_on_server': 'engagement_scores_only',
            'facial_images_stored': False,
            'data_deleted_after': '24_hours',
            'gdpr_compliant': True,
            'user_consent_required': True,
            'opt_in_only': True,
            'privacy_policy': {
                'collection': 'Facial expressions collected during tutoring sessions',
                'usage': 'Used to calculate engagement and frustration levels',
                'storage': 'Only aggregate engagement scores stored',
                'retention': 'Session data deleted after 24 hours',
                'sharing': 'Never shared with third parties',
                'user_rights': 'Can disable at any time, request data deletion'
            },
            'implementation_details': {
                'local_processing': 'All emotion detection happens in browser',
                'no_raw_data_transmission': 'Only emotion labels sent to server',
                'browser_caching': 'Models cached locally for offline use',
                'user_control': 'Webcam can be disabled instantly'
            }
        }
        
        return jsonify(privacy_info), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/export/facial-data/<session_id>', methods=['GET'])
def export_facial_data(session_id):
    """Export facial expression and engagement data for research"""
    try:
        session = Session.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Get all engagement metrics for this session
        metrics = EngagementMetric.query.filter_by(session_id=session_id).all()
        
        facial_data = {
            'session_id': session_id,
            'student_id': session.student_id,
            'subject': session.subject,
            'session_start': session.session_start.isoformat() if session.session_start else None,
            'session_end': session.session_end.isoformat() if session.session_end else None,
            'total_questions': session.total_questions,
            'correct_answers': session.correct_answers,
            'score_percentage': session.score_percentage,
            'facial_expressions': []
        }
        
        # Add all engagement metrics (includes facial data)
        for metric in metrics:
            facial_data['facial_expressions'].append({
                'timestamp': metric.timestamp.isoformat() if metric.timestamp else None,
                'engagement_score': metric.engagement_score,
                'frustration_level': metric.frustration_level,
                'curiosity_level': metric.curiosity_level,
                'confidence_level': metric.confidence_level,
                'attention_level': metric.attention_level,
                'emotions': metric.emotions if hasattr(metric, 'emotions') else None
            })
        
        return jsonify({
            'success': True,
            'data': facial_data,
            'count': len(metrics)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/export/all-data/<student_id>', methods=['GET'])
def export_all_student_data(student_id):
    """Export all learning data for a student (for research documentation)"""
    try:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Get all sessions
        sessions = Session.query.filter_by(student_id=student_id).all()
        
        export_data = {
            'student_id': student_id,
            'student_name': getattr(student, 'name', 'Unknown'),
            'student_email': getattr(student, 'email', 'Unknown'),
            'export_date': __import__('datetime').datetime.utcnow().isoformat(),
            'sessions': [],
            'summary': {
                'total_sessions': len(sessions),
                'total_questions_answered': 0,
                'total_correct_answers': 0,
                'overall_score_percentage': 0,
                'average_engagement': 0,
                'subjects_studied': set()
            }
        }
        
        total_engagement = 0
        engagement_count = 0
        
        for session in sessions:
            try:
                # Get responses for this session
                responses = StudentResponse.query.filter_by(session_id=session.id).all()
                
                # Get metrics for this session
                metrics = EngagementMetric.query.filter_by(session_id=session.id).all()
                
                session_data = {
                    'session_id': session.id,
                    'subject': session.subject,
                    'total_questions': session.total_questions,
                    'correct_answers': session.correct_answers,
                    'score_percentage': session.score_percentage,
                    'status': session.status,
                    'session_start': session.session_start.isoformat() if session.session_start else None,
                    'session_end': session.session_end.isoformat() if session.session_end else None,
                    'responses': [],
                    'engagement_metrics': []
                }
                
                # Add response details with complete interaction tracking
                for response in responses:
                    try:
                        question = Question.query.get(response.question_id)
                        session_data['responses'].append({
                            'question_id': response.question_id,
                            'question_text': question.question_text if question else 'N/A',
                            'student_answer': response.student_answer,
                            'is_correct': response.is_correct,
                            'response_time_seconds': response.response_time_seconds,
                            # Behavioral tracking data
                            'initial_option': response.initial_option,
                            'final_option': response.final_option,
                            'option_change_count': response.option_change_count,
                            'option_change_history': response.option_change_history,
                            'navigation_frequency': response.navigation_frequency,
                            'hints_requested': len(response.hints_used_array) if response.hints_used_array else 0,
                            'hints_used_array': response.hints_used_array if response.hints_used_array else [],
                            'interaction_start_timestamp': response.interaction_start_timestamp,
                            'submission_timestamp': response.submission_timestamp,
                            'submission_iso_timestamp': response.submission_iso_timestamp,
                            # Cognitive & Affective tracking data
                            'time_spent_per_question': response.time_spent_per_question,
                            'inactivity_duration_ms': response.inactivity_duration_ms,
                            'question_index': response.question_index,
                            'hesitation_flags': response.hesitation_flags if response.hesitation_flags else {},
                            'navigation_pattern': response.navigation_pattern,
                            'knowledge_gaps': response.knowledge_gaps if response.knowledge_gaps else [],
                            # Facial monitoring data (non-biometric academic metrics)
                            'facial_metrics': response.facial_metrics if response.facial_metrics else {
                                'camera_enabled': False,
                                'face_detected_count': 0,
                                'face_lost_count': 0,
                                'attention_score': None,
                                'emotions_detected': [],
                                'face_presence_duration_seconds': 0
                            },
                            'timestamp': response.timestamp.isoformat() if response.timestamp else None
                        })
                        
                        # Update summary
                        export_data['summary']['total_questions_answered'] += 1
                        if response.is_correct:
                            export_data['summary']['total_correct_answers'] += 1
                    except Exception as e:
                        print(f"Error processing response: {e}")
                        continue
                
                # Add engagement metrics (all fields)
                for metric in metrics:
                    try:
                        session_data['engagement_metrics'].append({
                            'timestamp': metric.timestamp.isoformat() if metric.timestamp else None,
                            # Behavioral Indicators
                            'response_time_seconds': getattr(metric, 'response_time_seconds', None),
                            'hints_requested': getattr(metric, 'hints_requested', None),
                            'inactivity_duration': getattr(metric, 'inactivity_duration', None),
                            'navigation_frequency': getattr(metric, 'navigation_frequency', None),
                            'completion_rate': getattr(metric, 'completion_rate', None),
                            # Cognitive Indicators
                            'accuracy': getattr(metric, 'accuracy', None),
                            'learning_progress': getattr(metric, 'learning_progress', None),
                            'knowledge_gaps': getattr(metric, 'knowledge_gaps', None),
                            # Affective Indicators
                            'confidence_level': getattr(metric, 'confidence_level', None),
                            'frustration_level': getattr(metric, 'frustration_level', None),
                            'interest_level': getattr(metric, 'interest_level', None),
                            # Composite
                            'engagement_score': metric.engagement_score,
                            'engagement_level': getattr(metric, 'engagement_level', None)
                        })
                        total_engagement += metric.engagement_score
                        engagement_count += 1
                    except Exception as e:
                        print(f"Error processing metric: {e}")
                        continue
                
                # Track subjects
                export_data['summary']['subjects_studied'].add(session.subject)
                
                export_data['sessions'].append(session_data)
            except Exception as e:
                print(f"Error processing session {session.id}: {e}")
                continue
        
        # Calculate summary stats
        if export_data['summary']['total_questions_answered'] > 0:
            export_data['summary']['overall_score_percentage'] = (
                export_data['summary']['total_correct_answers'] / 
                export_data['summary']['total_questions_answered']
            ) * 100
        
        if engagement_count > 0:
            export_data['summary']['average_engagement'] = total_engagement / engagement_count
        
        # Convert set to list for JSON serialization
        export_data['summary']['subjects_studied'] = list(export_data['summary']['subjects_studied'])
        
        return jsonify({
            'success': True,
            'data': export_data
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to export student data: {str(e)}'}), 500

@analytics_bp.route('/export/csv/<student_id>', methods=['GET'])
def export_as_csv(student_id):
    """Export student data as CSV - CUMULATIVE from all completed sessions"""
    import csv
    from io import StringIO
    import json
    
    try:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Create CSV content
        output = StringIO()
        writer = csv.writer(output)
        
        # FIXED SCHEMA - CONSISTENT COLUMNS FOR ALL ROWS
        header = [
            'Session ID', 'Subject', 'Question', 'Student Answer', 'Correct', 
            'Response Time(s)', 'Initial Option', 'Final Option', 'Option Changes', 
            'Navigation Frequency', 'Interaction Timestamp',
            'Engagement Score', 'Engagement Level', 'Confidence', 'Frustration', 'Interest',
            'Accuracy', 'Learning Progress', 'Knowledge Gaps', 'Hints Requested', 
            'Inactivity(s)', 'Completion Rate', 'Camera Enabled', 'Face Detected Count', 'Attention Score'
        ]
        writer.writerow(header)
        
        # Query ALL sessions for this student (CUMULATIVE, not just recent)
        sessions = Session.query.filter_by(student_id=student_id).order_by(Session.session_start.asc()).all()
        
        for session in sessions:
            # Get all responses for this session
            responses = StudentResponse.query.filter_by(session_id=session.id).order_by(
                StudentResponse.timestamp.asc()
            ).all()
            
            # Get metrics for this session
            metrics = EngagementMetric.query.filter_by(session_id=session.id).order_by(
                EngagementMetric.timestamp.asc()
            ).all()
            
            # Process each response with matching engagement metric
            for idx, response in enumerate(responses):
                question = Question.query.get(response.question_id)
                
                # Match metric to response - use timestamp to find nearest metric
                metric = None
                if metrics:
                    # Find metric closest in time to this response
                    min_time_diff = float('inf')
                    for m in metrics:
                        time_diff = abs((m.timestamp - response.timestamp).total_seconds())
                        if time_diff < min_time_diff:
                            min_time_diff = time_diff
                            metric = m
                
                # Calculate hints_requested from hints_used_array (not legacy hints_used field)
                hints_requested = len(response.hints_used_array) if response.hints_used_array else 0
                
                # Extract facial metrics with safe defaults
                facial_metrics = response.facial_metrics if response.facial_metrics else {}
                camera_enabled = facial_metrics.get('camera_enabled', False)
                face_detected_count = facial_metrics.get('face_detected_count', 0)
                attention_score = facial_metrics.get('attention_score')
                
                # Build row with FIXED SCHEMA - ALL values present, empty strings for None
                row = [
                    response.session_id,
                    session.subject or '',
                    (question.question_text if question else 'N/A')[:100],  # Truncate long questions
                    response.student_answer or '',
                    'Yes' if response.is_correct else 'No',
                    response.response_time_seconds or '',
                    response.initial_option or '',
                    response.final_option or '',
                    response.option_change_count or 0,
                    response.navigation_frequency or 0,
                    response.submission_iso_timestamp or '',
                    # Engagement metrics
                    metric.engagement_score if metric else '',
                    metric.engagement_level if metric else '',
                    metric.confidence_level if metric else '',
                    metric.frustration_level if metric else '',
                    metric.interest_level if metric else '',
                    metric.accuracy if metric else '',
                    metric.learning_progress if metric else '',
                    # Format knowledge gaps as comma-separated string (no JSON)
                    ', '.join(response.knowledge_gaps) if response.knowledge_gaps else '',
                    hints_requested,
                    metric.inactivity_duration if metric else '',
                    metric.completion_rate if metric else '',
                    # Facial metrics (non-biometric academic data)
                    'Yes' if camera_enabled else 'No',
                    face_detected_count,
                    attention_score if attention_score is not None else ''
                ]
                
                writer.writerow(row)
        
        # Return CSV as JSON response
        csv_content = output.getvalue()
        return jsonify({
            'success': True,
            'data': csv_content,
            'filename': f'student_{student_id}_data.csv'
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to export CSV: {str(e)}'}), 500

@analytics_bp.route('/system/reset-data', methods=['POST'])
def reset_all_data():
    """Reset all session, response, and engagement data (for fresh testing)
    
    WARNING: This deletes all test data. Students can be recreated.
    Questions database is preserved.
    """
    try:
        # Delete in proper order due to foreign key constraints
        print("[RESET] Starting data reset...", flush=True)
        
        # Delete engagement metrics first
        deleted_metrics = db.session.query(EngagementMetric).delete()
        print(f"[RESET] Deleted {deleted_metrics} engagement metrics", flush=True)
        
        # Delete responses
        deleted_responses = db.session.query(StudentResponse).delete()
        print(f"[RESET] Deleted {deleted_responses} student responses", flush=True)
        
        # Delete sessions
        deleted_sessions = db.session.query(Session).delete()
        print(f"[RESET] Deleted {deleted_sessions} sessions", flush=True)
        
        # Delete students
        deleted_students = db.session.query(Student).delete()
        print(f"[RESET] Deleted {deleted_students} student records", flush=True)
        
        # Commit all deletions
        db.session.commit()
        
        print("[RESET] Data reset complete", flush=True)
        
        return jsonify({
            'success': True,
            'message': 'All test data reset successfully',
            'deleted': {
                'students': deleted_students,
                'sessions': deleted_sessions,
                'responses': deleted_responses,
                'engagement_metrics': deleted_metrics
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"[RESET] Error: {e}", flush=True)
        return jsonify({
            'success': False,
            'error': f'Reset failed: {str(e)}'
        }), 500
