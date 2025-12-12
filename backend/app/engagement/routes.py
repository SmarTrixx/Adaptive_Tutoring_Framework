from flask import Blueprint, request, jsonify
from app import db
from app.engagement.tracker import EngagementIndicatorTracker
from app.models.engagement import EngagementMetric
from app.models.session import Session, StudentResponse

engagement_bp = Blueprint('engagement', __name__)
tracker = EngagementIndicatorTracker()

@engagement_bp.route('/track', methods=['POST'])
def track_engagement():
    """
    Track and record engagement metrics for a student response
    """
    data = request.get_json()
    
    session_id = data.get('session_id')
    student_id = data.get('student_id')
    response_data = data.get('response_data', {})
    affective_feedback = data.get('affective_feedback', {})
    
    if not session_id or not student_id:
        return jsonify({'error': 'Missing session_id or student_id'}), 400
    
    try:
        # Track behavioral indicators
        behavioral = tracker.track_behavioral_indicators(session_id, response_data)
        
        # Track cognitive indicators
        cognitive = tracker.track_cognitive_indicators(session_id)
        
        # Track affective indicators
        affective = tracker.track_affective_indicators(session_id, affective_feedback)
        
        # Calculate composite engagement score
        engagement_score = tracker.calculate_composite_engagement_score(
            behavioral, cognitive, affective
        )
        engagement_level = tracker.determine_engagement_level(engagement_score)
        
        # Save engagement metric to database
        metric = EngagementMetric(
            student_id=student_id,
            session_id=session_id,
            response_time_seconds=behavioral.get('response_time_seconds'),
            attempts_count=behavioral.get('attempts_count', 0),
            hints_requested=behavioral.get('hints_requested', 0),
            inactivity_duration=behavioral.get('inactivity_duration', 0),
            navigation_frequency=behavioral.get('navigation_frequency', 0),
            completion_rate=behavioral.get('completion_rate', 0),
            accuracy=cognitive.get('accuracy', 0),
            learning_progress=cognitive.get('learning_progress', 0),
            knowledge_gaps=cognitive.get('knowledge_gaps', []),
            confidence_level=affective.get('confidence_level'),
            frustration_level=affective.get('frustration_level'),
            interest_level=affective.get('interest_level'),
            engagement_score=engagement_score,
            engagement_level=engagement_level
        )
        
        db.session.add(metric)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'metric_id': metric.id,
            'engagement_score': engagement_score,
            'engagement_level': engagement_level,
            'behavioral': behavioral,
            'cognitive': cognitive,
            'affective': affective
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@engagement_bp.route('/session/<session_id>', methods=['GET'])
def get_session_engagement(session_id):
    """Get all engagement metrics for a session"""
    try:
        metrics = EngagementMetric.query.filter_by(session_id=session_id).all()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'metric_count': len(metrics),
            'metrics': [m.to_dict() for m in metrics]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@engagement_bp.route('/student/<student_id>/latest', methods=['GET'])
def get_latest_engagement(student_id):
    """Get the latest engagement metric for a student"""
    try:
        metric = EngagementMetric.query.filter_by(
            student_id=student_id
        ).order_by(EngagementMetric.timestamp.desc()).first()
        
        if not metric:
            return jsonify({'error': 'No engagement metrics found'}), 404
        
        return jsonify({
            'success': True,
            'metric': metric.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@engagement_bp.route('/statistics/<session_id>', methods=['GET'])
def get_engagement_statistics(session_id):
    """Get aggregated engagement statistics for a session"""
    try:
        metrics = EngagementMetric.query.filter_by(session_id=session_id).all()
        
        if not metrics:
            return jsonify({'error': 'No metrics found for session'}), 404
        
        # Calculate statistics
        avg_engagement = sum(m.engagement_score for m in metrics) / len(metrics)
        avg_accuracy = sum(m.accuracy for m in metrics) / len(metrics)
        avg_response_time = sum(m.response_time_seconds or 0 for m in metrics) / len(metrics)
        
        high_engagement = sum(1 for m in metrics if m.engagement_level == 'high')
        low_engagement = sum(1 for m in metrics if m.engagement_level == 'low')
        
        stats = {
            'total_metrics': len(metrics),
            'average_engagement_score': avg_engagement,
            'average_accuracy': avg_accuracy,
            'average_response_time': avg_response_time,
            'high_engagement_count': high_engagement,
            'medium_engagement_count': len(metrics) - high_engagement - low_engagement,
            'low_engagement_count': low_engagement
        }
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'statistics': stats
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
