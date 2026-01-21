# Engagement Metrics and Adaptive Mechanism - Technical Reference

## Executive Summary

This document provides a complete technical reference for how the Adaptive Intelligent Tutoring Framework measures student engagement, calculates engagement scores, and uses those scores to adapt the learning experience. It covers both the core behavioral/cognitive measurement systems and the optional facial expression signal integration.

**Key Characteristics:**
- **Primary Drivers**: Behavioral indicators (response time, navigation, hints) and cognitive indicators (accuracy, learning progress)
- **Soft Signals**: Affective indicators inferred from behavior, plus optional facial expression data
- **Modular Design**: All optional features can be disabled without affecting core functionality
- **Transparent**: All calculations deterministic and fully logged for audit trails

---

## Part 1: Engagement Indicators Collection

### 1.1 Behavioral Indicators (Observable, Directly Measured)

Behavioral indicators capture observable student actions during test interaction.

#### Response Time
- **What it measures**: How quickly student responds to questions
- **Collection point**: Frontend (`frontend/app.js` line ~800)
  ```javascript
  const responseTime = Date.now() - questionStartTime;  // milliseconds
  ```
- **Storage**: `StudentResponse.response_time_seconds` (converted to seconds)
- **Interpretation**:
  - Very fast (<3s): May indicate guessing or overconfidence
  - Optimal (5-15s): Thoughtful engagement
  - Slow (>30s): May indicate uncertainty, confusion, or distraction
- **Used in**: Difficulty adaptation, pacing adjustment, engagement calculation

#### Navigation Frequency
- **What it measures**: Count of Prev/Next button clicks on each question
- **Collection point**: Frontend button click handler
  ```javascript
  currentQuestionState.navigationCount++;  // Incremented on each click
  ```
- **Storage**: `StudentResponse.navigation_frequency`
- **Interpretation**:
  - 0 navigations: Sequential progression, no review
  - 1-3 navigations: Light review/verification
  - 5+ navigations: Potential distraction or high verification behavior
- **Used in**: Engagement scoring, pacing decisions, distraction detection

#### Option Changes
- **What it measures**: How many times student changes their selected answer before submission
- **Collection point**: Frontend option button click handlers
  ```javascript
  option_change_history: [
    { from: 'A', to: 'B', timestamp: 1234567890 },
    { from: 'B', to: 'C', timestamp: 1234567895 }
  ]
  option_change_count: 2
  ```
- **Storage**: `StudentResponse.option_change_count`, `option_change_history` (JSON array)
- **Interpretation**:
  - 0 changes: Decision confidence
  - 1-2 changes: Light reconsideration (normal)
  - 5+ changes: Significant indecision, may indicate confusion
- **Used in**: Frustration inference, engagement scoring, difficulty decisions

#### Hints Requested
- **What it measures**: How many hint viewing events occur before submission
- **Collection point**: Frontend hint button handler
  ```javascript
  currentQuestionState.hints_used.push({
    hint_text: "Hint content",
    timestamp: Date.now()
  });
  hints_requested = currentQuestionState.hints_used.length;
  ```
- **Storage**: `StudentResponse.hints_requested`, `hints_used_array` (JSON)
- **Interpretation**:
  - 0 hints: High confidence or fast completion
  - 1 hint: Normal support request
  - 3+ hints: Struggling with question, low confidence
- **Used in**: Frustration inference, hint frequency adaptation

#### Inactivity Duration
- **What it measures**: Periods of time without user interaction on current question
- **Collection point**: Frontend inactivity timer (see `startInactivityTracking()`)
  ```javascript
  if (lastActivityTime && (now - lastActivityTime) > INACTIVITY_THRESHOLD) {
    currentInactivityDuration += (now - lastActivityTime);
  }
  ```
- **Storage**: `StudentResponse.inactivity_duration_ms`
- **Interpretation**:
  - 0-5s: Normal engagement
  - 5-30s: Possible distraction
  - >30s: Significant disengagement or off-task behavior
- **Used in**: Engagement scoring, break recommendations

#### Completion Rate
- **What it measures**: Proportion of session questions answered vs. total
- **Calculation point**: Backend aggregation
  ```python
  completion_rate = answered_count / total_questions
  ```
- **Storage**: `EngagementMetric.completion_rate`
- **Interpretation**:
  - >80%: High persistence
  - 50-80%: Moderate completion
  - <30%: May indicate disengagement
- **Used in**: Pacing decisions, completion encouragement

---

### 1.2 Cognitive Indicators (Inferred from Performance)

Cognitive indicators measure learning and comprehension.

#### Accuracy
- **What it measures**: Correctness of student's response to each question
- **Calculation point**: Backend during response submission
  ```python
  is_correct = (student_answer == question.correct_option)
  accuracy = sum(correct_responses) / total_responses
  ```
- **Storage**: `StudentResponse.is_correct` (boolean), `EngagementMetric.accuracy` (ratio)
- **Interpretation**:
  - >80%: Strong understanding
  - 60-80%: Solid understanding with gaps
  - <50%: Struggling with material
- **Used in**: Difficulty adjustment, learning progress detection, knowledge gap identification

#### Learning Progress
- **What it measures**: Trend in accuracy across recent questions (last 5 responses)
- **Calculation point**: Backend in `track_cognitive_indicators()`
  ```python
  recent_responses = responses[-5:]  # Last 5 responses
  recent_correct = sum(1 for r in recent_responses if r.is_correct)
  learning_progress = recent_correct / len(recent_responses)
  ```
- **Storage**: `EngagementMetric.learning_progress` (0.0-1.0)
- **Interpretation**:
  - Increasing trend: Learning is occurring
  - Stable trend: Performance plateau
  - Declining trend: Fatigue or concept loss
- **Used in**: Difficulty adjustment decisions, break recommendations

#### Knowledge Gaps
- **What it measures**: Topic areas where student shows lower accuracy
- **Calculation point**: Backend aggregation by topic
  ```python
  gaps = [topic for topic in topics if topic_accuracy < 0.5]
  ```
- **Storage**: `EngagementMetric.knowledge_gaps` (JSON array of topic names)
- **Used in**: Content selection, targeted reinforcement, learning recommendations

---

### 1.3 Affective Indicators (Inferred from Behavioral Patterns)

Affective indicators estimate emotional and motivational states. **These are inferred, not directly measured.**

#### Confidence Level
- **What it infers**: Student's subjective confidence in answers
- **Inference logic** (from `backend/app/engagement/tracker.py`):
  ```python
  # Recent accuracy indicates confidence
  recent_accuracy = [correctness of last 3-5 responses]
  
  # Response time patterns indicate confidence
  response_time_fast = response_time < 5 seconds
  response_time_consistent = std_dev(response_times) < threshold
  
  confidence = (recent_accuracy * 0.6) + (response_time_fast * 0.4)
  ```
- **Range**: 0.0 (no confidence) to 1.0 (high confidence)
- **Used in**: Hint frequency, difficulty adjustment, engagement scoring

#### Frustration Level
- **What it infers**: Estimated frustration from behavioral patterns
- **Inference logic**:
  ```python
  # High option changes indicate indecision/frustration
  frequent_changes = option_change_count > 3
  
  # Slow responses with errors indicate frustration
  slow_incorrect = response_time > 20s AND is_incorrect
  
  # Error streaks indicate mounting frustration
  error_streak = 3+ consecutive errors
  
  frustration = (frequent_changes * 0.4) + (slow_incorrect * 0.35) + (error_streak * 0.25)
  ```
- **Range**: 0.0 (no frustration) to 1.0 (high frustration)
- **Used in**: Hint frequency, pacing suggestions, content selection

#### Interest Level
- **What it infers**: Estimated interest/motivation from engagement patterns
- **Inference logic**:
  ```python
  # Fast responses (without errors) indicate interest
  fast_correct = response_time < 8s AND is_correct
  
  # Session continuation indicates interest
  session_completeness = questions_answered / total_questions
  
  # Low inactivity indicates focus
  low_inactivity = inactivity_duration < 5s
  
  interest = (fast_correct * 0.4) + (session_completeness * 0.35) + (low_inactivity * 0.25)
  ```
- **Range**: 0.0 (no interest) to 1.0 (high interest)
- **Used in**: Content variety, engagement scoring, motivation detection

---

## Part 2: Engagement Score Calculation (Fusion)

### 2.1 Component Score Normalization

Each indicator category (behavioral, cognitive, affective) is normalized to a 0.0-1.0 scale.

**Behavioral Score** (`_normalize_behavioral()` in `fusion.py`):
```python
behavioral_score = 0.0

# Low variance in response time = consistency = engagement
response_time_deviation = std_dev(response_times) / mean(response_times)
consistency = max(0.0, 1.0 - response_time_deviation)
behavioral_score += consistency * 0.35

# Low inactivity = engagement
inactivity_normalized = min(1.0, inactivity_duration / 30.0)
engagement_from_activity = max(0.0, 1.0 - inactivity_normalized)
behavioral_score += engagement_from_activity * 0.35

# Moderate hint usage = engagement
hints_per_question = hints_requested / num_questions
hint_engagement = max(0.0, 1.0 - (hints_per_question * 0.5))
behavioral_score += hint_engagement * 0.30

# Clamp to valid range
behavioral_score = max(0.0, min(1.0, behavioral_score))
```

**Cognitive Score** (`_normalize_cognitive()` in `fusion.py`):
```python
cognitive_score = accuracy  # Direct measure: accuracy = competence

# Weight recent performance more heavily
recent_accuracy = learning_progress  # Last 5 responses
cognitive_score = (accuracy * 0.6) + (recent_accuracy * 0.4)

# Clamp to valid range
cognitive_score = max(0.0, min(1.0, cognitive_score))
```

**Affective Score** (`_normalize_affective()` in `fusion.py`):
```python
affective_score = 0.5  # Start neutral

# Confidence drives engagement
if confidence_level is not None:
    affective_score += (confidence_level * 0.35)

# Frustration reduces engagement
if frustration_level is not None:
    affective_score -= (frustration_level * 0.35)

# Interest drives engagement
if interest_level is not None:
    affective_score += (interest_level * 0.3)

# Clamp to valid range
affective_score = max(0.0, min(1.0, affective_score))
```

### 2.2 Weighted Fusion

Component scores are combined using fixed weights:

```python
BEHAVIORAL_WEIGHT = 0.40   # 40% of engagement (most reliable)
COGNITIVE_WEIGHT = 0.40    # 40% of engagement (direct performance measure)
AFFECTIVE_WEIGHT = 0.20    # 20% of engagement (inferred, less reliable)

engagement_score = (
    behavioral_score * BEHAVIORAL_WEIGHT +
    cognitive_score * COGNITIVE_WEIGHT +
    affective_score * AFFECTIVE_WEIGHT
)

# Final engagement classification
if engagement_score >= 0.80:
    engagement_level = 'high'
elif engagement_score >= 0.60:
    engagement_level = 'medium'
else:
    engagement_level = 'low'
```

**Why these weights?**
- Behavioral (40%): Observable, reliable, directly measurable
- Cognitive (40%): Objective performance data, most important for learning
- Affective (20%): Inferred from patterns, less certain, secondary signal

---

## Part 3: Adaptive Mechanism - Difficulty Adjustment

### 3.1 Core Difficulty Adaptation Algorithm

The adaptation engine uses accuracy as the primary driver, with engagement as a modulator.

**Location**: `backend/app/adaptation/engine.py` → `adapt_difficulty()`

**Algorithm (Precision Steps)**:

```python
current_difficulty = session.current_difficulty  # 0.0 to 1.0
accuracy = engagement_metric.accuracy
engagement_score = engagement_metric.engagement_score

# Rule-based stepping (deterministic)
if accuracy >= 0.99:           # Perfect/near-perfect
    step = +0.10               # Significant increase
    new_difficulty = current_difficulty + step
    
elif accuracy >= 0.80:         # High accuracy
    step = +0.10               # Same increase for consistency
    new_difficulty = current_difficulty + step
    
elif accuracy >= 0.67:         # Good but mixed (2/3 correct)
    step = +0.01               # Tiny increase for stability
    new_difficulty = current_difficulty + step
    
elif accuracy > 0.33:          # Marginal accuracy
    step = 0.00                # No change (wait for clarity)
    new_difficulty = current_difficulty
    
elif accuracy > 0.01:          # Low accuracy
    step = -0.10               # Significant decrease
    new_difficulty = current_difficulty - step
    
else:                           # Complete failure
    step = -0.10               # Significant decrease
    new_difficulty = current_difficulty - step

# Apply engagement modulator (prevents oscillation)
if engagement_score < 0.3 and new_difficulty == current_difficulty:
    # Very low engagement with marginal accuracy
    step = -0.05               # Smaller decrease to avoid frustration
    new_difficulty = current_difficulty - step
```

**Key Properties:**
1. **Deterministic**: Same accuracy always produces same difficulty change
2. **Symmetric**: Perfect accuracy (+0.10) mirrors complete failure (-0.10)
3. **Stable**: Marginal accuracy produces tiny steps (+0.01), not large jumps
4. **Adaptive Engagement**: Low engagement prevents aggressive increases
5. **Bounded**: Difficulty always stays within [min_difficulty, max_difficulty]

**Difficulty Band Mapping**:
```
Difficulty 0.0 - 0.35  →  Easy questions (difficulty rating 0.1 - 0.4)
Difficulty 0.35 - 0.65 →  Medium questions (difficulty rating 0.35 - 0.65)
Difficulty 0.65 - 1.0  →  Hard questions (difficulty rating 0.6 - 0.95)
```

### 3.2 Optional Facial Signal Integration

**Location**: `backend/app/adaptation/facial_signal_integration.py`

When enabled (see Configuration section below), facial expression data can optionally modify difficulty adjustments.

**How it works:**

```python
# Step 1: Extract engagement signal from facial data
facial_data = {
    'emotion_detected': 'frustrated',
    'emotion_confidence': 0.87,
    'gaze_pattern': 'scattered',
    'posture_type': 'slumped'
}

facial_signal, reason = processor.extract_engagement_signal(facial_data)
# facial_signal = 0.20 (low engagement due to frustration)

# Step 2: Compute facial modifier (soft signal only)
base_difficulty_delta = 0.10  # From accuracy (perfect answer)
facial_modifier = (facial_signal - 0.5) * 2  # Convert to -1 to +1 range
facial_adjustment = base_difficulty_delta * facial_modifier * DIFFICULTY_ADJUSTMENT_WEIGHT

# For this example:
# facial_modifier = (0.20 - 0.5) * 2 = -0.60
# facial_adjustment = 0.10 * (-0.60) * 0.10 = -0.006
# final_delta = 0.10 - 0.006 = 0.094 (slightly reduced increase)

# Step 3: Apply modification (clamped to bounds)
modified_delta = max(-0.15, min(0.15, base_delta + facial_adjustment))
new_difficulty = current_difficulty + modified_delta
```

**Critical Design Principle**: Facial signals ONLY adjust the magnitude of the decision, never override it. If accuracy says "increase difficulty by 0.10", facial data can modify it to 0.09 or 0.11, but never change the direction (increase → decrease).

---

## Part 4: Adaptive Mechanism - Pacing and Hints

### 4.1 Pacing Adaptation

**Purpose**: Adjust time expectations and question presentation speed

**Triggers** (from `adapt_pacing()`):

| Condition | Action | Reason |
|-----------|--------|--------|
| Slow response + Low engagement | Fast pacing | Prevent boredom |
| Fast response + Low accuracy | Slow pacing | Prevent rushing |
| High engagement + Slow response | Fast pacing | Challenge engaged learner |
| Low completion rate (<30%) | Slow pacing | Reduce cognitive load |
| Excessive navigation (>20 clicks) + Low engagement | Fast pacing | Reduce distraction |
| Normal conditions | Maintain pacing | No change needed |

**Pacing levels**: `slow` (60s limit) → `medium` (30s limit) → `fast` (15s limit)

### 4.2 Hint Frequency Adaptation

**Purpose**: Adjust how often hints are suggested

**Base Strategy Selection** (from `adapt_hint_frequency()`):

```python
if frustration > 0.7 or (confidence < 0.3 and attempts > 2):
    hint_strategy = 'generous'  # Proactive hints offered
elif confidence > 0.8 and accuracy > 0.7:
    hint_strategy = 'minimal'   # Few hints; student confident
else:
    hint_strategy = 'normal'    # Standard hint availability
```

**Optional Facial Modification**:
```python
if facial_modifier.is_enabled():
    # If facial shows high frustration, upgrade to 'generous'
    if facial_engagement_signal < 0.35:
        hint_strategy = 'generous'
    
    # If facial shows high engagement, downgrade to 'minimal'
    elif facial_engagement_signal > 0.85:
        hint_strategy = 'minimal'
```

---

## Part 5: Configuration and Control

### 5.1 Facial Signal Integration Configuration

**Location**: `backend/app/adaptation/facial_signal_integration.py` → `FacialSignalConfig`

```python
class FacialSignalConfig:
    # Master enable/disable switch
    ENABLED = False  # Set to True to activate
    
    # Emotion confidence threshold
    MIN_EMOTION_CONFIDENCE = 0.60  # Only use if 60%+ confident in emotion
    
    # Signal weights (how much facial data affects decisions)
    ENGAGEMENT_SIGNAL_WEIGHT = 0.15        # Max 15% engagement adjustment
    DIFFICULTY_ADJUSTMENT_WEIGHT = 0.10   # Max 10% difficulty adjustment
    HINT_SUGGESTION_WEIGHT = 0.20         # Max 20% hint adjustment
    
    # Emotion to engagement mapping
    EMOTION_ENGAGEMENT_MAP = {
        'happy': 0.95,
        'excited': 1.0,
        'confident': 0.85,
        'neutral': 0.60,
        'confused': 0.40,
        'frustrated': 0.20,
        'bored': 0.15,
        'anxious': 0.30,
        'sad': 0.25,
        'angry': 0.10
    }
```

**To Enable Facial Integration:**

1. Set `ENABLED = True` in `FacialSignalConfig`
2. Ensure facial data is being collected in frontend (currently disabled)
3. Implement actual facial detection (requires ML model, e.g., face-api.js)

**To Disable**: Set `ENABLED = False`. System behaves identically to before facial integration.

### 5.2 Core Adaptation Configuration

**Location**: `backend/config.py`

```python
ADAPTATION_CONFIG = {
    'min_difficulty': 0.0,
    'max_difficulty': 1.0,
    'difficulty_step_perfect': 0.10,    # Perfect accuracy increase
    'difficulty_step_stable': 0.01,     # Mixed accuracy increase
    'difficulty_step_failure': 0.10,    # Low accuracy decrease
    'enable_rl_learning': False,        # Reinforcement learning (future)
}

ENGAGEMENT_THRESHOLDS = {
    'response_time_fast': 3.0,      # Seconds (possible guessing)
    'response_time_slow': 30.0,     # Seconds (possible confusion)
    'high_engagement': 0.80,        # Engagement threshold
    'low_engagement': 0.40,         # Engagement threshold
    'high_accuracy': 0.80,
    'low_accuracy': 0.35,
}
```

---

## Part 6: Data Flow and Storage

### 6.1 Data Collection Flow

```
Student submits answer
    ↓
Frontend captures interaction data:
  - response_time
  - option_changes
  - navigation_frequency
  - hints_requested
  - facial_metrics (if enabled)
    ↓
POST /api/cbt/response/submit with full payload
    ↓
Backend `cbt/system.py` receives and processes:
  1. Save StudentResponse record (raw interaction data)
  2. Calculate engagement metrics
  3. Run adaptation engine (difficulty, pacing, hints)
  4. Return feedback with new difficulty
    ↓
Frontend displays feedback modal with:
  - Correctness
  - Explanation
  - New difficulty level
  - Engagement score (if available)
```

### 6.2 Database Schema

**StudentResponse Table** (one row per answer):
```python
class StudentResponse(db.Model):
    # Behavioral data
    response_time_seconds: float
    initial_option: str             # A, B, C, D
    final_option: str
    option_change_count: int
    option_change_history: JSON     # [{from, to, timestamp}, ...]
    navigation_frequency: int
    
    # Cognitive & Affective data
    time_spent_per_question: int    # Seconds
    inactivity_duration_ms: int     # Milliseconds
    hesitation_flags: JSON          # {rapidClicking, longHesitation, ...}
    
    # Facial data (if available)
    facial_metrics: JSON            # {camera_enabled, emotion, gaze, posture, ...}
    
    # Question/answer data
    is_correct: bool
    student_answer: str
    knowledge_gaps: JSON            # [{topic, area}, ...]
```

**EngagementMetric Table** (one row per question answered, aggregated):
```python
class EngagementMetric(db.Model):
    # Behavioral
    response_time_seconds: float
    hints_requested: int
    inactivity_duration: float
    navigation_frequency: int
    completion_rate: float
    
    # Cognitive
    accuracy: float                  # Overall accuracy
    learning_progress: float         # Recent accuracy trend
    knowledge_gaps: JSON
    
    # Affective (inferred)
    confidence_level: float
    frustration_level: float
    interest_level: float
    
    # Composite score
    engagement_score: float          # 0.0-1.0 (weighted fusion)
    engagement_level: str            # 'low', 'medium', 'high'
```

---

## Part 7: Logging and Auditability

### 7.1 Adaptation Logging

Every adaptation decision is logged to `AdaptationLog` table:

```python
class AdaptationLog(db.Model):
    student_id: str
    session_id: str
    adaptation_type: str             # 'difficulty', 'pacing', 'hints'
    trigger_metric: str              # What caused the change
    trigger_value: float             # Value of trigger (accuracy, engagement, etc.)
    old_value: float                 # Previous difficulty/pacing/etc.
    new_value: float                 # New difficulty/pacing/etc.
    reason: str                      # Human-readable explanation
    timestamp: datetime
    
    # Optional facial integration metadata
    facial_integration: JSON         # {enabled, signal_used, signal_value, reason}
```

**Example Log Entry**:
```json
{
    "student_id": "stu_123",
    "session_id": "sess_456",
    "adaptation_type": "difficulty",
    "trigger_metric": "high_accuracy",
    "trigger_value": 0.95,
    "old_value": 0.50,
    "new_value": 0.60,
    "reason": "High accuracy (95%), +0.10 step [Facial adjustment: Engagement signal 0.75 → +0.02]",
    "timestamp": "2026-01-10T15:30:45Z",
    "facial_integration": {
        "facial_integration_enabled": true,
        "facial_signal_used": true,
        "facial_engagement_signal": 0.75,
        "facial_signal_reason": "Emotion: confident (confidence: 95%)"
    }
}
```

### 7.2 Console Logging

All adaptation decisions logged to application logs with `[FACIAL]` prefix if facial data involved:

```
[ADAPTATION] Difficulty adjustment: accuracy=0.95 → step=+0.10
[FACIAL] Engagement score: (0.65 × 0.80) + (0.75 × 0.20) = 0.68 (Emotion: confident)
[FACIAL] Difficulty modified: Engagement signal -0.60 × 10% = -0.006 (base: +0.10 → final: +0.094)
[ADAPTATION] Hint frequency: generous (frustration_level=0.72 > 0.70)
```

---

## Part 8: Mathematical Formulas Reference

### 8.1 Engagement Score Calculation

```
behavioral_score = (consistency × 0.35) + (activity × 0.35) + (hints × 0.30)
cognitive_score = (overall_accuracy × 0.6) + (recent_accuracy × 0.4)
affective_score = 0.5 + (confidence × 0.35) - (frustration × 0.35) + (interest × 0.3)

engagement_score = (behavioral_score × 0.40) + (cognitive_score × 0.40) + (affective_score × 0.20)
```

### 8.2 Facial Signal Integration

```
facial_modifier = (facial_signal - 0.5) × 2         # Convert [0,1] to [-1,+1]
facial_adjustment = base_delta × facial_modifier × weight
modified_delta = clamp(base_delta + facial_adjustment, -0.15, +0.15)
```

Where:
- `facial_signal` = engagement inferred from emotion/gaze/posture [0, 1]
- `base_delta` = difficulty change from accuracy [−0.1, +0.1]
- `weight` = DIFFICULTY_ADJUSTMENT_WEIGHT (0.10)

### 8.3 Inferred Affective Indicators

**Confidence**:
```
confidence = (recent_accuracy × 0.6) + (fast_response × 0.4)
            where fast_response = 1 if response_time < 5s else 0
```

**Frustration**:
```
frustration = (option_changes > 3 × 0.4) + (slow_incorrect × 0.35) + (error_streak × 0.25)
             where slow_incorrect = 1 if response_time > 20s AND not is_correct else 0
                   error_streak = 1 if 3+ consecutive errors else 0
```

**Interest**:
```
interest = (fast_correct × 0.4) + (completion_rate × 0.35) + (low_inactivity × 0.25)
          where fast_correct = 1 if response_time < 8s AND is_correct else 0
                low_inactivity = 1 if inactivity < 5s else 0
```

---

## Part 9: Implementation Example Walkthrough

### Scenario: Student answers question with mixed engagement signals

```
Input: StudentResponse
{
    "is_correct": true,
    "response_time_seconds": 8.5,
    "option_change_count": 2,
    "navigation_frequency": 0,
    "hints_requested": 1,
    "inactivity_duration_ms": 0,
    "facial_metrics": {
        "emotion_detected": "confused",
        "emotion_confidence": 0.78,
        "gaze_pattern": "scattered",
        "posture_type": "slumped"
    }
}
```

**Step 1: Calculate Engagement Indicators**
```
Behavioral:
  - response_time: 8.5s (within optimal 5-15s range)
  - option_changes: 2 (normal reconsideration)
  - hints_requested: 1 (moderate support need)
  - navigation: 0 (sequential, focused)
  
  behavioral_score = 0.65 (good consistency, some uncertainty)

Cognitive:
  - accuracy: 1.0 (correct answer)
  
  cognitive_score = 1.0 (perfect response)

Affective (inferred):
  - confusion + scattered gaze → low confidence
  - slumped posture → low motivation
  
  affective_score = 0.40 (below neutral)
```

**Step 2: Fuse into Engagement Score**
```
engagement_score = (0.65 × 0.40) + (1.0 × 0.40) + (0.40 × 0.20)
                 = 0.26 + 0.40 + 0.08
                 = 0.74 → "medium" engagement
```

**Step 3: Adapt Difficulty (Core)**
```
Current difficulty: 0.50
Accuracy: 1.0 (100%)
Rule: accuracy >= 0.99 → +0.10 step

new_difficulty = 0.50 + 0.10 = 0.60
```

**Step 4: Optional Facial Modification** (if enabled)
```
Facial signal from: emotion=confused, gaze=scattered, posture=slumped
facial_engagement_signal = 0.30 (low engagement)

facial_modifier = (0.30 - 0.5) × 2 = -0.40
facial_adjustment = 0.10 × (-0.40) × 0.10 = -0.004

modified_difficulty = 0.50 + (0.10 - 0.004) = 0.596 ≈ 0.60
(Slight reduction in difficulty increase due to low engagement signals)
```

**Step 5: Log Adaptation**
```
AdaptationLog entry:
{
    "adaptation_type": "difficulty",
    "trigger_metric": "perfect_accuracy",
    "old_value": 0.50,
    "new_value": 0.60,
    "reason": "Perfect accuracy (100%), +0.10 step [Facial adjustment: Engagement signal 0.30 → -0.004]",
    "facial_integration": {
        "facial_integration_enabled": true,
        "facial_signal_used": true,
        "facial_engagement_signal": 0.30,
        "facial_signal_reason": "Emotion: confused (78%) | Gaze: scattered (-0.3) | Posture: slumped (-0.25)"
    }
}
```

**Step 6: Return to Student**
```
Response to frontend:
{
    "success": true,
    "is_correct": true,
    "current_difficulty": 0.60,
    "difficulty_delta": +0.10,
    "engagement_score": 0.74,
    "engagement_level": "medium"
}

Frontend displays:
✓ Correct!
Difficulty: 60% (📈 +10%)
Engagement: 74% 💙 Medium
```

---

## Part 10: Future Expansion Possibilities

### 10.1 Full Facial Analysis (If Hardware Available)

```python
# Future: When webcam/ML model available

FACIAL_ENHANCEMENTS = {
    "gaze_stability": {
        "description": "Track eye contact consistency",
        "adaptation": "Adjust break recommendations",
        "implementation": "Requires eye-tracking hardware"
    },
    "blink_rate": {
        "description": "Measure cognitive load via blink frequency",
        "adaptation": "Detect fatigue, suggest breaks",
        "implementation": "Requires video processing"
    },
    "micro_expressions": {
        "description": "Detect fleeting genuine emotions",
        "adaptation": "Better emotion inference",
        "implementation": "Requires advanced CV model"
    },
    "head_pose": {
        "description": "Detect engagement from posture dynamics",
        "adaptation": "Detect slouching, attention loss",
        "implementation": "Requires pose detection model"
    }
}
```

### 10.2 Reinforcement Learning Integration

Currently, `RLAdaptiveAgent` exists but is not active. Future implementation:

```python
# Future: Implement training loop

RL_ROADMAP = {
    "Phase 1": "Collect episodes (currently disabled, would break research validity)",
    "Phase 2": "Train Q-table offline on historical data",
    "Phase 3": "Validate learned policy against hand-tuned rules",
    "Phase 4": "A/B test learned vs. rule-based adaptation",
    "Phase 5": "Deploy if validation successful"
}

# Why not now?
# - Would introduce non-deterministic behavior (research invalid)
# - Would require explaining learned policies (transparency loss)
# - Current rule-based is transparent, auditable, reproducible
```

### 10.3 Multimodal Integration

```python
# Future: Combine multiple signal types

MULTIMODAL_FUSION = {
    "emotion_from_text": "Analyze student chat/reflections for sentiment",
    "engagement_from_audio": "Detect speech patterns indicating confusion",
    "attention_from_eye_tracking": "Real gaze data vs. inferred gaze",
    "stress_from_biometrics": "Optional: heart rate, skin conductance if available"
}

# Weighted fusion:
engagement = (
    0.40 * behavioral +           # Observable actions (most reliable)
    0.30 * cognitive +            # Performance (direct measure)
    0.15 * facial_emotion +       # Visual emotion (moderate reliability)
    0.10 * text_sentiment +       # Written sentiment (if available)
    0.05 * audio_patterns         # Speech analysis (if available)
)
```

---

## Part 11: Troubleshooting and Validation

### 11.1 Common Issues

| Issue | Symptom | Cause | Solution |
|-------|---------|-------|----------|
| Difficulty stuck at 0.5 | No adaptation happening | Engagement metrics not calculated | Verify StudentResponse data in database |
| Facial signals breaking system | Crashes when facial_data accessed | Facial data is None/invalid | Add null checks, disable facial integration |
| Engagement scores all 0.5 | No variation in engagement | All component scores neutral | Check behavioral/cognitive/affective calculation |
| Adaptation overshooting | Difficulty jumps too much | Facial adjustment multiplier too high | Reduce `DIFFICULTY_ADJUSTMENT_WEIGHT` |

### 11.2 Validation Checklist

- [ ] StudentResponse records have non-zero response_time_seconds
- [ ] EngagementMetric rows have engagement_score between 0.0 and 1.0
- [ ] AdaptationLog has entries for each response
- [ ] Difficulty changes are bounded within [0.0, 1.0]
- [ ] Facial data is either None or has valid emotion labels
- [ ] Facial integration can be disabled without crashing
- [ ] All timestamps are ISO 8601 format
- [ ] Navigation frequency accumulates correctly on revisits
- [ ] Option changes include all modifications before submission

---

## Part 12: References and Further Reading

**Key Files:**
- `backend/app/adaptation/engine.py` - Core adaptation logic
- `backend/app/adaptation/facial_signal_integration.py` - Optional facial integration
- `backend/app/engagement/tracker.py` - Engagement metric collection
- `backend/app/engagement/fusion.py` - Engagement score fusion
- `backend/app/engagement/indicators.py` - Indicator extraction
- `backend/app/cbt/system.py` - CBT system integration
- `frontend/app.js` - Frontend data collection (~2200 lines)

**Configuration Files:**
- `backend/config.py` - Adaptation thresholds
- `backend/app/adaptation/facial_signal_integration.py` → `FacialSignalConfig`

**Database Models:**
- `backend/app/models/engagement.py` - EngagementMetric schema
- `backend/app/models/session.py` - StudentResponse schema
- `backend/app/models/adaptation.py` - AdaptationLog schema

---

## Appendix: Quick Reference

### Engagement Score Interpretation

| Score | Level | Meaning | System Action |
|-------|-------|---------|----------------|
| 0.8-1.0 | High | Engaged, confident, learning well | Increase difficulty, reduce hints |
| 0.6-0.8 | Medium | Steady engagement, normal learning | Maintain difficulty, normal hints |
| 0.4-0.6 | Low | Reduced engagement, possible struggles | Maintain or decrease difficulty, offer hints |
| <0.4 | Very Low | Disengaged, frustrated, struggling | Decrease difficulty, increase support |

### Difficulty Band Reference

| Difficulty Range | Label | When Used | Question Characteristics |
|------------------|-------|-----------|--------------------------|
| 0.0 - 0.35 | Easy | Start, low engagement, struggling | Basic concepts, clear answers |
| 0.35 - 0.65 | Medium | Normal progression | Standard difficulty questions |
| 0.65 - 1.0 | Hard | High performance, high engagement | Advanced concepts, nuanced answers |

### Facial Integration Enable/Disable

**To Enable** (when facial data collection implemented):
```python
# File: backend/app/adaptation/facial_signal_integration.py
class FacialSignalConfig:
    ENABLED = True  # Change this
```

**To Disable** (default, no impact on system):
```python
class FacialSignalConfig:
    ENABLED = False  # System behavior unchanged
```

---

**Document Version**: 1.0  
**Last Updated**: January 10, 2026  
**Status**: Production Documentation  
**Audience**: Developers, Researchers, System Maintainers
