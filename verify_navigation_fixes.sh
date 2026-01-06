#!/usr/bin/env bash
# Navigation Fix Status Check
# Run this to verify all navigation fixes are in place

echo ""
echo "=========================================================================="
echo "  CBT NAVIGATION FIXES - VERIFICATION REPORT"
echo "=========================================================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "[1] Checking for session state reset on new test..."
if grep -q "sessionQuestionHistory = \[\]" frontend/app.js; then
    echo -e "${GREEN}✓${NC} Found: sessionQuestionHistory cleared on new session"
else
    echo -e "${RED}✗${NC} Missing: sessionQuestionHistory not cleared"
fi

if grep -q "currentQuestionIndex = 0" frontend/app.js && grep -q "sessionNavigationCount = 0" frontend/app.js; then
    echo -e "${GREEN}✓${NC} Found: currentQuestionIndex and sessionNavigationCount reset"
else
    echo -e "${RED}✗${NC} Missing: State variables not reset"
fi

echo ""
echo "[2] Checking Previous button logic..."
if grep -q "if (currentQuestionIndex === 0)" frontend/app.js; then
    echo -e "${GREEN}✓${NC} Found: Previous button blocked when currentQuestionIndex === 0"
else
    echo -e "${RED}✗${NC} Missing: Previous button check not found"
fi

if grep -q "Cannot go previous, at first question of session" frontend/app.js; then
    echo -e "${GREEN}✓${NC} Found: Proper logging for Previous button block"
else
    echo -e "${RED}✗${NC} Missing: Debug logging not found"
fi

echo ""
echo "[3] Checking Next button logic..."
if grep -q "if (isOnCurrentQuestion)" frontend/app.js && grep -q "Must answer current question first" frontend/app.js; then
    echo -e "${GREEN}✓${NC} Found: Next button blocked when on current question"
else
    echo -e "${RED}✗${NC} Missing: Next button blocking logic"
fi

if grep -q "atEndOfHistory && !isOnCurrentQuestion" frontend/app.js; then
    echo -e "${GREEN}✓${NC} Found: Proper end-of-history handling (doesn't end test)"
else
    echo -e "${RED}✗${NC} Missing: End-of-history logic"
fi

if ! grep -q "if (isLastQuestion) { showDashboard()" frontend/app.js; then
    echo -e "${GREEN}✓${NC} Found: Removed premature test end logic"
else
    echo -e "${YELLOW}⚠${NC} Warning: Old test-end-on-last-question logic may still exist"
fi

echo ""
echo "[4] Checking modal continuation fix..."
if grep -q "if (!currentSession)" frontend/app.js && grep -q "const testComplete = currentSession.questions_completed" frontend/app.js; then
    echo -e "${GREEN}✓${NC} Found: Modal handler uses currentSession and proper completion check"
else
    echo -e "${RED}✗${NC} Missing: Modal handler fix"
fi

echo ""
echo "[5] Checking test script..."
if [ -f "backend/scripts/test_navigation_fixes.py" ]; then
    echo -e "${GREEN}✓${NC} Found: test_navigation_fixes.py exists"
    if grep -q "test_previous_button_on_q1" backend/scripts/test_navigation_fixes.py; then
        echo -e "${GREEN}✓${NC} Found: Previous button test"
    fi
    if grep -q "test_navigation_flow" backend/scripts/test_navigation_fixes.py; then
        echo -e "${GREEN}✓${NC} Found: Navigation flow test"
    fi
else
    echo -e "${YELLOW}⚠${NC} Warning: test_navigation_fixes.py not found"
fi

echo ""
echo "=========================================================================="
echo ""
echo "Summary:"
echo "--------"
echo "These fixes address:"
echo "  1. Previous button disabled on Q1 of new session"
echo "  2. Next button doesn't end test prematurely during revisits"
echo "  3. Session state properly cleared when starting new test"
echo "  4. Modal handler uses correct session variable"
echo ""
echo "Verification:"
echo "  Run: python3 backend/scripts/test_navigation_fixes.py"
echo "  Check: Backend must be running at http://localhost:5000"
echo ""
echo "=========================================================================="
echo ""
