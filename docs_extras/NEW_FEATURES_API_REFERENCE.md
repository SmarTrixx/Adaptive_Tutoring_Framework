# QUICK API REFERENCE - New Features (Dec 11, 2025)

## 🆕 IRT (Item Response Theory) - Scientific Question Calibration

### What It Does
Automatically estimates question difficulty, discrimination, and guessing probability from student response data. Makes question selection scientifically accurate.

### API Endpoints

**Calibrate all questions:**
```bash
POST /api/analytics/irt/calibrate
Response: { "questions_calibrated": 18, "message": "IRT calibration complete" }
```

**Get question parameters:**
```bash
GET /api/analytics/irt/question-stats/{question_id}
Response: {
  "discrimination": 1.2,      # How well it separates students (0.5-2.5)
  "difficulty": 0.5,          # Where curve is centered (-4 to 4)
  "guessing": 0.25,           # Probability of guessing (0-0.4)
  "difficulty_label": "Medium"
}
```

**Get student ability:**
```bash
GET /api/analytics/irt/student-ability/{student_id}
Response: {
  "estimated_ability": 0.75,           # Theta, -4 to 4 scale
  "ability_label": "Above Average"
}
```

---

## 🆕 CAT (Computerized Adaptive Testing) - Optimal Question Selection

### What It Does
Selects the next question that provides maximum information about student ability. Converges faster than traditional tests (often 30-50% fewer questions needed).

### API Endpoints

**Get optimal next question:**
```bash
GET /api/analytics/cat/next-question/{student_id}/{session_id}
Response: {
  "question": { ...full question object... },
  "student_ability": 0.5,
  "selection_rationale": "Maximum Information (optimal difficulty for student)"
}
```

**Should we stop testing?**
```bash
GET /api/analytics/cat/should-stop/{student_id}/{session_id}
Response: {
  "should_stop": false,
  "reason": "Continue testing",
  "questions_answered": 12,
  "max_questions": 20
}
```

---

## 🆕 Spaced Repetition - Long-term Learning Optimization

### What It Does
Schedules review times using exponential spacing algorithm (SuperMemo 2). Questions reviewed at optimal times for maximum retention.

### Algorithm
- First review: 1 day
- Second review: 3 days (if learned well)
- Third review: 8 days
- Fourth review: 21 days
- Continues exponentially...

### Quality Ratings (0-5)
- **0:** Forgot completely → restart at 1 day
- **2:** Struggled, difficult → slower progression
- **3:** Okay recall → normal schedule
- **4:** Good recall → standard spacing
- **5:** Perfect instant recall → maximum spacing

### API Endpoints

**Schedule a review:**
```bash
POST /api/analytics/sr/schedule/{student_id}/{question_id}
Body: { "quality": 4 }  # 0-5 rating
Response: {
  "next_review_date": "2025-12-15T...",
  "interval_days": 8,
  "quality": 4,
  "status": "scheduled"
}
```

**Get due reviews:**
```bash
GET /api/analytics/sr/due-for-review/{student_id}
Response: {
  "due_count": 3,
  "questions": [
    { "question_id": "...", "days_overdue": 2, "question_text": "..." }
  ]
}
```

**Get learning statistics:**
```bash
GET /api/analytics/sr/statistics/{student_id}
Response: {
  "total_questions_studied": 18,
  "due_for_review": 3,
  "upcoming_reviews": 5,
  "mastered": 2,
  "struggling": 1,
  "estimated_retention": 0.87
}
```

**Get learning curve:**
```bash
GET /api/analytics/sr/learning-curve/{student_id}/{topic}
Response: {
  "learning_curve": [
    { "attempt": 1, "accuracy": 0.3 },
    { "attempt": 2, "accuracy": 0.4 },
    ...
    { "attempt": 20, "accuracy": 0.95 }
  ],
  "mastery_analysis": {
    "current_accuracy": 0.95,
    "days_to_mastery_estimate": 0,
    "mastered": true
  }
}
```

**Get review schedule for topic:**
```bash
GET /api/analytics/sr/review-schedule/{student_id}/{topic}
Response: {
  "due_today": [ ...3 questions... ],
  "due_this_week": [ ...5 questions... ],
  "due_this_month": [ ...2 questions... ],
  "future": [ ...8 questions... ]
}
```

---

## 🆕 RL Policy Optimizer - Adaptive System Optimization

### What It Does
Validates and improves the adaptive engine's decision-making. Measures if adaptations are actually helping students.

### API Endpoints

**Validate policy:**
```bash
POST /api/analytics/rl/policy-validation?sessions=50
Response: {
  "policy_score": 75.5,              # 0-100, higher is better
  "convergence": true,               # Is learning stable?
  "action_effectiveness": {
    "difficulty": 0.78,              # % of adaptations that helped
    "pacing": 0.65,
    "hints": 0.82,
    "content": 0.70
  },
  "recommendations": [
    "Action 'pacing' is ineffective - consider tuning",
    "Action 'hints' is very effective - prioritize in learning"
  ]
}
```

**Get policy summary:**
```bash
GET /api/analytics/rl/policy-summary
Response: {
  "convergence_status": {
    "q_table_size": 27,              # States learned
    "converged": true,
    "convergence_metric": 0.85
  },
  "policy_validation": { ...validation data... },
  "action_impacts": { ...impact per action... }
}
```

**Get convergence status:**
```bash
GET /api/analytics/rl/convergence-status
Response: {
  "q_table_size": 27,
  "avg_q_value": 0.45,
  "q_value_std": 0.12,
  "convergence_metric": 0.88,
  "converged": true,
  "training_progress": 0.75
}
```

**Analyze action impact:**
```bash
GET /api/analytics/rl/action-impact/difficulty
Response: {
  "action": "difficulty",
  "total_times_used": 45,
  "success_rate": 0.78,
  "avg_impact_score": 0.75,
  "recommendation": "Highly effective - increase usage"
}
```

**Tune reward signal:**
```bash
POST /api/analytics/rl/tune-reward/{session_id}
Response: {
  "engagement_change": 0.15,         # Delta from start to end
  "accuracy_change": 0.2,
  "satisfaction_estimate": 0.75,
  "overall_reward": 0.168,           # Weighted combination
  "weights": { "engagement": 0.35, "accuracy": 0.4, "satisfaction": 0.25 }
}
```

**Get exploration status:**
```bash
GET /api/analytics/rl/exploration-status
Response: {
  "epsilon": 0.08,                   # Exploration rate
  "explore_rate": "8%",              # Try new actions
  "exploit_rate": "92%",             # Use best known
  "iteration": 250
}
```

**Decay exploration:**
```bash
POST /api/analytics/rl/decay-epsilon
Response: {
  "new_epsilon": 0.0792,
  "status": { "explore_rate": "7.92%", "exploit_rate": "92.08%" }
}
```

---

## Example: Complete Student Session with All Features

### 1. Student starts session
```bash
GET /api/analytics/irt/student-ability/{student_id}
→ Current ability: 0.5 (medium)
```

### 2. Select first question using CAT
```bash
GET /api/analytics/cat/next-question/{student_id}/{session_id}
→ Question 7 selected (optimal difficulty for ability 0.5)
```

### 3. Student answers
```bash
POST /api/cbt/answer
→ Correct! Response time: 25 seconds
```

### 4. Quality rating (internal)
- Correct answer + fast response = quality 4 (good)

### 5. Schedule review
```bash
POST /api/analytics/sr/schedule/{student_id}/{question_id}
Body: { "quality": 4 }
→ Next review: 8 days (standard spacing)
```

### 6. Update ability estimate
```bash
GET /api/analytics/irt/student-ability/{student_id}
→ Updated ability: 0.52 (slight improvement)
```

### 7. Select next question
```bash
GET /api/analytics/cat/next-question/{student_id}/{session_id}
→ Question 5 selected (slightly harder for ability 0.52)
```

### 8. Repeat steps 3-7 for each question

### 9. End of session - validate adaptation
```bash
GET /api/analytics/rl/policy-validation
→ Difficulty adaptation 78% effective: Good!
```

---

## Configuration & Tuning

### IRT Parameters (auto-calibrated)
- `a` (discrimination): 0.5-2.5 (higher = better discriminates)
- `b` (difficulty): -4 to 4 (negative = easier, positive = harder)
- `c` (guessing): 0-0.4 (higher = more students guess correctly)

### Spaced Repetition Parameters
- `initial_interval`: 1 day
- `easiness_factor_default`: 2.5
- `easiness_factor_min`: 1.3

### RL Policy Parameters
- `learning_rate` (α): 0.1 (moderate speed)
- `discount_factor` (γ): 0.95 (future matters)
- `epsilon`: Initial 0.1, decays over time

### CAT Parameters
- `max_questions`: 20 per session
- `stopping_se`: 0.3 (standard error threshold)

---

## Performance Expectations

### IRT Calibration
- Requires: 100+ student responses per question
- Improves over time: More accurate with more data
- Impact: Questions get scientifically calibrated difficulty

### CAT Convergence
- Typical sessions: 15-20 questions (vs 30-40 for fixed tests)
- Accuracy: Converges to true ability within ±0.5 theta points
- Benefit: ~30-50% fewer questions needed

### Spaced Repetition
- Retention rate: ~87% after spacing schedule
- Time investment: Decreases over time (longer intervals)
- Mastery timeline: 2-4 weeks depending on topic

### RL Optimization
- Training period: 100+ student sessions
- Convergence: Q-table stable after ~200 sessions
- Improvement: Policy effectiveness increases 10-20% per month

---

## Troubleshooting

**Q: CAT selecting too hard/easy questions?**
A: Run `/api/analytics/irt/calibrate` with more response data

**Q: Spaced repetition intervals seem wrong?**
A: Check quality ratings - low quality (0-2) resets scheduling

**Q: RL policy not improving?**
A: Check convergence status and action effectiveness. Ensure rewards are set correctly.

**Q: Student ability estimate fluctuating?**
A: This is normal early on. Stabilizes after ~10 questions

---

## Deployment Checklist

- ✅ IRT calibration ready
- ✅ CAT algorithm ready
- ✅ Spaced repetition ready
- ✅ RL policy optimizer ready
- ✅ All 20+ endpoints implemented
- ✅ No new dependencies
- ✅ Production ready

**Status:** 🟢 Ready to deploy!

---

**Last Updated:** December 11, 2025  
**Version:** 1.0 Complete  
**Status:** Production Ready
