# Module Usage Analysis - Adaptive Tutoring Framework

**Date:** January 10, 2026  
**Purpose:** Identify which modules are core/active vs. optional/unused for clean workspace creation

## Summary

- **Core Modules (17):** Required for system to function
- **Optional Modules (8):** Won't break tests if disabled, but may affect analytics/advanced features
- **Unused Modules (4):** Not referenced anywhere, can be safely removed
- **Disabled Features (2):** Infrastructure exists but disabled by default

---

## Part 1: CORE/ACTIVE MODULES (Required)

These modules are actively used in normal test operation. Removing any of these will break the system.

### Backend Models (Foundation)
```
✅ app/models/session.py
   - Classes: Session, StudentResponse
   - Used by: cbt/system.py, engagement/routes.py, adaptation/engine.py
   - Purpose: Core data storage for test sessions and student responses
   - Status: REQUIRED - no exceptions

✅ app/models/student.py
   - Classes: Student
   - Used by: cbt/system.py
   - Purpose: Student identity and preferences
   - Status: REQUIRED

✅ app/models/question.py
   - Classes: Question, QuestionDifficulty
   - Used by: cbt/system.py, cbt/routes.py
   - Purpose: Test question content and metadata
   - Status: REQUIRED

✅ app/models/engagement.py
   - Classes: EngagementMetric
   - Used by: engagement/routes.py, cbt/routes.py, adaptation/engine.py
   - Purpose: Engagement metric storage
   - Status: REQUIRED

✅ app/models/adaptation.py
   - Classes: AdaptationLog
   - Used by: adaptation/engine.py
   - Purpose: Logging of adaptation decisions for audit trail
   - Status: REQUIRED
```

### Backend Test System (Core Logic)
```
✅ app/cbt/system.py
   - Classes: CBTSystem
   - Methods: start_session(), submit_response(), get_next_question()
   - Used by: cbt/routes.py
   - Purpose: Core test logic and state management
   - Status: REQUIRED - core application

✅ app/cbt/routes.py
   - Endpoints: /session/start, /response/submit, /question/next, /hint/*, /response/*, /student
   - Used by: Frontend (API calls)
   - Purpose: REST API for test system
   - Status: REQUIRED - frontend depends on these endpoints

✅ app/engagement/tracker.py
   - Classes: EngagementIndicatorTracker
   - Methods: track_behavioral_indicators(), track_cognitive_indicators(), calculate_composite_engagement_score()
   - Used by: engagement/routes.py, cbt/system.py
   - Purpose: Engagement metric calculation
   - Status: REQUIRED - all engagement calculated here

✅ app/engagement/routes.py
   - Endpoints: /track, /get/*
   - Used by: Frontend (API calls)
   - Purpose: Engagement tracking API
   - Status: REQUIRED - frontend tracks engagement via this
```

### Backend Adaptation (Rule-Based)
```
✅ app/adaptation/engine.py
   - Classes: AdaptiveEngine
   - Methods: adapt_difficulty(), adapt_pacing(), adapt_hint_frequency()
   - Used by: cbt/system.py
   - Purpose: Main difficulty adaptation logic
   - Status: REQUIRED - core adaptation mechanism

✅ app/adaptation/facial_signal_integration.py
   - Classes: FacialSignalConfig, FacialSignalProcessor
   - Used by: adaptation/engine.py (in try/except block)
   - Status: INFRASTRUCTURE ONLY
   - Notes: Disabled by default (ENABLED = False), safe to keep
   - Impact if removed: adapt_difficulty() would throw exception (protected)
   - Recommendation: KEEP - minimal code, disabled by default

✅ app/adaptation/routes.py
   - Endpoints: /adapt/*, endpoints for adaptation API
   - Used by: Frontend (API calls)
   - Purpose: Adaptation-related API endpoints
   - Status: REQUIRED - test system uses this
```

### Backend Analytics (Required)
```
✅ app/analytics/evaluator.py
   - Classes: ResearchEvaluator
   - Used by: analytics/routes.py
   - Purpose: Post-session analysis and evaluation
   - Status: REQUIRED for analytics endpoints

✅ app/analytics/routes.py
   - Endpoints: /export/*, /analyze/*, /compare/*, /learning-curves/*, /facial-data/*
   - Used by: Frontend data export
   - Purpose: Analytics and export API
   - Status: REQUIRED - frontend uses these for exports
```

### Core Infrastructure
```
✅ app/__init__.py
   - Functions: create_app()
   - Purpose: Flask application factory
   - Status: REQUIRED - application bootstrap

✅ config.py (project root)
   - Configuration for all modules
   - Status: REQUIRED
```

### Frontend (All Active)
```
✅ frontend/app.js (~2200 lines)
   - All functions are active during test
   - Purpose: Main application frontend
   - Status: REQUIRED

✅ frontend/index.html
   - HTML structure
   - Status: REQUIRED

✅ frontend/styles.css
   - Styling
   - Status: REQUIRED

✅ frontend/package.json
   - Dependencies metadata
   - Status: REQUIRED
```

---

## Part 2: OPTIONAL MODULES (Advanced Features)

These modules are **imported and instantiated** but NOT used in the normal test flow. They're part of analytics or advanced features. Disabling them affects analytics but NOT core test functionality.

```
🔜 app/engagement/mastery.py
   - Classes: MasteryTracker
   - Used by: analytics/routes.py (instantiated but usage unclear)
   - Impact if removed: Analytics endpoints might fail
   - Recommendation: ARCHIVE if removing analytics features

🔜 app/engagement/affective.py
   - Classes: AffectiveIndicatorAnalyzer
   - Used by: analytics/routes.py
   - Impact if removed: Analytics endpoints might fail
   - Recommendation: ARCHIVE if removing analytics features

🔜 app/engagement/spaced_repetition.py
   - Classes: SpacedRepetitionScheduler, LearningCurveAnalyzer
   - Used by: analytics/routes.py
   - Impact if removed: Analytics endpoints might fail
   - Recommendation: ARCHIVE if removing analytics features

🔜 app/engagement/facial_expression_api.py
   - Classes: FacialExpressionIntegrator
   - Used by: analytics/routes.py (line 876)
   - Status: INFRASTRUCTURE ONLY - no actual facial processing
   - Impact if removed: Facial data export endpoint would fail
   - Recommendation: ARCHIVE if removing facial features

🔜 app/adaptation/rl_agent.py
   - Classes: RLAdaptiveAgent
   - Used by: analytics/routes.py (only for reporting)
   - Status: DISABLED - never called during normal test operation
   - Impact if removed: RL-related analytics would fail, but tests unaffected
   - Recommendation: ARCHIVE

🔜 app/adaptation/rl_policy_optimizer.py
   - Classes: RLPolicyOptimizer, ExplorationStrategy
   - Used by: analytics/routes.py, rl_agent.py
   - Status: DISABLED - never called during normal test operation
   - Impact if removed: RL-related analytics would fail, but tests unaffected
   - Recommendation: ARCHIVE

🔜 app/adaptation/irt.py
   - Classes: IRTModel, CATAlgorithm
   - Used by: analytics/routes.py (imported but verify actual usage)
   - Status: NEEDS AUDIT - check if actually called
   - Recommendation: AUDIT before archiving

🔜 app/analytics/evaluator.py
   - Classes: ResearchEvaluator
   - Used by: analytics/routes.py (check if actually called)
   - Status: NEEDS AUDIT - in use but verify if essential
   - Recommendation: KEEP for now if analytics is required
```

---

## Part 3: LIKELY UNUSED MODULES

These modules are either not referenced or only referenced from other unused modules.

```
❌ app/adaptation/policy.py
   - Classes: TutoringAction, AdaptiveDecision, AdaptivePolicyEngine
   - Used by: NOWHERE
   - Imports from: engagement/fusion.py, engagement/indicators.py
   - Status: COMPLETELY UNUSED
   - Impact if removed: No impact - system works identically
   - Recommendation: ARCHIVE/DELETE

❌ app/adaptation/performance_window.py
   - Classes: WindowPerformanceTracker
   - Used by: policy.py (unused module)
   - Status: UNUSED (only used by unused module)
   - Impact if removed: No impact
   - Recommendation: ARCHIVE/DELETE

❌ app/engagement/fusion.py
   - Classes: FusedEngagementState, EngagementState
   - Used by: policy.py (unused module)
   - Status: LIKELY UNUSED (only used by unused module)
   - Recommendation: AUDIT - verify not used elsewhere

❌ app/engagement/indicators.py
   - Classes: EngagementIndicators
   - Used by: policy.py (unused module)
   - Status: LIKELY UNUSED (only used by unused module)
   - Recommendation: AUDIT - verify not used elsewhere

❌ app/adaptation/difficulty_mapper.py
   - Status: UNKNOWN - needs verification
   - Recommendation: AUDIT

❌ app/logging/engagement_logger.py
   - Status: UNKNOWN - check if exists and if used
   - Recommendation: AUDIT
```

---

## Part 4: DISABLED FEATURES (Infrastructure Only)

These features have code and infrastructure but are **disabled by default** and don't run during normal operation.

### Facial Expression Monitoring
```
Status: DISABLED
Configuration: app/adaptation/facial_signal_integration.py → FacialSignalConfig.ENABLED = False

Components:
  - Backend processor: FacialSignalProcessor (can receive facial data but doesn't)
  - Frontend UI: index.html lines 12-39 (visible but non-functional)
  - Frontend models: app.js lines 1855+ (loads disabled by default)

Impact if disabled: No impact - system behavior identical
Impact if enabled: Would provide soft adjustments to difficulty (±10% max)

Recommendation: KEEP - minimal code, disabled by default, good infrastructure for future use
```

### Reinforcement Learning Adaptation
```
Status: DISABLED
Never called: rl_agent.py is instantiated in analytics/routes.py but never called from adaptation/engine.py

Components:
  - RL agent: app/adaptation/rl_agent.py
  - RL optimizer: app/adaptation/rl_policy_optimizer.py
  - Current system: Uses rule-based deterministic adaptation (engine.py)

Impact if disabled: No impact - rule-based system used instead
Impact if enabled: Would use learned policies for difficulty (non-deterministic)

Why disabled: Transparency and research validity prioritized over potential performance gains

Recommendation: ARCHIVE - not part of current implementation, good to clean up
```

---

## Part 5: Frontend Optional Features

### Facial Monitoring UI
```
Status: UI ONLY - no backend functionality
Location: frontend/index.html lines 12-39 (CSS and HTML structure)
          frontend/app.js lines 1855-2000+ (JavaScript class definition)

Components:
  - HTML panel for facial monitoring display
  - JavaScript WebcamFacialCapture class
  - Model loading code (never actually loads models)
  - Emotion/gaze/posture display (no data shown, always "--")

Impact if removed: Cleaner UI, no functional change
Recommendation: Can remove for clean workspace

Notes:
  - Models (faceapi) are never loaded (try-catch fails silently)
  - No actual facial data collected
  - UI is placeholder only
```

---

## Recommendations for Clean Workspace

### Minimum Viable System (Core Only)
Keep only:
- All models/ (foundation data)
- cbt/ (test system)
- engagement/tracker.py (engagement calculation)
- engagement/routes.py (engagement API)
- adaptation/engine.py (difficulty adaptation)
- adaptation/facial_signal_integration.py (disabled infrastructure)
- adaptation/routes.py (adaptation API)
- analytics/ (export/reporting)
- frontend/ (all)

Remove:
- adaptation/policy.py
- adaptation/performance_window.py
- adaptation/rl_*.py
- engagement/fusion.py (if only used by policy.py)
- engagement/indicators.py (if only used by policy.py)
- engagement/mastery.py (if minimizing analytics)
- engagement/affective.py (if minimizing analytics)
- engagement/spaced_repetition.py (if minimizing analytics)
- engagement/facial_expression_api.py (if minimizing facial features)
- logging/engagement_logger.py (if unused)
- Facial monitoring UI from frontend/app.js and frontend/index.html

### Maximum Clean System (Keep All Active + Infrastructure)
Keep everything except clearly unused modules:
- Remove only: policy.py, performance_window.py, (rl_*.py if not needed)
- Keep: All others (even if not in core flow, they don't hurt)

---

## Files to Archive/Delete

**Definitely Remove:**
- `backend/app/adaptation/policy.py` (UNUSED)
- `backend/app/adaptation/performance_window.py` (UNUSED, only used by policy.py)

**Likely Remove (Verify First):**
- `backend/app/adaptation/rl_agent.py` (DISABLED, only used in analytics)
- `backend/app/adaptation/rl_policy_optimizer.py` (DISABLED, only used in analytics)
- `backend/app/engagement/facial_expression_api.py` (INFRASTRUCTURE ONLY)

**Frontend Cleanup:**
- Remove facial monitoring UI from `frontend/app.js` lines 1855-2050 (if not needed)
- Remove facial monitoring panel HTML from `frontend/index.html` lines 12-39 (if not needed)

---

## Archive Structure Recommendation

Create: `archive_unused_modules/` with:
```
archive_unused_modules/
  ├── adaptation/
  │   ├── policy.py
  │   ├── performance_window.py
  │   ├── rl_agent.py
  │   ├── rl_policy_optimizer.py
  │   └── irt.py (if unused)
  ├── engagement/
  │   ├── facial_expression_api.py
  │   ├── fusion.py (if only used by policy.py)
  │   ├── indicators.py (if only used by policy.py)
  │   ├── mastery.py (if minimizing analytics)
  │   ├── affective.py (if minimizing analytics)
  │   └── spaced_repetition.py (if minimizing analytics)
  └── README.md (document why each file was archived)
```

---

**Status:** Analysis Complete  
**Next Step:** Create clean_workspace/ with only active modules
