# User Guide - Adaptive Tutoring Framework

## Getting Started

### Prerequisites
- Backend running: `cd backend && python main.py` → http://localhost:5000
- Frontend running: `cd frontend && npx http-server -p 8000` → http://localhost:8000

### Accessing the Application
Open your web browser and go to: **http://localhost:8000**

---

## User Flow

### Step 1: Login / Registration Page

**What you see**:
- Title: "Welcome to Adaptive Tutoring"
- Subtitle: "Login with your email to continue. If you're new, just enter your details to create an account."
- Email field
- Name field
- "Login / Register" button
- Navigation (top right): Only shows "Login" link

**What to do**:
1. Enter your email address (e.g., `student@example.com`)
2. Enter your full name (e.g., `John Doe`)
3. Click "Login / Register"

**For New Users**:
- Your account will be created automatically
- You'll see: "Account created successfully! Welcome John Doe!"

**For Returning Users**:
- Enter your original email and name
- You'll see: "Welcome back John Doe!"

---

### Step 2: Subject Selection Page

**What you see**:
- Welcome message: "Welcome back, John Doe"
- Title: "Select Subject to Begin Test"
- 4 subject buttons:
  - 📐 Mathematics
  - 🔬 Science
  - 📚 English
  - 🏛️ History
- Navigation (top right): 
  - Dashboard
  - Start Test
  - Logout
  - 👤 John Doe

**What to do**:
Click any subject button to start a test in that subject.

---

### Step 3: Questions Page

**What you see**:
- **Progress Bar**: Shows how many questions you've completed (0/10, 1/10, etc.)
- **Statistics Cards**:
  - Correct: Number of correct answers
  - Difficulty: Current question difficulty level
  - Level: Subject name
- **Question**: The main question text
- **Answer Options**: 4 buttons labeled A, B, C, D
- **Submit Answer** button
- **(Optional) Get Hint** button (if hints are available)

**What to do**:
1. **Read the question carefully**
2. **Click the answer option** you think is correct (it will highlight in blue)
3. **Click "Submit Answer"** button
4. **See the feedback**:
   - ✓ Correct! (if you got it right)
   - ✗ Incorrect! Answer: A (if you got it wrong, showing the correct answer)
5. **Repeat** for all 10 questions

**Hints**:
- You can click "Get Hint" for additional help
- Some questions may have limited hints available

---

### Step 4: Test Completion Page

**What you see**:
- Alert showing: "Test completed! Correct: X/10"
- Redirected to Dashboard page
- Your statistics are updated

**Dashboard shows**:
- Total Sessions: Number of tests you've completed
- Total Questions: Total questions answered
- Accuracy: Your overall accuracy percentage
- Engagement Score: Your recent engagement rating

---

### Step 5: Navigation Features

**Logged In Users see**:

| Button/Link | Function |
|------------|----------|
| **Dashboard** | View your statistics and performance |
| **Start Test** | Go to subject selection page |
| **Logout** | Sign out of your account |
| **👤 John Doe** | Shows your name (not clickable) |

**Not Logged In Users see**:
| Button/Link | Function |
|------------|----------|
| **Login** | Go to login page |

---

## Features Explained

### Answer Selection
- Click any answer option (A, B, C, or D)
- The selected option will:
  - Turn blue border
  - Have light blue background
- You can change your selection by clicking a different option
- The previous selection will be deselected

### Progress Tracking
- Progress bar at top shows your completion percentage
- Text below shows: "Question 1 of 10", "Question 2 of 10", etc.
- Statistics update in real-time

### Feedback System
After each answer, you see:
- If **correct** ✓: Brief congratulations message
- If **incorrect** ✗: Shows which was the correct answer with explanation

### Session Management
- Each test is a separate session
- You can take multiple tests in different subjects
- All tests are saved to your profile
- Sessions auto-save, so you can take a test later

---

## Tips for Best Experience

1. **Use Your Real Email**: So you can login later with the same credentials
2. **Take Your Time**: There's no time limit per question
3. **Read Carefully**: Understand the question fully before answering
4. **Use Hints**: If unsure, get a hint (when available)
5. **Check Results**: Review your performance on the Dashboard
6. **Track Progress**: Watch your accuracy improve as you take more tests

---

## Troubleshooting

### Can't Login?
- **Problem**: "Failed to login" error
- **Solution**: 
  1. Make sure backend is running (`python main.py`)
  2. Check internet connection
  3. Try refreshing the page

### Subject Buttons Not Working?
- **Problem**: Clicking a subject does nothing
- **Solution**:
  1. Make sure you're logged in (see user name in top right)
  2. Refresh the page
  3. Check browser console (F12) for errors
  4. Make sure backend is running

### Can't See My Progress?
- **Problem**: Progress bar not updating
- **Solution**:
  1. Refresh the page
  2. Check browser cache settings
  3. Make sure JavaScript is enabled

### Can't Logout?
- **Problem**: Logout button not responding
- **Solution**:
  1. Try refreshing the page
  2. Clear browser cache
  3. Try logging in again

---

## Performance Metrics Explained

### Accuracy
Percentage of correct answers out of total questions answered.
- Formula: (Correct Answers / Total Questions) × 100
- Example: 8 correct out of 10 = 80% accuracy

### Difficulty Level
How hard the current/next question is.
- Ranges from 0% (easy) to 100% (hard)
- Difficulty adapts based on your performance
- Better accuracy → Harder questions

### Engagement Score
How engaged you are with the platform.
- Based on:
  - Time spent per question
  - Question completion rate
  - Hint usage
  - Test frequency

### Total Sessions
Total number of test sessions (complete tests) you've taken.

---

## Data Storage

### What We Store
- Your account information (email, name)
- Test sessions and scores
- Question responses
- Performance metrics
- Engagement data

### Privacy
- Data stored locally in database
- Can logout anytime to disconnect
- Data persists across sessions
- Browser local storage used for faster loading

---

## Frequently Asked Questions

**Q: Can I retake a test?**
A: Yes! You can take the same subject test multiple times. Each test is a new session.

**Q: Are my answers saved?**
A: Yes, all answers are saved to your profile and used to calculate your statistics.

**Q: Can I see which questions I got wrong?**
A: Currently, you see if each answer is correct immediately. Your statistics show overall accuracy.

**Q: Do I have a time limit per question?**
A: No, you can take as much time as you need per question.

**Q: Can I pause and resume a test?**
A: Currently, tests must be completed in one session. But you can logout and come back to take another test anytime.

**Q: How does difficulty adapt?**
A: Based on your previous answers. Correct answers trigger slightly harder questions; incorrect answers trigger easier ones.

**Q: Can I see hints before answering?**
A: You get hints by clicking the "Get Hint" button, but you should try answering first to get the most learning value.

**Q: How many hints can I use?**
A: Varies by question. Some may have 0, 1, or more hints available.

---

## Contact & Support

If you encounter any issues:
1. Check the error message carefully
2. Review the Troubleshooting section above
3. Check browser console (F12 → Console) for technical details
4. Make sure both frontend and backend are running
5. Try refreshing the page

---

## Happy Learning! 🎓

The Adaptive Tutoring Framework is designed to help you learn effectively with personalized difficulty adjustment. Good luck with your tests!
