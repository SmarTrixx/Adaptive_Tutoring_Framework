# API Documentation

## Base URL
```
http://localhost:5000/api
```

## Authentication
Currently uses student_id in request bodies. Future versions should implement JWT authentication.

---

## CBT (Computer-Based Testing) Endpoints

### 1. Create Student
**POST** `/cbt/student`

Creates a new student account.

**Request Body**:
```json
{
  "email": "student@example.com",
  "name": "John Doe"
}
```

**Response**:
```json
{
  "success": true,
  "student": {
    "id": "uuid",
    "email": "student@example.com",
    "name": "John Doe",
    "created_at": "2024-01-01T10:00:00",
    "last_activity": null,
    "preferred_difficulty": 0.5,
    "preferred_pacing": "medium"
  }
}
```

**Status Codes**: 201 (Created), 409 (Conflict - Email exists), 400 (Bad Request)

---

### 2. Get Student
**GET** `/cbt/student/<student_id>`

Retrieves student information.

**Response**:
```json
{
  "success": true,
  "student": { ...student object... }
}
```

**Status Codes**: 200 (OK), 404 (Not Found)

---

### 3. Start Session
**POST** `/cbt/session/start`

Initiates a new testing session.

**Request Body**:
```json
{
  "student_id": "uuid",
  "subject": "Mathematics",
  "num_questions": 10
}
```

**Response**:
```json
{
  "success": true,
  "session": {
    "session_id": "uuid",
    "student_id": "uuid",
    "subject": "Mathematics",
    "total_questions": 10,
    "current_difficulty": 0.5,
    "status": "active"
  }
}
```

**Status Codes**: 201 (Created), 400 (Bad Request), 404 (Student Not Found)

---

### 4. Get Next Question
**GET** `/cbt/question/next/<session_id>?difficulty=0.5`

Retrieves the next question adapted to current difficulty.

**Query Parameters**:
- `difficulty` (optional): Target difficulty level (0.0-1.0)

**Response**:
```json
{
  "success": true,
  "question": {
    "question_id": "uuid",
    "question_text": "What is 2+2?",
    "options": {
      "A": "3",
      "B": "4",
      "C": "5",
      "D": "6"
    },
    "difficulty": 0.2,
    "hints_available": 2
  }
}
```

**Status Codes**: 200 (OK), 400 (Bad Request), 404 (Not Found)

---

### 5. Submit Response
**POST** `/cbt/response/submit`

Records a student's answer.

**Request Body**:
```json
{
  "session_id": "uuid",
  "question_id": "uuid",
  "student_answer": "B",
  "response_time_seconds": 25.5
}
```

**Response**:
```json
{
  "success": true,
  "response": {
    "response_id": "uuid",
    "is_correct": true,
    "correct_answer": "B",
    "explanation": "2 + 2 = 4",
    "current_score": 75.0,
    "correct_count": 3,
    "total_answered": 4
  }
}
```

**Status Codes**: 201 (Created), 400 (Bad Request), 404 (Not Found)

---

### 6. Get Hint
**GET** `/cbt/hint/<session_id>/<question_id>?hint_index=0`

Provides a hint for the current question.

**Query Parameters**:
- `hint_index` (optional, default=0): Which hint to retrieve (0-based)

**Response**:
```json
{
  "success": true,
  "hint_data": {
    "hint": "Think about what happens when you add two identical numbers",
    "hint_number": 1,
    "total_hints": 2
  }
}
```

**Status Codes**: 200 (OK), 400 (Bad Request), 404 (Not Found)

---

### 7. End Session
**POST** `/cbt/session/end/<session_id>`

Completes a testing session and calculates final score.

**Response**:
```json
{
  "success": true,
  "session_summary": {
    "session_id": "uuid",
    "status": "completed",
    "final_score": 75.0,
    "correct_answers": 7,
    "total_questions": 10,
    "duration_seconds": 1845
  }
}
```

**Status Codes**: 200 (OK), 404 (Not Found)

---

### 8. Get Session Summary
**GET** `/cbt/session/<session_id>`

Retrieves detailed session information and performance metrics.

**Response**:
```json
{
  "success": true,
  "summary": {
    "session": { ...session object... },
    "statistics": {
      "total_questions_answered": 10,
      "correct_answers": 7,
      "incorrect_answers": 3,
      "final_score_percentage": 70.0,
      "total_hints_used": 2,
      "average_response_time": 22.5,
      "total_attempts": 11
    },
    "responses": [ ...array of response objects... ]
  }
}
```

**Status Codes**: 200 (OK), 404 (Not Found)

---

## Engagement Tracking Endpoints

### 1. Track Engagement
**POST** `/engagement/track`

Records engagement metrics for a response.

**Request Body**:
```json
{
  "student_id": "uuid",
  "session_id": "uuid",
  "response_data": {
    "question_id": "uuid",
    "response_time_seconds": 25.5
  },
  "affective_feedback": {
    "confidence": 0.8,
    "frustration": 0.2,
    "interest": 0.7
  }
}
```

**Response**:
```json
{
  "success": true,
  "metric_id": "uuid",
  "engagement_score": 0.72,
  "engagement_level": "high",
  "behavioral": { ...behavioral indicators... },
  "cognitive": { ...cognitive indicators... },
  "affective": { ...affective indicators... }
}
```

**Status Codes**: 201 (Created), 400 (Bad Request), 500 (Server Error)

---

### 2. Get Session Engagement
**GET** `/engagement/session/<session_id>`

Retrieves all engagement metrics for a session.

**Response**:
```json
{
  "success": true,
  "session_id": "uuid",
  "metric_count": 10,
  "metrics": [ ...array of metric objects... ]
}
```

**Status Codes**: 200 (OK), 500 (Server Error)

---

### 3. Get Latest Engagement
**GET** `/engagement/student/<student_id>/latest`

Retrieves the most recent engagement metric for a student.

**Response**:
```json
{
  "success": true,
  "metric": { ...latest engagement metric... }
}
```

**Status Codes**: 200 (OK), 404 (Not Found)

---

### 4. Get Engagement Statistics
**GET** `/engagement/statistics/<session_id>`

Aggregates engagement statistics for a session.

**Response**:
```json
{
  "success": true,
  "session_id": "uuid",
  "statistics": {
    "total_metrics": 10,
    "average_engagement_score": 0.65,
    "average_accuracy": 0.75,
    "average_response_time": 22.5,
    "high_engagement_count": 4,
    "medium_engagement_count": 5,
    "low_engagement_count": 1
  }
}
```

**Status Codes**: 200 (OK), 404 (Not Found)

---

## Adaptation Endpoints

### 1. Get Recommendations
**GET** `/adaptation/recommend/<student_id>/<session_id>`

Gets adaptation recommendations based on current engagement.

**Response**:
```json
{
  "success": true,
  "student_id": "uuid",
  "session_id": "uuid",
  "recommendations": {
    "difficulty": {
      "adapted": true,
      "old_difficulty": 0.5,
      "new_difficulty": 0.6,
      "reason": "Student performing well..."
    },
    "pacing": {
      "adapted": false,
      "current_pacing": "medium",
      "reason": "No adaptation needed"
    },
    "hints": {
      "provide_proactive_hints": true,
      "reduce_hint_threshold": false,
      "reason": "Student confused and frustrated..."
    },
    "content": {
      "strategies": [ ...array of strategies... ],
      "primary_strategy": { ...primary strategy... }
    }
  }
}
```

**Status Codes**: 200 (OK), 404 (Not Found), 500 (Server Error)

---

### 2. Get Adaptation Logs
**GET** `/adaptation/logs/<session_id>`

Retrieves all adaptation records for a session.

**Response**:
```json
{
  "success": true,
  "session_id": "uuid",
  "log_count": 5,
  "logs": [ ...array of adaptation logs... ]
}
```

**Status Codes**: 200 (OK), 500 (Server Error)

---

### 3. Get Adaptation Effectiveness
**GET** `/adaptation/effectiveness/<session_id>`

Analyzes the effectiveness of adaptations.

**Response**:
```json
{
  "success": true,
  "session_id": "uuid",
  "effectiveness_analysis": {
    "total_adaptations": 5,
    "effective": 4,
    "ineffective": 1,
    "unknown": 0,
    "effectiveness_rate": 0.8
  }
}
```

**Status Codes**: 200 (OK), 404 (Not Found)

---

## Analytics Endpoints

### 1. Student Summary
**GET** `/analytics/student/<student_id>/summary`

Gets overall summary of a student's learning.

**Response**:
```json
{
  "success": true,
  "student_id": "uuid",
  "summary": {
    "total_sessions": 5,
    "total_questions_answered": 50,
    "correct_answers": 38,
    "overall_accuracy": 76.0,
    "average_session_score": 72.5,
    "total_study_time_seconds": 4500,
    "last_activity": "2024-01-15T14:30:00"
  }
}
```

**Status Codes**: 200 (OK), 404 (Not Found)

---

### 2. Engagement Timeline
**GET** `/analytics/session/<session_id>/engagement_timeline`

Shows engagement metrics over time in a session.

**Response**:
```json
{
  "success": true,
  "session_id": "uuid",
  "timeline": [
    {
      "timestamp": "2024-01-15T10:00:00",
      "engagement_score": 0.65,
      "engagement_level": "medium",
      "accuracy": 0.75,
      "response_time": 22.5,
      "confidence": 0.7
    },
    ...
  ]
}
```

**Status Codes**: 200 (OK), 404 (Not Found)

---

### 3. Performance Analysis
**GET** `/analytics/session/<session_id>/performance_analysis`

Analyzes performance metrics including topic breakdown.

**Response**:
```json
{
  "success": true,
  "session_id": "uuid",
  "analysis": {
    "accuracy": 75.0,
    "correct_answers": 7,
    "incorrect_answers": 3,
    "total_questions": 10,
    "average_response_time": 22.5,
    "average_difficulty_level": 0.45,
    "topic_performance": {
      "Algebra": {
        "correct": 3,
        "total": 4,
        "accuracy": 75.0
      },
      "Geometry": {
        "correct": 4,
        "total": 6,
        "accuracy": 66.67
      }
    }
  }
}
```

**Status Codes**: 200 (OK), 404 (Not Found)

---

### 4. Student Progress
**GET** `/analytics/student/<student_id>/progress`

Tracks progress across multiple sessions.

**Response**:
```json
{
  "success": true,
  "student_id": "uuid",
  "progress": [
    {
      "session_id": "uuid",
      "session_date": "2024-01-10T10:00:00",
      "subject": "Mathematics",
      "score": 65.0,
      "correct_answers": 6,
      "total_questions": 10,
      "duration_minutes": 30.75
    },
    ...
  ],
  "trend": "improving"
}
```

**Status Codes**: 200 (OK), 404 (Not Found)

---

### 5. Engagement Trends
**GET** `/analytics/student/<student_id>/engagement_trends`

Shows engagement patterns across sessions.

**Response**:
```json
{
  "success": true,
  "student_id": "uuid",
  "session_trends": [
    {
      "session_id": "uuid",
      "average_engagement": 0.65,
      "average_confidence": 0.72,
      "engagement_level": "medium"
    },
    ...
  ]
}
```

**Status Codes**: 200 (OK), 404 (Not Found)

---

### 6. Dashboard
**GET** `/analytics/dashboard/<student_id>`

Comprehensive dashboard data for a student.

**Response**:
```json
{
  "success": true,
  "dashboard": {
    "student_info": { ...student object... },
    "statistics": {
      "total_sessions": 5,
      "total_questions": 50,
      "correct_answers": 38,
      "overall_accuracy": 76.0,
      "recent_engagement_score": 0.72
    },
    "recent_sessions": [ ...last 5 sessions... ]
  }
}
```

**Status Codes**: 200 (OK), 404 (Not Found)

---

## Error Handling

All endpoints follow standard HTTP status codes:

| Status | Meaning |
|--------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Resource doesn't exist |
| 409 | Conflict - Duplicate resource |
| 500 | Server Error - Internal error |

Error responses follow this format:
```json
{
  "error": "Description of what went wrong"
}
```

---

## Rate Limiting
Currently not implemented. Future versions should include rate limiting for production environments.

---

## CORS
CORS is enabled for all origins in development. Should be restricted in production.
