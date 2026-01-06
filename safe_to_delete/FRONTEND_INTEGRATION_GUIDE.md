# Interactive Frontend Integration Guide

## Overview

This guide provides a complete implementation of a **real-time, interactive frontend** for the Adaptive Intelligent Tutoring Framework. It enables actual user attempts, live engagement monitoring, and visual adaptation feedback aligned with the calibrated policy engine.

---

## Architecture

### Components Created

#### 1. **AdaptiveQuestion.jsx**
Main question presentation and response handling component.

**Features:**
- Live question display with options
- Response time tracking
- Single-click option selection
- Submit button with loading state
- Immediate correctness feedback
- Difficulty change visualization
- Policy decision explanation

**Props:**
```javascript
{
  question: {          // Question object from backend
    question_id,
    question_text,
    options,          // [{letter, text}, ...]
    difficulty,       // Current difficulty (0-1)
    question_number
  },
  session: {           // Session object
    id,
    current_difficulty,
    previous_difficulty,
    ...
  },
  onSubmit: (responseData) => {}, // Callback on submission
  isLoading: boolean   // Show loading state
}
```

**Integration:**
```javascript
import AdaptiveQuestion from './components/AdaptiveQuestion';

<AdaptiveQuestion
  question={currentQuestion}
  session={session}
  onSubmit={handleAnswerSubmit}
/>
```

---

#### 2. **SessionTimeline.jsx**
Historical view of all attempted questions with progression tracking.

**Features:**
- Question-by-question history
- Correctness indicators
- Difficulty changes per question
- Adaptation rationale
- Difficulty trajectory chart
- Engagement trajectory chart
- Statistics summary

**Props:**
```javascript
{
  session: {},                          // Session object
  responses: [                          // All student responses
    {
      question_id,
      is_correct,
      difficulty,
      response_time_seconds,
      student_answer,
      correct_answer
    },
    ...
  ],
  engagementHistory: [{...}, ...],     // Engagement scores over time
  adaptationHistory: [{...}, ...]      // Policy decisions over time
}
```

**Integration:**
```javascript
import SessionTimeline from './components/SessionTimeline';

<SessionTimeline
  session={session}
  responses={responses}
  engagementHistory={engagementHistory}
  adaptationHistory={adaptationHistory}
/>
```

---

#### 3. **EngagementIndicators.jsx**
Real-time engagement monitoring with behavioral, cognitive, and affective signals.

**Features:**
- Composite engagement score circle
- Behavioral indicators:
  - Response time analysis
  - Hints used
  - Number of attempts
  - Navigation frequency
- Cognitive indicators:
  - Accuracy calculation
  - Learning progress
  - Knowledge retention
- Affective indicators:
  - Frustration level
  - Interest level
  - Confidence level
- Adaptation recommendations
- Optional policy debug panel

**Props:**
```javascript
{
  currentEngagement: {      // Latest engagement metrics
    engagement_score,       // 0-1 composite score
    engagement_level,       // 'low', 'moderate', 'high'
    behavioral: {
      response_time_seconds,
      hints_used,
      attempts_count
    },
    cognitive: {
      accuracy,
      learning_progress
    },
    affective: {
      frustration_level,
      interest_level,
      confidence_level
    }
  },
  sessionData: {            // Additional session context
    correct_answers,
    total_answered,
    avg_response_time,
    current_difficulty
  },
  policyDebug: boolean      // Show debug panel
}
```

**Integration:**
```javascript
import EngagementIndicators from './components/EngagementIndicators';

<EngagementIndicators
  currentEngagement={engagement}
  sessionData={sessionData}
  policyDebug={showDebug}
/>
```

---

#### 4. **TestSessionPage.jsx**
Full-page test interface integrating all components.

**Features:**
- Two-column layout (question + monitoring)
- Live engagement display
- Quick statistics
- Question history sidebar (toggle)
- Debug controls (optional)
- Progress bar
- Completion screen
- Responsive design

**Usage:**
```javascript
import TestSessionPage from './pages/TestSessionPage';

<TestSessionPage
  studentId={studentId}
  sessionId={sessionId}
  subject="Mathematics"
/>
```

---

### Styling Files

All components use modular CSS files located in `frontend/src/styles/`:

- `AdaptiveQuestion.css` - Question panel styling
- `SessionTimeline.css` - Timeline and charts
- `EngagementIndicators.css` - Engagement monitoring UI
- `TestSession.css` - Main layout and responsive design

---

## API Integration

### Backend Endpoints Used

#### Session Management
```
POST   /api/cbt/session/start
GET    /api/cbt/question/next/{session_id}
GET    /api/cbt/session/{session_id}
POST   /api/cbt/session/end/{session_id}
```

#### Response Submission (Core)
```
POST   /api/cbt/response/submit
Headers: Content-Type: application/json
Body: {
  session_id: string,
  question_id: string,
  student_answer: string,
  response_time_seconds: number
}
Returns: {
  success: boolean,
  is_correct: boolean,
  current_difficulty: number,      // ← Updated difficulty
  explanation: string,
  correct_answer: string,
  ...
}
```

#### Engagement
```
GET    /api/engagement/last/{session_id}
POST   /api/engagement/track
```

#### Adaptation Logs (for transparency)
```
GET    /api/adaptation/logs/{session_id}
GET    /api/adaptation/effectiveness/{session_id}
```

### API Utilities

The `frontend/src/utils/api.js` file provides abstracted API calls:

```javascript
import {
  SessionAPI,
  ResponseAPI,
  EngagementAPI,
  AdaptationAPI,
  calculateResponseTime,
  formatDifficulty,
  getDifficultyColor
} from './utils/api';

// Start session
const { session } = await SessionAPI.startSession(
  studentId, 
  numQuestions, 
  subject
);

// Get next question
const { question } = await SessionAPI.getNextQuestion(sessionId);

// Submit answer
const result = await ResponseAPI.submitResponse(
  sessionId,
  questionId,
  studentAnswer,
  responseTime
);
// result contains: isCorrect, currentDifficulty, explanation, ...

// Get engagement data
const engagement = await EngagementAPI.getLastEngagement(sessionId);

// Get adaptation logs
const logs = await AdaptationAPI.getAdaptationLogs(sessionId);
```

---

## Real-World Integration Steps

### Step 1: Setup React Environment

```bash
cd frontend
npm install

# Ensure these are installed:
npm install react react-dom
```

### Step 2: Create Main App Component

```javascript
// src/App.jsx
import React, { useState } from 'react';
import TestSessionPage from './pages/TestSessionPage';
import LoginPage from './pages/LoginPage';

function App() {
  const [studentId, setStudentId] = useState(null);
  
  if (!studentId) {
    return <LoginPage onLogin={setStudentId} />;
  }
  
  return (
    <TestSessionPage 
      studentId={studentId}
      subject="Mathematics"
    />
  );
}

export default App;
```

### Step 3: Configure Backend URL

Create `.env` in frontend root:
```
REACT_APP_API_URL=http://localhost:5000/api
```

### Step 4: Start Frontend

```bash
npm start
```

The app will run at `http://localhost:3000`

---

## User Flow

### 1. Student Starts Test
- Navigates to test page
- Selects subject
- Session created on backend
- First question fetched
- Component tree: TestSessionPage → AdaptiveQuestion

### 2. Student Attempts Question
- Reads question
- Selects answer option
- Submits (response time tracked)
- Backend processes:
  - Checks correctness
  - Calculates engagement metrics
  - Applies adaptation policy
  - Returns new difficulty

### 3. Frontend Displays Feedback
- Shows correctness badge
- Shows explanation
- Shows new difficulty
- Shows policy reasoning
- Engagement panel updates live
- Timeline adds new entry

### 4. Next Question
- Fetches new question at current difficulty
- Response time counter resets
- Process repeats

### 5. Session Completion
- Shows final statistics
- Displays full trajectory
- Option to start new test

---

## Calibrated Policy Integration

The frontend **visualizes and respects** the calibrated policy:

### Window-Based Decisions (Every 5 Questions)
- Difficulty updates show at question 5, 10, 15, etc.
- Between windows, difficulty appears stable
- Backend accumulates 5 responses before deciding

### Performance × Engagement Matrix (Visible)
The adaptation indicator shows:
```
Performance: Excellent/Good/Fair/Poor (from accuracy)
Engagement:  High/Moderate/Low (from fused indicators)
→ Decision: +0.10 / +0.05 / maintain / -0.025 / -0.10
```

### Anti-Oscillation (Transparent)
- If difficulty alternates directions, step is dampened (×0.5)
- Timeline shows rationale for each decision

### Rushing Detection (Highlighted)
- Fast responses (< 2s) marked in behavioral indicators
- If perfect accuracy + rushing: caution flag appears
- Conservative step size (+0.025 instead of +0.05)

### Momentum Tracking (Observable)
- Consistent direction arrows in timeline
- Shows when system is "confident" about trend
- Multiple small steps vs sudden jump

---

## Key Features for Research

### 1. **Real-Time Visibility**
Every adaptation decision is:
- Immediately shown to student
- Logged with full rationale
- Accessible in timeline
- Displayed with metrics

### 2. **Engagement Signals**
Live display of:
- Behavioral patterns (response time, hints)
- Cognitive progress (accuracy, learning)
- Affective state (frustration, interest)
- Composite engagement score

### 3. **Policy Transparency**
Debug panel shows:
- Window size (5 questions)
- Current window performance
- Fused engagement score
- Rushing detection state
- Oscillation checks
- Momentum status

### 4. **Progression Tracking**
Timeline visualizes:
- Question-by-question history
- Difficulty trajectory chart
- Engagement trajectory chart
- Correct/incorrect pattern
- Response time trends

### 5. **Adaptation Feedback**
After each question (when adapted):
- New difficulty value
- Change percentage (+/-)
- Reason (e.g., "Good performance + Moderate engagement → Maintain")
- Evidence (accuracy, response time, engagement)

---

## Testing & Debugging

### Enable Debug Mode
```javascript
<EngagementIndicators
  policyDebug={true}  // Shows debug panel
/>
```

### Manual Engagement Override (Testing)
```javascript
// In TestSessionPage debug controls:
<input 
  type="range" 
  min="0" 
  max="1"
  onChange={(e) => setEngagementOverride(parseFloat(e.target.value))}
/>
```

### Check Backend Logs
```bash
cd backend
tail -f logs/engagement_logs/*.json
```

Logs show decision rationales:
```
[ADAPT Q5] Last 3: 3/3 (100%) | Excellent performance + moderate engagement → +0.05
```

---

## Performance Optimization

### Lazy Loading
```javascript
const AdaptiveQuestion = React.lazy(() => 
  import('./components/AdaptiveQuestion')
);
```

### Memoization
```javascript
const EngagementIndicators = React.memo(
  EngagementIndicators,
  (prevProps, nextProps) => 
    prevProps.currentEngagement.score === nextProps.currentEngagement.score
);
```

### CSS Optimization
- CSS files are modular (import only what's needed)
- Gradients and transitions use GPU acceleration
- Animations only on visible elements

---

## Troubleshooting

### Frontend Not Connecting to Backend
```bash
# Check backend is running
curl http://localhost:5000/api/health

# Check CORS headers
# Backend should have: 
# @app.after_request
# def add_cors_headers(response):
#   response.headers['Access-Control-Allow-Origin'] = '*'
```

### Difficulty Not Updating
- Check backend logs for adaptation decision
- Verify response includes `current_difficulty`
- Check window boundary (5th, 10th question, etc.)

### Engagement Not Showing
- Check `/api/engagement/last/{sessionId}` returns data
- Verify engagement indicators component receives props
- Check browser console for fetch errors

---

## Customization

### Change Colors
Edit color constants in component CSS or pass as props:
```javascript
const getDifficultyColor = (difficulty) => {
  if (difficulty < 0.33) return '#YOUR_EASY_COLOR';
  if (difficulty < 0.67) return '#YOUR_MEDIUM_COLOR';
  return '#YOUR_HARD_COLOR';
};
```

### Modify Question Display
Edit `AdaptiveQuestion.jsx`:
- Add image support
- Add multiple choice hints
- Add equation rendering (MathJax)
- Custom formatting

### Adjust Layout
`TestSession.css` uses CSS Grid:
```css
.test-content-grid {
  grid-template-columns: 2fr 1fr;  /* Change ratio */
}
```

---

## Production Considerations

1. **Environment Variables**
   - Set `REACT_APP_API_URL` to production backend
   - Use HTTPS for API calls

2. **Error Boundaries**
   - Wrap components in error boundaries
   - Provide fallback UI

3. **Analytics**
   - Log session start/end
   - Track user interactions
   - Monitor API response times

4. **Accessibility**
   - Add ARIA labels
   - Ensure color contrast (WCAG AA)
   - Support keyboard navigation

5. **Mobile Support**
   - Responsive CSS already included
   - Test on touch devices
   - Consider smaller option buttons

---

## Next Steps

1. ✅ Copy component files to `frontend/src/`
2. ✅ Verify backend endpoints match expectations
3. ✅ Set environment variables
4. ✅ Run `npm start`
5. ✅ Test with real user attempts
6. ✅ Monitor adaptation policy in action
7. ✅ Collect engagement and learning outcome data

---

## Research Objectives Alignment

| Objective | Implementation |
|-----------|-----------------|
| Real-time adaptation | Difficulty updates immediately after responses |
| Engagement-driven decisions | Fused engagement score modulates step size |
| Observable outcomes | Timeline and charts show progression |
| Decision transparency | Policy debug panel + rationale display |
| User interaction | Real attempts, no simulation |
| Policy compliance | Window-based, anti-oscillation, momentum |

---

## Support & Questions

For integration support or customization needs:
1. Check backend logs for decision rationale
2. Review `api.js` for correct endpoint structure
3. Verify network requests in browser DevTools
4. Check component prop types match backend responses

---

**Status**: ✅ Ready for deployment
**Components**: 4 major (AdaptiveQuestion, SessionTimeline, EngagementIndicators, TestSessionPage)
**Styles**: 4 CSS files (Responsive, optimized)
**API Integration**: Complete with utilities
**Testing**: Debug mode available
