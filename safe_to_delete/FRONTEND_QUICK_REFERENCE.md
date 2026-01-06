# Interactive Frontend Quick Reference Card

## 🚀 Start Here (3 Steps)

```bash
# 1. Install dependencies
cd frontend && npm install

# 2. Create .env
echo "REACT_APP_API_URL=http://localhost:5000/api" > .env

# 3. Start development server
npm start
# Opens http://localhost:3000
```

---

## 📦 Files Created

### Components (Copy to `src/components/`)
```
✅ AdaptiveQuestion.jsx         - Question display & submission
✅ SessionTimeline.jsx          - History & charts
✅ EngagementIndicators.jsx     - Real-time monitoring
✅ TestSessionPage.jsx          - Full layout
```

### Styles (Copy to `src/styles/`)
```
✅ AdaptiveQuestion.css
✅ SessionTimeline.css
✅ EngagementIndicators.css
✅ TestSession.css
```

### Utilities (Copy to `src/utils/`)
```
✅ api.js                       - API integration
```

### App (Replace `src/App.jsx`)
```
✅ App.jsx                      - Complete app with login
```

---

## 🎯 Key Features

| Feature | Status | Location |
|---------|--------|----------|
| Live question display | ✅ | AdaptiveQuestion |
| Response submission | ✅ | api.js → ResponseAPI |
| Difficulty updates | ✅ | TestSessionPage |
| Engagement monitoring | ✅ | EngagementIndicators |
| Question history | ✅ | SessionTimeline |
| Adaptation rationale | ✅ | SessionTimeline |
| Policy debug mode | ✅ | EngagementIndicators |
| Mobile responsive | ✅ | TestSession.css |
| User login | ✅ | App.jsx |

---

## 🔌 API Cheat Sheet

### Session Start
```javascript
await SessionAPI.startSession(studentId, 10, 'Mathematics')
// Returns: { session: { id, current_difficulty, ... } }
```

### Get Question
```javascript
await SessionAPI.getNextQuestion(sessionId)
// Returns: { question: { question_id, question_text, options, difficulty } }
```

### Submit Response
```javascript
await ResponseAPI.submitResponse(sessionId, questionId, answer, responseTime)
// Returns: { isCorrect, newDifficulty, explanation, ... }
```

### Get Engagement
```javascript
await EngagementAPI.getLastEngagement(sessionId)
// Returns: { engagement_score, engagement_level, behavioral, cognitive, affective }
```

### Get Logs
```javascript
await AdaptationAPI.getAdaptationLogs(sessionId)
// Returns: [ { rationale, delta, performance, ... }, ... ]
```

---

## 🎨 Component Props

### AdaptiveQuestion
```jsx
<AdaptiveQuestion
  question={{ question_id, question_text, options, difficulty }}
  session={{ id, current_difficulty }}
  onSubmit={(responseData) => {}}
  isLoading={false}
/>
```

### SessionTimeline
```jsx
<SessionTimeline
  session={session}
  responses={[{ question_id, is_correct, difficulty, response_time_seconds }]}
  engagementHistory={[{ engagement_score, engagement_level }]}
  adaptationHistory={[{ rationale, delta }]}
/>
```

### EngagementIndicators
```jsx
<EngagementIndicators
  currentEngagement={{
    engagement_score,
    engagement_level,
    behavioral: { response_time_seconds, hints_used, attempts_count },
    cognitive: { accuracy, learning_progress },
    affective: { frustration_level, interest_level, confidence_level }
  }}
  sessionData={{ correct_answers, total_answered, avg_response_time }}
  policyDebug={true}
/>
```

### TestSessionPage
```jsx
<TestSessionPage
  studentId={studentId}
  sessionId={sessionId}
  subject="Mathematics"
/>
```

---

## 🧪 Testing Commands

### Test Backend Connection
```bash
curl http://localhost:5000/api/health
# Expected: { "status": "healthy" }
```

### Test API Endpoint
```bash
curl -X POST http://localhost:5000/api/cbt/response/submit \
  -H "Content-Type: application/json" \
  -d '{"session_id":"X","question_id":"Y","student_answer":"A","response_time_seconds":5.0}'
```

### Check Logs
```bash
tail -f backend/logs/engagement_logs/*.json
tail -f backend/logs/adaptation_logs/*.json
```

---

## 🐛 Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| "Cannot GET /api/..." | Backend not running: `python3 main.py` |
| Difficulty not updating | Check: Question at boundary (5, 10, etc.) |
| Engagement not showing | Test: `/api/engagement/last/{sessionId}` |
| CSS not loading | Check: Import statements in components |
| Login fails | Verify: Backend `/api/cbt/student` endpoint |
| TypeErrors in console | Check: Props passed to components |

---

## 📊 Data Collection

### What's Logged
```
✅ Student responses (question_id, answer, is_correct, response_time)
✅ Engagement metrics (behavioral, cognitive, affective signals)
✅ Adaptation decisions (difficulty delta, rationale)
✅ Session summary (score, duration, performance)
```

### Where It's Stored
```
Frontend: localStorage (student, session data)
Backend: database + logs/engagement_logs/
        + logs/adaptation_logs/
```

### Data Export
```bash
# View engagement logs
cat backend/logs/engagement_logs/*.json

# View database
sqlite3 backend/instance/database.db ".tables"
```

---

## 🎯 User Flow

```
Login
  ↓
Select Subject
  ↓
Get Session ID & First Question
  ↓
LOOP (until 10 questions):
  Read Question
  Select Answer
  Submit (GET response time) → API
  Show Feedback (correct/incorrect)
  Show New Difficulty + Rationale
  Show Updated Engagement
  Add to Timeline
  Fetch Next Question
  ↓
End of Test
  Show Final Score
  Show Summary Stats
  Show Full Timeline
  Option: Start New Test
```

---

## 🌐 Environment Variables

### Development (.env)
```
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_ENABLE_DEBUG=true
```

### Production (.env)
```
REACT_APP_API_URL=https://your-api.com/api
REACT_APP_ENABLE_DEBUG=false
```

---

## 📱 Responsive Breakpoints

```css
Desktop:  ≥ 1024px  → 2-column layout
Tablet:   768-1024px → 1-column with sidebar
Mobile:   < 768px   → Full-width, stacked
```

---

## 🔐 Security Checklist

- [ ] API URL in `.env` (not hardcoded)
- [ ] HTTPS in production
- [ ] CORS configured at backend
- [ ] Session ID used (not stored in localStorage insecurely)
- [ ] No sensitive data logged
- [ ] Input validation at backend

---

## 🚀 Deployment

### Build for Production
```bash
npm run build
# Creates optimized bundle in `build/`
```

### Deploy To
- Vercel: `vercel`
- Netlify: Drag `build/` folder
- AWS: Configure S3 + CloudFront
- GCP: Cloud Storage + CDN

### Set Production API URL
```env
REACT_APP_API_URL=https://your-production-api.com/api
```

---

## 📊 Key Metrics to Track

### User Behavior
```
- Time per question (avg: 4-8 seconds)
- Hints used (0-3 per question)
- Session completion rate
- Questions attempted
```

### Adaptation Effectiveness
```
- Difficulty trajectory smoothness
- Window decisions consistency
- Learning gain vs difficulty level
- Engagement trend
```

### Technical Performance
```
- API response time (target: < 1s)
- Page load time (target: < 3s)
- Error rate (target: < 1%)
```

---

## 🎓 Research Metrics

### Collect These Data Points
```
Per Question:
- Question ID
- Student answer
- Correctness
- Response time
- Difficulty before/after
- Engagement score

Per Session:
- Student ID
- Total score
- Final difficulty
- Engagement trajectory
- Adaptation decisions

```

---

## 🔗 Quick Links

**Documentation**
- Full Guide: `FRONTEND_INTEGRATION_GUIDE.md`
- Readme: `INTERACTIVE_FRONTEND_README.md`
- Checklist: `IMPLEMENTATION_CHECKLIST.md`

**Backend**
- Policy: `backend/app/adaptation/policy.py`
- API: `backend/app/cbt/routes.py`
- Engagement: `backend/app/engagement/`

---

## 💡 Pro Tips

1. **Debug Engagement**: Open DevTools → Check `EngagementAPI.getLastEngagement()`
2. **Monitor Adaptation**: Look for "[ADAPT Q5]" messages in backend logs
3. **Test Quickly**: Create test user, answer 1 question, review response
4. **Check Data**: Open browser Network tab, inspect fetch responses
5. **Mobile Test**: Use DevTools device emulation (F12 → toggle device toolbar)

---

## ✅ Pre-Launch Checklist

```
Core Functionality:
  [ ] Login works
  [ ] Question displays
  [ ] Submit works (API call succeeds)
  [ ] Feedback appears
  [ ] Next question loads
  
Real-Time Features:
  [ ] Engagement score visible
  [ ] Difficulty updates
  [ ] Timeline shows questions
  [ ] Charts animate
  
Data Collection:
  [ ] Responses logged
  [ ] Engagement metrics captured
  [ ] Adaptation decisions recorded
  [ ] Logs in correct format
  
Polish:
  [ ] No console errors
  [ ] Mobile responsive
  [ ] Animations smooth
  [ ] Colors match design
```

---

## 🎉 Ready to Launch!

Your interactive frontend is complete and ready for:
- ✅ Real user testing
- ✅ Engagement monitoring
- ✅ Adaptation tracking
- ✅ Learning outcome measurement
- ✅ Research publication

---

## 📞 Quick Support

| Need | Resource |
|------|----------|
| How to start? | Read "Start Here" section above |
| Component help? | Check component source code comments |
| API error? | Run test curl commands in "Testing" section |
| Data missing? | Check logs in "Data Collection" section |
| Mobile issue? | Test with Device Emulation in DevTools |

---

**Status**: ✅ READY
**Est. Setup Time**: 10 minutes
**Est. First Test**: 15 minutes

`npm start` and happy learning! 🚀
