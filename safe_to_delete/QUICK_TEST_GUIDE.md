# 🧪 Quick Test Guide - See Adaptation In Action

## Immediate Test (5 minutes)

### Setup
1. **Clear browser cache** (Ctrl+Shift+R)
2. **Open** http://localhost:3000
3. **Check backend** is running (should see login screen)

### Test Flow

#### Step 1: Login
```
Input:
  Email: testuser123@example.com
  Name: Test User

Expected:
  ✓ Login succeeds
  ✓ Redirected to subject selection
  ✓ Welcome message shows your name
```

#### Step 2: Start Mathematics Test
```
Action:
  Click "📐 Mathematics" button

Expected:
  ✓ Session starts
  ✓ First question appears
  ✓ Progress shows "1 of 10"
  ✓ Difficulty shows "50%" (starting level)
  ✓ Correct count shows "0"
```

#### Step 3: Answer Questions - WATCH FOR ADAPTATION

**Question 1: Easy math question**
```
Answer: Select an option and click "✓ Submit Answer"

Expected Feedback Modal:
┌─────────────────────────────────────────┐
│              ✓                          │
│           Correct!                      │
│         Great work!                     │
│                                         │
│  Answer: ✓ Your answer was correct     │
│  Explanation: [detailed step-by-step]  │
│                                         │
│  ┌──────────────────┬─────────────────┐│
│  │   Difficulty     │   Score         ││
│  │      52%         │    10.0%        ││
│  │   📈 +2%        │  1 of 1 correct ││
│  └──────────────────┴─────────────────┘│
│                                         │
│  💡 Adaptive Feedback:                 │
│  Your performance is strong!           │
│  Difficulty increased slightly...      │
│                                         │
│  Loading next question...              │
└─────────────────────────────────────────┘

Key Observations:
  ✓ Difficulty changed: 50% → 52% (📈 +2%)
  ✓ Score shows progress
  ✓ Explanation visible
  ✓ This is REAL-TIME ADAPTATION!
```

**Question 2: Slightly Harder Question**
```
If you answer correctly again:
  Difficulty: 52% → 54% (📈 +2%)
  Score: 20%

If you answer incorrectly:
  Difficulty: 52% → 49% (📉 -3%)
  Score: decreases
```

### Pattern to Observe

```
Question 1: Correct → Difficulty 50% to 52%
Question 2: Correct → Difficulty 52% to 54%
Question 3: Correct → Difficulty 54% to 56%
Question 4: Correct → Difficulty 56% to 58%
Question 5: Incorrect → Difficulty 58% to 55% (📉 -3%)
```

**This is the policy engine working in real-time!**

---

## What You're Testing

### ✅ Connection Check
- Frontend can reach backend
- Session created successfully
- Questions retrieved correctly

### ✅ Adaptation Check
- Difficulty changes after each answer
- Direction (up/down) matches performance
- Magnitude (%) is reasonable (±1-3%)

### ✅ Feedback Check
- Modal appears (not alert box)
- Shows correctness with visual
- Shows difficulty change
- Shows explanation
- Auto-closes and loads next question

### ✅ Data Logging Check
- Backend logs each response
- Engagement metrics recorded
- Adaptation decisions saved

---

## How to Verify Logs

### Backend Terminal
```bash
# If backend is running in terminal, you should see:
[INFO] Session started: {session_id: ...}
[INFO] Question returned: {question_id: ...}
[INFO] Response received: {is_correct: true, ...}
[INFO] Difficulty updated: 0.50 -> 0.52
```

### Browser Console (F12)
```javascript
// After submitting an answer, you should see:
Submit response: {success: true, is_correct: true, ...}
[DIFFICULTY DEBUG] Received from backend: {current_difficulty: 0.52...}
[DIFFICULTY DEBUG] Updated: currentSession.current_difficulty = 0.52
```

---

## Expected Difficulty Progression

### Scenario A: You answer all correctly
```
Q1: 50% ✓ → 52%
Q2: 52% ✓ → 54%
Q3: 54% ✓ → 56%
Q4: 56% ✓ → 58%
Q5: 58% ✓ → 60% [WINDOW: Hard questions block applied]
Q6: 60% ✓ → 61%
```

### Scenario B: You answer some wrong
```
Q1: 50% ✓ → 52%
Q2: 52% ✓ → 54%
Q3: 54% ✗ → 51% [Difficulty drops]
Q4: 51% ✓ → 53%
Q5: 53% ✓ → 55% [WINDOW: Normal progression]
```

### Scenario C: You struggle
```
Q1: 50% ✗ → 47%
Q2: 47% ✗ → 44%
Q3: 44% ✓ → 46%
Q4: 46% ✗ → 43%
Q5: 43% ✓ → 45% [WINDOW: Easier questions block]
```

---

## 5-Question Checkpoint (First Window)

At question 5, the backend makes a policy decision:

```
✓ All correct (50%+ engagement):
  → Apply harder questions block
  → Difficulty continues rising
  
✗ Mixed performance:
  → Maintain current difficulty
  → Adaptive pressure continues
  
✗ Mostly wrong:
  → Apply easier block
  → Re-calibrate student level
```

**You won't see this explicitly, but difficulty pattern will reflect it!**

---

## Success Criteria

| Criterion | How to Check |
|-----------|-------------|
| System Connected | Login works, questions appear |
| Difficulty Changing | See different % after each question |
| Right Direction | Correct → ↑, Wrong → ↓ |
| Realistic Changes | ±1% to ±5% per question |
| Feedback Appearing | Modal, not alert |
| Speed | Modal appears instantly |
| Explanation | Visible and detailed |
| Auto-Next | Modal closes, question loads auto |

---

## Common Observations

### Good Signs ✓
- Difficulty bounces up/down matching your answers
- Changes appear immediately after submit
- Modal shows detailed feedback
- Score percentage increases as you get more right
- Questions seem appropriate difficulty

### Concerning Signs ✗
- Difficulty never changes (stuck at 50%)
- Alert boxes instead of modals
- No explanation shown
- Page refreshes instead of auto-loading
- Questions are too easy or too hard

---

## Troubleshooting During Test

### If Modal Doesn't Appear
```
1. Check F12 Console for errors
2. Make sure backend is running:
   curl http://localhost:5000/api/
3. Hard refresh browser: Ctrl+Shift+R
4. Try again on next question
```

### If Difficulty Doesn't Change
```
1. Check console logs (F12)
2. Look for "current_difficulty" in response
3. Verify backend API response with curl:
   curl -X POST http://localhost:5000/api/cbt/response/submit...
4. Restart backend if needed
```

### If Performance is Slow
```
1. Close other browser tabs
2. Check internet connection
3. Verify localhost:5000 is responsive
4. Check backend console for errors
```

---

## What's Being Tested

### Frontend
- ✓ Page loads correctly
- ✓ Login works
- ✓ Questions display
- ✓ Answer submission works
- ✓ Feedback modal appears
- ✓ Auto-loads next question

### Backend
- ✓ Receives answer submission
- ✓ Validates correctness
- ✓ Calculates new difficulty
- ✓ Returns updated data
- ✓ Logs session data

### System Integration
- ✓ HTTP communication working
- ✓ JSON parsing correct
- ✓ State management working
- ✓ Data persistence working

---

## Post-Test Review

After completing 10 questions:

```
Expected Final Screen:
╔═════════════════════════════════╗
║      🎉 Test Complete!         ║
║                                 ║
║     Final Score: [X]%          ║
║     Correct: [Y] of 10         ║
║     Performance: [LEVEL]       ║
║                                 ║
║   📊 View Dashboard             ║
║   🔄 Start New Test            ║
╚═════════════════════════════════╝

Check:
- Score matches your performance
- Correct count accurate
- Difficulty trajectory shown
- Option to try again or review
```

---

## Rapid Testing Checklist

```
□ Browser opens to http://localhost:3000
□ Login form appears
□ Can login successfully
□ Subject buttons visible
□ Can start Mathematics test
□ Question displays with all 4 options
□ Can select options (they highlight)
□ Submit button works
□ ⭐ Feedback modal appears (KEY!)
□ ⭐ Difficulty shows change (KEY!)
□ ⭐ Explanation visible (KEY!)
□ Modal auto-closes
□ Next question loads
□ Progress bar advances
□ Correct count updates
□ Can complete all 10 questions
□ Final score screen appears
□ Can start new test

If all checked: ✅ SYSTEM WORKING!
```

---

## Video/Screen Recording Tip

If you want to record evidence of adaptation:
1. Open http://localhost:3000
2. Start screen recording (native OS tool)
3. Login and start test
4. Answer 5 questions, watching difficulty numbers
5. Record the difficulty changing with each answer
6. Stop recording

**This will show the real-time adaptation clearly!**

---

## Next Steps After Verification

1. ✅ Complete this test
2. ✅ Run 5-10 more test sessions
3. ✅ Collect engagement data
4. ✅ Review adaptation patterns
5. ✅ Verify learning outcomes
6. ✅ Export data for analysis

---

**Expected Time**: 5-10 minutes
**Difficulty**: Easy (just click and watch)
**Importance**: Critical - validates entire system
**Status**: Ready to test!

Good luck! 🚀
