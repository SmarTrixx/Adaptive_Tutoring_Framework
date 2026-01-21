# SYSTEM INTEGRATION GUIDE

## Complete Framework for Adaptive Tutoring System Evaluation

You now have a complete, production-ready system for generating authentic research data from your adaptive tutoring implementation. This guide shows how all components work together.

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  YOUR FLASK API                              │
│  (localhost:5000/api/session/start, /api/response/submit)   │
└────────────┬────────────────────────────────────────────────┘
             │ (HTTP requests)
             │
┌────────────▼────────────────────────────────────────────────┐
│          LEARNER SIMULATION (learner_simulation.py)          │
│                                                               │
│  • Creates 5 learner archetypes                              │
│  • Instantiates 20 simulated learners (10 per condition)    │
│  • Each makes 10 API calls with realistic behavior           │
│  • Captures ALL system responses                             │
│  • Saves to: /data/simulated/simulation_complete.json        │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
   ┌─────────────────────┐
   │  Raw System Data    │  2-5 MB JSON file
   │  (200+ responses)   │
   └──────────┬──────────┘
              │
              │
┌─────────────▼────────────────────────────────────────────────┐
│     DATA PROCESSING (process_simulation_data.py)             │
│                                                               │
│  • Extracts structured data                                  │
│  • Normalizes system outputs                                 │
│  • Computes Chapter 4 tables                                 │
│  • Generates CSV exports                                     │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
   ┌──────────────────────────────┐
   │  Processed Results            │
   │  • Table 4.1 (Characteristics)│
   │  • Table 4.3 (Performance)    │
   │  • Table 4.5 (Engagement)     │
   │  • Table 4.6 (Behavior)       │
   │  • Table 4.7 (Adaptations)    │
   │  • Raw CSV exports            │
   └──────────┬───────────────────┘
              │
              ▼
   ┌──────────────────────┐
   │  Thesis Integration  │
   │  Chapter 4: Results  │
   └──────────────────────┘
```

---

## Execution Timeline

### Pre-Execution (5 min)
```bash
# Step 1: Validate system readiness
cd /home/smartz/Desktop/Major\ Projects/adaptive-tutoring-framework
python3 data/preflight_check.py

# Expected output: "✓ All checks PASSED - Ready to run simulation!"
```

### Execution (5-15 min)
```bash
# Step 2A: Ensure Flask server is running
python3 backend/main.py
# (Or however your project starts the Flask server)

# Step 2B: In another terminal, run simulation
cd /home/smartz/Desktop/Major\ Projects/adaptive-tutoring-framework
python3 data/learner_simulation.py

# Expected output: 
# "20 learners complete"
# "200+ interactions captured"
# "Raw data saved: data/simulated/simulation_complete.json"
```

### Post-Execution (2 min)
```bash
# Step 3: Process raw data into tables
python3 data/process_simulation_data.py

# Expected output:
# "5 tables generated"
# "Saved to: data/processed/"
```

### Review (30 min)
```bash
# Step 4: Examine outputs
ls -lh data/processed/  # Check file sizes and timestamps
head -5 data/processed/Table_4.3.csv  # Preview a table
cat data/processed/Table_4.3.csv | less  # Full table review
```

---

## Data Flow Example

### Request Flow
```
LearnerSimulator (ADAPT-001, High-Ability)
  ↓
generate_response()
  ↓ (Creates realistic interaction)
{
  "response_time_seconds": 12.3,
  "student_answer": "Option B",
  "hints_used": 0,
  "option_changes": 1,
  "pauses_during_response": 0
}
  ↓ (Sends to Flask API)
POST /api/response/submit
  ↓
Flask System
  ↓ (Processes response)
Checks: Is answer correct? Accuracy trend? Engagement level?
Updates: Difficulty, Engagement, Engagement Status
  ↓ (Returns system response)
{
  "is_correct": true,
  "engagement_score": 85.5,
  "new_difficulty": 6,
  "engagement_level": "high",
  "accuracy_recent": 0.92,
  "previous_difficulty": 5
}
  ↓ (Captured in raw data)
simulation_complete.json
  ↓ (100% real system output)
```

### Processing Flow
```
simulation_complete.json (Raw)
  ↓
extract_from_simulation()
  ↓
responses_df (200 rows × 8 columns)
engagement_df (180 rows × 5 columns)
adaptations_df (45 rows × 6 columns)
  ↓
Compute by condition (adaptive vs non-adaptive)
  ↓
Table 4.3:
  Group,Mean Accuracy,Total Questions
  Adaptive,82.0% ± 12.3%,100
  Non-Adaptive,68.5% ± 18.7%,100
  ↓
  (This number comes from: sum of is_correct / count, grouped by condition)
```

---

## File Specifications

### Input Files

#### Flask API Endpoints
**Endpoint 1**: `POST /api/session/start`
- **Input**: `{"student_id": "string", "subject": "string", "preferred_difficulty": int}`
- **Output**: `{"session_id": "string", "initial_difficulty": int, ...}`
- **Used by**: `SimulatedLearner.start_session()`

**Endpoint 2**: `POST /api/response/submit`
- **Input**: `{"session_id": "string", "student_answer": "string", "response_time_seconds": float, "option_changes": int, "hints_used": int, "pauses_during_response": int}`
- **Output**: `{"is_correct": bool, "engagement_score": float, "new_difficulty": int, "engagement_level": "string", "accuracy_recent": float, "previous_difficulty": int}`
- **Used by**: `SimulatedLearner.submit_response()`

### Output Files

#### `/data/simulated/simulation_complete.json`
```json
{
  "metadata": {
    "timestamp": "2024-01-15T10:30:00",
    "total_learners": 20,
    "total_interactions": 205,
    "conditions": ["adaptive", "non_adaptive"]
  },
  "adaptive": [
    {
      "learner_id": "ADAPT-001",
      "profile": "High-Ability Stable",
      "session_id": "sess-abc123",
      "interactions": [
        {
          "timestamp": "2024-01-15T10:30:45",
          "request": {
            "response_time_seconds": 12.3,
            "student_answer": "Option B",
            "hints_used": 0,
            "option_changes": 1,
            "pauses_during_response": 0
          },
          "response": {
            "is_correct": true,
            "engagement_score": 85.5,
            "new_difficulty": 6,
            "engagement_level": "high",
            "accuracy_recent": 0.92,
            "previous_difficulty": 5
          }
        }
      ]
    }
  ],
  "non_adaptive": [ ... ]
}
```

#### `/data/processed/Table_4.3.csv`
```csv
Group,Mean Accuracy,Total Questions
Adaptive,82.0% ± 12.3%,100
Non-Adaptive,68.5% ± 18.7%,100
```

---

## Learner Profile Specifications

### Profile 1: High-Ability Stable
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| response_time_mean | 12.0 seconds | Fast, confident responses |
| response_time_std | 2.0 | Low variance = consistent |
| accuracy_mean | 0.90 | 90% correct |
| accuracy_std | 0.08 | Low variance = reliable |
| hint_usage_probability | 0.05 | Rarely needs hints |
| pauses_per_response | 0.1 | Minimal hesitation |
| option_changes_probability | 0.05 | Confident in choices |
| disengagement_trigger | False | Won't disengage |

### Profile 2: Average Learner
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| response_time_mean | 20.0 seconds | Moderate pace |
| response_time_std | 5.0 | Some variance |
| accuracy_mean | 0.65 | 65% correct |
| accuracy_std | 0.15 | Moderate variance |
| hint_usage_probability | 0.20 | Uses hints sometimes |
| pauses_per_response | 0.5 | Normal hesitation |
| option_changes_probability | 0.15 | Some uncertainty |
| disengagement_trigger | False | Stable engagement |

### Profile 3: Low-Ability Struggling
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| response_time_mean | 28.0 seconds | Slow, deliberate |
| response_time_std | 8.0 | High variance |
| accuracy_mean | 0.45 | 45% correct |
| accuracy_std | 0.20 | High variance |
| hint_usage_probability | 0.50 | Frequently uses hints |
| pauses_per_response | 2.0 | Frequent pauses |
| option_changes_probability | 0.40 | Highly uncertain |
| disengagement_trigger | True | Risk of disengagement |

### Profile 4: Anxious Learner
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| response_time_mean | 22.0 seconds | Moderate speed |
| response_time_std | 12.0 | Highly erratic |
| accuracy_mean | 0.60 | 60% correct |
| accuracy_std | 0.18 | Inconsistent |
| hint_usage_probability | 0.35 | Seeks reassurance |
| pauses_per_response | 1.5 | Frequent hesitation |
| option_changes_probability | 0.45 | Second-guesses often |
| stress_sensitivity | True | Affected by difficulty |

### Profile 5: Disengaging Learner
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| response_time_mean | 35.0 seconds | Very slow |
| response_time_std | 15.0 | Highly inconsistent |
| accuracy_mean | 0.40 | 40% correct |
| accuracy_std | 0.22 | High variance |
| hint_usage_probability | 0.60 | Depends on hints |
| pauses_per_response | 3.5 | Many pauses |
| option_changes_probability | 0.50 | Highly uncertain |
| disengagement_trigger | True | High drop risk |

---

## Critical Integration Points

### 1. Flask API Must Return Expected Fields

For simulation to capture system outputs correctly, your API responses must include:

```python
# /api/response/submit endpoint must return:
{
    "is_correct": Boolean,              # Required: Was answer correct?
    "engagement_score": Float,          # Required: Current engagement (0-100)
    "new_difficulty": Integer,          # Required: New difficulty level
    "engagement_level": String,         # Required: "low", "medium", or "high"
    "accuracy_recent": Float,           # Required: Recent accuracy ratio
    "previous_difficulty": Integer,     # Required: Previous difficulty (for adaptive events)
    ...any other fields...             # Optional: captured but not processed
}
```

### 2. Learner Simulation Must Match Your Data Model

If your system uses different field names or structures:

**Before simulation**:
1. Open `/data/learner_simulation.py`
2. In `LearnerSimulator.submit_response()` method
3. Adjust field mappings to match your API
4. Example: If your API returns `student_engagement` instead of `engagement_score`, change line accordingly

**Example modification**:
```python
# Original
self.learner.current_engagement = system_data['engagement_score']

# Modified for different API
self.learner.current_engagement = system_data['student_engagement']
```

### 3. API Endpoint Paths Must Be Correct

Verify your Flask routes match:
- `POST /api/session/start` — Initialize session
- `POST /api/response/submit` — Submit response

If different, update in `learner_simulation.py`:
```python
# Line in LearnerSimulator class
BASE_URL = "http://localhost:5000"

# Modify if different:
response = requests.post(f"{BASE_URL}/api/session/start", ...)
# vs
response = requests.post(f"{BASE_URL}/your/custom/path", ...)
```

---

## Quality Validation Checklist

Before relying on results:

### Data Capture
- [ ] All 200+ interactions logged
- [ ] No "missing field" errors in simulation output
- [ ] Random learner behaviors visible (different response times, hints used)
- [ ] System responses captured for both conditions

### Data Structure
- [ ] simulation_complete.json is valid JSON
- [ ] All adaptive learners have ~10 interactions
- [ ] All non-adaptive learners have ~10 interactions
- [ ] Engagement scores in reasonable range (0-100)
- [ ] Difficulty values in expected range (1-10)

### Table Generation
- [ ] All 5 tables generated successfully
- [ ] No NaN or infinity values in tables
- [ ] Adaptive mean > Non-adaptive mean (typically)
- [ ] Statistics make sense (std < mean, etc.)
- [ ] Sample sizes match (10 per condition)

### Comparative Validity
- [ ] Same learner profiles in both conditions
- [ ] Same question count per learner (10)
- [ ] Only system mode differs (adaptive vs fixed)
- [ ] Adaptation events only in adaptive condition
- [ ] No adaptation events in non-adaptive condition

---

## Troubleshooting Decision Tree

```
Issue: "Connection refused" or "Failed to connect"
└─ Action: Is Flask server running? 
   └─ No → Start Flask server first
   └─ Yes → Is it on localhost:5000? 
      └─ No → Update API_URL in learner_simulation.py
      └─ Yes → Check Flask logs for errors

Issue: "KeyError: 'engagement_score'" during processing
└─ Action: Did API return expected fields?
   └─ No → Check Flask endpoint implementation
          Verify all required fields in response
   └─ Yes → Check field names match in process_simulation_data.py

Issue: "File not found" for simulation_complete.json
└─ Action: Did simulation run to completion?
   └─ No → Check for errors during execution
          Verify /data/simulated/ directory exists
   └─ Yes → Check file location:
           ls -l /data/simulated/

Issue: Empty or minimal response data
└─ Action: Did learners complete all 10 questions?
   └─ No → Check learner_simulation.py logic
          Verify num_questions parameter (should be 10)
   └─ Yes → Check API responses weren't errors
           Add debugging: print(system_data) in submit_response()
```

---

## Example Output Verification

### Simulate Raw Data Check
```bash
# Count total interactions captured
python3 -c "
import json
with open('data/simulated/simulation_complete.json') as f:
    data = json.load(f)
    adapt = sum(len(l['interactions']) for l in data['adaptive'])
    nonadapt = sum(len(l['interactions']) for l in data['non_adaptive'])
    print(f'Adaptive: {adapt} interactions')
    print(f'Non-adaptive: {nonadapt} interactions')
    print(f'Total: {adapt + nonadapt} interactions')
"
```

### Simulate Table Check
```bash
# Check table generation
python3 -c "
import pandas as pd
import os
path = 'data/processed'
for f in ['Table_4.1.csv', 'Table_4.3.csv', 'Table_4.5.csv']:
    df = pd.read_csv(os.path.join(path, f))
    print(f'\n{f}:')
    print(df.to_string())
"
```

---

## Documentation Map

| Document | Purpose | Audience |
|----------|---------|----------|
| `SIMULATION_WORKFLOW.md` | Complete step-by-step guide | You + any collaborators |
| `SIMULATION_READY.md` | Status and readiness summary | You + advisors |
| `SYSTEM_INTEGRATION_GUIDE.md` | This document - technical details | Developers + you |
| Code comments in .py files | Implementation details | Code reviewers |
| README.md in /data/ | Quick reference | Quick lookup |

---

## Performance Expectations

### Execution Time
- **Preflight check**: 10-20 seconds
- **Simulation (20 learners × 10 questions)**: 5-15 minutes (depends on API response time)
- **Data processing**: 5-10 seconds

### File Sizes
- **simulation_complete.json**: 2-5 MB
- **Each CSV table**: 1-10 KB
- **Total output**: <10 MB

### System Requirements
- **Python 3.7+**
- **4GB RAM** (more than enough)
- **100MB disk space** (plenty)
- **Flask server**: Running on localhost:5000

---

## Success Indicators

You'll know the system is working correctly when:

✓ **Preflight check passes all 7 tests**
✓ **Simulation runs 20 learners without errors**
✓ **~200+ interactions captured in JSON**
✓ **All 5 tables generated with real data**
✓ **Tables show meaningful differences between conditions**
✓ **Every number is traceable to a system response**
✓ **Results are reproducible (same system = same data)**
✓ **Engagement scores in expected range (0-100)**
✓ **Adaptations only in adaptive condition**
✓ **Non-adaptive condition has no adaptation events**

---

## Next Steps

1. **Read** `SIMULATION_WORKFLOW.md` for complete context
2. **Run** `preflight_check.py` to validate system
3. **Execute** `learner_simulation.py` to capture raw data
4. **Process** `process_simulation_data.py` to generate tables
5. **Review** `/data/processed/` tables
6. **Integrate** tables into Chapter 4
7. **Write** interpretation text
8. **Cite** system data as your methodology

---

**Status**: ✓ Complete Framework Ready

**You Have**: Production-ready system for generating authentic research data directly from your implementation.

**You Need To Do**: Execute the three Python scripts in order, review outputs, integrate tables into thesis.

