# Quick Reference Card

## 📋 Adaptive Intelligent Tutoring Framework - Quick Start

### ⚡ Start in 5 Minutes

```bash
# Terminal 1: Backend
cd backend
python3 -m venv venv
source venv/bin/activate  # or: venv\Scripts\activate (Windows)
pip install -r requirements.txt
python main.py

# Terminal 2: Frontend
cd frontend
python -m http.server 8000
```

**Access**: http://localhost:8000

---

## 🔗 API Quick Links

### Student Management
```bash
# Create student
POST /api/cbt/student
{"email": "user@example.com", "name": "User Name"}

# Get student
GET /api/cbt/student/{student_id}
```

### Test Sessions
```bash
# Start session
POST /api/cbt/session/start
{"student_id": "uuid", "subject": "Mathematics", "num_questions": 10}

# End session
POST /api/cbt/session/end/{session_id}

# Get session summary
GET /api/cbt/session/{session_id}
```

### Questions & Answers
```bash
# Get next question
GET /api/cbt/question/next/{session_id}?difficulty=0.5

# Submit answer
POST /api/cbt/response/submit
{"session_id": "uuid", "question_id": "uuid", "student_answer": "B", "response_time_seconds": 25.5}

# Get hint
GET /api/cbt/hint/{session_id}/{question_id}
```

### Engagement & Adaptation
```bash
# Track engagement
POST /api/engagement/track
{"student_id": "uuid", "session_id": "uuid", "response_data": {...}, "affective_feedback": {...}}

# Get recommendations
GET /api/adaptation/recommend/{student_id}/{session_id}
```

### Analytics
```bash
# Get dashboard
GET /api/analytics/dashboard/{student_id}

# Get progress
GET /api/analytics/student/{student_id}/progress

# Get engagement trends
GET /api/analytics/student/{student_id}/engagement_trends
```

---

## 📚 Documentation Map

| Need | Read This |
|------|-----------|
| **Project overview** | [README.md](README.md) |
| **Install/setup** | [docs/SETUP.md](docs/SETUP.md) |
| **Architecture** | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| **Engagement system** | [docs/ENGAGEMENT_INDICATORS.md](docs/ENGAGEMENT_INDICATORS.md) |
| **All API endpoints** | [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) |
| **For developers** | [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) |
| **Testing** | [docs/TESTING.md](docs/TESTING.md) |
| **Production deploy** | [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) |

---

## 🔧 Common Commands

```bash
# Backend
cd backend
source venv/bin/activate              # Activate venv
pip install -r requirements.txt       # Install packages
python main.py                        # Run server
pytest                                # Run tests

# Database
python scripts/seed_questions.py      # Load sample data
sqlite3 tutoring_system.db            # Open database

# Frontend
cd frontend
python -m http.server 8000            # Start server
http-server -p 8000                   # Alternative (requires npm)
```

---

## 📊 Key Endpoints (Quick Reference)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/cbt/student` | POST | Create student |
| `/api/cbt/session/start` | POST | Start test |
| `/api/cbt/question/next/{id}` | GET | Get question |
| `/api/cbt/response/submit` | POST | Submit answer |
| `/api/cbt/session/end/{id}` | POST | End test |
| `/api/engagement/track` | POST | Track engagement |
| `/api/adaptation/recommend/{s}/{ss}` | GET | Get adaptations |
| `/api/analytics/dashboard/{id}` | GET | View dashboard |

---

## 🎯 Engagement Framework

### Dimensions (Weights)
- **Behavioral** (35%): Response time, attempts, navigation, hints, inactivity
- **Cognitive** (40%): Accuracy, learning progress, knowledge gaps
- **Affective** (25%): Confidence, frustration, interest

### Score Range
- **0.0-0.3**: Low engagement → Intervention needed
- **0.3-0.7**: Medium engagement → Normal progression
- **0.7-1.0**: High engagement → Optimal learning

### Adaptations Triggered
- Low accuracy ≤ 40% → Decrease difficulty
- High accuracy ≥ 80% AND engagement ≥ 70% → Increase difficulty
- Low confidence < 40% + high frustration > 60% → Provide hints
- Knowledge gaps identified → Focus content

---

## 🚀 Deployment Quick Start

### Heroku
```bash
git push heroku main
heroku config:set FLASK_ENV=production
heroku run python backend/main.py
```

### Docker
```bash
docker-compose up -d
# Access at http://localhost:5000
```

### VPS (Ubuntu)
See [DEPLOYMENT.md](docs/DEPLOYMENT.md#option-3-traditional-vps-deployment-ubuntunginx)

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 5000 in use | `lsof -i :5000` then `kill -9 <PID>` |
| Database error | `rm backend/tutoring_system.db` then rerun |
| Import error | `pip install -r requirements.txt` |
| CORS error | Ensure backend running on http://localhost:5000 |
| Module not found | Check venv activated: `source venv/bin/activate` |

More troubleshooting: [SETUP.md](docs/SETUP.md#troubleshooting)

---

## 📈 Database Models

```
Student
├─ id, email, name
├─ preferred_difficulty, preferred_pacing
└─ relationships: sessions, engagement_metrics

Question
├─ id, subject, topic, difficulty
├─ question_text, options A-D, correct_option
├─ explanation, hints[]
└─ relationships: responses

Session
├─ id, student_id, subject, status
├─ total_questions, score_percentage
├─ start_time, end_time
└─ relationships: responses, metrics, logs

StudentResponse
├─ id, session_id, question_id
├─ student_answer, is_correct
├─ response_time_seconds, attempts, hints_used
└─ relationships: engagement_metrics

EngagementMetric
├─ behavioral_score, cognitive_score, affective_score
├─ composite_engagement_score, engagement_level
└─ timestamp

AdaptationLog
├─ adaptation_type (difficulty/pacing/hints/content)
├─ old_value, new_value, reason
└─ effectiveness tracking
```

---

## 🎓 Learning Path

1. **Beginner**: Read [README.md](README.md)
2. **User**: Follow [SETUP.md](docs/SETUP.md)
3. **Developer**: Study [ARCHITECTURE.md](docs/ARCHITECTURE.md) + [DEVELOPMENT.md](docs/DEVELOPMENT.md)
4. **Deployer**: Review [DEPLOYMENT.md](docs/DEPLOYMENT.md)
5. **Researcher**: Deep dive [ENGAGEMENT_INDICATORS.md](docs/ENGAGEMENT_INDICATORS.md)

---

## 📞 Key Contacts

- **Issues**: Check docs first, then code comments
- **Setup**: [SETUP.md](docs/SETUP.md)
- **Development**: [DEVELOPMENT.md](docs/DEVELOPMENT.md)
- **API**: [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)

---

## ✅ Pre-Launch Checklist

- [ ] Backend installed: `pip install -r requirements.txt`
- [ ] Database exists: `python main.py` creates it
- [ ] Sample data loaded: `python scripts/seed_questions.py`
- [ ] Tests pass: `pytest`
- [ ] Frontend accessible: http://localhost:8000
- [ ] API health check: `curl http://localhost:5000/health`

---

## 🎉 You're Ready!

1. **Start Backend**: `python main.py` (in backend/)
2. **Start Frontend**: `python -m http.server 8000` (in frontend/)
3. **Visit**: http://localhost:8000
4. **Read**: [README.md](README.md) for overview

---

## 📝 Important Files

```
adaptive-tutoring-framework/
├── README.md                    ← Start here
├── INDEX.md                     ← Navigation guide
├── IMPLEMENTATION_SUMMARY.md    ← What's done
├── PROJECT_COMPLETION_REPORT.md ← Full report
├── backend/
│   ├── main.py                 ← Run this
│   ├── config.py               ← Configure this
│   ├── requirements.txt         ← Install first
│   └── scripts/seed_questions.py ← Load data
├── frontend/
│   ├── index.html              ← Main page
│   └── app.js                  ← JavaScript
└── docs/
    ├── SETUP.md                ← Installation
    ├── ARCHITECTURE.md         ← System design
    ├── API_DOCUMENTATION.md    ← Endpoints
    └── DEPLOYMENT.md           ← Production
```

---

## 🔑 Environment Variables

```bash
FLASK_ENV=development              # or production
DATABASE_URL=sqlite:///tutoring_system.db
SECRET_KEY=your-secret-key
DEBUG=True                         # Development only
```

---

## 🌐 URLs

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:8000 |
| **API** | http://localhost:5000 |
| **Health Check** | http://localhost:5000/health |
| **API Base** | http://localhost:5000/api |

---

## ⚙️ System Requirements

- Python 3.8+
- pip (Python package manager)
- ~100MB disk space
- No special hardware needed

---

## 🏆 Project Stats

- **Files**: 32
- **Code Lines**: 4720+
- **API Endpoints**: 20+
- **Database Models**: 6
- **Documentation Pages**: 8
- **Status**: ✅ Production Ready

---

**Version**: 1.0.0 | **Status**: ✅ Complete | **Last Updated**: January 2024

For more info: [INDEX.md](INDEX.md) | [README.md](README.md)
