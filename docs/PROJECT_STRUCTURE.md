# Adaptive Intelligent Tutoring Framework - Project Structure

## Overview

This document describes the production-ready project structure optimized for research submission and supervisor review.

## Directory Organization

```
adaptive-tutoring-framework/
├── backend/                          # Flask API server (Port 5000)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── adaptation/               # Adaptive difficulty engine
│   │   │   ├── engine.py             # Main adaptation logic
│   │   │   ├── irt.py                # Item Response Theory
│   │   │   └── rl_agent.py           # Reinforcement learning
│   │   ├── analytics/                # Data analysis & export
│   │   │   ├── routes.py             # Analytics API endpoints
│   │   │   └── engagement_fusion.py  # Engagement score fusion
│   │   ├── cbt/                      # Computer-Based Testing
│   │   │   ├── models.py             # Student, Session, Response models
│   │   │   └── routes.py             # CBT API endpoints
│   │   ├── engagement/               # Engagement tracking
│   │   │   ├── behavioral.py         # Behavioral indicators
│   │   │   ├── cognitive.py          # Cognitive indicators
│   │   │   └── affective.py          # Affective indicators
│   │   ├── logging/                  # Data logging system
│   │   │   └── engagement_logger.py  # Structured logging
│   │   ├── models/                   # Database models
│   │   └── utils/                    # Helper functions
│   ├── config.py                     # Flask configuration
│   ├── main.py                       # Application entry point
│   ├── requirements.txt              # Python dependencies
│   ├── instance/                     # Instance-specific files
│   ├── tests/                        # Unit & integration tests
│   │   ├── test_api.py
│   │   ├── test_models.py
│   │   ├── test_integration.py
│   │   └── conftest.py
│   └── scripts/                      # Utility scripts
│       ├── seed_questions.py         # Database seeding
│       └── add_more_questions.py
│
├── frontend/                         # React-based UI (Port 3000)
│   ├── app.js                        # Main application logic
│   ├── index.html                    # HTML entry point
│   ├── styles.css                    # Global styles
│   ├── package.json                  # Node dependencies
│   └── src/                          # Source components
│       ├── components/               # Reusable UI components
│       ├── pages/                    # Page components
│       └── utils/                    # Frontend utilities
│
├── docs/                             # Production documentation
│   ├── ACADEMIC_REPORT.md            # Research report
│   ├── ARCHITECTURE.md               # System design & architecture
│   ├── API_DOCUMENTATION.md          # API reference guide
│   ├── SETUP.md                      # Installation & setup
│   ├── DEPLOYMENT.md                 # Deployment guide
│   ├── TESTING.md                    # Testing & validation
│   ├── DEVELOPMENT.md                # Development workflow
│   ├── STAKEHOLDER_BRIEF.md          # Executive summary
│   └── ENGAGEMENT_INDICATORS.md      # Engagement metrics reference
│
├── safe_to_delete/                   # Redundant & intermediate files
│   ├── README.md                     # What's in this folder
│   └── [old docs, test scripts, backups]
│
├── README.md                         # Project overview
├── PROJECT_STRUCTURE.md              # This file
├── project_explanation.txt           # Quick project description
├── 1.csv                             # Sample student data export
├── 1.json                            # Sample session data export
└── .gitignore                        # Git configuration

```

## Key Files & Components

### Frontend (`frontend/`)

**Main Application**: `app.js` (1292 lines)
- **Authentication**: Student login/logout
- **Session Management**: Test creation and tracking  
- **Question Display**: Real-time adaptive question rendering
- **Feedback Modal**: Displays correctness, explanations, difficulty changes
- **Data Export**: CSV/JSON export for research analysis
- **Response Time Tracking**: Captures real user interaction timing

**Critical Functions**:
- `setupUI()` - Application initialization
- `showQuestion()` - Display current question with **response time capture**
- `submitSelectedAnswer()` - Handle answer submission with **real elapsed time calculation**
- `showFeedbackModal()` - Display feedback with close button and **12-second auto-dismiss**
- `exportAsCSV()` / `exportAllStudentData()` - Research data export

### Backend (`backend/`)

**Core Models** (`app/cbt/models.py`):
- `Student` - User identity and authentication
- `Session` - Test session with metadata
- `StudentResponse` - Individual answer with correctness and timing
- `Question` - Test items with difficulty ratings
- `EngagementMetric` - Per-response engagement indicators

**Adaptive Engine** (`app/adaptation/engine.py`):
- Window-based adaptation policy (Q1-5: Explore, Q6-10: Exploit)
- Difficulty adjustment: ±10% based on correctness
- Engagement modulation: Adjust difficulty by engagement score
- Response time consideration: Affects engagement calculation

**Engagement System** (`app/engagement/`):
- **Behavioral**: Response time deviation, inactivity, hint usage
- **Cognitive**: Accuracy trends, consistency, knowledge gaps
- **Affective**: Frustration, confusion, boredom detection
- **Fusion**: Composite engagement score (0-1)

**Analytics & Export** (`app/analytics/routes.py`):
- CSV export with engagement metrics per response
- JSON export with full session details
- All-student data aggregation for research

### API Endpoints

#### Authentication
- `POST /api/cbt/student` - Login/register student

#### Session Management
- `POST /api/cbt/session/start` - Start new test session
- `GET /api/cbt/session/{id}` - Get session details

#### Testing
- `GET /api/cbt/question/next/{session_id}` - Fetch next question
- `POST /api/cbt/response/submit` - Submit answer with **response_time_seconds**
- `GET /api/cbt/hint/{session_id}/{question_id}` - Get hint

#### Analytics
- `GET /api/analytics/engagement/{session_id}` - Session engagement data
- `GET /api/analytics/export/csv/{student_id}` - Download CSV with metrics
- `GET /api/analytics/export/all-data/{student_id}` - Download JSON with all data
- `GET /api/analytics/export/facial-data/{session_id}` - Facial analysis data

## Data Flow

```
User Input (Frontend)
    ↓
Question Display (app.js: showQuestion)
    ├→ Capture: questionStartTime = Date.now()
    ├→ Render question
    └→ User selects answer
    ↓
Submit Answer (app.js: submitSelectedAnswer)
    ├→ Calculate: responseTime = (Date.now() - questionStartTime) / 1000
    ├→ POST /api/cbt/response/submit
    └→ Include: response_time_seconds (MEASURED, not hardcoded)
    ↓
Backend Processing (backend/app/cbt/routes.py)
    ├→ Receive response_time_seconds
    ├→ Check correctness
    ├→ Calculate engagement indicators
    ├→ Store StudentResponse + EngagementMetric
    ├→ Adapt difficulty (Adaptation Engine)
    └→ Log to JSON file
    ↓
Feedback Display (app.js: showFeedbackModal)
    ├→ Show: ✓/✗ correctness
    ├→ Show: Explanation
    ├→ Show: Difficulty change
    ├→ Button: "Continue to Next Question"
    └→ Auto-dismiss: After 12 seconds (extended from 3s)
    ↓
Data Export (app.js: exportAsCSV/exportAllStudentData)
    ├→ GET /api/analytics/export/csv/{student_id}
    ├→ Receive: Fresh data with real response_time_seconds
    └→ Download: CSV/JSON file
```

## Recent Fixes (Session 3)

### ✅ Fixed: Modal Auto-Dismiss UX
- **Was**: 3-second auto-dismiss (users couldn't read content)
- **Now**: 12-second timeout with close button (user-controllable)
- **Location**: `frontend/app.js` lines 331-450

### ✅ Fixed: Response Time Measurement
- **Was**: Hardcoded to 30 seconds
- **Now**: Real measurement from question render to submission
- **How**: 
  - Store `questionStartTime` when question renders
  - Calculate: `(Date.now() - questionStartTime) / 1000`
  - Pass real elapsed time to backend
- **Location**: `frontend/app.js` lines 10 (variable), 653 (capture), 724 (calculation)

### ✅ Fixed: CSV Export Data Consistency
- **Was**: Using only first metric (stale data, no variation)
- **Now**: Proper metric-response mapping with fresh data
- **Location**: `backend/app/analytics/routes.py` lines 1148-1227

### ✅ Cleaned: Project Structure
- **Moved**: 58+ intermediate docs to `safe_to_delete/`
- **Kept**: 9 essential documents for research
- **Added**: `safe_to_delete/README.md` with documentation
- **Result**: Clean, professional structure ready for submission

## Running the System

### Start Backend
```bash
cd backend
source venv/bin/activate
python main.py
# Server runs on http://localhost:5000
```

### Start Frontend
```bash
cd frontend
npx http-server -p 3000
# Server runs on http://localhost:3000
```

### Run Tests
```bash
cd backend
pytest tests/
pytest tests/test_integration.py --verbose
```

### Export Data
1. Navigate to Dashboard
2. Click "Export All Data (JSON)" or "Export as CSV"
3. Data includes:
   - Real response times (in seconds)
   - All engagement metrics per response
   - Session summaries and student progress

## For Research Submission

**Essential Files to Include**:
1. `backend/` - Complete API implementation
2. `frontend/` - Complete UI code
3. `docs/ARCHITECTURE.md` - System design
4. `docs/TESTING.md` - Validation methodology
5. `docs/ACADEMIC_REPORT.md` - Research context
6. `README.md` - Quick start guide

**Files to Remove Before Submission**:
- `safe_to_delete/` folder (not needed)
- Sample exports (`1.csv`, `1.json`) - recreate fresh data
- `project_explanation.txt` - superseded by README.md

**Database Seeding**:
```bash
cd backend/scripts
python seed_questions.py  # Populate questions
```

## For Supervisor Review

**Recommended Reading Order**:
1. `README.md` (5 min) - Project overview
2. `docs/ACADEMIC_REPORT.md` (15 min) - Research context
3. `docs/ARCHITECTURE.md` (20 min) - System design
4. `docs/API_DOCUMENTATION.md` (15 min) - Technical reference
5. `backend/app/adaptation/engine.py` (20 min) - Core logic
6. `docs/TESTING.md` (10 min) - Validation approach

**Total Review Time**: ~85 minutes for complete understanding

## Project Statistics

- **Frontend**: 1,292 lines of JavaScript
- **Backend**: 2,500+ lines of Python (across modules)
- **Documentation**: 9 essential guides
- **Test Coverage**: Unit + integration tests
- **API Endpoints**: 10+ routes
- **Data Models**: 6 core models
- **Adaptation Algorithms**: IRT + Reinforcement Learning

---

**Last Updated**: January 5, 2026  
**Status**: Production-Ready, Research Submission Ready  
**Fixes Applied**: 4 critical issues resolved  
