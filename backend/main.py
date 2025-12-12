import os
from app import create_app, db
from app.models import Student, Question, QuestionDifficulty

# Create Flask app
app = create_app(os.getenv('FLASK_ENV', 'development'))

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Student': Student,
        'Question': Question,
        'QuestionDifficulty': QuestionDifficulty
    }

@app.route('/')
def index():
    return {
        'message': 'Adaptive Intelligent Tutoring Framework API',
        'version': '1.0.0',
        'status': 'active'
    }

@app.route('/health')
def health():
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
