# Interactive Frontend Implementation Checklist

## 📋 Pre-Implementation

### Environment Setup
- [ ] Node.js 14+ installed (`node --version`)
- [ ] npm or yarn available (`npm --version`)
- [ ] Backend running at `http://localhost:5000`
- [ ] Backend `/health` endpoint accessible
- [ ] SQLite database populated with questions

### Code Files Created
- [ ] `frontend/src/components/AdaptiveQuestion.jsx`
- [ ] `frontend/src/components/SessionTimeline.jsx`
- [ ] `frontend/src/components/EngagementIndicators.jsx`
- [ ] `frontend/src/pages/TestSessionPage.jsx`
- [ ] `frontend/src/styles/AdaptiveQuestion.css`
- [ ] `frontend/src/styles/SessionTimeline.css`
- [ ] `frontend/src/styles/EngagementIndicators.css`
- [ ] `frontend/src/styles/TestSession.css`
- [ ] `frontend/src/utils/api.js`
- [ ] `frontend/src/App.jsx` (updated with complete implementation)

### Documentation
- [ ] `FRONTEND_INTEGRATION_GUIDE.md` created
- [ ] `INTERACTIVE_FRONTEND_README.md` created
- [ ] Component API documented

---

## 🔧 Configuration

### Backend Verification
- [ ] Backend supports CORS headers
  ```python
  @app.after_request
  def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response
  ```

- [ ] Verify endpoints:
  ```bash
  curl http://localhost:5000/api/health
  # Expected: { "status": "healthy" }
  ```

- [ ] Create test student:
  ```bash
  curl -X POST http://localhost:5000/api/cbt/student \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com","name":"Test User"}'
  ```

### Environment Variables
- [ ] Create `frontend/.env`
  ```
  REACT_APP_API_URL=http://localhost:5000/api
  REACT_APP_ENABLE_DEBUG=true
  ```

---

## 📦 Installation

### Install Dependencies
```bash
cd frontend
npm install
```

### Verify Installation
```bash
npm list react react-dom
# Should show versions
```

---

## 🧪 Testing Components

### Test Each Component Independently

#### AdaptiveQuestion
```javascript
// In a test page
import AdaptiveQuestion from './components/AdaptiveQuestion';

const testQuestion = {
  question_id: '1',
  question_text: 'What is 2 + 2?',
  options: [
    { letter: 'A', text: '3' },
    { letter: 'B', text: '4' },
    { letter: 'C', text: '5' },
    { letter: 'D', text: '6' }
  ],
  difficulty: 0.5
};

<AdaptiveQuestion
  question={testQuestion}
  session={{ id: 'test', current_difficulty: 0.5 }}
  onSubmit={(data) => console.log(data)}
/>
```

#### SessionTimeline
```javascript
import SessionTimeline from './components/SessionTimeline';

const testResponses = [
  {
    question_id: '1',
    is_correct: true,
    difficulty: 0.5,
    response_time_seconds: 4.2
  }
];

<SessionTimeline
  session={{ id: 'test' }}
  responses={testResponses}
  engagementHistory={[{ engagement_score: 0.6 }]}
/>
```

#### EngagementIndicators
```javascript
import EngagementIndicators from './components/EngagementIndicators';

<EngagementIndicators
  currentEngagement={{
    engagement_score: 0.65,
    engagement_level: 'moderate',
    behavioral: { response_time_seconds: 5.0 },
    cognitive: { accuracy: 0.8 },
    affective: { frustration_level: 'neutral' }
  }}
  sessionData={{ correct_answers: 8, total_answered: 10 }}
  policyDebug={true}
/>
```

---

## 🚀 Running the Application

### Start Development Server
```bash
cd frontend
npm start
```

Expected output:
```
Compiled successfully!

Local:            http://localhost:3000
```

### Initial Screen
- Login form should appear
- Enter test email and name
- Click "Sign In / Register"

### Dashboard
- 4 subject cards should appear
- Click any subject to start test

### First Question
- Question should load
- 4 multiple choice options
- Difficulty bar visible
- "Submit Answer" button active

---

## 🔄 API Integration Testing

### Test 1: Submit Response
```bash
# With valid session from dashboard
curl -X POST http://localhost:5000/api/cbt/response/submit \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "YOUR_SESSION_ID",
    "question_id": "YOUR_QUESTION_ID",
    "student_answer": "A",
    "response_time_seconds": 5.0
  }'
```

Expected response:
```json
{
  "success": true,
  "is_correct": true/false,
  "current_difficulty": 0.525,
  "explanation": "...",
  "current_score": 50.0,
  ...
}
```

### Test 2: Engagement Data
```bash
curl http://localhost:5000/api/engagement/last/YOUR_SESSION_ID
```

Expected: Engagement metrics with score and indicators

### Test 3: Adaptation Logs
```bash
curl http://localhost:5000/api/adaptation/logs/YOUR_SESSION_ID
```

Expected: List of adaptation decisions with rationale

---

## 🎯 Functional Testing

### Test: Question Submission Flow
- [ ] Click option
- [ ] Option highlights
- [ ] Submit button enables
- [ ] Click submit
- [ ] API call made (check DevTools Network)
- [ ] Feedback appears
- [ ] Difficulty updates
- [ ] New question loads

### Test: Engagement Indicators
- [ ] Engagement score visible
- [ ] Behavioral section shows response time
- [ ] Cognitive section shows accuracy
- [ ] Affective section shows emotions
- [ ] Debug panel available (if enabled)

### Test: Timeline
- [ ] Click "History" button
- [ ] Timeline panel appears
- [ ] All questions listed
- [ ] Difficulty chart visible
- [ ] Engagement chart visible
- [ ] Rationale shown for each question

### Test: Adaptation Visibility
After question 5, 10, etc.:
- [ ] Difficulty changes shown
- [ ] Reason appears (e.g., "Excellent + Engaged → +0.10")
- [ ] New difficulty reflects policy
- [ ] Timeline shows decision

---

## 🐛 Debugging

### Browser DevTools
1. Open DevTools: F12 or Ctrl+Shift+I
2. **Network Tab**:
   - Check API calls to backend
   - Verify response status 200, 201
   - Check response payload (look for `current_difficulty`)
3. **Console Tab**:
   - No errors (red messages)
   - Check API utility logs
   - Look for warnings

### Common Issues

#### "Cannot GET /api/..."
- [ ] Backend not running
- [ ] Wrong API URL in `.env`
- [ ] CORS not enabled

**Fix**: 
```bash
# Check backend
curl http://localhost:5000/api/health

# Verify .env
cat frontend/.env
```

#### Difficulty Not Updating
- [ ] Response doesn't include `current_difficulty`
- [ ] Not at question boundary (5, 10, etc.)
- [ ] Session ended

**Fix**:
```bash
# Check response
curl -X POST http://localhost:5000/api/cbt/response/submit ... | python -m json.tool
# Should have "current_difficulty" field
```

#### Engagement Not Showing
- [ ] Endpoint returns 404
- [ ] Component doesn't receive props

**Fix**:
```bash
# Test endpoint
curl http://localhost:5000/api/engagement/last/SESSION_ID

# Check component
# Open DevTools → Console
# Look for errors in EngagementIndicators
```

---

## 📊 Test Scenario

### Recommended Test Sequence

1. **Create Student**
   - [ ] Login as "Test User"
   - [ ] Email: test@example.com

2. **Start Test**
   - [ ] Choose Mathematics
   - [ ] Session ID appears in logs

3. **Answer 5 Questions**
   - [ ] Difficulty stable
   - [ ] Engagement score updates
   - [ ] Timeline shows questions

4. **Check Adaptation**
   - [ ] At Q5, difficulty changes
   - [ ] Reason displayed
   - [ ] Chart updates

5. **Complete 10 Questions**
   - [ ] All questions answered
   - [ ] Final score shown
   - [ ] Summary statistics visible

6. **Review Results**
   - [ ] Difficulty trajectory visible
   - [ ] All adaptations explained
   - [ ] Engagement trend shown

---

## 📈 Performance Checks

### Load Time
- [ ] Home page: < 2 seconds
- [ ] First question: < 3 seconds
- [ ] Next question: < 2 seconds
- [ ] Answer submission: < 1 second response

### Browser Requirements
- [ ] Works in Chrome 90+
- [ ] Works in Firefox 88+
- [ ] Works in Safari 14+
- [ ] Works on mobile (iOS Safari, Chrome Mobile)

### Memory Usage
- [ ] No memory leaks (DevTools → Memory)
- [ ] < 100MB RAM during test
- [ ] Smooth scrolling in timeline

---

## ✨ Visual Verification

### UI Elements
- [ ] Header with app title
- [ ] Navigation buttons visible
- [ ] Question text readable
- [ ] Options properly spaced
- [ ] Submit button functional
- [ ] Progress bar updates
- [ ] Colors match design (purple, green, red, orange)

### Responsive Design
- [ ] Desktop (1920px): 2-column layout
- [ ] Tablet (768px): 1-column with sidebar
- [ ] Mobile (375px): Stacked, scrollable
- [ ] All text readable on mobile

### Animations
- [ ] Smooth transitions on hover
- [ ] Progress bar animates
- [ ] Charts animate on update
- [ ] No jank or stuttering

---

## 🔒 Security Check

- [ ] API URL configured (not hardcoded)
- [ ] No sensitive data in localStorage (only student ID)
- [ ] Session ID used correctly
- [ ] No XSS vulnerabilities (React default escaping)
- [ ] No CSRF (API calls use fetch, backend validates)

---

## 📚 Documentation

- [ ] Updated README with quick start
- [ ] Component props documented
- [ ] API endpoints listed
- [ ] Troubleshooting guide created
- [ ] Code comments added where complex

---

## 🚀 Deployment Readiness

### Before Production

```bash
# Production build
npm run build

# Test build locally
npm install -g serve
serve -s build

# Should run at http://localhost:3000
```

- [ ] Build completes without errors
- [ ] No console warnings
- [ ] Bundle size reasonable (< 5MB)
- [ ] All assets included

### Environment Variables (Production)
```env
REACT_APP_API_URL=https://your-api.com/api
REACT_APP_ENABLE_DEBUG=false
```

---

## 🎓 Research Data Collection

### Enable Logging
- [ ] Engagement logs created in backend
- [ ] Adaptation decisions logged
- [ ] Question responses recorded
- [ ] Timestamps included

### Data Export
```bash
# Collected data location
backend/logs/engagement_logs/
backend/logs/adaptation_logs/

# Database
backend/instance/database.db
```

### Metrics to Track
- [ ] Student ID → Question ID → Response
- [ ] Difficulty before/after
- [ ] Engagement score
- [ ] Response time
- [ ] Policy decision rationale
- [ ] Learning outcome (final score)

---

## ✅ Final Checklist

### Core Functionality
- [ ] Login/Register works
- [ ] Question displays correctly
- [ ] Options are selectable
- [ ] Submit works (API call succeeds)
- [ ] Feedback appears (correct/incorrect)
- [ ] New difficulty shown
- [ ] Next question loads
- [ ] Test completes at 10 questions

### Engagement Features
- [ ] Engagement score visible
- [ ] Behavioral indicators update
- [ ] Cognitive indicators calculate
- [ ] Affective indicators display
- [ ] Recommendations appear

### Adaptation Visibility
- [ ] Difficulty changes visible
- [ ] Policy rationale shown
- [ ] Timeline updates
- [ ] Charts visualize progression

### Polish
- [ ] No console errors
- [ ] Responsive on all screen sizes
- [ ] Loading states functional
- [ ] Error messages helpful
- [ ] Animations smooth
- [ ] Colors match design
- [ ] Readable on all devices

---

## 🎯 Success Criteria

✅ **Application is ready when**:
1. All components render without errors
2. User can complete 10-question test
3. Difficulty adapts every 5 questions
4. Engagement metrics visible and updating
5. Timeline shows complete progression
6. Adaptation rationale transparent
7. No API errors or network issues
8. Responsive design works on mobile
9. Data collected and logged correctly
10. Ready for real user testing

---

## 📝 Log File Locations

Track these for debugging:

```
Frontend Logs (Browser Console):
  - API errors
  - Component state changes
  - Fetch requests/responses

Backend Logs:
  backend/logs/engagement_logs/
  backend/logs/adaptation_logs/

Database:
  backend/instance/database.db

Session Data:
  localStorage: currentStudent, currentSession
```

---

## 🎉 Next Steps After Implementation

1. **User Testing**
   - [ ] Test with 5-10 real students
   - [ ] Collect feedback on UI/UX
   - [ ] Monitor engagement metrics

2. **Data Analysis**
   - [ ] Review adaptation logs
   - [ ] Calculate learning gains
   - [ ] Analyze engagement patterns

3. **Refinement**
   - [ ] Adjust policy if needed
   - [ ] Improve UI based on feedback
   - [ ] Add features based on usage

4. **Publication**
   - [ ] Prepare research paper
   - [ ] Include metrics and results
   - [ ] Discuss findings

---

**Status**: Ready to implement
**Estimated Time**: 30-60 minutes
**Difficulty**: Medium (most code provided)
**Support**: See documentation files

Good luck with your interactive tutoring system! 🚀
