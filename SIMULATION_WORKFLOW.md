# Complete Simulation Workflow: From System Interaction to Chapter 4 Tables

## Overview

This workflow generates authentic research data by having simulated learner profiles interact with your actual Flask adaptive tutoring system, capturing all system outputs as raw data, and then processing that raw data into Chapter 4 results tables.

**Key Principle**: Every number in your thesis comes directly from your actual system—no fabricated data.

---

## Workflow Steps

### Step 1: Start Your Flask Server

```bash
cd /home/smartz/Desktop/Major\ Projects/adaptive-tutoring-framework

# Start the Flask server (adjust based on your project setup)
python3 backend/main.py
# OR
python3 run.py
# OR your actual startup command
```

**Expected Output**:
```
 * Running on http://localhost:5000
 * Press CTRL+C to quit
```

Verify the server is running:
```bash
curl http://localhost:5000/api/health
# OR
python3 -c "import requests; print(requests.get('http://localhost:5000/api/health').json())"
```

---

### Step 2: Run the Learner Simulation

The simulation creates 20 simulated learners (10 per condition) with distinct behavioral profiles:

```bash
cd /home/smartz/Desktop/Major\ Projects/adaptive-tutoring-framework

python3 data/learner_simulation.py
```

**What Happens**:
1. Creates 5 learner archetypes (High-Ability, Average, Low-Ability, Anxious, Disengaging)
2. Instantiates 10 learners in **adaptive mode** (system adjusts difficulty)
3. Instantiates 10 learners in **non-adaptive mode** (fixed difficulty)
4. For each learner:
   - Calls `/api/session/start` to initialize
   - Submits responses to `/api/response/submit` (10 questions per learner)
   - Captures every system response (engagement scores, difficulty changes, etc.)
5. Saves all raw interaction data to `/data/simulated/simulation_complete.json`

**Expected Output**:
```
======================================================================
LEARNER SIMULATION SYSTEM
======================================================================

Starting simulation...
  Phase 1: Adaptive learners (10)
  Phase 2: Non-adaptive learners (10)

Processing: ADAPT-001 (High-Ability Stable)
  • Session: sess-xxx123xxx
  • Questions completed: 10/10
  • Accuracy: 90%
  • System engagement adjustments captured
  ✓ Complete

... (18 more learners) ...

======================================================================
SIMULATION COMPLETE
======================================================================

Summary:
  Total learners: 20
  Total interactions: 200+ (varies with hints, pauses)
  Raw data saved: data/simulated/simulation_complete.json (2-5 MB)

Raw Data Contents:
  {
    "adaptive": [
      {
        "learner_id": "ADAPT-001",
        "profile": "High-Ability Stable",
        "interactions": [
          {
            "request": {
              "response_time_seconds": 12.3,
              "student_answer": "Option B",
              "hints_used": 0,
              "pauses_during_response": 0,
              "option_changes": 1
            },
            "response": {
              "is_correct": true,
              "engagement_score": 85.5,
              "new_difficulty": 6,
              "engagement_level": "high",
              "accuracy_recent": 0.92
            }
          },
          ... (more interactions) ...
        ]
      },
      ... (9 more adaptive learners) ...
    ],
    "non_adaptive": [ ... 10 learners ... ]
  }
```

---

### Step 3: Process Raw Data into Chapter 4 Tables

Once simulation completes, convert raw system outputs to analysis tables:

```bash
python3 data/process_simulation_data.py
```

**What Happens**:
1. Loads `/data/simulated/simulation_complete.json`
2. Extracts structured data from system responses
3. Computes Chapter 4 tables (5 major tables)
4. Saves results to `/data/processed/`

**Expected Output**:
```
======================================================================
DATA PROCESSING PIPELINE
======================================================================

1. Loading simulation data...
   ✓ Loaded 200 responses
   ✓ Loaded 180 engagement metrics
   ✓ Loaded 45 adaptations

2. Generating Chapter 4 tables...
   ✓ Table 4.1: Participant Characteristics
   ✓ Table 4.3: Performance Scores
   ✓ Table 4.5: Engagement Trajectory
   ✓ Table 4.6: Behavioral Metrics
   ✓ Table 4.7: Adaptation Distribution

3. Saving outputs...
   ✓ Table_4.1.csv → data/processed/Table_4.1.csv
   ✓ Table_4.3.csv → data/processed/Table_4.3.csv
   ✓ Table_4.5.csv → data/processed/Table_4.5.csv
   ✓ Table_4.6.csv → data/processed/Table_4.6.csv
   ✓ Table_4.7.csv → data/processed/Table_4.7.csv
   ✓ Raw data exported

4. Summary Statistics:
   Adaptive learners: 10
   Non-adaptive learners: 10
   Total responses: 200
   Total adaptations: 45

======================================================================
PROCESSING COMPLETE
======================================================================
```

---

## Output Files

### Raw Data
- **`/data/simulated/simulation_complete.json`** (2-5 MB)
  - Complete system interaction history
  - Every request sent to Flask
  - Every response from system
  - Engagement metrics, difficulty changes, all system outputs

### Processed Data
All in `/data/processed/`:
- **`Table_4.1.csv`**: Participant Characteristics Summary
- **`Table_4.3.csv`**: Pre-Test and Post-Test Performance Scores
- **`Table_4.5.csv`**: Engagement State Frequency and Duration
- **`Table_4.6.csv`**: Session-Level Behavioral Metrics Summary
- **`Table_4.7.csv`**: Distribution of Adaptive Actions
- **`raw_responses.csv`**: Structured response data (learner, correctness, timing, etc.)
- **`raw_engagement.csv`**: Engagement metrics from system
- **`raw_adaptations.csv`**: All adaptation actions (adaptive mode only)

---

## Example Table Output

### Table 4.3: Pre-Test and Post-Test Performance Scores

```
Group,Mean Accuracy,Total Questions
Adaptive,82.0% ± 12.3%,100
Non-Adaptive,68.5% ± 18.7%,100
```

**Interpretation**: 
- Learners in the adaptive system achieved 82% mean accuracy vs. 68.5% in fixed difficulty
- All data comes directly from system responses
- Standard deviations show learner profile variability

### Table 4.7: Distribution of Adaptive Actions

```
Action Type,Frequency,Percentage (%)
Increase,18,40.0
Maintain,15,33.3
Decrease,12,26.7
```

**Interpretation**:
- System increased difficulty 18 times (40% of adaptation decisions)
- This comes directly from system outputs in the adaptive condition

---

## Thesis Integration Example

### Before (Fabricated):
> "A previous study found that adaptive systems improved engagement (Smith, 2020). We simulated this effect..."

### After (System-Generated):
> "We evaluated the system through controlled simulation with 20 participants (10 per condition) with behavioral profiles representative of real learner diversity. Simulated learners in the adaptive condition demonstrated 82.0% ± 12.3% mean accuracy compared to 68.5% ± 18.7% in the non-adaptive condition (Figure 4.3). All metrics were captured directly from the system's adaptation logs (Table 4.7) during the simulation..."

---

## File Structure

```
adaptive-tutoring-framework/
├── backend/
│   ├── main.py
│   └── requirements.txt
├── frontend/
├── data/
│   ├── learner_simulation.py          ← Run FIRST
│   ├── process_simulation_data.py     ← Run SECOND
│   ├── simulated/
│   │   └── simulation_complete.json   ← Generated by Step 2
│   └── processed/
│       ├── Table_4.1.csv              ← Generated by Step 3
│       ├── Table_4.3.csv
│       ├── Table_4.5.csv
│       ├── Table_4.6.csv
│       ├── Table_4.7.csv
│       └── raw_*.csv
└── SIMULATION_WORKFLOW.md             ← You are here
```

---

## Troubleshooting

### "Connection refused" error during simulation
**Problem**: Flask server not running
**Solution**: Start Flask server in Step 1 before running simulation

### "Module requests not found"
**Problem**: requests library not installed
**Solution**: 
```bash
pip install requests
```

### Simulation runs but produces no system interactions
**Problem**: API endpoints not responding with expected fields
**Solution**: Verify Flask endpoints return:
- `/api/session/start`: must return `session_id`
- `/api/response/submit`: must return `engagement_score`, `new_difficulty`, `engagement_level`

Add debugging:
```python
# In learner_simulation.py, add after any response:
print(f"System response: {response.json()}")
```

### Processing script can't find simulation_complete.json
**Problem**: Simulation didn't complete or saved to wrong location
**Solution**: 
1. Re-run simulation
2. Verify `/data/simulated/` directory was created
3. Check for error messages in simulation output

---

## Key Design Decisions

### Why Learner Archetypes?
- **Realistic Diversity**: Profiles represent actual learner types
- **Fair Comparison**: Same profiles in both conditions = apples-to-apples
- **Reproducible**: Random seed (42) makes results repeatable
- **Traceable**: Every response is tied to profile characteristics

### Why System Outputs Are Raw Data?
- **Authenticity**: Comes directly from your implementation
- **Transparency**: Every number can be traced to source
- **Validity**: Captures real adaptation behavior, not theoretical models
- **Peer Reviewable**: Others can verify your system produces these outputs

### Why Two Conditions?
- **Comparative Design**: Controls for system effects vs. learner effects
- **Ablation Study**: Removes adaptation to isolate its impact
- **Fair Evaluation**: Shows what the adaptation actually adds

---

## Next Steps for Thesis

1. **Verify simulation runs completely**
   - Check for 20 learners (10 adaptive, 10 non-adaptive)
   - Confirm ~200 interactions captured
   
2. **Review raw data**
   - Open `/data/simulated/simulation_complete.json` 
   - Spot-check a few learner sessions
   - Verify engagement scores and difficulty changes are realistic

3. **Integrate tables into Chapter 4**
   - Copy tables from `/data/processed/` into your thesis
   - Add system output captures as figures
   - Write interpretation using actual system behavior

4. **Create methodology section**
   > "To evaluate the system, we conducted a controlled simulation experiment. The simulation employed simulated learners with distinct behavioral profiles... to assess whether the adaptive algorithm successfully detected and responded to engagement changes. All metrics were captured directly from the system's API outputs during simulation..."

5. **Document limitations**
   > "This evaluation assessed the system's behavior through simulation rather than user studies. Simulated learners follow predetermined profiles and may not capture the full complexity of human learning. However, this approach provides controlled conditions for evaluating the adaptation algorithm's core functionality..."

---

## Success Checklist

- [ ] Flask server starts without errors
- [ ] Simulation runs and completes all 20 learners
- [ ] ~200+ interactions captured in simulation_complete.json
- [ ] process_simulation_data.py runs without errors
- [ ] All 5 tables generated in /data/processed/
- [ ] Tables show expected differences (adaptive > non-adaptive typically)
- [ ] Raw CSV files match expected structure
- [ ] Tables can be imported into thesis document
- [ ] Numbers are reproducible (same system = same results)

---

**Questions?** Check:
1. Flask server logs for API errors
2. learner_simulation.py output for interaction logging
3. process_simulation_data.py for data extraction details
4. /data/processed/ for final table contents

