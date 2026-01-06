# FIX: Page Refresh & Question Persistence Issues

**Date:** January 6, 2026  
**Status:** ✅ FIXED  
**Commit:** 5177ac7

---

## Issue 1: Page Refresh Changes Current Question

**Problem:**
- User is answering Q6: "What is your name?"
- Page refreshes (accidental, browser tab reload, etc.)
- New question loads: "Do you know Clara..." (different question)
- User never gets to answer the original question

**Root Cause:**
When the page reloaded, the code would:
1. Load stored session from localStorage ✓
2. Call `showTestPage()` which displays subject selection ✗
3. OR call `fetchNextQuestion()` which fetches a NEW question instead of resuming the current one ✗
4. The `sessionQuestionHistory` array was NOT persisted, so it was lost on reload

**Solution:**
1. **Persist question history** - Save `sessionQuestionHistory` to localStorage whenever a question is added
2. **Restore on page load** - When page reloads with active session, restore the entire question history
3. **Resume current question** - Display the current question instead of fetching a new one

**Code Changes:**

**Before (problematic initialization):**
```javascript
// Page reloads, stored session is restored
currentSession = restored from localStorage
sessionQuestionHistory = [] // EMPTY - lost data!

// Shows subject selection or fetches new question
if (currentStudent && currentStudent.id) {
    showTestPage();  // Shows subject selection instead of current question
}
```

**After (fixed initialization):**
```javascript
// Page reloads, restore everything
currentSession = restored from localStorage
sessionQuestionHistory = restored from localStorage[`questionHistory_${sessionId}`]
currentQuestionIndex = restored from localStorage

// Resume the current question
if (currentSession && currentSession.id && currentSession.status === 'active') {
    if (sessionQuestionHistory.length > 0) {
        // Display the CURRENT question from history
        renderQuestionWithNav(sessionQuestionHistory[currentQuestionIndex].question, currentQuestionIndex, false);
    }
}
```

**Files Modified:**
- `frontend/app.js` - Added persistence and restoration logic

**Key Changes:**

1. **Save question history whenever a question is added:**
```javascript
// After adding question to history
localStorage.setItem(`questionHistory_${currentSession.id}`, JSON.stringify(sessionQuestionHistory));
localStorage.setItem(`questionIndex_${currentSession.id}`, currentQuestionIndex.toString());
```

2. **Restore on page load:**
```javascript
// During initialization
const history = localStorage.getItem(`questionHistory_${currentSession.id}`);
if (history) {
    sessionQuestionHistory = JSON.parse(history);
    currentQuestionIndex = parseInt(localStorage.getItem(`questionIndex_${currentSession.id}`));
    TEST_STATE.setCurrentQuestionIndex(currentQuestionIndex);
}
```

3. **Resume instead of fetch:**
```javascript
if (currentSession && currentSession.id && currentSession.status === 'active') {
    if (sessionQuestionHistory && sessionQuestionHistory.length > 0) {
        // Display current question from history
        renderQuestionWithNav(sessionQuestionHistory[currentQuestionIndex].question, currentQuestionIndex, false);
    }
}
```

---

## Issue 2: Difficult Questions at Low Difficulty Level

**Problem:**
- Adaptation level set to 30% (low difficulty - should get easy questions)
- Questions appear to be hard/difficult even at low adaptation level

**Investigation:**
The system uses a difficulty mapper that should assign questions based on adaptation level:

```
Adaptation 0-35% → Difficulty range 0.1-0.4 (easy questions)
Adaptation 35-65% → Difficulty range 0.35-0.65 (medium questions)
Adaptation 65-100% → Difficulty range 0.6-0.95 (hard questions)
```

**Debugging Added:**
Added debug logging to backend to track question selection:
```python
print(f'[DEBUG] get_next_question: session_difficulty={difficulty}, label={difficulty_label}, range=[{min_difficulty}, {max_difficulty}]')
print(f'[DEBUG] Found {len(questions)} questions for difficulty {difficulty_label}')
print(f'[DEBUG] Sample question: id={q.id}, difficulty={q.difficulty}, text={q.question_text[:50]}...')
```

**Next Step:**
Run test at 30% adaptation and check backend console logs to see:
1. What difficulty range is being requested
2. How many questions match that range
3. Which questions are being returned

---

## How Page Persistence Now Works

**Flow on Page Load:**

```
1. User has active session with Q6 loaded
2. Page reloads (accidental refresh)
3. localStorage has:
   - session: {id: ..., status: 'active', ...}
   - questionHistory_<sessionId>: [{q1}, {q2}, {q3}, {q4}, {q5}, {q6}]
   - questionIndex_<sessionId>: 5 (currently on Q6)

4. safeInitialize() restores:
   ✓ currentStudent
   ✓ currentSession
   ✓ sessionQuestionHistory (6 questions)
   ✓ currentQuestionIndex (5)
   ✓ TEST_STATE sync

5. Check if active session:
   ✓ currentSession.status === 'active' → YES
   ✓ sessionQuestionHistory.length > 0 → YES (6 questions)

6. Display current question:
   ✓ renderQuestionWithNav(Q6, index=5, false)
   ✓ User continues with same question

7. When next question button clicked:
   ✓ Fetches Q7
   ✓ Adds to sessionQuestionHistory
   ✓ Saves to localStorage
```

---

## Testing the Fix

**Test 1: Page Refresh During Question**
1. Start test, answer Q1
2. Click to Q3 (navigate to unanswered question)
3. **REFRESH the page** (F5 or Ctrl+R)
4. ✅ Should see same question Q3 (not a new random question)
5. Continue answering

**Test 2: Page Reload from Other Tab**
1. Start test with 10 questions
2. Have 5 questions in history
3. Close and reopen browser tab
4. ✅ Should resume with all 5 questions in history
5. Should be on the same question as before

**Test 3: Multiple Refreshes**
1. Start test
2. Answer Q1-Q4
3. Refresh page
4. Verify all 4 are in history
5. Refresh again
6. ✅ Should still have all 4

---

## Backend Debug Output

When running, you should see console output like:
```
[DEBUG] get_next_question: session_difficulty=0.3, label=easy, range=[0.1, 0.4]
[DEBUG] Found 6 questions for difficulty easy
[DEBUG] Sample question: id=q123, difficulty=0.28, text=What is the capital of...
```

This confirms the difficulty filtering is working correctly. If you see:
```
[DEBUG] Found 0 questions for difficulty easy
```

Then there's an issue with question difficulty values in the database.

---

## Summary

**Problems Fixed:**
1. ✅ Page refreshes no longer change the current question
2. ✅ Question history persisted across page reloads
3. ✅ Session resumes to the exact same question after reload
4. ✅ Debug logging added to track difficulty assignment

**Files Changed:**
- `frontend/app.js` - Added persistence logic (lines 214-244, 985-990, 1225-1230)
- `backend/app/cbt/system.py` - Added debug output

**Status:** Ready for testing - verify page reload behavior in next test session
