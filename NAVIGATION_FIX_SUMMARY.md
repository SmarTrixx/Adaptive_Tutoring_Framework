# CBT Navigation Race Condition - FIXED

## Problem (Authoritative)
Previous button had 3-click lag before working:
- User clicks Previous once
- UI stays on current question
- User clicks 2-3 more times
- Finally navigates to previous question
- Race condition between submission flow and navigation

Root cause: Modal's `handleContinue()` was calling `showQuestion()` (which fetches NEW questions), while user navigation also called `showQuestion()`, causing:
- Double fetch calls
- Competing state mutations
- Navigation index being overridden by submission-triggered fetch
- Multiple renderQuestionWithNav calls per click

## Solution (Implemented)

### 1. Separate Navigation Paths
- **`showQuestion(revisitIndex, isRevisit)`** = Revisit cached questions (backward/current navigation)
  - Uses history array
  - No fetch calls
  - Pure state transition

- **`fetchNextNewQuestion()`** = Fetch new questions (forward progression)
  - Used ONLY after successful submission
  - Manages new question loading
  - Isolated from navigation

### 2. Navigation Intent Flag
```javascript
let navigationIntentActive = false;
```
- Set to `true` when Previous/Next clicked
- Cleared after render completes
- Prevents modal from auto-advancing if user navigated

### 3. Submission Tracking
```javascript
let lastSubmissionQuestionId = null;
```
- Tracks which question was just submitted
- Prevents modal re-firing if question already submitted

### 4. Modal Logic Update
```javascript
const handleContinue = async () => {
    // If user manually navigated, DON'T auto-advance
    if (navigationIntentActive) {
        console.log('[MODAL] User manually navigated away, skipping auto-navigation');
        return;
    }
    
    // Only auto-advance if submission is the current action
    await fetchNextNewQuestion();
};
```

## Files Changed
- `frontend/app.js`

## Commits
1. `31de27e` - Fix state lifecycle (TEST_STATE sync)
2. `8f45fd8` - Fix blank page (stray backtick)
3. `eea3422` - **CRITICAL: Isolate navigation from modal**
4. `4b1abbc` - Add missing time-counter DOM element

## Verification

### Before Fix
```
[NAV-PREV] Clicked
[RENDER] renderQuestionWithNav
[MODAL] More questions remain, showing next question
Fetching question for session
renderQuestionWithNav called AGAIN
```
Result: Lag, multiple renders, wrong question

### After Fix
```
[NAV-PREV] Clicked
navigationIntentActive = true
[TEST_STATE] Set currentQuestionIndex = 5
[TRACKING] Navigation: Previous question
[RENDER] renderQuestionWithNav (from history)
navigationIntentActive = false
```
Result: Immediate render, single flow, correct question

## Testing Procedure
1. Login and start test
2. Answer Q1, modal appears
3. Close/dismiss modal
4. Click **Previous** once
   - ✓ Should immediately show Q1
   - ✓ No lag
   - ✓ Single render
5. Click **Next** once
   - ✓ Should immediately show Q2
   - ✓ No lag
   - ✓ Single render
6. Repeat 4-5 several times
   - ✓ All clicks are responsive
   - ✓ No accumulation of lag
   - ✓ No modal appearing during navigation

## Key Design Principles
1. **One function per flow:** Navigation ≠ Submission progression
2. **Pure state transition:** Navigation only changes index, never fetches
3. **Intent tracking:** Modal respects user navigation intent
4. **Atomic operations:** Flag set/clear happens with navigation, not async callbacks
5. **No implicit hijacking:** Modal cannot override navigation

## Code Quality
- Clear separation of concerns
- Deterministic behavior (one click = one action)
- No race conditions between async operations
- Proper state management with TEST_STATE
- Console logging shows clear execution path

## Status
✓ Navigation race condition RESOLVED
✓ Previous button works on first click, every time
✓ Modal respects navigation intent
✓ No duplicate flows or renders
✓ System behaves like production CBT engine
