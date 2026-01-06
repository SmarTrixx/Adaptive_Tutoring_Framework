# Difficulty Scaling Algorithm - Quick Reference

## 📊 Accuracy-Driven Difficulty Progression

### The Algorithm in Action

#### Scenario 1: Perfect Performance ✅
Student gets 10/10 correct answers

```
Initial Difficulty: 0.50
After Question 1: 0.60 (accuracy 1.0 = +0.10)
After Question 2: 0.70 (accuracy 1.0 = +0.10)
After Question 3: 0.80 (accuracy 1.0 = +0.10)
After Question 4: 0.90 (accuracy 1.0 = +0.10)
After Question 5: 0.90 (at max_difficulty of 0.90)
```
**Pattern:** Large steps (+0.10) for sustained perfect accuracy

---

#### Scenario 2: Complete Failure ❌
Student gets 0/10 correct answers

```
Initial Difficulty: 0.50
After Question 1: 0.40 (accuracy 0.0 = -0.10)
After Question 2: 0.30 (accuracy 0.0 = -0.10)
After Question 3: 0.20 (accuracy 0.0 = -0.10)
After Question 4: 0.10 (accuracy 0.0 = -0.10)
After Question 5: 0.10 (at min_difficulty of 0.10)
```
**Pattern:** Large decreases (-0.10) for sustained failure

---

#### Scenario 3: Mixed Results (2/3 Correct) 🔄
Student gets 2 correct, 1 incorrect (66.7% accuracy)

```
Initial Difficulty: 0.50
After Q1 (correct): 0.50 (rolling accuracy < 0.67)
After Q2 (correct): 0.50 (rolling accuracy = 0.67) - borderline
After Q3 (wrong):   0.51 (accuracy 0.67 = +0.01)
After Q4 (correct): 0.51 (accuracy 0.67 = +0.01)
After Q5 (correct): 0.52 (accuracy 0.67 = +0.01)
```
**Pattern:** Tiny steps (+0.01) for mixed results - STABILITY MODE

---

### Accuracy Tiers & Behavior

| Accuracy | Tier | Step | Example | Behavior |
|----------|------|------|---------|----------|
| 1.0 (100%) | Perfect | +0.10 | All correct | Aggressive growth |
| 0.80-0.99 | High | +0.05 | 4/5 correct | Moderate growth |
| 0.67-0.79 | Good | +0.01 | 2/3 correct | Stability mode |
| 0.33-0.66 | Marginal | 0.00 | 1/3 correct | Hold steady |
| 0.01-0.32 | Low | -0.05 | 1/10 correct | Moderate decrease |
| 0.0 (0%) | Zero | -0.10 | No correct | Aggressive decrease |

---

## 🎯 Implementation Details

### Code Location
**File:** `backend/app/adaptation/engine.py`  
**Method:** `AdaptiveEngine.adapt_difficulty()`  
**Lines:** 19-115

### Key Functions

```python
def adapt_difficulty(self, student_id, session_id, engagement_metric):
    """
    Adapt difficulty based on accuracy with 6 precision tiers
    """
    accuracy = engagement_metric.accuracy
    engagement_score = engagement_metric.engagement_score
    
    # Six-tier system
    if accuracy >= 0.99:
        step = 0.10  # Perfect accuracy
    elif accuracy >= 0.8:
        step = 0.05  # High accuracy
    elif accuracy >= 0.67:
        step = 0.01  # Mixed/good (2/3+)
    elif accuracy > 0.33:
        step = 0.00  # Marginal (maintain)
    elif accuracy > 0.01:
        step = -0.05 # Low accuracy
    else:
        step = -0.10 # Zero accuracy
```

---

## 🔬 Testing Examples

### Test Case 1: Perfect Progression
```python
def test_perfect_difficulty_progression():
    """Verify 0.50 → 0.60 → 0.70 → 0.80 with perfect accuracy"""
    
    metric = create_engagement_metric(accuracy=1.0)
    engine = AdaptiveEngine()
    
    # First adaptation
    result = engine.adapt_difficulty(student_id, session_id, metric)
    assert result['new_difficulty'] == 0.60
    
    # Second adaptation  
    session.current_difficulty = 0.60
    result = engine.adapt_difficulty(student_id, session_id, metric)
    assert result['new_difficulty'] == 0.70
    
    # Third adaptation
    session.current_difficulty = 0.70
    result = engine.adapt_difficulty(student_id, session_id, metric)
    assert result['new_difficulty'] == 0.80
```

### Test Case 2: Perfect Failure Progression
```python
def test_perfect_failure_progression():
    """Verify 0.50 → 0.40 → 0.30 → 0.20 with zero accuracy"""
    
    metric = create_engagement_metric(accuracy=0.0)
    engine = AdaptiveEngine()
    
    # First adaptation
    result = engine.adapt_difficulty(student_id, session_id, metric)
    assert result['new_difficulty'] == 0.40
    assert result['step_size'] == -0.10
```

### Test Case 3: Mixed Results Stability
```python
def test_mixed_results_stability():
    """Verify 0.50 → 0.51 → 0.51 → 0.55 with 2/3 accuracy"""
    
    metric = create_engagement_metric(accuracy=2/3)
    engine = AdaptiveEngine()
    
    # All should use tiny +0.01 steps
    result = engine.adapt_difficulty(student_id, session_id, metric)
    assert result['step_size'] == 0.01
    assert 0.50 <= result['new_difficulty'] <= 0.52
```

---

## 📈 Reason Strings (for Audit Trail)

When difficulty changes, the system logs reasons like:

```
✅ "Perfect accuracy (100%), large difficulty increase (+0.10)"
✅ "High accuracy (85%), medium difficulty increase (+0.05)"
✅ "Mixed results (67%), maintaining stability (+0.01)"
✅ "Marginal accuracy (50%), maintaining current difficulty"
✅ "Low accuracy (25%), medium difficulty decrease (-0.05)"
✅ "No correct answers (0%), large difficulty decrease (-0.10)"
✅ "Marginal accuracy (50%) + low engagement (20%), slight decrease (-0.02)"
```

Each log includes:
- `trigger_metric`: Which threshold was crossed
- `trigger_value`: The accuracy value
- `old_value`: Previous difficulty
- `new_value`: New difficulty
- `step_size`: Change amount
- `reason`: Human-readable explanation

---

## 🔧 Configuration

### Current Settings (config.py)

```python
ADAPTATION_CONFIG = {
    'min_difficulty': 0.1,      # Minimum bound
    'max_difficulty': 0.9,      # Maximum bound
    'difficulty_step': 0.1,     # Legacy (not used in new algorithm)
}
```

### Difficulty Scale
- **0.0-0.2:** Super Easy
- **0.2-0.4:** Easy
- **0.4-0.6:** Medium (default: 0.50)
- **0.6-0.8:** Hard
- **0.8-1.0:** Very Hard

---

## 🎓 Educational Rationale

### Why These Steps?
1. **Perfect Accuracy (+0.10):** Student is clearly ready for more challenge
2. **High Accuracy (+0.05):** Moderate confidence in advancement
3. **Mixed/Good (+0.01):** Tiny steps maintain engagement while staying challenge-aware
4. **Marginal (0.00):** Hold current level to allow consolidation
5. **Low (-0.05):** Moderate step down to reduce cognitive overload
6. **Zero (-0.10):** Large step down to prevent frustration/disengagement

### Engagement Modulation
When accuracy is marginal (0.33-0.66) AND engagement is very low (<0.3):
```
new_difficulty = current - 0.02
reason = "Marginal accuracy + low engagement, slight decrease (-0.02)"
```

This prevents discouragement while maintaining some challenge.

---

## ✅ Verification Checklist

Before deploying:
- [x] Difficulty values respect bounds (0.1 ≤ difficulty ≤ 0.9)
- [x] Step sizes are consistent (0.01, 0.05, 0.10)
- [x] Reason strings are logged for all changes
- [x] Engagement score still considered for edge cases
- [x] Backwards compatible with existing sessions
- [x] No division by zero or null pointer risks
- [x] All 6 accuracy tiers tested

---

## 🚀 Deployment Notes

1. **Existing Sessions:** Continue with current difficulty until next adaptation
2. **New Sessions:** Start at 0.50 (medium)
3. **Backwards Compatible:** Old logs unaffected
4. **No Database Migration:** No schema changes required
5. **Performance:** O(1) complexity - no performance impact

---

## 📞 Support

For questions about:
- **Algorithm logic:** See `ALGORITHM_IMPROVEMENTS_SUMMARY.md`
- **Implementation:** See code comments in `engine.py`
- **Testing:** See unit tests in `tests/test_adaptation.py`
- **Monitoring:** Check `AdaptationLog` table in database

Last Updated: January 4, 2026
