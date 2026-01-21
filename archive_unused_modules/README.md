# Archive of Unused/Optional Modules

**Purpose:** This directory contains modules that were identified as unused or optional during the project cleanup on January 10, 2026.

**Important:** These files are kept for reference only. The main system functions identically without them.

---

## Modules in This Archive

### `adaptation/policy.py`
- **Status:** UNUSED
- **Reason:** AdaptivePolicyEngine class is defined but never instantiated or called anywhere in the system
- **Used by:** Nobody (orphaned code)
- **Impact if deleted:** Zero impact - system behavior unchanged
- **Notes:** Contains RL-inspired policy logic that was superseded by rule-based adaptation in engine.py

### `adaptation/performance_window.py`
- **Status:** UNUSED
- **Reason:** WindowPerformanceTracker is only imported by policy.py, which is itself unused
- **Used by:** policy.py only (unused module)
- **Impact if deleted:** Zero impact
- **Notes:** Related to performance tracking over time windows

### ⚠️ Note on RL Modules

The following modules were examined but NOT archived because they are used by analytics/routes.py:

- `adaptation/rl_agent.py` - Used by analytics for reporting
- `adaptation/rl_policy_optimizer.py` - Used by analytics for reporting

However, they are NOT called during normal test operation, only during analytics computation.

**If removing analytics features:** These modules can be archived along with analytics/routes.py

### `engagement/fusion.py`
- **Status:** LIKELY UNUSED
- **Reason:** FusedEngagementState and EngagementState are imported by policy.py (unused module)
- **Used by:** policy.py primarily
- **Impact if deleted:** policy.py would fail (already unused), minimal other impact
- **Notes:** Was intended for engagement state fusion but replaced by simpler approaches

### `engagement/indicators.py`
- **Status:** LIKELY UNUSED
- **Reason:** EngagementIndicators class is imported by policy.py (unused module)
- **Used by:** policy.py primarily
- **Impact if deleted:** policy.py would fail (already unused), minimal other impact
- **Notes:** Engagement indicator definitions

---

## Why These Modules Aren't Active

### 1. **Policy-Based Adaptation (Replaced)**
- Original design included `policy.py` with RL-inspired decision making
- Actual implementation uses simpler rule-based adaptation in `engine.py`
- Policy code remains but is never called
- Removing it has zero functional impact

### 2. **Reinforcement Learning (Deliberately Disabled)**
- `rl_agent.py` and `rl_policy_optimizer.py` exist for future use
- NOT activated in core system because:
  - Would introduce non-deterministic behavior (bad for research)
  - Rule-based system is transparent and reproducible
  - RL would complicate validation and auditing
- Kept these files because:
  - Low overhead when disabled
  - Could be enabled in future with `FacialSignalConfig.ENABLED = True`
  - Good reference implementation for future work

### 3. **Advanced Engagement Analysis (Optional)**
- `mastery.py`, `affective.py`, `spaced_repetition.py` are instantiated but not actively used in core flow
- Only used in analytics endpoints for post-session analysis
- Can be disabled if minimizing feature scope

---

## What To Do With These Files

### Option 1: Keep (Recommended for Research)
Leave files in archive. Pros:
- Reference implementations for future work
- Don't break analytics if someone imports them
- Good documentation of design evolution
- Easy to re-enable if needed

Cons:
- Takes up space
- Slightly confusing for new developers

### Option 2: Delete Completely (Recommended for Production)
Remove files entirely. Pros:
- Cleaner codebase
- No confusion about what's active
- Smaller package size

Cons:
- Lose reference implementations
- Would need to re-implement if RL/policy-based approach is reconsidered

### Option 3: Separate Repository
Move to separate `legacy_implementations/` repo. Pros:
- Keeps main repo clean
- Maintains reference implementations
- Can be reactivated independently

---

## How To Restore Files

If you need any of these modules, restore from this archive:

```bash
# Restore individual file
cp archive_unused_modules/adaptation/policy.py backend/app/adaptation/

# Or restore entire adaptation subfolder
cp -r archive_unused_modules/adaptation/* backend/app/adaptation/
```

---

## Files That SHOULD Stay in Main System

Even though some of these look "optional", these MUST stay:

- **engagement/tracker.py** - Core engagement calculation (ACTIVE)
- **engagement/routes.py** - Engagement API (ACTIVE)
- **adaptation/engine.py** - Core adaptation logic (ACTIVE)
- **adaptation/facial_signal_integration.py** - Infrastructure (disabled but safe)
- All models/ - Data structures (REQUIRED)
- All in cbt/ - Test system (REQUIRED)

---

## Verification

The system was tested with these modules archived and verified to work identically:
- ✅ Test system runs
- ✅ Engagement metrics calculated
- ✅ Difficulty adapts
- ✅ Data exports work
- ✅ No console errors

---

**Archive Date:** January 10, 2026  
**Reason:** Project cleanup and removal of misleading claims about inactive features  
**Impact Assessment:** Zero functional impact on active system
