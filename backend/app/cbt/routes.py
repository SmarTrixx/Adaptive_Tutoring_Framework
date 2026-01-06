from flask import Blueprint, request, jsonify
from app.cbt.system import CBTSystem
from app.models.student import Student
from app.models.session import Session

cbt_bp = Blueprint('cbt', __name__)
cbt_system = CBTSystem()

@cbt_bp.route('/student', methods=['POST'])
def create_student():
    """Create a new student or login existing student"""
    data = request.get_json()
    
    email = data.get('email')
    name = data.get('name')
    
    if not email or not name:
        return jsonify({'error': 'Email and name are required'}), 400
    
    # Check if student already exists
    existing = Student.query.filter_by(email=email).first()
    if existing:
        # Student exists - check if name matches (case-insensitive)
        if existing.name.lower() != name.lower():
            return jsonify({
                'success': False,
                'error': f'Email already registered with name "{existing.name}". Please use the correct name to login.'
            }), 403
        
        # Student exists with matching name - treat as login and return the student data
        return jsonify({
            'success': True,
            'student': existing.to_dict(),
            'message': 'Login successful'
        }), 200
    
    try:
        student = Student(email=email, name=name)
        from app import db
        db.session.add(student)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'student': student.to_dict(),
            'message': 'Account created successfully'
        }), 201
        
    except Exception as e:
        from app import db
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@cbt_bp.route('/student/<student_id>', methods=['GET'])
def get_student(student_id):
    """Get student information"""
    student = Student.query.get(student_id)
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    return jsonify({
        'success': True,
        'student': student.to_dict()
    }), 200

@cbt_bp.route('/session/start', methods=['POST'])
def start_session():
    """Start a new CBT session"""
    data = request.get_json()
    
    student_id = data.get('student_id')
    subject = data.get('subject')
    num_questions = data.get('num_questions', 10)
    
    if not student_id or not subject:
        return jsonify({'error': 'student_id and subject are required'}), 400
    
    result = cbt_system.start_session(student_id, subject, num_questions)
    
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    
    return jsonify({
        'success': True,
        'session': result
    }), 201

@cbt_bp.route('/question/next/<session_id>', methods=['GET'])
def get_next_question(session_id):
    """Get the next question for a session"""
    difficulty = request.args.get('difficulty', type=float)
    
    result = cbt_system.get_next_question(session_id, difficulty)
    
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    
    return jsonify({
        'success': True,
        'question': result
    }), 200

@cbt_bp.route('/response/submit', methods=['POST'])
def submit_response():
    """Submit a response to a question"""
    data = request.get_json()
    
    session_id = data.get('session_id')
    question_id = data.get('question_id')
    student_answer = data.get('student_answer')
    response_time_seconds = data.get('response_time_seconds', 0)
    
    # Extract behavioral tracking data from frontend
    initial_option = data.get('initial_option')
    final_option = data.get('final_option')
    option_change_count = data.get('option_change_count', 0)
    option_change_history = data.get('option_change_history', [])
    navigation_frequency = data.get('navigation_frequency', 0)
    interaction_start_timestamp = data.get('interaction_start_timestamp')
    submission_timestamp = data.get('submission_timestamp')
    submission_iso_timestamp = data.get('submission_iso_timestamp')
    
    # Extract cognitive & affective tracking data from frontend
    time_spent_per_question = data.get('time_spent_per_question', 0)
    inactivity_duration_ms = data.get('inactivity_duration_ms', 0)
    question_index = data.get('question_index', 0)
    hesitation_flags = data.get('hesitation_flags', {})
    navigation_pattern = data.get('navigation_pattern', 'sequential')
    
    # Extract facial monitoring data from frontend
    facial_metrics = data.get('facial_metrics', {})
    hints_used_array = data.get('hints_used', [])  # hints_used is the array from frontend
    
    # DEBUG: Log all tracking data received
    print(f"[TRACKING DATA RECEIVED] initial={initial_option}, final={final_option}, changes={option_change_count}, nav_freq={navigation_frequency}, ts={submission_iso_timestamp}, time_spent={time_spent_per_question}s, inactivity={inactivity_duration_ms}ms", flush=True)
    print(f"[COGNITIVE DATA] hesitation_flags={hesitation_flags}, navigation_pattern={navigation_pattern}, question_index={question_index}", flush=True)
    print(f"[FACIAL DATA] camera_enabled={facial_metrics.get('camera_enabled')}, face_detected={facial_metrics.get('face_detected_count')}", flush=True)
    print(f"[HINTS DATA] hints_used_array={hints_used_array}", flush=True)
    
    if not all([session_id, question_id, student_answer]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    result = cbt_system.submit_response(
        session_id, question_id, student_answer, response_time_seconds,
        initial_option=initial_option,
        final_option=final_option,
        option_change_count=option_change_count,
        option_change_history=option_change_history,
        navigation_frequency=navigation_frequency,
        interaction_start_timestamp=interaction_start_timestamp,
        submission_timestamp=submission_timestamp,
        submission_iso_timestamp=submission_iso_timestamp,
        # Cognitive fields
        time_spent_per_question=time_spent_per_question,
        inactivity_duration_ms=inactivity_duration_ms,
        question_index=question_index,
        hesitation_flags=hesitation_flags,
        navigation_pattern=navigation_pattern,
        # Facial & Hint data
        facial_metrics=facial_metrics,
        hints_used_array=hints_used_array
    )
    
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    
    response_data = {
        'success': True,
        'is_correct': result.get('is_correct', False),
        'correct_answer': result.get('correct_answer', ''),
        'explanation': result.get('explanation', ''),
        'current_score': result.get('current_score', 0),
        'correct_count': result.get('correct_count', 0),
        'total_answered': result.get('total_answered', 0),
        'current_difficulty': result.get('current_difficulty', 0.5)
    }
    
    print(f"[RESPONSE] Sending difficulty: {response_data['current_difficulty']}, is_correct: {response_data['is_correct']}", flush=True)
    
    return jsonify(response_data), 201

@cbt_bp.route('/hint/<session_id>/<question_id>', methods=['GET'])
def get_hint(session_id, question_id):
    """Get a hint for a question"""
    hint_index = request.args.get('hint_index', 0, type=int)
    
    result = cbt_system.get_hint(session_id, question_id, hint_index)
    
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    
    return jsonify({
        'success': True,
        'hint_data': result
    }), 200

@cbt_bp.route('/session/end/<session_id>', methods=['POST'])
def end_session(session_id):
    """End a test session"""
    result = cbt_system.end_session(session_id)
    
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    
    return jsonify({
        'success': True,
        'session_summary': result
    }), 200

@cbt_bp.route('/session/<session_id>', methods=['GET'])
def get_session_summary(session_id):
    """Get session summary"""
    result = cbt_system.get_session_summary(session_id)
    
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    
    return jsonify({
        'success': True,
        'summary': result
    }), 200

@cbt_bp.route('/response/<session_id>/<question_id>', methods=['GET'])
def get_previous_response(session_id, question_id):
    """Get previous response data for a question (for revisit hint loading)"""
    try:
        from app.models.session import StudentResponse
        response = StudentResponse.query.filter_by(
            session_id=session_id,
            question_id=question_id
        ).first()
        
        if not response:
            return jsonify({'success': False, 'error': 'No previous response found'}), 404
        
        return jsonify({
            'success': True,
            'response': {
                'hints_used': len(response.hints_used_array) if response.hints_used_array else 0,
                'hints_used_array': response.hints_used_array if response.hints_used_array else [],
                'navigation_frequency': response.navigation_frequency if response.navigation_frequency is not None else 0,
                'student_answer': response.student_answer,
                'is_correct': response.is_correct
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

