# Frontend Testing Guide

## Fixed Issues

### 1. **Session ID Was Undefined**
   - **Problem**: The request to `/api/cbt/question/next/undefined` showed the session ID wasn't being captured
   - **Root Cause**: Frontend wasn't properly handling the session response from the backend
   - **Solution**: Updated `startSession()` to handle both session response formats from the backend

### 2. **Subject Selection Not Working**
   - **Problem**: Clicking subject buttons did nothing or showed errors
   - **Root Cause**: 
     - No student validation before attempting session start
     - Session ID not properly stored in currentSession variable
   - **Solution**: 
     - Added validation in `startSession()` to ensure student is logged in
     - Properly parse and store session data from API response

### 3. **Confusing Interface - No Login Flow**
   - **Problem**: UI wasn't guiding users through the login process clearly
   - **Root Cause**: 
     - Login page wasn't clearly indicating what needed to be done
     - After login, redirect wasn't clear
   - **Solution**:
     - Improved login UI with better labels and placeholders
     - Changed post-login redirect from Dashboard to Subject Selection (showTestPage)
     - Added console logging to track state changes

## Testing Steps

### Step 1: Open Frontend
```
Navigate to http://localhost:8000
```
You should see the login page with:
- Email input field
- Name input field
- Login/Register button

### Step 2: Create Student Account
1. Enter an email: `student@example.com`
2. Enter a name: `John Doe`
3. Click "Login / Register"

**Expected Result**: 
- Welcome alert: "Welcome John Doe!"
- Redirects to Subject Selection page
- Shows "Welcome back, John Doe" at the top

### Step 3: Select Subject
Click any subject button (Mathematics, Science, English, or History)

**Expected Result**:
- Session starts
- Questions page loads with:
  - Progress bar (0/10)
  - Statistics cards (Correct, Difficulty, Subject)
  - Question text
  - 4 clickable answer buttons (A, B, C, D)
  - Submit Answer button
  - (Optional) Get Hint button

### Step 4: Answer Questions
1. Click an answer button (it should highlight in blue)
2. Click "Submit Answer"

**Expected Result**:
- Alert shows if answer was correct or incorrect
- If incorrect, shows the correct answer
- Loads next question
- Progress bar updates
- Correct count updates

### Step 5: Complete Test
- Answer all 10 questions
- After 10 questions, completion alert appears
- Redirects to Dashboard

## Backend Requirements

Ensure the backend is running:
```bash
cd backend
python main.py
```

The backend should be accessible at:
- Base URL: http://localhost:5000
- API Base: http://localhost:5000/api

## Key API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/cbt/student` | POST | Create/login student |
| `/api/cbt/session/start` | POST | Start test session |
| `/api/cbt/question/next/{session_id}` | GET | Get next question |
| `/api/cbt/response/submit` | POST | Submit answer |
| `/api/cbt/hint/{session_id}/{question_id}` | GET | Get hint |
| `/api/analytics/dashboard/{student_id}` | GET | Get student stats |

## Debugging

Check browser console (F12) for:
- `console.log` statements showing state changes
- Errors in network requests
- Session data being logged

Example good log sequence:
```
setupUI() -> showLoginPage()
handleLogin() -> createStudent()
Student created/logged in: {id: "...", name: "John Doe", ...}
showTestPage()
startSession('Mathematics')
Session response: {success: true, session_id: "...", ...}
Current session set to: {id: "...", ...}
showQuestion()
Fetching question for session: ...
Question response: {success: true, question: {...}}
```

## Common Issues

### Issue: "Session not found" error
- **Cause**: Session ID didn't save properly
- **Solution**: Check browser console for session data logging

### Issue: "No active session" alert
- **Cause**: currentSession is null or undefined
- **Solution**: Check if you completed Step 2 (login) and Step 3 (subject selection)

### Issue: Backend returns 404 on question endpoint
- **Cause**: Session ID is "undefined" in the URL
- **Solution**: Session wasn't created properly - check Step 3 logs

### Issue: Same questions repeat
- **Cause**: Backend filtering isn't working
- **Solution**: Check if database has enough questions (need 10+)
