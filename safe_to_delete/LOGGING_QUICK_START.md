# Logging System Quick Start Guide

## For Researchers (Thesis Evaluation)

### Where Is My Data?

All logged data is stored in: `/tmp/engagement_logs/`

Each session creates 4 files:
```
session_123_questions.csv      ← Per-question records (45 rows per session)
session_123_questions.json     ← Same data, JSON format
session_123_windows.csv        ← Window summaries (3 rows per session)
session_123_windows.json       ← Same data, JSON format
```

### Quick Analysis

**Load and analyze in Python**:
```python
import csv
import json

# Load CSV
with open('/tmp/engagement_logs/session_123_questions.csv') as f:
    questions = list(csv.DictReader(f))

# Load JSON
with open('/tmp/engagement_logs/session_123_windows.json') as f:
    windows = json.load(f)

# Analyze accuracy progression
accuracies = [1 if q['response_correctness'] == 'True' else 0 for q in questions]
print(f"Overall accuracy: {sum(accuracies) / len(accuracies):.1%}")

# Analyze difficulty trajectory
difficulties = [float(q['question_difficulty']) for q in questions]
print(f"Difficulty: {difficulties[0]:.3f} → {difficulties[-1]:.3f}")

# Analyze engagement
engagement = [float(q['engagement_score']) for q in questions]
print(f"Average engagement: {sum(engagement) / len(engagement):.4f}")
```

### Data Dictionary

**Key fields per question**:
- `response_correctness`: "True" or "False"
- `response_time_seconds`: Float seconds
- `question_difficulty`: 0.0-1.0 scale
- `engagement_score`: 0.0-1.0 overall engagement
- `engagement_categorical_state`: "engaged", "neutral", "struggling", or "disengaged"
- `engagement_behavioral_component`: 0.0-1.0 behavioral score
- `engagement_cognitive_component`: 0.0-1.0 cognitive score  
- `engagement_affective_component`: 0.0-1.0 affective score
- `engagement_primary_driver`: Human-readable reason (e.g., "Struggling (many hints)")
- `decision_primary_action`: "increase_difficulty", "decrease_difficulty", or "maintain_difficulty"
- `decision_difficulty_delta`: Numeric change applied
- `decision_rationale`: Why the decision was made

### Statistical Analysis

**Correlation analysis**:
```python
from scipy.stats import pearsonr

# Correlation between engagement and performance
engagement = [float(q['engagement_score']) for q in questions]
correctness = [1 if q['response_correctness'] == 'True' else 0 for q in questions]

correlation, p_value = pearsonr(engagement, correctness)
print(f"Engagement-Performance correlation: {correlation:.3f} (p={p_value:.4f})")
```

**Trend analysis**:
```python
# Engagement progression by window
engagement_by_window = []
for window in windows['windows']:
    engagement_by_window.append({
        'window': window['window_number'],
        'avg_engagement': window['avg_engagement_score'],
        'accuracy': window['accuracy'],
        'difficulty_change': window['total_difficulty_change']
    })

for w in engagement_by_window:
    print(f"Window {w['window']}: {w['avg_engagement']:.4f} engagement, "
          f"{w['accuracy']:.1%} accuracy, {w['difficulty_change']:+.3f} difficulty")
```

### Export to Excel

For Excel analysis:
```python
import pandas as pd

# Load CSV directly
questions_df = pd.read_csv('/tmp/engagement_logs/session_123_questions.csv')
windows_df = pd.read_csv('/tmp/engagement_logs/session_123_windows.csv')

# Export to Excel
with pd.ExcelWriter('/tmp/analysis.xlsx') as writer:
    questions_df.to_excel(writer, sheet_name='Questions', index=False)
    windows_df.to_excel(writer, sheet_name='Windows', index=False)

print("✓ Exported to analysis.xlsx")
```

---

## For Developers (Logging Integration)

### Add Logging to Your Feature

```python
from app.logging.engagement_logger import EngagementLogger
import datetime

# Create logger for session
logger = EngagementLogger(session_id="my_student_123")

# After making an adaptive decision, log it
logger.log_question(
    session_id=logger.session_id,
    question_number=1,
    timestamp=datetime.datetime.now().isoformat(),
    
    # Question details
    question_id="q_456",
    question_difficulty=0.5,
    response_correctness=True,
    response_time_seconds=4.2,
    
    # Engagement indicators (from extraction)
    behavioral_response_time_deviation=-0.15,
    behavioral_inactivity_duration=0.0,
    behavioral_hint_usage_count=0,
    behavioral_rapid_guessing_probability=0.05,
    cognitive_accuracy_trend=1.0,
    cognitive_consistency_score=0.9,
    cognitive_load=0.3,
    affective_frustration_probability=0.1,
    affective_confusion_probability=0.05,
    affective_boredom_probability=0.2,
    
    # Fused engagement (from fusion engine)
    engagement_score=0.72,
    engagement_categorical_state="engaged",
    engagement_behavioral_component=0.75,
    engagement_cognitive_component=0.80,
    engagement_affective_component=0.60,
    engagement_confidence=0.85,
    engagement_primary_driver="Engaged student with high accuracy",
    
    # Adaptation decision (from policy)
    decision_primary_action="maintain_difficulty",
    decision_secondary_actions=json.dumps([]),
    decision_difficulty_delta=0.0,
    decision_rationale="Student is engaged and performing well; maintain current difficulty",
    decision_engagement_influenced=True,
    
    # Result
    resulting_difficulty_level=0.5
)

# After each window (5 questions), log summary
logger.log_window_summary(
    session_id=logger.session_id,
    window_number=1,
    timestamp=datetime.datetime.now().isoformat(),
    window_size=5,
    correct_count=4,
    incorrect_count=1,
    accuracy=0.8,
    avg_response_time=3.8,
    avg_engagement_score=0.68,
    avg_behavioral_score=0.72,
    avg_cognitive_score=0.75,
    avg_affective_score=0.55,
    dominant_engagement_state="engaged",
    primary_driver_summary="Generally engaged with occasional confusion",
    difficulty_at_start=0.5,
    difficulty_at_end=0.625,
    total_difficulty_change=0.125,
    decisions_count=5,
    increase_count=2,
    decrease_count=1,
    maintain_count=2
)

# Export when session ends
logger.export_all(output_dir="/tmp/engagement_logs")
print(f"✓ Logs exported")
```

### Validate Your Logs

```bash
# Run the validation suite
cd backend
python3 scripts/test_logging_completeness.py
```

Expected output: ✅ ALL CHECKS PASSED

### Debug Logging Issues

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Create logger with debug output
logger = EngagementLogger(session_id="debug_session")

# Try to log with incomplete data
try:
    logger.log_question(
        session_id=logger.session_id,
        question_number=1,
        timestamp="2026-01-04T10:00:00",
        question_id="q_001",
        # Missing: question_difficulty, response_correctness, etc.
    )
except ValueError as e:
    print(f"✓ Caught error: {e}")

# Check what was logged to disk
logger.print_summary()
```

### Requirements

```
python >= 3.8
```

No external dependencies (uses only stdlib: csv, json, datetime, pathlib, logging)

---

## Troubleshooting

### "No module named 'app.logging.engagement_logger'"

**Solution**: Make sure you're in the `backend/` directory:
```bash
cd /path/to/backend
python3 scripts/your_script.py
```

### "Cannot write to /tmp/engagement_logs/"

**Solution**: Check directory permissions:
```bash
ls -la /tmp/ | grep engagement_logs
# If missing, logs will create it automatically
```

### "Missing required field in log entry"

**Solution**: Provide all required fields:
```python
# ✗ Wrong - missing many fields
logger.log_question(session_id="s1", question_number=1, timestamp="...")

# ✓ Right - all required fields
logger.log_question(
    session_id="s1",
    question_number=1,
    timestamp="...",
    question_id="q1",
    question_difficulty=0.5,
    response_correctness=True,
    response_time_seconds=4.2,
    # ... all other required fields ...
)
```

### "CSV export shows empty cells"

**Solution**: This is expected. Some fields may be null:
- `decision_secondary_actions` often empty (no secondary actions)
- Some indicators may be 0 or null in edge cases

This is **not** a data quality issue. See validation report for details.

---

## Performance Notes

- **Per-question logging**: ~1ms
- **Per-window logging**: ~2ms
- **CSV export**: ~50ms for 45 questions
- **JSON export**: ~30ms for 45 questions

No performance impact on main tutoring loop.

---

## Next Steps

1. **For thesis evaluation**: Load data from `/tmp/engagement_logs/` and analyze with your preferred tools
2. **For deployment**: Migrate logging to your permanent database using these same field names
3. **For new features**: Use this logging framework to track new adaptations
4. **For papers**: Reference the `LOGGING_SYSTEM.md` documentation

---

**Questions?** Check `/docs/LOGGING_SYSTEM.md` for comprehensive documentation.
