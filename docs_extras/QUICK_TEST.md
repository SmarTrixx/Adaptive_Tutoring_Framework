# Quick Test Guide

## Current Setup

**Backend**: Running on http://localhost:5000
**Frontend**: Running on http://localhost:8000

## Test Case 1: New Student Registration

**Steps**:
1. Open http://localhost:8000 in browser
2. You should see login page with message "Login with your email to continue. If you're new, just enter your details to create an account."
3. Enter:
   - Email: `john.doe@example.com`
   - Name: `John Doe`
4. Click "Login / Register"

**Expected Results**:
- ✅ Alert appears: "Account created successfully! Welcome John Doe!"
- ✅ Redirected to subject selection page
- ✅ Page shows "Welcome back, John Doe" at the top
- ✅ Navigation shows:
  - Dashboard (link)
  - Start Test (link)
  - Logout (link)
  - 👤 john.doe@example.com (user info)
- ✅ Subject buttons are visible and clickable

**Console Output** (Open DevTools F12 → Console):
```
Attempted login/register for: john.doe@example.com
Login response: {success: true, student: {...}, message: "Account created successfully"}
Student logged in: {id: "...", email: "john.doe@example.com", name: "John Doe"}
```

---

## Test Case 2: Existing Student Login

**Steps**:
1. Refresh the page (or close and reopen)
2. You should see login page again
3. Enter the SAME email and name:
   - Email: `john.doe@example.com`
   - Name: `John Doe`
4. Click "Login / Register"

**Expected Results**:
- ✅ Alert appears: "Welcome back John Doe!"
- ✅ Redirected to subject selection page
- ✅ Navigation properly shows logged-in state
- ✅ Student data loaded from database (not localStorage)

**Console Output**:
```
Attempted login/register for: john.doe@example.com
Login response: {success: true, student: {...}, message: "Login successful"}
Student logged in: {id: "...", email: "john.doe@example.com", name: "John Doe"}
```

---

## Test Case 3: Subject Selection & Questions

**Steps**:
1. From subject selection page, click "📐 Mathematics"

**Expected Results**:
- ✅ No error message
- ✅ Page displays question with:
  - Progress bar showing 0/10
  - Question text
  - 4 answer options (A, B, C, D)
  - "Submit Answer" button
  - (Optional) "Get Hint" button
- ✅ Statistics cards show:
  - Correct: 0
  - Difficulty: (some percentage)
  - Level: Mathematics

**Console Output**:
```
Starting session for student: [student-id] subject: Mathematics
Session response: {success: true, session: {...}}
Current session set to: {id: "...", subject: "Mathematics", ...}
Fetching question for session: [session-id]
Question response: {success: true, question: {...}}
```

---

## Test Case 4: Answer a Question

**Steps**:
1. Click any answer option (A, B, C, or D)
2. The button should highlight in blue with light blue background
3. Click "Submit Answer" button

**Expected Results**:
- ✅ Answer option highlights when clicked
- ✅ Alert appears showing if answer was correct or incorrect
- ✅ If incorrect, shows: "✗ Incorrect! Answer: [correct letter]"
- ✅ If correct, shows: "✓ Correct!"
- ✅ Next question loads automatically
- ✅ Progress bar updates (1/10, 2/10, etc.)
- ✅ Correct count increments if answer was right

**Console Output**:
```
Submitting answer: {questionId: "...", answer: "A", responseTime: 30}
Submit response: {success: true, is_correct: true|false, ...}
```

---

## Test Case 5: Complete a Full Test

**Steps**:
1. Continue answering all 10 questions
2. After the 10th question is submitted

**Expected Results**:
- ✅ Alert shows: "Test completed! Correct: [X]/10"
- ✅ Redirected to Dashboard page
- ✅ Dashboard shows statistics:
  - Total Sessions: 1
  - Total Questions: 10
  - Accuracy: (calculated percentage)

---

## Test Case 6: Logout

**Steps**:
1. From any logged-in page, click "Logout" in navigation

**Expected Results**:
- ✅ Redirected to login page
- ✅ Navigation shows ONLY "Login" button
- ✅ User info disappears from navigation
- ✅ Dashboard and Start Test buttons hidden

**LocalStorage** (DevTools → Application → Local Storage):
- ✅ `student` key is removed
- ✅ `session` key is removed

---

## Test Case 7: Check Navigation Protection

**Steps**:
1. Logout (if currently logged in)
2. Try to manually access dashboard by typing in console:
   ```javascript
   showDashboard()
   ```

**Expected Results**:
- ✅ Page redirects to login page
- ✅ No dashboard content shown

---

## Troubleshooting

### Issue: "Please enter both email and name" alert
- **Cause**: One or both fields are empty
- **Solution**: Fill in both fields before submitting

### Issue: Login hangs or doesn't respond
- **Cause**: Backend not running or not accessible
- **Solution**: Check backend is running with `python main.py`

### Issue: Subject button doesn't work / no error shown
- **Cause**: Button type not set to "button", causing form submission
- **Check**: Open DevTools → Console, should see "Starting session for student: ..."
- **Solution**: Refresh page and try again

### Issue: "No active session" error when questions page tries to load
- **Cause**: Session didn't save properly or sessionId is undefined
- **Solution**: 
  1. Check console for session response
  2. Look for errors in session response
  3. Ensure Backend is returning proper session_id

### Issue: Same question appears multiple times
- **Cause**: Backend question filtering not working
- **Solution**: Check if database has enough questions (need 10+)

---

## Key Behaviors to Verify

| Feature | Status | Notes |
|---------|--------|-------|
| New student can register | ✅ | Should see "Account created" message |
| Existing student can login | ✅ | Should see "Welcome back" message |
| Navigation hides before login | ✅ | Only "Login" visible |
| Navigation shows after login | ✅ | "Dashboard", "Start Test", "Logout" visible |
| User name displayed in nav | ✅ | Shows "👤 Name" |
| Subject buttons work | ✅ | Session starts, questions load |
| Answer selection highlights | ✅ | Button turns blue when selected |
| Answer submission works | ✅ | Shows correct/incorrect feedback |
| Progress bar updates | ✅ | Shows 1/10, 2/10, etc. |
| Correct count updates | ✅ | Increments on correct answers |
| Test completion shows results | ✅ | Alert with final score |
| Logout works | ✅ | Returns to login, clears data |

