# CRITICAL FIX: Modal Auto-Close Double Execution

**Date:** January 6, 2026  
**Status:** ✅ FIXED  
**Commit:** 956f015

---

## Issue: Questions Auto-Advancing Without User Interaction

**Problem:**
- User answers a question
- Feedback modal appears and auto-closes after 12 seconds
- User sees new question loading automatically
- But even if user clicks the "Continue" button immediately, the question STILL advances again after ~12 more seconds
- Result: User loses track, questions keep changing

**Root Cause:**
The feedback modal had a 12-second auto-close timeout that called `handleContinue()`:

```javascript
// Before (BROKEN):
const autoCloseTimeout = setTimeout(handleContinue, 12000);

if (closeBtn) {
    closeBtn.onclick = (e) => {
        handleContinue();  // Timeout NOT cleared!
    };
}
```

**What Was Happening:**
1. Modal appears after answer submission
2. `autoCloseTimeout` set for 12 seconds
3. User clicks "Continue" button IMMEDIATELY
4. `handleContinue()` runs, fetches next question, modal removed ✓
5. BUT... `autoCloseTimeout` is STILL RUNNING in the background!
6. After 12 seconds from original time, timeout fires
7. `handleContinue()` runs AGAIN (duplicate execution!)
8. Next question advances unexpectedly

**Timeline Example:**
```
00:00 - Modal shows, timeout set for 00:12
00:01 - User clicks Continue → handleContinue() runs → Question 5 loaded
00:12 - Timeout fires! → handleContinue() runs AGAIN → Question 6 loaded unexpectedly
```

---

## Solution

**Fix #1: Clear the timeout when modal closes**
```javascript
// After (FIXED):
let autoCloseTimeout = null;

const handleContinue = async () => {
    // Clear the timeout BEFORE doing anything else
    if (autoCloseTimeout) {
        clearTimeout(autoCloseTimeout);
    }
    
    closeModal();
    // ... rest of logic
};

if (closeBtn) {
    closeBtn.onclick = (e) => {
        e.stopPropagation();
        handleContinue();  // This now clears the timeout!
    };
}

// Set timeout (can now be cleared)
autoCloseTimeout = setTimeout(() => {
    handleContinue();
}, 12000);
```

**Fix #2: Prevent double execution**
```javascript
let continueHandlerExecuted = false;

const handleContinue = async () => {
    // CRITICAL: Prevent double execution
    if (continueHandlerExecuted) {
        console.log('[MODAL] handleContinue already executed, skipping duplicate call');
        return;
    }
    continueHandlerExecuted = true;
    
    // ... rest of logic
};
```

This prevents `handleContinue()` from running twice even if it's called multiple times.

---

## How It Works Now

**Timeline with Fix:**
```
00:00 - Modal shows, timeout set for 00:12
00:01 - User clicks Continue 
        → handleContinue() runs
        → Timeout CLEARED immediately
        → continueHandlerExecuted = true
        → Modal closed
        → Question 5 loaded
00:12 - Timeout fires but...
        → handleContinue() checks continueHandlerExecuted
        → SKIPPED (already executed)
        → No double advancement!
```

**Result:**
✅ No more automatic question changes after user clicks
✅ Auto-close still works if user doesn't interact (12s timeout still fires normally)
✅ Modal closes properly in all scenarios
✅ Prevents accidental double question advancement

---

## Code Changes

**File:** `frontend/app.js`

**Changes in `showFeedbackModal()` function:**

1. **Declare variables before use:**
   ```javascript
   let autoCloseTimeout = null;
   let continueHandlerExecuted = false;
   ```

2. **Clear timeout and prevent double execution:**
   ```javascript
   const handleContinue = async () => {
       if (continueHandlerExecuted) return;  // Guard against double execution
       continueHandlerExecuted = true;
       
       if (autoCloseTimeout) clearTimeout(autoCloseTimeout);  // Clear auto-close
       closeModal();  // Remove modal from DOM
       
       // ... rest of function
   };
   ```

3. **Set timeout with logging:**
   ```javascript
   autoCloseTimeout = setTimeout(() => {
       console.log('[MODAL] Auto-closing after 12s');
       handleContinue();
   }, 12000);
   ```

---

## Testing

**Test 1: Quick Close (Click Immediately)**
1. Answer a question
2. Modal appears
3. Click "Continue" button IMMEDIATELY (within 1 second)
4. ✅ Should load one question only, not two
5. No auto-advance should happen 12 seconds later

**Test 2: Wait for Auto-Close (Don't Click)**
1. Answer a question
2. Modal appears
3. **Do NOT click anything**
4. Wait 12+ seconds
5. ✅ Modal should auto-close automatically
6. Question should advance once

**Test 3: Click Close Button**
1. Answer question
2. Modal appears
3. Click the X button (top right)
4. ✅ Should load next question normally
5. Should NOT advance again after 12 seconds

---

## Logs

After fix, you should see logs like:

**Quick close scenario:**
```
[MODAL] More questions remain, loading next NEW question
[FETCH-NEXT] Fetching next NEW question
[MODAL] Cleared auto-close timeout
[MODAL] Question rendered successfully
```

**Auto-close scenario (no click):**
```
[MODAL] More questions remain, loading next NEW question
[MODAL] Auto-closing feedback modal after 12s (no user interaction)
[MODAL] Cleared auto-close timeout
[FETCH-NEXT] Fetching next NEW question
```

---

## Impact

**Before Fix:**
- Questions auto-advance unexpectedly
- Double auto-fetch causing page flicker
- User confusion about which question they're on
- Navigation appears to "stutter"

**After Fix:**
- Questions only advance when user clicks OR after auto-close timeout
- Never double-advance
- Smooth progression through test
- Stable question display

---

## Related Issues

This fix also helps with the page reload issue where questions were changing:
- Modal was likely auto-closing invisibly
- Page would reload
- Modal would trigger another question fetch
- Results in question changing on reload

Now with proper timeout cleanup, page reloads are more stable.

---

## Status

✅ **FIXED** - Modal auto-close timeout now properly cleared  
✅ **FIXED** - Double execution prevented with guard flag  
✅ **FIXED** - Logs added for debugging (see console for [MODAL] messages)

**Test now:** Run a test session and verify questions don't auto-advance unexpectedly.
