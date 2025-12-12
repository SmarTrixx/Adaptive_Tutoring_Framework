from flask import Blueprint, request, jsonify
from app.adaptation.engine import AdaptiveEngine
from app.models.adaptation import AdaptationLog

adaptation_bp = Blueprint('adaptation', __name__)
engine = AdaptiveEngine()

@adaptation_bp.route('/recommend/<student_id>/<session_id>', methods=['GET'])
def get_recommendations(student_id, session_id):
    """Get adaptation recommendations for a student"""
    try:
        recommendations = engine.get_adaptation_recommendations(student_id, session_id)
        
        return jsonify({
            'success': True,
            'student_id': student_id,
            'session_id': session_id,
            'recommendations': recommendations
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@adaptation_bp.route('/logs/<session_id>', methods=['GET'])
def get_adaptation_logs(session_id):
    """Get all adaptation logs for a session"""
    try:
        logs = AdaptationLog.query.filter_by(session_id=session_id).all()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'log_count': len(logs),
            'logs': [log.to_dict() for log in logs]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@adaptation_bp.route('/effectiveness/<session_id>', methods=['GET'])
def get_adaptation_effectiveness(session_id):
    """Analyze effectiveness of adaptations in a session"""
    try:
        logs = AdaptationLog.query.filter_by(session_id=session_id).all()
        
        if not logs:
            return jsonify({'error': 'No adaptation logs found'}), 404
        
        # Calculate effectiveness metrics
        total_adaptations = len(logs)
        effective_adaptations = sum(1 for log in logs if log.was_effective)
        ineffective_adaptations = sum(1 for log in logs if log.was_effective == False)
        unknown_effectiveness = total_adaptations - effective_adaptations - ineffective_adaptations
        
        effectiveness_rate = effective_adaptations / total_adaptations if total_adaptations > 0 else 0
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'effectiveness_analysis': {
                'total_adaptations': total_adaptations,
                'effective': effective_adaptations,
                'ineffective': ineffective_adaptations,
                'unknown': unknown_effectiveness,
                'effectiveness_rate': effectiveness_rate
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
