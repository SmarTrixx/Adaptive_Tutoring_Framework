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
    
    if not all([session_id, question_id, student_answer]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    result = cbt_system.submit_response(
        session_id, question_id, student_answer, response_time_seconds
    )
    
    if isinstance(result, tuple):
        return jsonify(result[0]), result[1]
    
    return jsonify({
        'success': True,
        'is_correct': result.get('is_correct', False),
        'correct_answer': result.get('correct_answer', ''),
        'explanation': result.get('explanation', ''),
        'current_score': result.get('current_score', 0),
        'correct_count': result.get('correct_count', 0),
        'total_answered': result.get('total_answered', 0)
    }), 201

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
