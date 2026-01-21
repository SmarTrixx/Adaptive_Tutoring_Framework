# QUICK REFERENCE CHECKLIST

## 📍 YOUR LOCATION: Everything Ready for Execution

Print this page and check off items as you proceed.

---

## ✓ Pre-Execution Checklist (5 minutes)

- [ ] **Read**: `SIMULATION_WORKFLOW.md` (understand the process)
- [ ] **Verify**: Flask server can be started
- [ ] **Verify**: Python packages installed (requests, pandas, numpy, scipy)
- [ ] **Verify**: `/data/simulated/` directory exists (or will auto-create)
- [ ] **Run**: `python3 data/preflight_check.py`
  - [ ] All 7 checks pass ✓
  - [ ] No errors reported
  - [ ] System is ready

---

## ✓ Execution Checklist (20 minutes total)

### Step 1: Start Flask Server (Terminal 1)
```bash
cd /home/smartz/Desktop/Major\ Projects/adaptive-tutoring-framework
python3 backend/main.py
# (or your Flask startup command)
```
- [ ] Flask server starts without errors
- [ ] Output shows: "Running on http://localhost:5000"
- [ ] Server is listening on port 5000

### Step 2: Run Simulation (Terminal 2)
```bash
cd /home/smartz/Desktop/Major\ Projects/adaptive-tutoring-framework
python3 data/learner_simulation.py
```
- [ ] Script starts without errors
- [ ] Processes 10 adaptive learners
- [ ] Processes 10 non-adaptive learners
- [ ] Output shows: "SIMULATION COMPLETE"
- [ ] Confirms: "Raw data saved: data/simulated/simulation_complete.json"

### Step 3: Verify Raw Data
```bash
ls -lh data/simulated/simulation_complete.json
```
- [ ] File exists
- [ ] File size 2-5 MB
- [ ] Created recently (check timestamp)

### Step 4: Process Data
```bash
python3 data/process_simulation_data.py
```
- [ ] Script starts without errors
- [ ] Shows: "Loading simulation data..."
- [ ] Shows: "Generating Chapter 4 tables..."
- [ ] Shows: "Saving outputs..."
- [ ] Output shows: "PROCESSING COMPLETE"
- [ ] Shows summary with learner counts and statistics

### Step 5: Verify Output Files
```bash
ls -lh data/processed/
```
- [ ] Table_4.1.csv exists
- [ ] Table_4.3.csv exists
- [ ] Table_4.5.csv exists
- [ ] Table_4.6.csv exists
- [ ] Table_4.7.csv exists
- [ ] raw_responses.csv exists
- [ ] raw_engagement.csv exists
- [ ] raw_adaptations.csv exists
- [ ] All files have recent timestamps

---

## ✓ Quality Assurance Checklist (5 minutes)

### Verify Data Integrity
- [ ] Open `data/processed/Table_4.3.csv`
  - [ ] Contains "Group", "Mean Accuracy", "Total Questions" columns
  - [ ] Shows "Adaptive" and "Non-Adaptive" rows
  - [ ] Adaptive accuracy > Non-adaptive accuracy
  - [ ] Numbers are in realistic ranges

- [ ] Open `data/processed/Table_4.7.csv`
  - [ ] Shows adaptation actions (Increase, Maintain, Decrease)
  - [ ] Only appears in adaptive condition files
  - [ ] Percentages sum to approximately 100%

- [ ] Open `data/processed/raw_responses.csv`
  - [ ] Has 200+ rows (one per interaction)
  - [ ] Columns include: is_correct, response_time_seconds, etc.
  - [ ] Data looks reasonable (response times 5-60 seconds, mostly)

- [ ] Open `data/simulated/simulation_complete.json`
  - [ ] Valid JSON format (can parse)
  - [ ] Contains "adaptive" and "non_adaptive" sections
  - [ ] Each learner has "interactions" array
  - [ ] Each interaction has "request" and "response" objects

### Verify Logic
- [ ] Adaptive learners have more varied difficulty scores
- [ ] Non-adaptive learners have consistent difficulty
- [ ] Engagement scores in range 0-100
- [ ] Accuracy percentages in range 0-100
- [ ] Response times generally positive (5-60 seconds)

---

## ✓ Thesis Integration Checklist (30 minutes)

### Copy Tables to Document
- [ ] Open your thesis Chapter 4 document
- [ ] Navigate to Results section
- [ ] Create "System Evaluation Results" subsection

- [ ] Insert Table 4.1 (Participant Characteristics)
  - [ ] Paste content from `data/processed/Table_4.1.csv`
  - [ ] Format as professional table
  - [ ] Add caption and reference

- [ ] Insert Table 4.3 (Performance Scores)
  - [ ] Paste content from `data/processed/Table_4.3.csv`
  - [ ] Format as professional table
  - [ ] Add caption and reference

- [ ] Insert Table 4.5 (Engagement Trajectory)
  - [ ] Paste content from `data/processed/Table_4.5.csv`
  - [ ] Format as professional table
  - [ ] Add caption and reference

- [ ] Insert Table 4.6 (Behavioral Metrics)
  - [ ] Paste content from `data/processed/Table_4.6.csv`
  - [ ] Format as professional table
  - [ ] Add caption and reference

- [ ] Insert Table 4.7 (Adaptation Distribution)
  - [ ] Paste content from `data/processed/Table_4.7.csv`
  - [ ] Format as professional table
  - [ ] Add caption and reference

### Write Interpretation Text
- [ ] Add Methods subsection explaining:
  - [ ] You used simulated learners with 5 profile types
  - [ ] 20 total learners (10 adaptive, 10 non-adaptive)
  - [ ] Each completed 10 questions via Flask API
  - [ ] All metrics captured from system responses

- [ ] Add Results section interpreting each table:
  - [ ] What the table shows
  - [ ] Key findings
  - [ ] Comparison between conditions
  - [ ] Statistical significance (if applicable)

- [ ] Add Discussion section including:
  - [ ] What results mean for your research question
  - [ ] Alignment with hypotheses
  - [ ] Limitations of approach
  - [ ] Implications for implementation

---

## ✓ Final Verification Checklist (2 minutes)

- [ ] All 5 thesis tables are in Chapter 4
- [ ] All tables have captions and are referenced in text
- [ ] Methodology section explains the evaluation approach
- [ ] Results section interprets the data
- [ ] Discussion section addresses implications
- [ ] All numbers in text match table values
- [ ] No errors or typos in table content
- [ ] Formatting is consistent and professional
- [ ] Chapter reads coherently from methodology through results

---

## 🎯 SUCCESS INDICATORS

You'll know everything is working correctly when:

✓ Preflight check: All 7 checks PASS
✓ Simulation: 20 learners complete without errors
✓ Raw data: ~200+ interactions captured
✓ Processing: All 5 tables generated
✓ Data quality: Adaptive > Non-adaptive (typically)
✓ Files: All 8 output files created
✓ Thesis: Tables formatted and integrated
✓ Text: Interpretation written and reviewed
✓ Final: Chapter 4 reads professionally complete

---

## 📊 IF SOMETHING FAILS

| Error | Check | Fix |
|-------|-------|-----|
| "Connection refused" | Is Flask running? | Start Flask server first |
| "Module not found" | Run preflight check | Install missing package |
| "File not found" | Did simulation complete? | Check for error messages |
| "Invalid JSON" | Check file size | Re-run simulation |
| Empty table data | Verify simulation ran fully | Check interaction count |
| Wrong API response | Check endpoint names | See SYSTEM_INTEGRATION_GUIDE.md |

---

## 📱 QUICK COMMAND REFERENCE

```bash
# Pre-execution
python3 data/preflight_check.py

# Simulation (after Flask starts)
python3 data/learner_simulation.py

# Processing
python3 data/process_simulation_data.py

# Verify outputs exist
ls -l data/processed/Table_*.csv

# View a table
cat data/processed/Table_4.3.csv

# Check file sizes
du -sh data/simulated/ data/processed/
```

---

## 📖 DOCUMENTATION REFERENCE

| Need | Read This File |
|------|-----------------|
| Full walkthrough | SIMULATION_WORKFLOW.md |
| Quick summary | DELIVERY_SUMMARY.md |
| Status check | SIMULATION_READY.md |
| Technical details | SYSTEM_INTEGRATION_GUIDE.md |
| Navigation | SYSTEM_INDEX.md |
| This checklist | QUICK_REFERENCE.md |

---

## ⏱️ TIME TRACKING

Track your progress:

| Task | Est. Time | Start | End | Duration |
|------|-----------|-------|-----|----------|
| Read documentation | 15 min | ___ | ___ | ___ |
| Run preflight check | 1 min | ___ | ___ | ___ |
| Start Flask server | 1 min | ___ | ___ | ___ |
| Run simulation | 15 min | ___ | ___ | ___ |
| Run processing | 1 min | ___ | ___ | ___ |
| Review outputs | 5 min | ___ | ___ | ___ |
| Integrate tables | 20 min | ___ | ___ | ___ |
| Write interpretation | 30 min | ___ | ___ | ___ |
| Final review | 10 min | ___ | ___ | ___ |
| **TOTAL** | **~90 min** | | | |

---

## 🎓 THESIS INTEGRATION EXAMPLES

### Copy This to Methodology
> "System evaluation was conducted through simulation with 20 simulated learners representing five behavioral profiles (High-Ability, Average, Low-Ability, Anxious, Disengaging). Each learner completed 10 questions while interacting with the actual Flask implementation. Metrics were captured directly from the system's API responses, enabling assessment of the adaptation algorithm's behavior without user studies."

### Copy This to Results
> "Table 4.3 presents accuracy results. The adaptive condition achieved XX% mean accuracy compared to YY% in the fixed-difficulty baseline. Table 4.7 shows the system's adaptation distribution, with XX% difficulty increases, YY% maintains, and ZZ% decreases, indicating systematic response to performance signals."

### Copy This to Discussion
> "The simulation results validate the core functionality of the adaptive algorithm. The engagement and performance metrics (Tables 4.5-4.6) demonstrate the system successfully identifies and responds to learner state changes..."

---

## ✅ FINAL CHECKLIST ITEM

- [ ] **Everything is ready. You can now proceed with execution.**

**Next Step**: Run `python3 data/preflight_check.py`

**Then**: Follow SIMULATION_WORKFLOW.md for complete instructions

**Result**: Working Chapter 4 with real system data

---

**Print this checklist and check items off as you proceed through the workflow.**

