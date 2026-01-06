#!/bin/bash
# QUICK START VERIFICATION SCRIPT
# Run this after deployment to verify all critical fixes are working

set -e

echo "========================================================================"
echo "ADAPTIVE TUTORING FRAMEWORK - POST-DEPLOYMENT VERIFICATION"
echo "========================================================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backend is running
echo -e "\n${YELLOW}Checking if backend is running...${NC}"
if ! curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo -e "${RED}✗ Backend not running on localhost:5000${NC}"
    echo "  Please start backend with: python3 backend/main.py"
    exit 1
fi
echo -e "${GREEN}✓ Backend is running${NC}"

# Check Python availability
echo -e "\n${YELLOW}Checking Python availability...${NC}"
if ! python3 --version > /dev/null 2>&1; then
    echo -e "${RED}✗ Python3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python3 available$(python3 --version)${NC}"

# Run Test 1: Critical fixes verification
echo -e "\n${YELLOW}Running Test 1: Critical Fixes Verification...${NC}"
echo "-----------------------------------------------------------------"
if python3 backend/scripts/test_cbr_fixes.py; then
    echo -e "${GREEN}✓ Test 1 PASSED${NC}"
else
    echo -e "${RED}✗ Test 1 FAILED${NC}"
    exit 1
fi

# Run Test 2: State correctness verification
echo -e "\n${YELLOW}Running Test 2: State Correctness Verification...${NC}"
echo "-----------------------------------------------------------------"
if python3 backend/scripts/test_state_correctness.py; then
    echo -e "${GREEN}✓ Test 2 PASSED${NC}"
else
    echo -e "${RED}✗ Test 2 FAILED${NC}"
    exit 1
fi

# Final summary
echo -e "\n========================================================================"
echo -e "${GREEN}✓ ALL VERIFICATION TESTS PASSED${NC}"
echo "========================================================================"

echo -e "\nVerification Summary:"
echo -e "  ${GREEN}✓${NC} Progress tracking: CORRECT"
echo -e "  ${GREEN}✓${NC} Engagement display: WORKING"
echo -e "  ${GREEN}✓${NC} Navigation logic: CORRECT"
echo -e "  ${GREEN}✓${NC} Data integrity: VERIFIED"
echo -e "  ${GREEN}✓${NC} Button state control: WORKING"

echo -e "\n${GREEN}System is ready for production use.${NC}"

echo -e "\nNext Steps:"
echo "  1. Monitor system logs for 24 hours"
echo "  2. Test with real student sessions"
echo "  3. Verify engagement updates in real-time"
echo "  4. Check progress tracking accuracy"
echo "  5. Confirm navigation works as expected"

echo -e "\nDocumentation:"
echo "  - FINAL_REPORT.md: Complete analysis"
echo "  - DEPLOYMENT_CHECKLIST.md: Deployment guide"
echo "  - CBT_FIXES_COMPLETE.md: Technical details"

echo "========================================================================"
