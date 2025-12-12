# Installation & Setup Guide

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Node.js 14+ (for frontend development)
- Git (for version control)

## Backend Setup

### 1. Navigate to Backend Directory
```bash
cd adaptive-tutoring-framework/backend
```

### 2. Create Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Environment Variables
Create a `.env` file in the backend directory:
```
FLASK_ENV=development
FLASK_APP=main.py
DATABASE_URL=sqlite:///tutoring_system.db
SECRET_KEY=your-secret-key-here
```

### 5. Initialize Database
```bash
python main.py
```

The database will be created automatically on first run.

### 6. Load Sample Data (Optional)
```bash
python -c "
from main import app, db
from app.models import Question, Student
import json

with app.app_context():
    # Add sample questions
    questions = [
        {
            'subject': 'Mathematics',
            'topic': 'Algebra',
            'difficulty': 0.3,
            'question_text': 'What is 2+2?',
            'option_a': '3',
            'option_b': '4',
            'option_c': '5',
            'option_d': '6',
            'correct_option': 'B',
            'explanation': '2 plus 2 equals 4',
            'hints': ['Think about counting', 'Count: 1, 2, 3, 4']
        }
    ]
    
    for q_data in questions:
        q = Question(**q_data)
        db.session.add(q)
    
    db.session.commit()
    print('Sample data loaded!')
"
```

### 7. Run Backend Server
```bash
python main.py
```

Server will start at `http://localhost:5000`

## Frontend Setup

### 1. Navigate to Frontend Directory
```bash
cd adaptive-tutoring-framework/frontend
```

### 2. Create Local Server (if needed)
For development, you can use Python's built-in server:

```bash
# Python 3
python -m http.server 8000

# Python 2
python -m SimpleHTTPServer 8000
```

Or use Node.js http-server:
```bash
npm install -g http-server
http-server -p 8000
```

### 3. Access the Application
Open your browser and navigate to:
- Frontend: `http://localhost:8000`
- Backend API: `http://localhost:5000`

## Testing

### Run Backend Tests
```bash
cd backend
pytest
```

### Test API Endpoints
Use cURL, Postman, or the provided frontend:

```bash
# Create a student
curl -X POST http://localhost:5000/api/cbt/student \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test Student"}'

# Start a session
curl -X POST http://localhost:5000/api/cbt/session/start \
  -H "Content-Type: application/json" \
  -d '{"student_id":"<student_id>","subject":"Mathematics","num_questions":10}'

# Get next question
curl http://localhost:5000/api/cbt/question/next/<session_id>
```

## Project Structure

```
adaptive-tutoring-framework/
├── backend/
│   ├── app/
│   │   ├── models/           # Data models
│   │   ├── engagement/       # Engagement tracking
│   │   ├── adaptation/       # Adaptive engine
│   │   ├── cbt/              # Testing system
│   │   └── analytics/        # Analytics
│   ├── requirements.txt      # Python dependencies
│   ├── config.py            # Configuration
│   ├── main.py              # Entry point
│   └── tutoring_system.db   # SQLite database
├── frontend/
│   ├── index.html           # Main HTML
│   ├── app.js              # Application logic
│   ├── styles.css          # Styles
│   └── src/
│       ├── components/      # React components (future)
│       ├── pages/          # Page components (future)
│       └── utils/          # Helper functions
└── docs/
    ├── ARCHITECTURE.md     # System design
    ├── ENGAGEMENT_INDICATORS.md
    ├── API_DOCUMENTATION.md
    └── SETUP.md           # This file
```

## Configuration

### Backend Config (`config.py`)
```python
# Engagement thresholds
ENGAGEMENT_THRESHOLDS = {
    'response_time_slow': 30,      # seconds
    'response_time_fast': 5,       # seconds
    'inactivity_threshold': 60,    # seconds
    'low_engagement_score': 0.3,
    'high_engagement_score': 0.7
}

# Adaptation parameters
ADAPTATION_CONFIG = {
    'min_difficulty': 0.1,
    'max_difficulty': 0.9,
    'difficulty_step': 0.1,
    'max_retries': 3,
    'hint_threshold': 0.5
}
```

Modify these values to adjust system behavior.

## Troubleshooting

### Issue: Port Already in Use
```bash
# Change Flask port
python main.py --port 5001

# Change frontend port
http-server -p 8001
```

### Issue: Database Lock
```bash
# Delete the database and reinitialize
rm backend/tutoring_system.db
python backend/main.py
```

### Issue: CORS Errors
- Ensure Flask has CORS enabled (it does by default)
- Check that API_BASE_URL in frontend/app.js matches your backend server

### Issue: Dependencies Not Installing
```bash
# Upgrade pip
pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v
```

## Production Deployment

### 1. Use PostgreSQL Instead of SQLite
Update `.env`:
```
DATABASE_URL=postgresql://user:password@localhost/tutoring_db
```

Install PostgreSQL driver:
```bash
pip install psycopg2-binary
```

### 2. Set Production Configuration
```
FLASK_ENV=production
DEBUG=False
```

### 3. Use Production WSGI Server
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

### 4. Restrict CORS in Production
Update `app/__init__.py`:
```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://yourdomain.com"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"]
    }
})
```

### 5. Use HTTPS
Deploy behind a reverse proxy (Nginx) with SSL certificates.

### 6. Environment Variables
Use a secret management service (AWS Secrets Manager, HashiCorp Vault, etc.)

## Next Steps

1. **Add Sample Questions**: Populate the question bank
2. **Customize Thresholds**: Adjust engagement thresholds for your use case
3. **Implement Authentication**: Add user authentication and authorization
4. **Frontend Enhancement**: Build a more sophisticated frontend
5. **Data Analysis**: Use analytics to improve the framework
6. **Testing**: Conduct user testing and collect feedback

## Support

For issues or questions:
1. Check the documentation in `/docs`
2. Review API examples in `API_DOCUMENTATION.md`
3. Check Flask and SQLAlchemy documentation
4. Open an issue in the project repository

## License

This project is for academic research purposes.
