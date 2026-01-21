#!/usr/bin/env python3
"""
Pre-Flight Checklist
====================

Validates that your system is ready to run the complete simulation workflow.
Run this BEFORE starting the full simulation to catch configuration issues early.
"""

import sys
import json
import requests
from pathlib import Path
from typing import Tuple

# ============================================================================
# CONFIGURATION
# ============================================================================

API_URL = "http://localhost:5000"
SIMULATION_DIR = Path("/home/smartz/Desktop/Major Projects/adaptive-tutoring-framework/data/simulated")
PROCESSED_DIR = Path("/home/smartz/Desktop/Major Projects/adaptive-tutoring-framework/data/processed")

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def check_python_env() -> Tuple[bool, str]:
    """Verify Python packages are available."""
    required = ['requests', 'pandas', 'numpy', 'scipy']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        return False, f"Missing packages: {', '.join(missing)}\nInstall: pip install {' '.join(missing)}"
    return True, "All required packages installed"

def check_flask_server() -> Tuple[bool, str]:
    """Verify Flask server is running and responding."""
    try:
        # Try basic connectivity
        response = requests.get(f"{API_URL}/", timeout=5)
        return True, f"Flask server responding (status: {response.status_code})"
    except requests.exceptions.ConnectionError:
        return False, f"Cannot connect to {API_URL}. Is Flask server running?"
    except Exception as e:
        return False, f"Flask connection error: {str(e)}"

def check_api_endpoints() -> Tuple[bool, str]:
    """Verify required API endpoints exist and respond correctly."""
    errors = []
    
    # Check /api/session/start endpoint
    try:
        response = requests.post(
            f"{API_URL}/api/session/start",
            json={"student_id": "TEST-001", "subject": "math", "preferred_difficulty": 5},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if 'session_id' not in data:
                errors.append("✗ /api/session/start: Response missing 'session_id' field")
            else:
                # Store for next test
                test_session_id = data['session_id']
        else:
            errors.append(f"✗ /api/session/start: Unexpected status {response.status_code}")
    except Exception as e:
        errors.append(f"✗ /api/session/start: {str(e)}")
        return False, "\n".join(errors)
    
    # Check /api/response/submit endpoint (if session was created)
    try:
        if test_session_id:
            response = requests.post(
                f"{API_URL}/api/response/submit",
                json={
                    "session_id": test_session_id,
                    "student_answer": "A",
                    "response_time_seconds": 15.0,
                    "option_changes": 1,
                    "hints_used": 0,
                    "pauses_during_response": 0
                },
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                required_fields = ['engagement_score', 'new_difficulty', 'engagement_level']
                missing = [f for f in required_fields if f not in data]
                if missing:
                    errors.append(f"✗ /api/response/submit: Missing fields: {missing}")
                else:
                    # All good
                    pass
            else:
                errors.append(f"✗ /api/response/submit: Unexpected status {response.status_code}")
    except Exception as e:
        errors.append(f"✗ /api/response/submit: {str(e)}")
    
    if errors:
        return False, "\n".join(errors)
    return True, "All required endpoints present and responding correctly"

def check_directories() -> Tuple[bool, str]:
    """Verify required directories exist or can be created."""
    try:
        SIMULATION_DIR.mkdir(parents=True, exist_ok=True)
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        return True, f"Directories ready:\n  • {SIMULATION_DIR}\n  • {PROCESSED_DIR}"
    except Exception as e:
        return False, f"Cannot create directories: {str(e)}"

def check_simulation_script() -> Tuple[bool, str]:
    """Verify simulation script exists and is readable."""
    script_path = Path("/home/smartz/Desktop/Major Projects/adaptive-tutoring-framework/data/learner_simulation.py")
    if not script_path.exists():
        return False, f"Simulation script not found: {script_path}"
    try:
        with open(script_path, 'r') as f:
            content = f.read()
            if 'class LearnerSimulator' not in content:
                return False, "Simulation script corrupted or incomplete"
        return True, f"Simulation script present and valid"
    except Exception as e:
        return False, f"Cannot read simulation script: {str(e)}"

def check_processing_script() -> Tuple[bool, str]:
    """Verify processing script exists and is readable."""
    script_path = Path("/home/smartz/Desktop/Major Projects/adaptive-tutoring-framework/data/process_simulation_data.py")
    if not script_path.exists():
        return False, f"Processing script not found: {script_path}"
    try:
        with open(script_path, 'r') as f:
            content = f.read()
            if 'def process_simulation_data' not in content:
                return False, "Processing script corrupted or incomplete"
        return True, f"Processing script present and valid"
    except Exception as e:
        return False, f"Cannot read processing script: {str(e)}"

def check_simulation_data() -> Tuple[bool, str]:
    """Check if simulation data already exists (optional)."""
    data_file = SIMULATION_DIR / "simulation_complete.json"
    if data_file.exists():
        try:
            with open(data_file, 'r') as f:
                data = json.load(f)
                num_adaptive = len(data.get('adaptive', []))
                num_nonadapt = len(data.get('non_adaptive', []))
                return True, f"Existing simulation data found:\n  • {num_adaptive} adaptive learners\n  • {num_nonadapt} non-adaptive learners"
        except Exception as e:
            return False, f"Simulation data exists but is corrupted: {str(e)}"
    return True, "No existing simulation data (ready for fresh run)"

# ============================================================================
# MAIN CHECK RUNNER
# ============================================================================

def run_checks():
    """Run all validation checks and report results."""
    
    print("="*70)
    print("PRE-FLIGHT CHECKLIST: Simulation System Readiness")
    print("="*70)
    print()
    
    checks = [
        ("1. Python Environment", check_python_env),
        ("2. Flask Server", check_flask_server),
        ("3. API Endpoints", check_api_endpoints),
        ("4. Directory Structure", check_directories),
        ("5. Simulation Script", check_simulation_script),
        ("6. Processing Script", check_processing_script),
        ("7. Simulation Data", check_simulation_data),
    ]
    
    results = []
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            passed, message = check_func()
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{check_name}: {status}")
            print(f"  {message}")
            print()
            
            results.append((check_name, passed, message))
            if not passed and "FAIL" in status:
                all_passed = False
        except Exception as e:
            print(f"{check_name}: ✗ ERROR")
            print(f"  {str(e)}")
            print()
            results.append((check_name, False, str(e)))
            all_passed = False
    
    # Summary
    print("="*70)
    print("SUMMARY")
    print("="*70)
    
    if all_passed:
        print("✓ All checks PASSED - Ready to run simulation!")
        print()
        print("Next steps:")
        print("  1. python3 data/learner_simulation.py          (Run simulation)")
        print("  2. python3 data/process_simulation_data.py     (Process data)")
        print("  3. Check /data/processed/ for output tables")
        return 0
    else:
        failed = [r for r in results if not r[1]]
        print(f"✗ {len(failed)} check(s) FAILED:")
        for name, _, message in failed:
            print(f"  • {name}")
        print()
        print("Fix the issues above before running simulation.")
        return 1

if __name__ == "__main__":
    sys.exit(run_checks())
