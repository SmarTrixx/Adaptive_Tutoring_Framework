# Adaptive Intelligent Tutoring Framework

A computer-based testing (CBT) system that adapts learning difficulty and content in real-time based on continuous engagement and performance monitoring.

## Documentation Status (January 10, 2026)

**✅ Refactored:** All documentation has been audited and corrected to accurately reflect implemented features only.

**Key Changes:**
- Removed misleading claims about facial emotion recognition (infrastructure only, not active)
- Removed misleading claims about reinforcement learning in core system (disabled in favor of rule-based)
- Added clear separation between ✅ **implemented** and 🔜 **future/optional** features
- Created `CLEAN_WORKSPACE_GUIDE.md` for minimal project structure
- Archived truly unused modules (policy.py, performance_window.py) to `archive_unused_modules/`

**For Full Details:** See `ACADEMIC_SYSTEM_OVERVIEW2.md`, `MODULE_USAGE_ANALYSIS.md`, and `CLEAN_WORKSPACE_GUIDE.md`

---

## System Overview

The Adaptive Intelligent Tutoring Framework implements an intelligent testing environment that:

- **Monitors engagement** through behavioral, cognitive, and affective indicators
- **Adapts difficulty** based on student performance and engagement state
- **Tracks learning progress** with detailed behavioral and cognitive metrics
- **Exports comprehensive data** for academic research and analysis

The system maintains stable engagement by adjusting question difficulty, pacing, and pedagogical interventions (hints, feedback) based on real-time learner state.

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python 3.8+, Flask REST API |
| **ORM** | SQLAlchemy with SQLite/PostgreSQL |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Data Processing** | NumPy, Pandas |

## Architecture

The system follows a three-tier REST architecture:

```
┌─────────────────────────────────────────┐
│   Frontend (Browser)                    │
│   - Session management                  │
│   - Question display & interaction      │
│   - Real-time engagement tracking       │
└────────────────┬────────────────────────┘
                 │ REST API
┌────────────────▼────────────────────────┐
│   Backend (Flask)                       │
│   - CBT system (test logic)             │
│   - Adaptation engine                   │
│   - Engagement calculator               │
│   - Data export & analytics             │
└────────────────┬────────────────────────┘
                 │ ORM
┌────────────────▼────────────────────────┐
│   Database (SQLAlchemy)                 │
│   - Student records                     │
│   - Sessions & responses                │
│   - Engagement metrics                  │
│   - Adaptation logs                     │
└─────────────────────────────────────────┘
```

## Project Structure

```
backend/
├── app/
│   ├── models/           # Database schemas (Student, Session, Response, etc.)
│   ├── cbt/              # Test system (session, question selection, submission)
│   ├── adaptation/       # Difficulty mapping and adaptation logic
│   ├── engagement/       # Engagement indicators and scoring
│   ├── analytics/        # Data export, analytics, reset functionality
│   └── __init__.py       # Flask app factory, blueprint registration
├── main.py              # Server entry point
├── config.py            # Configuration
└── requirements.txt     # Python dependencies

frontend/
├── index.html           # Single-page app structure
├── app.js              # Complete test interface (2200+ lines)
│                       # - Session management
│                       # - Question rendering
│                       # - Response submission
│                       # - Engagement tracking
│                       # - Data persistence (localStorage)
├── styles.css          # Responsive design
└── package.json

docs/                   # Detailed documentation
├── ARCHITECTURE.md     # Technical design
├── API_DOCUMENTATION.md # REST endpoints
├── SETUP.md           # Installation & running
└── ...

reset_data.py          # CLI tool for data-only reset (preserves schema)
```

## Core Systems

### 1. Computer-Based Testing (CBT)

**Features:**
- Session creation with configurable question count (default 10)
- Difficulty-aware selection - questions selected from appropriate difficulty bands
- Question randomization - varied questions within difficulty range
- Response tracking - captures answer, time, and behavioral metrics per question
- Session completion - automatic end when question limit reached

**Key Endpoints:**
- `POST /api/cbt/student` - Student login/registration
- `POST /api/cbt/session/start` - Create new test session
- `GET /api/cbt/question/next/:session_id` - Fetch next question
- `POST /api/cbt/response/submit` - Submit answer with all metrics
- `GET /api/cbt/response/:session_id/:question_id` - Retrieve previous response
- `GET /api/cbt/hint/:session_id/:question_id` - Get contextual hint

### 2. Engagement Indicators

The system tracks four categories of indicators in real-time:

| Category | Indicators | Measurement |
|----------|-----------|-------------|
| **Behavioral** | Response time, navigation, option changes | Direct observation |
| **Cognitive** | Accuracy, learning progress, knowledge gaps | Performance-based |
| **Affective** | Confidence, frustration, interest | Inferred from behavior |
| **Temporal** | Inactivity, hesitation patterns, engagement trends | Time-based analysis |

**Engagement Score:**
- Range: 0.0 (very low) to 1.0 (very high)
- Levels: Low (< 0.4), Medium (0.4-0.7), High (> 0.7)
- Updated after each response submission
- Composite score from all indicator categories

**Key Endpoints:**
- `GET /api/engagement/get/:session_id` - Current engagement score
- `POST /api/engagement/track` - Record engagement metrics

### 3. Adaptive Engine

**Difficulty Adaptation:**
- Range: 0.0 (easiest) to 1.0 (hardest)
- Maps to question difficulty bands:
  - 0.0-0.35: Easy questions (difficulty 0.1-0.4)
  - 0.35-0.65: Medium questions (difficulty 0.35-0.65)
  - 0.65-1.0: Hard questions (difficulty 0.6-0.95)
- Updated after each response based on correctness
- Adjusted by ±5-10% per response

**Adaptation Logic:**
- Correct answer → Difficulty increases slightly
- Incorrect answer → Difficulty decreases
- Magnitude of change scaled by engagement level

### 4. Data Collection & Export

**Tracked per Response:**
- Student answer and correctness
- Response time (seconds)
- Navigation patterns (Prev/Next clicks)
- Option changes (initial vs final answer)
- Hints requested and used
- Hesitation indicators
- Inactivity duration
- Facial monitoring data (if enabled)
- Engagement indicators at submission
- Timestamp (ISO 8601)

**Export Formats:**
- **CSV**: Tabular data with all columns for spreadsheet analysis
- **JSON**: Structured nested data for programmatic access

**Key Endpoints:**
- `GET /api/analytics/export/csv/:student_id` - Download CSV
- `GET /api/analytics/export/all-data/:student_id` - Download JSON
- `GET /api/analytics/dashboard/:student_id` - Analytics summary

## Running the System

### Local Development

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python main.py
```
Server runs on `http://localhost:5000`

**Frontend:**
Open `frontend/index.html` in a browser or serve via:
```bash
cd frontend
python -m http.server 3000
```
Navigate to `http://localhost:3000` or open index.html directly

### Configuration

**Backend (`backend/config.py`):**
- `DEBUG` - Enable/disable debug mode
- `FLASK_ENV` - Environment (development/production)
- `DATABASE_URL` - Database connection string

**Frontend (`frontend/app.js`):**
- `API_BASE_URL` - Backend API location (default: `http://localhost:5000/api`)

## Data Management

### Data Reset

To reset all session and response data while preserving database schema:

```bash
python reset_data.py
```

Interactive confirmation required. Use `--confirm` flag to skip:
```bash
python reset_data.py --confirm
```

**What is deleted:**
- All student sessions and responses
- All engagement metrics
- All adaptation logs

**What is preserved:**
- Database schema and indexes
- Question bank
- Student profile records

### Database Schema

**Core Models:**
- `Student` - User profiles with email, name, preferred difficulty
- `Session` - Test instances with student, subject, difficulty tracking
- `StudentResponse` - Individual question responses with all behavioral/cognitive data
- `EngagementMetric` - Engagement scores per response
- `Question` - Question bank with difficulty ratings
- `QuestionDifficulty` - Difficulty metadata

**Relationships:**
```
Student (1) ──→ (many) Session
Session (1) ──→ (many) StudentResponse
StudentResponse (1) ──→ (1) EngagementMetric
StudentResponse (many) ──→ (1) Question
```

## Key Features

### Persistent Sessions
- Students can resume interrupted tests from exact question
- Navigation history and state preserved across page reloads
- Question history restored automatically via localStorage

### Question Randomization
- Questions randomly selected within difficulty band
- Prevents same question repetition across sessions
- Ensures varied question presentation within same adaptation level

### Modal Feedback System
- Feedback modal displays after each response with results and metrics
- Auto-closes after 12 seconds for unattended submissions
- User can close immediately without waiting
- Timeout properly cleared to prevent double advancement

### Comprehensive Data Tracking
Every interaction recorded with:
- Exact timestamps (ISO 8601)
- Complete behavioral metrics
- Cognitive performance indicators
- Engagement state at submission time
- Metadata for analysis

## API Response Format

All endpoints return JSON with consistent structure:

**Success Response:**
```json
{
  "success": true,
  "data": { /* endpoint-specific data */ }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Human-readable error message"
}
```

## Monitoring & Validation

**Frontend Console Logging:**
Enable debug logging in `app.js` for tracking:
- `[SESSION]` - Session lifecycle events
- `[FETCH-NEXT]` - Question fetching
- `[SUBMISSION]` - Response submission
- `[MODAL]` - Modal behavior
- `[ENGAGEMENT]` - Engagement calculation
- `[TIMER]` - Elapsed time tracking
- `[PERSIST]` - Data persistence

**Backend Logging:**
Flask development server logs:
- HTTP requests (method, endpoint, status)
- Database operations
- Adaptation decisions
- Engagement calculations

## Troubleshooting

| Issue | Solution |
|-------|----------|
| API calls fail with 404 | Verify `API_BASE_URL` in `app.js` matches backend |
| Questions not loading | Check backend is running on port 5000 |
| Data not saving | Verify database path accessible and writable |
| Session lost on reload | Check browser allows localStorage |
| Port 5000 in use | `lsof -i :5000` then `kill -9 <PID>` |

## Academic Suitability

The system is designed for research and academic testing:

- **Data completeness**: Every interaction recorded with timestamp
- **Data consistency**: All metrics calculated deterministically
- **Data realism**: Actual student behavior, no simulations
- **Reproducibility**: Identical test conditions for all students
- **Exportability**: Data available in standard formats (CSV/JSON)

For detailed academic documentation, see `ACADEMIC_SYSTEM_OVERVIEW.md`

## Documentation Structure

- **README.md** (this file) - Technical overview and quickstart
- **ACADEMIC_SYSTEM_OVERVIEW.md** - Academic methodology and framework
- **docs/ARCHITECTURE.md** - Detailed system architecture
- **docs/API_DOCUMENTATION.md** - Complete REST API reference
- **docs/SETUP.md** - Installation and deployment guide

## Version

**Version**: 1.0.0  
**Last Updated**: January 2026

