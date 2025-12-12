# Testing Guide

## Overview
This guide provides instructions for testing the Adaptive Intelligent Tutoring Framework.

## Test Types

### 1. Unit Tests
Test individual components in isolation.

### 2. Integration Tests
Test how components work together.

### 3. Manual API Testing
Test endpoints using curl, Postman, or the frontend.

### 4. End-to-End Testing
Complete workflow testing through the frontend.

---

## Setup for Testing

### Prerequisites
```bash
cd backend
pip install pytest pytest-cov
```

### Create Test Database
Tests use an in-memory SQLite database to avoid affecting production data.

---

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_models.py
```

### Run Specific Test
```bash
pytest tests/test_engagement.py::test_engagement_calculation
```

### Run with Coverage
```bash
pytest --cov=app --cov-report=html
```

### Run in Verbose Mode
```bash
pytest -v
```

---

## Test Categories

### A. Model Tests (`test_models.py`)

#### Test Student Model
```python
def test_create_student():
    student = Student(
        email="test@example.com",
        name="Test Student",
        preferred_difficulty=0.5,
        preferred_pacing="medium"
    )
    db.session.add(student)
    db.session.commit()
    
    assert student.id is not None
    assert student.email == "test@example.com"
```

#### Test Question Model
```python
def test_create_question():
    question = Question(
        subject="Mathematics",
        topic="Algebra",
        difficulty=QuestionDifficulty.MEDIUM,
        question_text="What is 2+2?",
        option_a="3",
        option_b="4",
        option_c="5",
        option_d="6",
        correct_option="B",
        explanation="2+2=4",
        hints=["Count your fingers"]
    )
    db.session.add(question)
    db.session.commit()
    
    assert question.id is not None
```

#### Test Session Model
```python
def test_create_session():
    student = Student(email="test@example.com", name="Test")
    session = Session(
        student_id=student.id,
        subject="Mathematics",
        total_questions=10
    )
    db.session.add(student)
    db.session.add(session)
    db.session.commit()
    
    assert session.status == "active"
    assert session.score_percentage == 0.0
```

### B. Engagement Tests (`test_engagement.py`)

#### Test Engagement Calculation
```python
def test_calculate_composite_engagement():
    tracker = EngagementIndicatorTracker()
    
    behavioral = 0.8
    cognitive = 0.75
    affective = 0.7
    
    engagement = tracker.calculate_composite_engagement_score(
        behavioral, cognitive, affective
    )
    
    expected = (0.35 * 0.8) + (0.40 * 0.75) + (0.25 * 0.7)
    assert abs(engagement - expected) < 0.01
```

#### Test Engagement Level Classification
```python
def test_engagement_level_classification():
    tracker = EngagementIndicatorTracker()
    
    # Low engagement
    level = tracker.determine_engagement_level(0.2)
    assert level == "low"
    
    # Medium engagement
    level = tracker.determine_engagement_level(0.5)
    assert level == "medium"
    
    # High engagement
    level = tracker.determine_engagement_level(0.8)
    assert level == "high"
```

#### Test Behavioral Indicators
```python
def test_track_behavioral_indicators():
    tracker = EngagementIndicatorTracker()
    
    response_data = {
        'response_time_seconds': 15.5,
        'attempts': 2,
        'hints_used': 0,
        'completed': True
    }
    
    behavioral = tracker.track_behavioral_indicators(response_data)
    
    assert 0 <= behavioral <= 1
    assert 'response_time' in str(behavioral)
```

### C. Adaptation Tests (`test_adaptation.py`)

#### Test Difficulty Adaptation
```python
def test_adapt_difficulty_increase():
    engine = AdaptiveEngine()
    
    engagement = {'accuracy': 0.85, 'engagement_score': 0.75}
    current_difficulty = 0.5
    
    new_difficulty = engine.adapt_difficulty(
        current_difficulty, engagement
    )
    
    assert new_difficulty > current_difficulty
    assert new_difficulty <= 0.9
```

#### Test Difficulty Adaptation Decrease
```python
def test_adapt_difficulty_decrease():
    engine = AdaptiveEngine()
    
    engagement = {'accuracy': 0.35, 'engagement_score': 0.4}
    current_difficulty = 0.7
    
    new_difficulty = engine.adapt_difficulty(
        current_difficulty, engagement
    )
    
    assert new_difficulty < current_difficulty
    assert new_difficulty >= 0.1
```

#### Test Pacing Adaptation
```python
def test_adapt_pacing():
    engine = AdaptiveEngine()
    
    engagement = {'response_time': 45, 'engagement_score': 0.25}
    
    pacing = engine.adapt_pacing(engagement)
    
    assert pacing in ['slow', 'medium', 'fast']
```

#### Test Hint Frequency Adaptation
```python
def test_adapt_hint_frequency():
    engine = AdaptiveEngine()
    
    engagement = {'confidence': 0.3, 'frustration': 0.7}
    
    provide_hints = engine.adapt_hint_frequency(engagement)
    
    assert isinstance(provide_hints, bool)
    assert provide_hints == True  # Low confidence, high frustration
```

### D. CBT System Tests (`test_cbt.py`)

#### Test Session Creation
```python
def test_start_session():
    system = CBTSystem()
    student = Student(email="test@example.com", name="Test")
    
    session = system.start_session(student.id, "Mathematics")
    
    assert session.status == "active"
    assert session.subject == "Mathematics"
```

#### Test Question Selection
```python
def test_get_next_question():
    system = CBTSystem()
    session = Session(
        student_id="student1",
        subject="Mathematics",
        total_questions=10
    )
    
    question = system.get_next_question(session.id)
    
    assert question is not None
    assert question.subject == "Mathematics"
```

#### Test Answer Submission
```python
def test_submit_response():
    system = CBTSystem()
    
    response = system.submit_response(
        session_id="session1",
        question_id="q1",
        student_answer="B",
        response_time=20.5
    )
    
    assert response['is_correct'] is not None
```

#### Test Score Calculation
```python
def test_session_score_calculation():
    session = Session(
        student_id="student1",
        subject="Mathematics",
        total_questions=10
    )
    
    # Mock correct responses
    session.correct_count = 8
    
    assert session.score_percentage == 80.0
```

### E. Analytics Tests (`test_analytics.py`)

#### Test Student Summary
```python
def test_get_student_summary():
    analytics = Analytics()
    summary = analytics.get_student_summary("student1")
    
    assert 'total_sessions' in summary
    assert 'total_questions_answered' in summary
    assert 'overall_accuracy' in summary
```

#### Test Progress Tracking
```python
def test_get_student_progress():
    analytics = Analytics()
    progress = analytics.get_student_progress("student1")
    
    assert isinstance(progress, list)
    if progress:
        assert 'session_id' in progress[0]
        assert 'score' in progress[0]
```

---

## Manual API Testing with cURL

### 1. Create Student
```bash
curl -X POST http://localhost:5000/api/cbt/student \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "name": "Test User"
  }'

# Response:
# {
#   "success": true,
#   "student": {
#     "id": "uuid",
#     "email": "testuser@example.com",
#     "name": "Test User",
#     ...
#   }
# }
```

### 2. Get Student
```bash
curl http://localhost:5000/api/cbt/student/uuid
```

### 3. Start Session
```bash
curl -X POST http://localhost:5000/api/cbt/session/start \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "uuid",
    "subject": "Mathematics",
    "num_questions": 10
  }'
```

### 4. Get Next Question
```bash
curl "http://localhost:5000/api/cbt/question/next/session_uuid?difficulty=0.5"
```

### 5. Submit Answer
```bash
curl -X POST http://localhost:5000/api/cbt/response/submit \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session_uuid",
    "question_id": "question_uuid",
    "student_answer": "B",
    "response_time_seconds": 25.5
  }'
```

### 6. Get Hint
```bash
curl "http://localhost:5000/api/cbt/hint/session_uuid/question_uuid"
```

### 7. End Session
```bash
curl -X POST http://localhost:5000/api/cbt/session/end/session_uuid
```

### 8. Track Engagement
```bash
curl -X POST http://localhost:5000/api/engagement/track \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "uuid",
    "session_id": "session_uuid",
    "response_data": {
      "response_time_seconds": 25.5,
      "attempts": 1,
      "hints_used": 0
    },
    "affective_feedback": {
      "confidence": 0.8,
      "frustration": 0.2,
      "interest": 0.7
    }
  }'
```

### 9. Get Analytics Dashboard
```bash
curl http://localhost:5000/api/analytics/dashboard/student_uuid
```

---

## Testing Checklist

### Backend Functionality
- [ ] All models create successfully
- [ ] Relationships work correctly
- [ ] Engagement calculation produces 0-1 values
- [ ] Engagement levels classify correctly
- [ ] Difficulty adaptation applies correct thresholds
- [ ] All adaptation strategies execute without errors
- [ ] Session score calculation is accurate
- [ ] API endpoints return correct status codes
- [ ] Error responses include helpful messages

### Frontend Integration
- [ ] Login form submits correctly
- [ ] Student creation successful
- [ ] Session starts without errors
- [ ] Questions display properly
- [ ] Answer submission works
- [ ] Engagement tracking posts data
- [ ] Dashboard loads and displays stats
- [ ] Navigation between pages works

### Data Integrity
- [ ] Student data persists
- [ ] Session data complete
- [ ] Response records accurate
- [ ] Engagement metrics calculated correctly
- [ ] No data loss on errors

### Performance
- [ ] API responses < 200ms
- [ ] Question loading quick
- [ ] No database locks
- [ ] Frontend responsive

---

## Debugging Tips

### Enable Logging
```python
# In config.py
FLASK_ENV = 'development'
DEBUG = True

# In Python code
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Database
```bash
# Connect to SQLite database
sqlite3 backend/tutoring_system.db

# View tables
.tables

# Query students
SELECT * FROM student;

# Query sessions
SELECT * FROM session;
```

### Check API Responses
```bash
# Verbose curl output
curl -v http://localhost:5000/api/cbt/student/uuid

# Save response to file
curl http://localhost:5000/api/cbt/student/uuid > response.json
```

### Monitor Backend Logs
```bash
# Run with logging
FLASK_ENV=development python main.py

# Watch logs in another terminal
tail -f logs/app.log
```

---

## Performance Testing

### Load Testing with Apache Bench
```bash
# Simple load test: 100 requests, 10 concurrent
ab -n 100 -c 10 http://localhost:5000/api/cbt/student/uuid

# Results show response time and throughput
```

### Load Testing with wrk
```bash
# 10 connections, 2 threads, 10 second duration
wrk -t2 -c10 -d10s http://localhost:5000/api/cbt/student/uuid
```

---

## Expected Test Results

When all tests pass:
- 40+ unit tests pass
- 0 failures
- 0 errors
- Coverage > 80%

---

## Continuous Integration

Add to `.github/workflows/tests.yml` for automated testing:
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest --cov=app
```

---

## Troubleshooting Tests

### Tests Fail with Database Errors
```bash
# Clear test database
rm backend/test_tutoring_system.db
pytest
```

### Import Errors
```bash
# Ensure backend directory structure is correct
ls -la backend/app/models/
# Should see: __init__.py, student.py, question.py, etc.
```

### Fixture Issues
```python
# Ensure fixtures are properly defined
def test_with_session(app, client):
    with app.app_context():
        # Database operations here
        pass
```

---

## Next Steps

1. Run `pytest` to ensure all tests pass
2. Add more tests as you add features
3. Aim for >80% code coverage
4. Run performance tests before deployment
5. Set up continuous integration

For additional testing needs, refer to [pytest documentation](https://docs.pytest.org/).
