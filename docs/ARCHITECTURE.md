# System Architecture

## Overview
The Adaptive Intelligent Tutoring Framework is designed with a modular architecture that separates concerns into distinct layers.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                           │
│  (HTML/CSS/JavaScript - Student Interface & Dashboard)      │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/REST APIs
┌────────────────────────▼────────────────────────────────────┐
│                   Backend API Layer (Flask)                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Route Handlers / API Endpoints                      │   │
│  │  - CBT Routes    - Engagement Routes                │   │
│  │  - Adaptation Routes  - Analytics Routes             │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              Business Logic Layer                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  • CBT System (Test Management)                      │   │
│  │  • Engagement Tracker (Indicator Collection)         │   │
│  │  • Adaptive Engine (Real-time Adaptation)            │   │
│  │  • Analytics Engine (Data Analysis)                  │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│               Data Models Layer (SQLAlchemy)                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  • Student          • Question                        │   │
│  │  • Session          • StudentResponse                │   │
│  │  • EngagementMetric • AdaptationLog                  │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│             Database Layer (SQLite/PostgreSQL)              │
└─────────────────────────────────────────────────────────────┘
```

## Module Breakdown

### 1. CBT System Module (`app/cbt/`)
Manages computer-based testing functionality:
- Session creation and management
- Question delivery
- Response submission and tracking
- Hint provisioning
- Score calculation

### 2. Engagement Module (`app/engagement/`)
Tracks and calculates engagement indicators:
- **Behavioral Indicators**: Response time, attempts, navigation, hints, inactivity
- **Cognitive Indicators**: Accuracy, learning progress, knowledge gaps
- **Affective Indicators**: Confidence, frustration, interest
- Composite engagement score calculation

### 3. Adaptation Module (`app/adaptation/`)
Core adaptive engine that applies real-time adaptations:
- Difficulty adaptation
- Pacing adjustment
- Hint frequency optimization
- Content selection strategies
- Logs all adaptations and their effectiveness

### 4. Analytics Module (`app/analytics/`)
Provides insights and reporting:
- Student progress tracking
- Session analysis
- Engagement trends
- Adaptation effectiveness
- Dashboard generation

### 5. Models Layer (`app/models/`)
Core data structures:
- `Student`: Learner information and preferences
- `Question`: Question bank with metadata
- `Session`: Test sessions with performance data
- `StudentResponse`: Individual answer records
- `EngagementMetric`: Collected engagement indicators
- `AdaptationLog`: Record of system adaptations

## Data Flow

### Typical Learning Session Flow

```
1. Student Login/Registration
   ↓
2. Select Subject & Start Session
   ↓
3. Receive Question (Difficulty-Adapted)
   ↓
4. Student Answers + System Records Response
   ↓
5. Track Engagement Indicators
   - Behavioral: Response time, attempts, hints
   - Cognitive: Accuracy, learning progress
   - Affective: Confidence, frustration
   ↓
6. Calculate Engagement Score
   ↓
7. Adaptive Engine Applies Adaptations
   - Adjust difficulty level
   - Modify pacing
   - Adjust hint strategy
   - Select next question
   ↓
8. Log Adaptations & Effectiveness
   ↓
9. Repeat from Step 3 or End Session
   ↓
10. Generate Session Summary & Analytics
```

## API Structure

### CBT Endpoints
- `POST /api/cbt/student` - Create student
- `GET /api/cbt/student/<id>` - Get student info
- `POST /api/cbt/session/start` - Start session
- `GET /api/cbt/question/next/<session_id>` - Get next question
- `POST /api/cbt/response/submit` - Submit answer
- `GET /api/cbt/hint/<session_id>/<question_id>` - Get hint
- `POST /api/cbt/session/end/<session_id>` - End session
- `GET /api/cbt/session/<session_id>` - Get session summary

### Engagement Endpoints
- `POST /api/engagement/track` - Track engagement
- `GET /api/engagement/session/<session_id>` - Get session metrics
- `GET /api/engagement/student/<id>/latest` - Get latest metric
- `GET /api/engagement/statistics/<session_id>` - Get statistics

### Adaptation Endpoints
- `GET /api/adaptation/recommend/<student_id>/<session_id>` - Get recommendations
- `GET /api/adaptation/logs/<session_id>` - Get adaptation logs
- `GET /api/adaptation/effectiveness/<session_id>` - Analyze effectiveness

### Analytics Endpoints
- `GET /api/analytics/student/<id>/summary` - Student summary
- `GET /api/analytics/session/<id>/engagement_timeline` - Engagement timeline
- `GET /api/analytics/session/<id>/performance_analysis` - Performance analysis
- `GET /api/analytics/student/<id>/progress` - Progress tracking
- `GET /api/analytics/student/<id>/engagement_trends` - Engagement trends
- `GET /api/analytics/dashboard/<id>` - Full dashboard

## Key Features

### Real-time Adaptation
The system adapts multiple parameters in real-time:
- **Difficulty**: Increased when performing well, decreased when struggling
- **Pacing**: Adjusted based on response time patterns
- **Hint Provision**: Proactive hints for low confidence, restricted for high confidence
- **Content Selection**: Focuses on weak areas while maintaining confidence

### Engagement Tracking
Continuous monitoring of three engagement dimensions:
- **Behavioral**: Objective metrics from interaction logs
- **Cognitive**: Derived from performance data
- **Affective**: Self-reported and inferred from behavior

### Persistent Storage
All data is stored for analysis:
- Student profiles and preferences
- Complete test session history
- Individual response records
- Engagement metrics timeline
- Adaptation decision logs

### Analytics & Reporting
Comprehensive insights generation:
- Student progress reports
- Session performance analysis
- Engagement trend visualization
- Adaptation effectiveness measurement
- Knowledge gap identification

## Technology Stack

- **Backend**: Python, Flask, SQLAlchemy
- **Database**: SQLite (development), PostgreSQL (production)
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Data Analysis**: NumPy, Pandas, Scikit-learn
- **APIs**: RESTful design with JSON
