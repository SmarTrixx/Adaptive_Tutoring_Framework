# State Lifecycle Corruption - Root Cause Analysis

## Critical Issues Identified

### 1. **Timer Leaks & Re-initialization**
- `startTimeTracking()` creates a NEW `setInterval` EVERY time `renderQuestionWithNav()` is called
- Old timers are never cleared before creating new ones
- Result: Multiple timers running simultaneously, causing UI flickers and resets

### 2. **Navigation State Recomputed on Every Render**
- `canNavigateNext` calculated inside `renderQuestionWithNav()`
- Recalculated every time HTML is re-rendered
- PROBLEM: If any effect or callback re-renders, navigation state is recalculated
- Result: Next button state becomes unreliable

### 3. **Time Counter Reset on Re-render**
- Timer display starts from 0:00 every time `renderQuestionWithNav()` is called
- New interval with `startTime = Date.now()` on each call
- Result: Time resets whenever question is re-rendered

### 4. **Engagement Score DOM-Based**
- `document.getElementById('engagement-score')` updated directly
- If HTML is re-rendered, engagement score reverts to "--"
- Result: Engagement appears to reset

### 5. **inactivityTimer Not Cleaned**
- `startInactivityTracking()` creates interval but previous one not always cleared
- Multiple intervals tracking inactivity simultaneously
- Result: State corruption from conflicting timers

---

## Solution Architecture

### Authoritative State Object (Never Reset)

```javascript
const TEST_STATE = {
    currentQuestionIndex: 0,        // Current position
    highestAnsweredIndex: -1,        // Highest question answered
    sessionId: null,                 // Current session
    timePerQuestion: {},             // { questionId: seconds }
    engagementScores: {},            // { questionId: score }
    
    // Methods to enforce rules
    canNavigateNext() {
        return this.currentQuestionIndex < this.highestAnsweredIndex;
    },
    
    canNavigatePrev() {
        return this.currentQuestionIndex > 0;
    },
    
    isOnCurrentQuestion() {
        return this.currentQuestionIndex === this.highestAnsweredIndex;
    }
};
```

### Timer Management (Singleton)

- One active timer per question
- Timer ONLY updates DOM for time display
- Timer does NOT mutate navigation state
- Timer cleanup on question change

### Render Function (Stateless Display)

- Read from TEST_STATE, never write
- Display current values from authoritative state
- Never recompute navigation eligibility

---

## Implementation Plan

1. Create TEST_STATE object with getter methods
2. Fix timer leaks (clear before creating, cleanup on question change)
3. Decouple navigation eligibility from render
4. Preserve engagement scores across re-renders
5. Prevent time reset on re-render
