# Development Guide

## Project Overview
The Adaptive Intelligent Tutoring Framework is a full-stack web application designed to provide personalized learning experiences through real-time engagement tracking and adaptive content delivery.

## Development Environment Setup

### Required Tools
- Python 3.8+ with pip
- Node.js 14+ with npm (optional for frontend)
- PostgreSQL or SQLite (included with Python)
- Git for version control
- Code editor (VS Code, PyCharm, etc.)
- Postman or cURL for API testing

### Initial Setup
```bash
# Clone repository
git clone <repository-url>
cd adaptive-tutoring-framework

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py

# In another terminal, frontend setup
cd frontend
python -m http.server 8000
```

## Project Architecture

### Directory Structure Explained

```
backend/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── models/               # Database models
│   │   ├── __init__.py
│   │   ├── student.py        # Student model with preferences
│   │   ├── question.py       # Question bank with hints
│   │   ├── session.py        # Test session tracking
│   │   ├── engagement.py     # Engagement metrics
│   │   └── adaptation.py     # Adaptation logs
│   ├── engagement/           # Engagement tracking module
│   │   ├── __init__.py
│   │   ├── tracker.py        # EngagementIndicatorTracker class
│   │   └── routes.py         # Flask endpoints
│   ├── adaptation/           # Adaptation engine
│   │   ├── __init__.py
│   │   ├── engine.py         # AdaptiveEngine class
│   │   └── routes.py         # Flask endpoints
│   ├── cbt/                  # Computer-Based Testing
│   │   ├── __init__.py
│   │   ├── system.py         # CBTSystem class
│   │   └── routes.py         # Flask endpoints
│   └── analytics/            # Analytics and reporting
│       ├── __init__.py
│       └── routes.py         # Analytics endpoints
├── config.py                 # Configuration management
├── main.py                   # Entry point
├── requirements.txt          # Python dependencies
└── tutoring_system.db        # SQLite database (auto-created)

frontend/
├── index.html                # Main HTML template
├── app.js                    # Application logic
├── styles.css                # Styling
└── package.json              # npm configuration

docs/
├── README.md                 # Main documentation
├── ARCHITECTURE.md           # System design
├── ENGAGEMENT_INDICATORS.md  # Engagement framework
├── API_DOCUMENTATION.md      # API endpoints
├── SETUP.md                  # Installation guide
├── TESTING.md                # Testing guide
└── DEVELOPMENT.md            # This file
```

## Key Components

### 1. Flask Application Factory (`app/__init__.py`)
```python
def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(cbt_bp)
    app.register_blueprint(engagement_bp)
    app.register_blueprint(adaptation_bp)
    app.register_blueprint(analytics_bp)
    
    return app
```

**Why**: Allows flexible app configuration and testing with different settings.

### 2. Database Models (`app/models/`)
- **Student**: Learner profiles with preferences
- **Question**: Question bank with metadata and hints
- **Session**: Test sessions with performance tracking
- **StudentResponse**: Individual answer records
- **EngagementMetric**: Calculated engagement indicators
- **AdaptationLog**: Records of all system adaptations

**Why**: SQLAlchemy ORM provides database abstraction and automatic migrations.

### 3. Engagement Tracker (`app/engagement/tracker.py`)
```python
class EngagementIndicatorTracker:
    def track_behavioral_indicators(self, response_data):
        """Calculate behavioral engagement (response time, attempts, etc.)"""
        
    def track_cognitive_indicators(self, performance_data):
        """Calculate cognitive engagement (accuracy, learning progress)"""
        
    def track_affective_indicators(self, student_feedback):
        """Estimate affective engagement (confidence, frustration, interest)"""
        
    def calculate_composite_engagement_score(self, behavioral, cognitive, affective):
        """Combine three dimensions with weights: 35%, 40%, 25%"""
```

**Why**: Separates engagement logic from API routes for testability.

### 4. Adaptation Engine (`app/adaptation/engine.py`)
```python
class AdaptiveEngine:
    def adapt_difficulty(self, current_difficulty, engagement):
        """Adjust question difficulty based on performance"""
        
    def adapt_pacing(self, engagement):
        """Modify time limits based on response patterns"""
        
    def adapt_hint_frequency(self, engagement):
        """Adjust hint availability based on confidence/frustration"""
        
    def adapt_content_selection(self, student_id, session_id):
        """Focus on knowledge gaps and learning preferences"""
```

**Why**: Encapsulates adaptation logic separately for modularity and testing.

### 5. CBT System (`app/cbt/system.py`)
Manages the complete test lifecycle:
- Start session
- Deliver questions
- Submit answers
- Calculate scores
- Generate summaries

**Why**: Keeps core testing logic separate from API routes.

### 6. API Routes (`app/*/routes.py`)
Each module has a `routes.py` file defining Flask endpoints that:
- Accept HTTP requests
- Call business logic classes
- Return JSON responses

**Why**: Follows Flask blueprints pattern for modular routing.

## Development Workflow

### Adding a New Feature

#### Step 1: Update Models (if needed)
```python
# app/models/example.py
class NewModel(db.Model):
    __tablename__ = 'new_model'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

#### Step 2: Add Business Logic
```python
# app/example/logic.py
class ExampleLogic:
    def do_something(self, data):
        # Implementation
        return result
```

#### Step 3: Create Routes
```python
# app/example/routes.py
example_bp = Blueprint('example', __name__)

@example_bp.route('/example/<id>', methods=['GET'])
def get_example(id):
    # Implementation
    return jsonify({"success": True, "data": example})
```

#### Step 4: Register Blueprint
```python
# app/__init__.py
app.register_blueprint(example_bp, url_prefix='/api/example')
```

#### Step 5: Write Tests
```python
# tests/test_example.py
def test_do_something():
    logic = ExampleLogic()
    result = logic.do_something(test_data)
    assert result is not None
```

### Configuration Management

#### Development Settings
```python
# config.py
class DevelopmentConfig:
    DEBUG = True
    TESTING = False
    DATABASE_URL = 'sqlite:///tutoring_system.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

#### Production Settings
```python
class ProductionConfig:
    DEBUG = False
    TESTING = False
    DATABASE_URL = 'postgresql://user:password@host/dbname'
```

#### Testing Settings
```python
class TestingConfig:
    DEBUG = True
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'
```

## Code Style & Standards

### Python Style (PEP 8)
```python
# Good: Clear, follows PEP 8
def calculate_engagement_score(behavioral, cognitive, affective):
    """Calculate composite engagement score with weighted dimensions."""
    weights = {'behavioral': 0.35, 'cognitive': 0.40, 'affective': 0.25}
    score = (
        weights['behavioral'] * behavioral +
        weights['cognitive'] * cognitive +
        weights['affective'] * affective
    )
    return min(1.0, max(0.0, score))  # Clamp to 0-1

# Bad: Unclear naming, no docstring
def calc_score(b, c, a):
    return (0.35 * b + 0.40 * c + 0.25 * a)
```

### Documentation Standards
```python
def method_name(param1, param2):
    """
    Brief description of what the method does.
    
    Args:
        param1 (type): Description of param1
        param2 (type): Description of param2
        
    Returns:
        type: Description of return value
        
    Raises:
        ExceptionType: When this exception occurs
        
    Example:
        >>> result = method_name(value1, value2)
        >>> print(result)
    """
```

### Error Handling
```python
# Good: Specific error handling
try:
    student = Student.query.get(student_id)
    if not student:
        return {'error': 'Student not found'}, 404
except SQLAlchemyError as e:
    return {'error': 'Database error'}, 500

# Bad: Catching all exceptions silently
try:
    student = Student.query.get(student_id)
except:
    pass
```

## Common Development Tasks

### Database Operations

#### Create New Table
1. Add model to `app/models/`
2. Delete existing `tutoring_system.db`
3. Run `python main.py` (creates fresh database)

#### Query Data
```python
# Get single record
student = Student.query.get(student_id)

# Query with filters
students = Student.query.filter_by(name='John').all()

# Relationship queries
sessions = student.sessions  # If relationship defined
```

#### Update Data
```python
student = Student.query.get(student_id)
student.name = 'New Name'
db.session.commit()
```

### Testing Changes

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_engagement.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run with verbose output
pytest -v
```

### API Testing

```bash
# Test endpoint
curl -X POST http://localhost:5000/api/endpoint \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'

# Save to file for inspection
curl http://localhost:5000/api/endpoint > response.json
```

## Performance Optimization

### Database Queries
```python
# Bad: N+1 query problem
for student in students:
    print(student.sessions)  # Query per student

# Good: Eager loading
students = Student.query.options(
    joinedload(Student.sessions)
).all()
```

### Caching
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_question_difficulty_distribution(subject):
    # Expensive query
    return distribution
```

### Response Optimization
```python
# Good: Return only needed fields
question = Question.query.get(id)
return {
    'id': question.id,
    'text': question.question_text,
    'options': [question.option_a, question.option_b, ...]
}

# Bad: Return entire object (includes hints, explanations)
return question.to_dict()
```

## Debugging Strategies

### Print Debugging
```python
import logging

logger = logging.getLogger(__name__)
logger.debug(f"Student ID: {student_id}, Engagement: {engagement}")
```

### Interactive Debugging
```python
# In code where debugging needed
import pdb; pdb.set_trace()

# Or use Flask shell
flask shell
>>> from app.models import Student
>>> student = Student.query.first()
>>> student.name
```

### Logging Configuration
```python
# config.py
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

## Git Workflow

### Feature Branch Development
```bash
# Create feature branch
git checkout -b feature/engagement-tracking

# Make changes
git add .
git commit -m "Add behavioral engagement tracking"

# Push to remote
git push origin feature/engagement-tracking

# Create pull request for review
```

### Commit Message Guidelines
```
Short (50 char max): Add behavioral engagement indicator tracking

Longer explanation (72 char wrap):
- Implemented response time tracking
- Added attempts counter
- Integrated with engagement calculator
- Updated tests

Fixes #123
```

## Deployment Checklist

Before deploying to production:
- [ ] All tests pass (`pytest`)
- [ ] Code coverage > 80%
- [ ] No unhandled exceptions
- [ ] Configuration for production environment
- [ ] Database migrations tested
- [ ] API endpoints documented
- [ ] Performance tested under load
- [ ] Security review completed
- [ ] Error handling in place
- [ ] Logging configured

## Resources

### Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Python PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [REST API Design Guidelines](https://restfulapi.net/)

### Tools
- [Postman](https://www.postman.com/) - API testing
- [VS Code](https://code.visualstudio.com/) - Code editor
- [PyCharm](https://www.jetbrains.com/pycharm/) - Python IDE
- [SQLite Browser](https://sqlitebrowser.org/) - Database inspection

### Learning
- Flask tutorial: https://flask.palletsprojects.com/tutorial/
- SQLAlchemy ORM: https://docs.sqlalchemy.org/orm/
- REST API best practices: https://restfulapi.net/

## Contributing Guidelines

1. **Code Quality**: Follow PEP 8, write docstrings
2. **Testing**: Add tests for new features
3. **Documentation**: Update docs with changes
4. **Commits**: Write clear, descriptive commit messages
5. **Reviews**: Request code review before merging

## Troubleshooting

### ImportError: No module named 'app'
```bash
# Ensure you're in the backend directory
cd adaptive-tutoring-framework/backend
python main.py
```

### Database is locked
```bash
# Remove and recreate database
rm tutoring_system.db
python main.py
```

### Port already in use
```bash
# Find process using port 5000
lsof -i :5000
# Kill process
kill -9 <PID>
```

### Virtual environment not activated
```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows
```

## Next Steps

1. Set up development environment
2. Run existing tests to ensure everything works
3. Explore the codebase
4. Make a small change and verify tests still pass
5. Create your first feature branch
6. Start development!

For questions or issues, refer to the main [README.md](../README.md).
