// Main Application JavaScript

console.log('[APP] app.js loaded at', new Date().toISOString());
console.log('[APP] document.readyState:', document.readyState);
console.log('[APP] document.getElementById("root"):', document.getElementById('root'));

const API_BASE_URL = 'http://localhost:5000/api';

// Student and Session Management
let currentStudent = null;
let currentSession = null;

// Response Time Tracking
let questionStartTime = null;

// Per-Question Interaction Tracking
let currentQuestionState = {
    questionId: null,
    questionIndex: 0,
    initialOption: null,
    finalOption: null,
    optionChangeCount: 0,
    navigationCount: 0,
    optionChangeHistory: [],
    interactionStartTime: null,
    questionDisplayTime: null,
    lastActivityTime: null,
    isRevisit: false,
    hesitationFlags: {
        rapidClicking: false,
        longHesitation: false,
        frequentSwitching: false
    },
    // Facial monitoring data per question
    facial_data: {
        camera_enabled: false,
        face_detected_count: 0,
        face_lost_count: 0,
        attention_scores: [],  // Array of attention scores
        emotions_detected: [],  // Array of {emotion, confidence, timestamp}
        face_presence_duration_seconds: 0
    },
    // Hint usage per question
    hints_requested: 0,
    hints_used: []  // Array of {hint_text, timestamp}
};

// Session-level Navigation & History Tracking
let sessionNavigationCount = 0;
let sessionQuestionHistory = []; // Track all questions in session with responses
let currentQuestionIndex = 0; // Track position in current session
let questionResponses = {}; // Map of question_id -> {response, attempts, timestamps}
let inactivityTimer = null;
let lastInteractionTime = null;
let currentInactivityDuration = 0;

// CRITICAL: Prevent modal hijacking after navigation
let lastSubmissionQuestionId = null; // Track which question was just submitted
let navigationIntentActive = false; // Flag when user intentionally navigates (not submission flow)

// ============================================================================
// AUTHORITATIVE TEST STATE - NEVER RESET BY TIMERS OR RENDERS
// ============================================================================

const TEST_STATE = {
    // Immutable during question display
    currentQuestionIndex: 0,        // Current question position in history
    highestAnsweredIndex: -1,        // Highest question that has been answered
    sessionId: null,                 // Current session
    
    // Per-question engagement and time (persists across re-renders)
    timeStartPerQuestion: {},        // { questionId: Date.now() }
    engagementPerQuestion: {},       // { questionId: score }
    
    // Timers (one active at a time)
    activeTimeInterval: null,        // Currently running time timer
    activeInactivityInterval: null,  // Currently running inactivity timer
    
    // Navigation rules (never overridden by render)
    canNavigateNext() {
        // Can only navigate forward if we've answered more questions than current position
        return this.currentQuestionIndex < this.highestAnsweredIndex;
    },
    
    canNavigatePrev() {
        return this.currentQuestionIndex > 0;
    },
    
    isOnCurrentQuestion() {
        return this.currentQuestionIndex === this.highestAnsweredIndex;
    },
    
    // Update authoritative state (called from backend responses only)
    setCurrentQuestionIndex(index) {
        this.currentQuestionIndex = index;
        console.log('[TEST_STATE] Set currentQuestionIndex =', index);
    },
    
    setHighestAnsweredIndex(index) {
        if (index > this.highestAnsweredIndex) {
            this.highestAnsweredIndex = index;
            console.log('[TEST_STATE] Set highestAnsweredIndex =', index);
        }
    },
    
    // Store engagement (never resets)
    setEngagementForQuestion(questionId, score) {
        this.engagementPerQuestion[questionId] = score;
        console.log('[TEST_STATE] Set engagement for Q' + questionId + ' =', score);
    },
    
    getEngagementForQuestion(questionId) {
        return this.engagementPerQuestion[questionId] || 0;
    },
    
    // Timer management
    clearAllTimers() {
        if (this.activeTimeInterval) {
            clearInterval(this.activeTimeInterval);
            this.activeTimeInterval = null;
        }
        if (this.activeInactivityInterval) {
            clearInterval(this.activeInactivityInterval);
            this.activeInactivityInterval = null;
        }
    },
    
    startQuestionTimer(questionId) {
        this.clearAllTimers();
        this.timeStartPerQuestion[questionId] = Date.now();
        console.log('[TEST_STATE] Started timer for Q' + questionId);
    },
    
    getTimeElapsedForQuestion(questionId) {
        const startTime = this.timeStartPerQuestion[questionId];
        if (!startTime) return 0;
        return Math.floor((Date.now() - startTime) / 1000);
    }
};

// Safe initialization function
function safeInitialize() {
    console.log('[APP] safeInitialize() called');
    const root = document.getElementById('root');
    if (!root) {
        console.error('[APP] ERROR: root element not found!');
        return;
    }
    try {
        console.log('[APP] Calling setupUI...');
        setupUI();
        console.log('[APP] setupUI() completed successfully');
    } catch (error) {
        console.error('[APP] Error in setupUI():', error, error.stack);
        // Show error on page
        root.innerHTML = '<div style="color: red; padding: 20px; font-family: monospace; white-space: pre-wrap;">' +
            'ERROR: ' + error.message + '\n\n' + error.stack + '</div>';
    }
}

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    console.log('[APP] DOMContentLoaded fired');
    safeInitialize();
});

// Fallback: if document is already loaded, initialize immediately
if (document.readyState === 'loading') {
    console.log('[APP] Document is still loading, waiting for DOMContentLoaded');
} else {
    console.log('[APP] Document already loaded, initializing immediately');
    safeInitialize();
}

// Triple safety: try after a tiny delay
setTimeout(() => {
    if (!document.getElementById('content')?.innerHTML) {
        console.log('[APP] Content still empty after DOMContentLoaded, retrying...');
        safeInitialize();
    }
}, 100);

function setupUI() {
    const root = document.getElementById('root');
    root.innerHTML = `
        <div class="container">
            <header style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; border-radius: 0; margin: 0 0 30px 0; box-shadow: 0 4px 20px rgba(102, 126, 234, 0.2);">
                <h1 style="margin: 0 0 10px 0; font-size: 32px;">🎓 Adaptive Intelligent Tutoring</h1>
                <p style="margin: 0; opacity: 0.95; font-size: 16px; font-weight: 300;">Personalized learning with real-time engagement tracking</p>
            </header>
            
            <nav id="navbar" style="display: flex; gap: 15px; justify-content: center; padding: 20px; background: white; border-bottom: 1px solid #e0e0e0; align-items: center; margin: 0 0 30px 0;">
                <div id="nav-links" style="display: flex; gap: 12px; align-items: center;"></div>
                <div id="user-info" style="margin-left: auto;"></div>
            </nav>
            
            <div id="content"></div>
        </div>
    `;
    
    // Load stored student data
    const student = localStorage.getItem('student');
    if (student) {
        try {
            currentStudent = JSON.parse(student);
            console.log('Loaded student from storage:', currentStudent);
        } catch (e) {
            console.error('Error parsing student data:', e);
            localStorage.removeItem('student');
            currentStudent = null;
        }
    }
    
    const session = localStorage.getItem('session');
    if (session) {
        try {
            currentSession = JSON.parse(session);
            console.log('Loaded session from storage:', currentSession);
        } catch (e) {
            console.error('Error parsing session data:', e);
            localStorage.removeItem('session');
            currentSession = null;
        }
    }
    
    updateNavigation();
    
    // Show appropriate page based on login status
    if (currentStudent && currentStudent.id) {
        console.log('User logged in, showing test page');
        showTestPage();
    } else {
        console.log('User not logged in, showing login page');
        showLoginPage();
    }
}

function updateNavigation() {
    const navLinks = document.getElementById('nav-links');
    const userInfo = document.getElementById('user-info');
    
    navLinks.innerHTML = '';
    userInfo.innerHTML = '';
    
    if (!currentStudent) {
        // Not logged in - only show login
        navLinks.innerHTML = `
            <a href="#" onclick="showLoginPage()" style="padding: 10px 20px; cursor: pointer; text-decoration: none; color: white; border-radius: 6px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); font-weight: 600; transition: all 0.2s;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 8px 20px rgba(102, 126, 234, 0.3)'" onmouseout="this.style.transform='none'; this.style.boxShadow='none';">Login</a>
        `;
    } else {
        // Logged in - check if session is active
        const sessionActive = currentSession && currentSession.id && currentSession.status === 'active';
        
        // Disable Dashboard and Start Test if session is active
        const dashboardDisabled = sessionActive ? 'disabled' : '';
        const testPageDisabled = sessionActive ? 'disabled' : '';
        const dashboardStyle = sessionActive ? 'color: #ccc; opacity: 0.5; cursor: not-allowed;' : 'color: #667eea;';
        const testPageStyle = sessionActive ? 'color: #ccc; opacity: 0.5; cursor: not-allowed;' : 'color: #667eea;';
        
        // Show dashboard, start test, and logout
        navLinks.innerHTML = `
            <a href="#" onclick="${sessionActive ? 'return false;' : 'showDashboard();'}" style="padding: 10px 20px; cursor: pointer; text-decoration: none; ${dashboardStyle} font-weight: 600; border-radius: 6px; transition: all 0.2s;" ${sessionActive ? '' : 'onmouseover="this.style.background=\'#f0f5ff\'" onmouseout="this.style.background=\'transparent\'"'}>Dashboard</a>
            <a href="#" onclick="${sessionActive ? 'return false;' : 'showTestPage();'}" style="padding: 10px 20px; cursor: pointer; text-decoration: none; ${testPageStyle} font-weight: 600; border-radius: 6px; transition: all 0.2s;" ${sessionActive ? '' : 'onmouseover="this.style.background=\'#f0f5ff\'" onmouseout="this.style.background=\'transparent\'"'}>Start Test</a>
            <a href="#" onclick="logout()" style="padding: 10px 20px; cursor: pointer; text-decoration: none; color: white; font-weight: 600; border-radius: 6px; background: #ff6b6b; transition: all 0.2s;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 8px 20px rgba(255, 107, 107, 0.3)'" onmouseout="this.style.transform='none'; this.style.boxShadow='none';">Logout</a>
        `;
        userInfo.innerHTML = `<span style="color: #333; font-weight: 600;">👤 ${currentStudent.name}</span>`;
    }
}

async function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('email').value;
    const name = document.getElementById('name').value;
    
    if (!email || !name) {
        alert('Please enter both email and name');
        return;
    }
    
    await loginOrRegisterStudent(email, name);
}

async function loginOrRegisterStudent(email, name) {
    try {
        console.log('Attempting login/register for:', email);
        
        const response = await fetch(`${API_BASE_URL}/cbt/student`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, name })
        });
        
        const data = await response.json();
        console.log('Login response:', data, 'Status:', response.status);
        
        if (data.success && data.student) {
            // Student logged in or registered successfully
            currentStudent = data.student;
            console.log('Student logged in:', currentStudent);
            localStorage.setItem('student', JSON.stringify(currentStudent));
            localStorage.removeItem('session'); // Clear any old session
            currentSession = null;
            
            updateNavigation();
            
            // Show appropriate message
            if (response.status === 201) {
                alert('Account created successfully! Welcome ' + currentStudent.name + '!');
            } else {
                alert('Welcome back ' + currentStudent.name + '!');
            }
            
            showTestPage();
        } else if (response.status === 403) {
            // Email exists but name doesn't match
            alert('Error: ' + data.error);
            // Clear the form for retry
            document.getElementById('email').value = '';
            document.getElementById('name').value = '';
        } else {
            alert('Error: ' + (data.error || 'Login failed'));
        }
    } catch (error) {
        console.error('Error during login:', error);
        alert('Failed to login: ' + error.message);
    }
}

async function startSession(subject) {
    // Validate that we have a current student
    if (!currentStudent || !currentStudent.id) {
        alert('Please login first before starting a test');
        showLoginPage();
        return;
    }

    try {
        console.log('Starting session for student:', currentStudent.id, 'subject:', subject);
        
        const response = await fetch(`${API_BASE_URL}/cbt/session/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                student_id: currentStudent.id,
                subject: subject,
                num_questions: 10
            })
        });
        
        const data = await response.json();
        console.log('Session response:', data);
        
        if (data.success) {
            // Backend returns: { success: true, session: { session_id, subject, ... } }
            const sessionData = data.session || {};
            const sessionId = sessionData.session_id; // Note: it's session_id, not id
            
            if (!sessionId) {
                console.error('Session response:', data);
                throw new Error('No session ID received from server');
            }
            
            currentSession = {
                id: sessionId,
                student_id: sessionData.student_id || currentStudent.id,
                subject: sessionData.subject,
                num_questions: sessionData.total_questions || 10,
                current_difficulty: sessionData.current_difficulty || 0.5,
                status: sessionData.status || 'active',
                questions_completed: 0,
                correct_answers: 0
            };
            
            console.log('Current session set to:', currentSession);
            localStorage.setItem('session', JSON.stringify(currentSession));
            
            // CRITICAL FIX: Update navigation to disable Dashboard/Start buttons
            updateNavigation();
            
            // CRITICAL FIX: Clear all session state for new test
            sessionQuestionHistory = [];
            currentQuestionIndex = 0;
            sessionNavigationCount = 0;
            questionResponses = {};
            console.log('[SESSION] Reset for new test: history cleared, index=0, navCount=0');
            
            // Add a small delay to ensure state is ready
            setTimeout(() => showQuestion(), 100);
        } else {
            alert('Error: ' + (data.error || 'Failed to start session'));
        }
    } catch (error) {
        console.error('Error starting session:', error);
        alert('Failed to start session: ' + error.message);
    }
}

function logout() {
    currentStudent = null;
    currentSession = null;
    localStorage.removeItem('student');
    localStorage.removeItem('session');
    updateNavigation();
    showLoginPage();
}

async function submitAnswer(questionId, answer, responseTime) {
    try {
        // CRITICAL: Mark this submission to prevent modal hijacking after navigation
        lastSubmissionQuestionId = questionId;
        navigationIntentActive = false;  // Reset flag - this is a submission
        
        // Stop inactivity tracking
        if (inactivityTimer) clearInterval(inactivityTimer);
        
        // Calculate time spent on this question
        const timeSpent = currentQuestionState.questionDisplayTime ? 
            Math.round((Date.now() - currentQuestionState.questionDisplayTime) / 1000) : 
            responseTime;
        
        // Build complete submission payload with all tracked behavioral and cognitive data
        const submissionPayload = {
            session_id: currentSession.id,
            question_id: questionId,
            student_answer: answer,
            response_time_seconds: responseTime,
            
            // Behavioral: Option Changes
            initial_option: currentQuestionState.initialOption,
            final_option: currentQuestionState.finalOption,
            option_change_count: currentQuestionState.optionChangeCount,
            option_change_history: currentQuestionState.optionChangeHistory,
            
            // Behavioral: Navigation
            navigation_frequency: currentQuestionState.navigationCount,
            question_index: currentQuestionState.questionIndex,
            
            // Cognitive: Time & Activity
            time_spent_per_question: timeSpent,
            inactivity_duration_ms: currentInactivityDuration,
            
            // Cognitive: Behavioral Patterns
            hesitation_flags: currentQuestionState.hesitationFlags,
            navigation_pattern: 'sequential', // Can be revisit, skip, backtrack
            
            // Facial Monitoring Data
            facial_metrics: {
                camera_enabled: currentQuestionState.facial_data.camera_enabled || facialMonitoringEnabled || false,
                face_detected_count: currentQuestionState.facial_data.face_detected_count || 0,
                face_lost_count: currentQuestionState.facial_data.face_lost_count || 0,
                attention_score: currentQuestionState.facial_data.attention_scores.length > 0 
                    ? (currentQuestionState.facial_data.attention_scores.reduce((a, b) => a + b, 0) / currentQuestionState.facial_data.attention_scores.length)
                    : null,
                emotions_detected: currentQuestionState.facial_data.emotions_detected || [],
                face_presence_duration_seconds: currentQuestionState.facial_data.face_presence_duration_seconds || 0
            },
            
            // Hint Usage Data
            hints_requested: currentQuestionState.hints_requested || 0,
            hints_used: currentQuestionState.hints_used || [],
            
            // Timestamps
            interaction_start_timestamp: currentQuestionState.interactionStartTime,
            submission_timestamp: Date.now(),
            submission_iso_timestamp: new Date().toISOString()
        };
        
        console.log('[SUBMISSION] Complete interaction payload:', submissionPayload);
        
        const response = await fetch(`${API_BASE_URL}/cbt/response/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(submissionPayload)
        });
        
        const data = await response.json();
        console.log('[SUBMISSION] Response:', data);
        
        if (data.success) {
            // Track this response
            questionResponses[questionId] = {
                correct: data.is_correct,
                response: answer,
                timestamp: Date.now()
            };
            
            // Update session with response data
            if (data.session) {
                currentSession = data.session;
                localStorage.setItem('session', JSON.stringify(currentSession));
            } else {
                // Use unique_answered from backend for progress tracking
                // This ensures progress only counts unique answered questions, not revisits
                if (data.unique_answered !== undefined) {
                    currentSession.questions_completed = data.unique_answered;
                } else {
                    // Fallback for backward compatibility
                    currentSession.questions_completed = (currentSession.questions_completed || 0) + 1;
                }
                if (data.is_correct) {
                    currentSession.correct_answers = (currentSession.correct_answers || 0) + 1;
                }
                if (data.current_difficulty !== undefined && data.current_difficulty !== null) {
                    currentSession.current_difficulty = data.current_difficulty;
                    localStorage.setItem('session', JSON.stringify(currentSession));
                }
            }
            
            // Show detailed feedback with adaptation info
            const correctAnswer = data.correct_answer || 'Unknown';
            const explanation = data.explanation || '';
            const oldDifficulty = currentSession.current_difficulty || 0.5;
            const newDifficulty = data.current_difficulty || oldDifficulty;
            const difficultyDelta = (newDifficulty - oldDifficulty).toFixed(2);
            const difficultyChange = difficultyDelta > 0 ? '📈 Increased' : difficultyDelta < 0 ? '📉 Decreased' : '→ No change';
            
            // Show detailed feedback with adaptation info and engagement
            showFeedbackModal(
                data.is_correct,
                correctAnswer,
                explanation,
                newDifficulty,
                difficultyChange,
                difficultyDelta,
                data,
                currentSession
            );
            
            // Track engagement - pass backend engagement score
            await trackEngagement(data);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error submitting answer:', error);
        alert('Failed to submit answer: ' + error.message);
    }
}

async function trackEngagement(responseData) {
    try {
        // CRITICAL FIX: Store engagement in TEST_STATE (persists across re-renders)
        if (responseData.engagement_score !== undefined) {
            const score = responseData.engagement_score || 0;
            const questionId = currentQuestionState.questionId;
            
            // Store in authoritative TEST_STATE
            TEST_STATE.setEngagementForQuestion(questionId, score);
            
            // Also update DOM immediately
            const engagementScore = document.getElementById('engagement-score');
            if (engagementScore) {
                engagementScore.textContent = (score * 100).toFixed(0) + '%';
                console.log('[ENGAGEMENT] Stored in TEST_STATE for Q' + questionId + ':', score);
            }
        }
        
        // Also send tracking data for analytics
        await fetch(`${API_BASE_URL}/engagement/track`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                student_id: currentStudent.id,
                session_id: currentSession.id,
                response_data: responseData
            })
        });
    } catch (error) {
        console.error('Error tracking engagement:', error);
    }
}

async function fetchAndDisplayEngagementScore() {
    try {
        const response = await fetch(`${API_BASE_URL}/engagement/get/${currentSession.id}`);
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.engagement_metrics) {
                const engagementScore = document.getElementById('engagement-score');
                if (engagementScore) {
                    const score = data.engagement_metrics.overall_engagement_score || 0;
                    engagementScore.textContent = (score * 100).toFixed(0) + '%';
                }
            }
        }
    } catch (error) {
        console.error('Error fetching engagement score:', error);
    }
}

function showFeedbackModal(isCorrect, correctAnswer, explanation, newDifficulty, difficultyChange, difficultyDelta, fullData, session) {
    // Create modal overlay - CAPTURE ALL KEYBOARD EVENTS
    const modal = document.createElement('div');
    const modalId = 'feedbackModal_' + Date.now();
    modal.id = modalId;
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.6);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        animation: fadeIn 0.2s ease-in;
    `;
    
    // Set focus to modal to capture keyboard events
    modal.tabIndex = 0;
    
    // Prevent all keyboard events from bubbling to background
    modal.addEventListener('keydown', (e) => {
        e.stopPropagation();
        e.preventDefault();
        
        // Only allow Enter, Escape, and Space to close/continue
        if (e.key === 'Enter' || e.key === 'Escape' || e.key === ' ') {
            handleContinue();
        }
    }, true);
    
    modal.addEventListener('keyup', (e) => {
        e.stopPropagation();
        e.preventDefault();
    }, true);
    
    modal.addEventListener('keypress', (e) => {
        e.stopPropagation();
        e.preventDefault();
    }, true);
    
    const statusColor = isCorrect ? '#48bb78' : '#f56565';
    const statusBg = isCorrect ? '#f0fff4' : '#fff5f5';
    const statusEmoji = isCorrect ? '✓' : '✗';
    
    const diffColor = difficultyDelta > 0 ? '#ed8936' : difficultyDelta < 0 ? '#4299e1' : '#718096';
    
    modal.innerHTML = `
        <div style="background: white; border-radius: 16px; padding: 40px; max-width: 600px; width: 90%; box-shadow: 0 20px 60px rgba(0,0,0,0.3); animation: slideUp 0.3s ease; position: relative;">
            <button id="closeModalBtn" style="position: absolute; top: 16px; right: 16px; background: #e0e0e0; border: none; border-radius: 50%; width: 32px; height: 32px; font-size: 18px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s;" onmouseover="this.style.background='#d0d0d0'" onmouseout="this.style.background='#e0e0e0';">×</button>
            
            <div style="text-align: center; margin-bottom: 30px;">
                <div style="display: inline-block; background: ${statusBg}; width: 80px; height: 80px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-bottom: 20px;">
                    <span style="font-size: 40px; color: ${statusColor};">${statusEmoji}</span>
                </div>
                <h2 style="margin: 0 0 10px 0; color: ${statusColor}; font-size: 28px;">${isCorrect ? 'Correct!' : 'Incorrect'}</h2>
                <p style="color: #999; margin: 0; font-size: 16px;">${isCorrect ? 'Great work!' : 'Keep practicing!'}</p>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                <div style="color: #666; font-size: 13px; font-weight: 600; text-transform: uppercase; margin-bottom: 10px;">Answer</div>
                <div style="color: #333; font-size: 16px; font-weight: 500; margin-bottom: 15px;">
                    ${isCorrect ? '✓ Your answer was correct' : '✗ Correct answer: <strong>' + correctAnswer + '</strong>'}
                </div>
                ${explanation ? `
                    <div style="color: #666; font-size: 14px; line-height: 1.6; padding-top: 15px; border-top: 1px solid #e2e8f0;">
                        <strong>Explanation:</strong><br>${explanation}
                    </div>
                ` : ''}
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 25px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 16px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 11px; opacity: 0.9; margin-bottom: 6px; text-transform: uppercase;">Difficulty</div>
                    <div style="font-size: 24px; font-weight: bold;">${(newDifficulty * 100).toFixed(0)}%</div>
                    <div style="font-size: 12px; opacity: 0.85; margin-top: 6px;">
                        <span style="color: ${diffColor};">${difficultyChange}</span>
                        <span style="opacity: 0.7;"> ${difficultyDelta >= 0 ? '+' : ''}${(difficultyDelta * 100).toFixed(0)}%</span>
                    </div>
                </div>
                <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 16px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 11px; opacity: 0.9; margin-bottom: 6px; text-transform: uppercase;">Score</div>
                    <div style="font-size: 24px; font-weight: bold;">${(fullData.current_score || 0).toFixed(0)}%</div>
                    <div style="font-size: 12px; opacity: 0.85; margin-top: 6px;">
                        ${(fullData.correct_count || 0)} of ${(fullData.total_answered || 0)} correct
                    </div>
                </div>
            </div>
            
            <div style="background: #fffff0; border-left: 4px solid #f6ad55; padding: 16px; border-radius: 6px; margin-bottom: 25px;">
                <div style="color: #975a16; font-size: 13px; font-weight: 600; margin-bottom: 6px;">💡 Adaptive Feedback</div>
                <div style="color: #744210; font-size: 14px;">
                    ${isCorrect ? 'Your performance is strong! Difficulty increased slightly to challenge you further.' : 'Difficulty will adjust to help you learn more effectively.'}
                </div>
            </div>
            
            <div style="text-align: center;">
                <button id="continueBtn_${modalId}" style="padding: 12px 30px; font-size: 14px; font-weight: 600; cursor: pointer; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; transition: all 0.2s;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 8px 20px rgba(102, 126, 234, 0.4)'" onmouseout="this.style.transform='none'; this.style.boxShadow='none';">Continue to Next Question →</button>
            </div>
        </div>
        <style>
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            @keyframes slideUp {
                from {
                    opacity: 0;
                    transform: translateY(20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        </style>
    `;
    
    document.body.appendChild(modal);
    
    // Set focus to modal to capture all keyboard events
    modal.focus();
    
    // Disable pointer events on background content while modal is open
    const content = document.getElementById('content');
    const originalPointerEvents = content.style.pointerEvents;
    content.style.pointerEvents = 'none';
    
    // Handle close button
    const closeBtn = document.getElementById('closeModalBtn');
    const continueBtn = document.getElementById('continueBtn_' + modalId);
    
    const closeModal = () => {
        if (modal && modal.parentNode) {
            modal.remove();
            // Restore pointer events to background
            content.style.pointerEvents = originalPointerEvents;
        }
    };
    
    const handleContinue = async () => {
        closeModal();
        
        // CRITICAL FIX: Only auto-navigate if submission is current action, not if user navigated
        if (navigationIntentActive) {
            console.log('[MODAL] User manually navigated away, skipping modal auto-navigation');
            return;
        }
        
        // After submission, proceed based on session state
        // CRITICAL FIX: Use currentSession not session (which is undefined)
        if (!currentSession) {
            console.error('[MODAL] No current session, returning to test page');
            showTestPage();
            return;
        }
        
        // Check if test is complete (all questions answered)
        const testComplete = currentSession.questions_completed >= currentSession.num_questions;
        
        await new Promise(resolve => setTimeout(resolve, 300));
        
        if (testComplete) {
            // All questions answered - show dashboard
            console.log('[MODAL] Test complete, showing dashboard');
            showDashboard();
        } else {
            // More questions to answer - load next NEW question (forward progression only)
            console.log('[MODAL] More questions remain, loading next NEW question');
            await fetchNextNewQuestion();
        }
    };
    
    if (closeBtn) {
        closeBtn.onclick = (e) => {
            e.stopPropagation();
            handleContinue();
        };
    }
    
    if (continueBtn) {
        continueBtn.onclick = (e) => {
            e.stopPropagation();
            handleContinue();
        };
    }
    
    // Auto-close after 12 seconds if user hasn't dismissed (extended from 3s)
    const autoCloseTimeout = setTimeout(handleContinue, 12000);
}

// UI Display Functions
function showLoginPage() {
    const content = document.getElementById('content');
    content.innerHTML = `
        <div style="max-width: 450px; margin: 80px auto; background: white; padding: 50px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
            <div style="text-align: center; margin-bottom: 40px;">
                <h2 style="color: #667eea; margin: 0 0 10px 0; font-size: 28px;">Welcome</h2>
                <p style="color: #999; margin: 0; font-size: 14px;">Sign in to your account or create a new one</p>
            </div>
            
            <form onsubmit="handleLogin(event)" style="display: flex; flex-direction: column; gap: 20px;">
                <div>
                    <label style="display: block; margin-bottom: 8px; font-weight: 500; color: #333; font-size: 14px;">Email Address</label>
                    <input type="email" id="email" required placeholder="your@email.com" style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 16px; box-sizing: border-box; transition: border-color 0.2s;" onfocus="this.style.borderColor='#667eea'" onblur="this.style.borderColor='#ddd'">
                </div>
                
                <div>
                    <label style="display: block; margin-bottom: 8px; font-weight: 500; color: #333; font-size: 14px;">Full Name</label>
                    <input type="text" id="name" required placeholder="John Doe" style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 16px; box-sizing: border-box; transition: border-color 0.2s;" onfocus="this.style.borderColor='#667eea'" onblur="this.style.borderColor='#ddd'">
                    <small style="color: #999; font-size: 12px; margin-top: 5px; display: block;">Make sure this matches your registered name</small>
                </div>
                
                <button type="submit" style="padding: 14px; background: #667eea; color: white; border: none; border-radius: 6px; font-size: 16px; font-weight: 600; cursor: pointer; margin-top: 10px; transition: background 0.2s;" onmouseover="this.style.background='#5568d3'" onmouseout="this.style.background='#667eea';">Sign In / Register</button>
            </form>
            
            <div style="margin-top: 30px; padding-top: 30px; border-top: 1px solid #eee; text-align: center;">
                <p style="color: #999; font-size: 13px; margin: 0;">
                    <strong>First time?</strong> Enter your details to create an account.<br>
                    <strong>Returning?</strong> Use your original email and name to login.
                </p>
            </div>
        </div>
    `;
}

function showTestPage() {
    if (!currentStudent || !currentStudent.id) {
        showLoginPage();
        return;
    }

    const content = document.getElementById('content');
    content.innerHTML = `
        <div style="max-width: 700px; margin: 40px auto; background: white; padding: 50px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
            <div style="margin-bottom: 40px; text-align: center;">
                <p style="color: #999; font-size: 14px; margin: 0 0 10px 0;">Ready to learn?</p>
                <h2 style="color: #333; margin: 0; font-size: 32px;">Hi, ${currentStudent.name}</h2>
                <p style="color: #999; font-size: 14px; margin: 10px 0 0 0;">Choose a subject to get started</p>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 40px;">
                <button type="button" onclick="startSession('Mathematics')" style="padding: 25px; font-size: 18px; cursor: pointer; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; font-weight: 600; transition: transform 0.2s, box-shadow 0.2s;" onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 8px 20px rgba(102, 126, 234, 0.3)'" onmouseout="this.style.transform='none'; this.style.boxShadow='none';">
                    📐<br>Mathematics
                </button>
                <button type="button" onclick="startSession('Science')" style="padding: 25px; font-size: 18px; cursor: pointer; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; border: none; border-radius: 8px; font-weight: 600; transition: transform 0.2s, box-shadow 0.2s;" onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 8px 20px rgba(245, 87, 108, 0.3)'" onmouseout="this.style.transform='none'; this.style.boxShadow='none';">
                    🔬<br>Science
                </button>
                <button type="button" onclick="startSession('English')" style="padding: 25px; font-size: 18px; cursor: pointer; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; border: none; border-radius: 8px; font-weight: 600; transition: transform 0.2s, box-shadow 0.2s;" onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 8px 20px rgba(79, 172, 254, 0.3)'" onmouseout="this.style.transform='none'; this.style.boxShadow='none';">
                    📚<br>English
                </button>
                <button type="button" onclick="startSession('History')" style="padding: 25px; font-size: 18px; cursor: pointer; background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: white; border: none; border-radius: 8px; font-weight: 600; transition: transform 0.2s, box-shadow 0.2s;" onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 8px 20px rgba(250, 112, 154, 0.3)'" onmouseout="this.style.transform='none'; this.style.boxShadow='none';">
                    🏛️<br>History
                </button>
            </div>
            
            <div style="background: #f8f9ff; border-left: 4px solid #667eea; padding: 20px; border-radius: 6px; text-align: center;">
                <p style="color: #666; margin: 0; font-size: 14px;">
                    💡 Each test contains 10 questions.<br>Difficulty adapts based on your performance!
                </p>
            </div>
        </div>
    `;
}

// CRITICAL FIX: Isolated function for fetching NEXT NEW question (forward progression only)
// This is separate from showQuestion() which handles revisitation
// Called ONLY by modal after successful submission
async function fetchNextNewQuestion() {
    if (!currentSession || !currentSession.id) {
        console.error('[FETCH-NEXT] No active session');
        showTestPage();
        return;
    }

    try {
        console.log('[FETCH-NEXT] Fetching next NEW question for session:', currentSession.id);
        const response = await fetch(
            `${API_BASE_URL}/cbt/question/next/${currentSession.id}`
        );
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('[FETCH-NEXT] Question response:', data);
        
        // Check if test is completed
        if (data.status === 'completed') {
            // Mark session as completed
            if (currentSession) {
                currentSession.status = 'completed';
                localStorage.setItem('session', JSON.stringify(currentSession));
                updateNavigation();  // Re-enable Dashboard and Start Test buttons
            }
            console.log('[FETCH-NEXT] Test is complete');
            showDashboard();
            return;
        }
        
        if (data.success && data.question) {
            const question = data.question;
            
            // Initialize fresh state for new question
            currentQuestionState = {
                questionId: question.question_id,
                questionIndex: sessionQuestionHistory.length,
                initialOption: null,
                finalOption: null,
                optionChangeCount: 0,
                navigationCount: 0,  // FIXED: Each question starts with 0 navigation count
                optionChangeHistory: [],
                interactionStartTime: Date.now(),
                questionDisplayTime: Date.now(),
                lastActivityTime: Date.now(),
                isRevisit: false,
                hesitationFlags: {
                    rapidClicking: false,
                    longHesitation: false,
                    frequentSwitching: false
                },
                facial_data: {
                    camera_enabled: facialMonitoringEnabled || false,
                    face_detected_count: 0,
                    face_lost_count: 0,
                    attention_scores: [],
                    emotions_detected: [],
                    face_presence_duration_seconds: 0
                },
                hints_requested: 0,
                hints_used: []
            };
            
            // Add to session history
            sessionQuestionHistory.push({
                questionId: question.question_id,
                questionIndex: currentQuestionState.questionIndex,
                question: question,
                completed: false
            });
            currentQuestionIndex = sessionQuestionHistory.length - 1;
            
            // CRITICAL: Sync TEST_STATE with new question
            TEST_STATE.setCurrentQuestionIndex(currentQuestionIndex);
            TEST_STATE.setHighestAnsweredIndex(currentQuestionIndex);
            
            // Capture the time when question is rendered
            questionStartTime = Date.now();
            console.log('[FETCH-NEXT] Question rendered at:', new Date(questionStartTime).toISOString());
            console.log('[FETCH-NEXT] Initialized question state:', currentQuestionState);
            console.log('[FETCH-NEXT] Question index:', currentQuestionIndex, 'History length:', sessionQuestionHistory.length);
            console.log('[FETCH-NEXT] TEST_STATE synced: currentIndex=' + currentQuestionIndex + ', highestIndex=' + TEST_STATE.highestAnsweredIndex);
            
            // Render the question
            renderQuestionWithNav(question, currentQuestionIndex, false);
            startInactivityTracking();
            await fetchAndDisplayEngagementScore();
        } else {
            throw new Error(data.error || 'Failed to load question');
        }
    } catch (error) {
        console.error('[FETCH-NEXT] Error fetching question:', error);
        alert('Failed to load question: ' + error.message);
    }
}

async function showQuestion(revisitIndex = null, isRevisit = false) {
    if (!currentSession || !currentSession.id) {
        console.error('No active session. Session:', currentSession);
        alert('No active session. Please start a test first.');
        showTestPage();
        return;
    }

    // If revisiting a question, use the question from history
    if (isRevisit && revisitIndex !== null && sessionQuestionHistory[revisitIndex]) {
        const historyItem = sessionQuestionHistory[revisitIndex];
        const question = historyItem.question;
        
        // Sync TEST_STATE with revisit
        TEST_STATE.setCurrentQuestionIndex(revisitIndex);
        currentQuestionIndex = revisitIndex;
        
        currentQuestionState = {
            questionId: question.question_id,
            questionIndex: revisitIndex,
            initialOption: null,
            finalOption: null,
            optionChangeCount: 0,
            navigationCount: 0,  // FIXED: Each question starts with 0 navigation count
            optionChangeHistory: [],
            interactionStartTime: Date.now(),
            questionDisplayTime: Date.now(),
            lastActivityTime: Date.now(),
            isRevisit: true,
            hesitationFlags: {
                rapidClicking: false,
                longHesitation: false,
                frequentSwitching: false
            },
            facial_data: {
                camera_enabled: facialMonitoringEnabled || false,
                face_detected_count: 0,
                face_lost_count: 0,
                attention_scores: [],
                emotions_detected: [],
                face_presence_duration_seconds: 0
            },
            hints_requested: 0,
            hints_used: []
        };
        
        questionStartTime = Date.now();
        console.log('[TRACKING] Revisiting question:', {index: revisitIndex, questionId: question.question_id});
        console.log('[TEST_STATE] Synced to revisit index:', revisitIndex);
        
        renderQuestionWithNav(question, revisitIndex, true);
        startInactivityTracking();
        return;
    }

    try {
        console.log('Fetching question for session:', currentSession.id);
        const response = await fetch(
            `${API_BASE_URL}/cbt/question/next/${currentSession.id}`
        );
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Question response:', data);
        
        // Check if test is completed
        if (data.status === 'completed') {
            // Mark session as completed
            if (currentSession) {
                currentSession.status = 'completed';
                localStorage.setItem('session', JSON.stringify(currentSession));
                updateNavigation();  // Re-enable Dashboard and Start Test buttons
            }
            
            const content = document.getElementById('content');
            const scorePercent = data.final_score ? Math.round(data.final_score) : 0;
            const performanceLevel = scorePercent >= 80 ? 'Excellent!' : scorePercent >= 60 ? 'Good!' : 'Keep practicing!';
            
            content.innerHTML = `
                <div style="max-width: 800px; margin: 0 auto; padding: 30px 20px; text-align: center;">
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 50px 30px; border-radius: 12px; color: white; margin-bottom: 30px;">
                        <h1 style="margin: 0 0 20px 0; font-size: 48px; font-weight: bold;">🎉 Test Complete!</h1>
                        <p style="margin: 0; font-size: 20px; opacity: 0.95;">${data.message || 'You have completed all questions.'}</p>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 30px;">
                        <div style="background: #f0f5ff; padding: 25px; border-radius: 8px; border-left: 4px solid #667eea;">
                            <div style="color: #999; font-size: 13px; margin-bottom: 8px; text-transform: uppercase;">Final Score</div>
                            <div style="font-size: 36px; font-weight: bold; color: #667eea;">${scorePercent}%</div>
                        </div>
                        <div style="background: #f0fff4; padding: 25px; border-radius: 8px; border-left: 4px solid #48bb78;">
                            <div style="color: #999; font-size: 13px; margin-bottom: 8px; text-transform: uppercase;">Correct Answers</div>
                            <div style="font-size: 36px; font-weight: bold; color: #48bb78;">${data.correct_answers}/${data.total_questions}</div>
                        </div>
                        <div style="background: #fffff0; padding: 25px; border-radius: 8px; border-left: 4px solid #f6ad55;">
                            <div style="color: #999; font-size: 13px; margin-bottom: 8px; text-transform: uppercase;">Performance</div>
                            <div style="font-size: 28px; font-weight: bold; color: #f6ad55;">${performanceLevel}</div>
                        </div>
                    </div>
                    
                    <div style="background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 15px rgba(0,0,0,0.1); margin-bottom: 30px;">
                        <p style="color: #666; font-size: 16px; line-height: 1.6; margin: 0;">
                            Thank you for taking the test! Your responses have been saved and will help us personalize your learning experience.
                        </p>
                    </div>
                    
                    <div style="display: flex; gap: 15px; justify-content: center;">
                        <button onclick="showDashboard()" style="padding: 14px 30px; font-size: 16px; font-weight: 600; cursor: pointer; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; transition: all 0.2s;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 8px 20px rgba(102, 126, 234, 0.3)'" onmouseout="this.style.transform='none'; this.style.boxShadow='none';">📊 View Dashboard</button>
                        <button onclick="showTestPage()" style="padding: 14px 30px; font-size: 16px; font-weight: 600; cursor: pointer; background: white; border: 2px solid #667eea; color: #667eea; border-radius: 8px; transition: all 0.2s;" onmouseover="this.style.background='#f0f5ff'" onmouseout="this.style.background='white';">🔄 Start New Test</button>
                    </div>
                </div>
            `;
            return;
        }
        
        if (data.success) {
            const question = data.question;
            
            // Validate question object
            if (!question || !question.question_id) {
                console.error('Invalid question object received:', question);
                console.log('Full response:', data);
                alert('Error: Invalid question data received. Refreshing...');
                showQuestion();  // Retry
                return;
            }
            
            // Initialize per-question state tracking
            currentQuestionState = {
                questionId: question.question_id,
                questionIndex: currentSession.questions_completed || 0,
                initialOption: null,
                finalOption: null,
                optionChangeCount: 0,
                navigationCount: 0,  // FIXED: Each question starts with 0 navigation count
                optionChangeHistory: [],
                interactionStartTime: Date.now(),
                questionDisplayTime: Date.now(),
                lastActivityTime: Date.now(),
                isRevisit: false,
                hesitationFlags: {
                    rapidClicking: false,
                    longHesitation: false,
                    frequentSwitching: false
                },
                facial_data: {
                    camera_enabled: facialMonitoringEnabled || false,
                    face_detected_count: 0,
                    face_lost_count: 0,
                    attention_scores: [],
                    emotions_detected: [],
                    face_presence_duration_seconds: 0
                },
                hints_requested: 0,
                hints_used: []
            };
            
            // Add to session history
            sessionQuestionHistory.push({
                questionId: question.question_id,
                questionIndex: currentQuestionState.questionIndex,
                question: question,
                completed: false
            });
            currentQuestionIndex = sessionQuestionHistory.length - 1;
            
            // CRITICAL: Sync TEST_STATE with new question
            TEST_STATE.setCurrentQuestionIndex(currentQuestionIndex);
            TEST_STATE.setHighestAnsweredIndex(currentQuestionIndex);  // Track progress
            
            // Capture the time when question is rendered
            questionStartTime = Date.now();
            console.log('Question rendered at:', new Date(questionStartTime).toISOString());
            console.log('[TRACKING] Initialized question state:', currentQuestionState);
            console.log('[TRACKING] Question index:', currentQuestionIndex, 'History length:', sessionQuestionHistory.length);
            console.log('[TEST_STATE] Synced to new question index:', currentQuestionIndex, 'highestAnsweredIndex:', TEST_STATE.highestAnsweredIndex);
            
            // Use renderQuestionWithNav to display with navigation buttons
            console.log('[FLOW] About to call renderQuestionWithNav');
            renderQuestionWithNav(question, currentQuestionIndex, false);
            console.log('[FLOW] renderQuestionWithNav completed');
            startInactivityTracking();
            // Fetch and display engagement score
            await fetchAndDisplayEngagementScore();
        } else {
            throw new Error(data.error || 'Failed to load question');
        }
    } catch (error) {
        console.error('Error fetching question:', error);
        alert('Failed to load question: ' + error.message);
    }
}

function selectOption(element, value) {
    // Track option selection for this question
    if (!currentQuestionState.initialOption) {
        currentQuestionState.initialOption = value;
        console.log('[TRACKING] Initial option selected:', value);
    } else if (currentQuestionState.finalOption !== value && value !== currentQuestionState.initialOption) {
        currentQuestionState.optionChangeCount++;
        currentQuestionState.optionChangeHistory.push({
            from: currentQuestionState.finalOption || currentQuestionState.initialOption,
            to: value,
            timestamp: Date.now()
        });
        
        // Detect frequent switching pattern
        if (currentQuestionState.optionChangeCount >= 2) {
            currentQuestionState.hesitationFlags.frequentSwitching = true;
        }
        
        console.log('[TRACKING] Option changed to:', value, 'Total changes:', currentQuestionState.optionChangeCount);
    }
    
    currentQuestionState.finalOption = value;
    recordInteractionActivity();
    
    document.querySelectorAll('.option-button').forEach(opt => {
        opt.classList.remove('selected');
        opt.style.borderColor = '#e0e0e0';
        opt.style.background = 'white';
        opt.style.color = '#333';
    });
    element.classList.add('selected');
    element.style.borderColor = '#667eea';
    element.style.background = 'linear-gradient(135deg, #f0f5ff 0%, #e8eaf6 100%)';
    element.style.color = '#667eea';
    element.style.fontWeight = '600';
    element.dataset.selected = value;
}

function recordInteractionActivity() {
    lastInteractionTime = Date.now();
    currentInactivityDuration = 0;
}

function startInactivityTracking() {
    lastInteractionTime = Date.now();
    currentInactivityDuration = 0;
    
    // CRITICAL FIX: Clear existing inactivity timer before creating new one
    if (inactivityTimer) {
        clearInterval(inactivityTimer);
        inactivityTimer = null;
    }
    
    // Check inactivity every 500ms
    inactivityTimer = setInterval(() => {
        const elapsed = Date.now() - lastInteractionTime;
        currentInactivityDuration = elapsed;
        
        // Flag if > 10 seconds of inactivity
        if (elapsed > 10000) {
            currentQuestionState.hesitationFlags.longHesitation = true;
        }
    }, 500);
    
    console.log('[INACTIVITY] Tracking started for Q' + currentQuestionState.questionId);
}

function startTimeTracking() {
    const timeCounter = document.getElementById('time-counter');
    if (!timeCounter) {
        console.warn('[TIMER] time-counter element not found');
        return;
    }
    
    // CRITICAL FIX: Clear any existing timer before creating new one
    TEST_STATE.clearAllTimers();
    
    // Get current question ID from currentQuestionState
    const questionId = currentQuestionState.questionId;
    if (!questionId) {
        console.error('[TIMER] No question ID set');
        return;
    }
    
    // Start the timer in TEST_STATE
    TEST_STATE.startQuestionTimer(questionId);
    
    // Update display every 100ms from authoritative TEST_STATE
    // CRITICAL: Re-query element each iteration to handle DOM re-renders
    TEST_STATE.activeTimeInterval = setInterval(() => {
        // Re-query element from DOM each time (handles re-renders)
        const currentTimeCounter = document.getElementById('time-counter');
        if (!currentTimeCounter) {
            // Element no longer exists (DOM re-rendered)
            TEST_STATE.clearAllTimers();
            console.log('[TIMER] time-counter element removed, cleared timers');
            return;
        }
        
        // Get elapsed time from TEST_STATE (never resets)
        const elapsed = TEST_STATE.getTimeElapsedForQuestion(questionId);
        const minutes = Math.floor(elapsed / 60);
        const seconds = elapsed % 60;
        currentTimeCounter.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        
        console.log('[TIMER] Question', questionId, 'elapsed:', elapsed, 's');
    }, 100);
}

function navigatePreviousQuestion() {
    // CRITICAL FIX: Set navigation intent to prevent modal hijacking
    navigationIntentActive = true;
    
    // CRITICAL FIX: Use TEST_STATE navigation rules (never override on re-render)
    if (!TEST_STATE.canNavigatePrev()) {
        navigationIntentActive = false;
        console.log('[NAV-PREV] Blocked - TEST_STATE.canNavigatePrev() = false');
        return;
    }
    
    // Navigate to previous question
    TEST_STATE.setCurrentQuestionIndex(TEST_STATE.currentQuestionIndex - 1);
    sessionNavigationCount++;
    currentQuestionState.navigationCount++;
    console.log('[TRACKING] Navigation: Previous question via TEST_STATE', {
        from: TEST_STATE.currentQuestionIndex + 1, 
        to: TEST_STATE.currentQuestionIndex,
        navCount: sessionNavigationCount
    });
    showQuestion(TEST_STATE.currentQuestionIndex, true);
    navigationIntentActive = false;
}

function navigateNextQuestion() {
    // CRITICAL FIX: Set navigation intent to prevent modal hijacking
    navigationIntentActive = true;
    
    // CRITICAL FIX: Use TEST_STATE navigation rules (never override on re-render/timer)
    if (!TEST_STATE.canNavigateNext()) {
        navigationIntentActive = false;
        console.log('[NAV-NEXT] Blocked - TEST_STATE.canNavigateNext() = false, isOnCurrentQuestion=' + TEST_STATE.isOnCurrentQuestion());
        return;
    }
    
    // Navigate to next question in history
    const nextIndex = TEST_STATE.currentQuestionIndex + 1;
    if (nextIndex < sessionQuestionHistory.length) {
        TEST_STATE.setCurrentQuestionIndex(nextIndex);
        sessionNavigationCount++;
        currentQuestionState.navigationCount++;
        console.log('[TRACKING] Navigation: Next question via TEST_STATE', {
            from: TEST_STATE.currentQuestionIndex - 1,
            to: nextIndex,
            navCount: sessionNavigationCount
        });
        showQuestion(nextIndex, true);
    } else {
        console.log('[NAV-NEXT] At end of history, cannot navigate further');
    }
    navigationIntentActive = false;
}


function submitSelectedAnswer(questionId) {
    const selectedOption = document.querySelector('.option-button.selected');
    const selectedAnswer = selectedOption ? selectedOption.dataset.value : null;

    if (!selectedAnswer) {
        alert('Please select an answer before submitting');
        return;
    }

    // Calculate real response time from when question was rendered
    let responseTime = 30;
    if (questionStartTime) {
        const elapsedMs = Date.now() - questionStartTime;
        responseTime = Math.max(1, Math.round(elapsedMs / 1000));
        console.log(`Response time calculated: ${elapsedMs}ms = ${responseTime}s`);
    } else {
        console.warn('questionStartTime not set, using default 30s');
    }

    console.log('[TRACKING] Final question state before submission:', currentQuestionState);
    console.log('[TRACKING] Inactivity duration:', currentInactivityDuration, 'ms');
    console.log('[TRACKING] Hesitation flags:', currentQuestionState.hesitationFlags);

    submitAnswer(questionId, selectedAnswer, responseTime);
}

async function getHint(sessionId, questionId) {
    try {
        recordInteractionActivity();
        const response = await fetch(
            `${API_BASE_URL}/cbt/hint/${sessionId}/${questionId}`
        );
        const data = await response.json();
        
        if (data.success) {
            // CRITICAL: Record hint usage in current question state
            if (currentQuestionState.questionId === questionId) {
                currentQuestionState.hints_requested = (currentQuestionState.hints_requested || 0) + 1;
                currentQuestionState.hints_used.push({
                    hint_text: data.hint_data.hint,
                    timestamp: Date.now()
                });
                console.log('[HINT] Recorded hint #' + currentQuestionState.hints_requested + ' for Q' + questionId);
            }
            
            alert('Hint: ' + data.hint_data.hint);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error getting hint:', error);
        alert('Failed to get hint');
    }
}

// ============================================================================
// ENHANCED QUESTION DISPLAY WITH NAVIGATION & TRACKING
// ============================================================================

function renderQuestionWithNav(question, questionIndex, isRevisit) {
    console.log('[RENDER] renderQuestionWithNav called with:', {questionIndex, isRevisit, questionId: question.question_id});
    
    const content = document.getElementById('content');
    const progressPercent = currentSession && currentSession.num_questions 
                ? ((currentSession.questions_completed || 0) / currentSession.num_questions) * 100 
                : 0;
    
    // CRITICAL FIX: Use TEST_STATE methods for navigation eligibility
    // These survive re-renders and timer ticks
    const canNavigatePrev = TEST_STATE.canNavigatePrev();
    const canNavigateNext = TEST_STATE.canNavigateNext();
    const isOnCurrentQuestion = TEST_STATE.isOnCurrentQuestion();
    const isRevisiting = currentQuestionState && currentQuestionState.isRevisit;
    const isLastQuestion = questionIndex >= currentSession.num_questions - 1;
    
    console.log('[RENDER] Navigation state from TEST_STATE:', {
        canNavigatePrev, 
        canNavigateNext, 
        isLastQuestion,
        isOnCurrentQuestion,
        isRevisiting,
        currentQuestionIndex: TEST_STATE.currentQuestionIndex,
        highestAnsweredIndex: TEST_STATE.highestAnsweredIndex
    });
    
    content.innerHTML = `
        <div style="max-width: 900px; margin: 0 auto; padding: 30px 20px;">
            <!-- Progress Bar -->
            <div style="margin-bottom: 30px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <span style="font-size: 14px; color: #999;">Progress</span>
                    <span style="font-size: 14px; color: #667eea; font-weight: 600;">
                        ${(currentSession.questions_completed || 0)} of ${currentSession.num_questions}
                    </span>
                </div>
                <div style="background: #e8eaf6; height: 8px; border-radius: 10px; overflow: hidden;">
                    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); height: 100%; width: ${progressPercent}%; transition: width 0.3s;"></div>
                </div>
            </div>
            
            <!-- Stats Grid with Time & Attempts -->
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 30px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 16px; border-radius: 8px; text-align: center; color: white;">
                    <div style="font-size: 11px; opacity: 0.9; margin-bottom: 6px;">CORRECT</div>
                    <div style="font-size: 28px; font-weight: bold;">${currentSession.correct_answers || 0}</div>
                </div>
                <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 16px; border-radius: 8px; text-align: center; color: white;">
                    <div style="font-size: 11px; opacity: 0.9; margin-bottom: 6px;">DIFFICULTY</div>
                    <div style="font-size: 28px; font-weight: bold;">${(currentSession.current_difficulty * 100).toFixed(0)}%</div>
                </div>
                <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 16px; border-radius: 8px; text-align: center; color: white;">
                    <div style="font-size: 11px; opacity: 0.9; margin-bottom: 6px;">ENGAGEMENT</div>
                    <div style="font-size: 28px; font-weight: bold;" id="engagement-score">--</div>
                </div>
                <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 16px; border-radius: 8px; text-align: center; color: white;">
                    <div style="font-size: 11px; opacity: 0.9; margin-bottom: 6px;">TIME</div>
                    <div style="font-size: 20px; font-weight: bold;" id="time-counter">0:00</div>
                </div>
            </div>
            </div>
            
            <!-- Question Card -->
            <div style="background: white; padding: 40px; border-radius: 12px; box-shadow: 0 2px 15px rgba(0,0,0,0.1); margin-bottom: 30px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px;">
                    <h3 style="margin: 0; font-size: 22px; line-height: 1.7; color: #222; font-weight: 600; flex: 1;">
                        ${question.question_text}
                    </h3>
                    ${isRevisit ? '<span style="background: #fff3cd; color: #856404; padding: 6px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; white-space: nowrap; margin-left: 15px;">REVISIT</span>' : ''}
                </div>
                <div id="options" style="margin: 30px 0 25px 0;"></div>
            </div>
            
            <!-- Action Buttons -->
            <div style="display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 20px;">
                <button onclick="submitSelectedAnswer('${question.question_id}')" 
                        style="flex: 1; min-width: 180px; padding: 16px; font-size: 16px; font-weight: 600; cursor: pointer; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; transition: all 0.2s; box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);" 
                        onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 8px 20px rgba(102, 126, 234, 0.4)'" 
                        onmouseout="this.style.transform='none'; this.style.boxShadow='0 2px 8px rgba(102, 126, 234, 0.2)';">
                    ✓ Submit Answer
                </button>
                ${question.hints_available > 0 ? 
                    `<button onclick="getHint('${currentSession.id}', '${question.question_id}')" 
                             style="flex: 1; min-width: 140px; padding: 16px; font-size: 16px; font-weight: 600; cursor: pointer; background: white; border: 2px solid #e0e0e0; border-radius: 8px; transition: all 0.2s; color: #555;" 
                             onmouseover="this.style.borderColor='#667eea'; this.style.color='#667eea'; this.style.background='#f0f5ff';" 
                             onmouseout="this.style.borderColor='#e0e0e0'; this.style.color='#555'; this.style.background='white';">
                        💡 Hint (${question.hints_available})
                    </button>` 
                    : ''}
            </div>
            
            <!-- Navigation Buttons -->
            <div style="display: flex; gap: 12px; justify-content: space-between;">
                <button onclick="navigatePreviousQuestion()" 
                        ${!canNavigatePrev ? 'disabled' : ''}
                        style="flex: 1; padding: 14px; font-size: 14px; font-weight: 600; cursor: ${canNavigatePrev ? 'pointer' : 'not-allowed'}; background: ${canNavigatePrev ? 'white' : '#f0f0f0'}; color: ${canNavigatePrev ? '#667eea' : '#ccc'}; border: 2px solid ${canNavigatePrev ? '#667eea' : '#e0e0e0'}; border-radius: 8px; transition: all 0.2s; opacity: ${canNavigatePrev ? '1' : '0.6'};" 
                        ${canNavigatePrev ? "onmouseover=\"this.style.background='#f0f5ff'\" onmouseout=\"this.style.background='white'\"" : ''}>
                    ← Previous
                </button>
                <button onclick="navigateNextQuestion()" 
                        ${!canNavigateNext ? 'disabled' : ''}
                        style="flex: 1; padding: 14px; font-size: 14px; font-weight: 600; cursor: ${canNavigateNext ? 'pointer' : 'not-allowed'}; background: ${canNavigateNext ? 'white' : '#f0f0f0'}; color: ${canNavigateNext ? '#667eea' : '#ccc'}; border: 2px solid ${canNavigateNext ? '#667eea' : '#e0e0e0'}; border-radius: 8px; transition: all 0.2s; opacity: ${canNavigateNext ? '1' : '0.6'};" 
                        ${canNavigateNext ? "onmouseover=\"this.style.background='#f0f5ff'\" onmouseout=\"this.style.background='white'\"" : ''}>
                    Next →
                </button>
            </div>
        </div>
    `;
    
    console.log('[RENDER] HTML set to content element');
    console.log('[RENDER] Navigation buttons HTML included in innerHTML');
    
    // Render options
    const optionsDiv = document.getElementById('options');
    for (const [key, value] of Object.entries(question.options)) {
        const button = document.createElement('button');
        button.className = 'option-button';
        button.dataset.value = key;
        button.type = 'button';
        button.textContent = `${key}. ${value}`;
        button.style.cssText = `
            display: block;
            width: 100%;
            padding: 18px;
            margin-bottom: 12px;
            border: 2px solid #e0e0e0;
            background: white;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            text-align: left;
            transition: all 0.2s;
            font-weight: 500;
            color: #333;
        `;
        button.onmouseover = () => {
            if (!button.classList.contains('selected')) {
                button.style.borderColor = '#667eea';
                button.style.background = '#f0f5ff';
            }
        };
        button.onmouseout = () => {
            if (!button.classList.contains('selected')) {
                button.style.borderColor = '#e0e0e0';
                button.style.background = 'white';
            }
        };
        button.onclick = () => {
            selectOption(button, key);
            recordInteractionActivity();
        };
        optionsDiv.appendChild(button);
    }
    
    // Start timer display
    startTimeTracking();
    
    // CRITICAL FIX: Restore engagement score from TEST_STATE (never reset on re-render)
    const engagementScoreElement = document.getElementById('engagement-score');
    if (engagementScoreElement) {
        const savedEngagement = TEST_STATE.getEngagementForQuestion(question.question_id);
        if (savedEngagement > 0) {
            engagementScoreElement.textContent = (savedEngagement * 100).toFixed(0) + '%';
            console.log('[RENDER] Restored engagement for Q' + question.question_id + ':', savedEngagement);
        } else {
            engagementScoreElement.textContent = '--';
        }
    }
}

// Data Export Functions for Research
async function exportFacialData(sessionId) {
    try {
        const response = await fetch(
            `${API_BASE_URL}/analytics/export/facial-data/${sessionId}`
        );
        
        if (!response.ok) {
            throw new Error('Failed to export facial data');
        }
        
        const data = await response.json();
        
        if (data.success) {
            // Download as JSON
            const json = JSON.stringify(data.data, null, 2);
            const blob = new Blob([json], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `facial_data_${sessionId}.json`;
            a.click();
            URL.revokeObjectURL(url);
            alert('✅ Facial data exported successfully!');
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error exporting facial data:', error);
        alert('Failed to export facial data: ' + error.message);
    }
}

async function exportAllStudentData(studentId) {
    try {
        const response = await fetch(
            `${API_BASE_URL}/analytics/export/all-data/${studentId}`
        );
        
        if (!response.ok) {
            throw new Error('Failed to export student data');
        }
        
        const data = await response.json();
        
        if (data.success) {
            // Download as JSON
            const json = JSON.stringify(data.data, null, 2);
            const blob = new Blob([json], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `student_data_${studentId}_${new Date().toISOString().split('T')[0]}.json`;
            a.click();
            URL.revokeObjectURL(url);
            alert('✅ All student data exported successfully!');
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error exporting student data:', error);
        alert('Failed to export student data: ' + error.message);
    }
}

async function exportAsCSV(studentId) {
    try {
        const response = await fetch(
            `${API_BASE_URL}/analytics/export/csv/${studentId}`
        );
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            // Download as CSV
            const blob = new Blob([data.data], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = data.filename || `student_data_${studentId}_${new Date().toISOString().split('T')[0]}.csv`;
            a.click();
            URL.revokeObjectURL(url);
            alert('✅ CSV data exported successfully!');
        } else {
            throw new Error(data.error || 'Failed to export CSV data');
        }
    } catch (error) {
        console.error('Error exporting CSV:', error);
        alert('Failed to export CSV: ' + error.message);
    }
}


async function showDashboard() {
    if (!currentStudent) {
        showLoginPage();
        return;
    }
    
    try {
        const response = await fetch(
            `${API_BASE_URL}/analytics/dashboard/${currentStudent.id}`
        );
        const data = await response.json();
        
        if (data.success) {
            const dashboard = data.dashboard;
            const stats = dashboard.statistics;
            const content = document.getElementById('content');
            
            content.innerHTML = `
                <div style="max-width: 1000px; margin: 0 auto; padding: 20px;">
                    <div style="margin-bottom: 30px;">
                        <h2 style="color: #333; margin: 0 0 10px 0;">📊 Your Learning Dashboard</h2>
                        <p style="color: #999; margin: 0;">Track your progress and performance</p>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px;">
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(102, 126, 234, 0.2);">
                            <div style="font-size: 14px; opacity: 0.9; margin-bottom: 10px;">TOTAL SESSIONS</div>
                            <div style="font-size: 42px; font-weight: bold; margin-bottom: 10px;">${stats.total_sessions || 0}</div>
                            <div style="font-size: 12px; opacity: 0.8;">Tests completed</div>
                        </div>
                        
                        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(245, 87, 108, 0.2);">
                            <div style="font-size: 14px; opacity: 0.9; margin-bottom: 10px;">ACCURACY</div>
                            <div style="font-size: 42px; font-weight: bold; margin-bottom: 10px;">${stats.overall_accuracy || 0}%</div>
                            <div style="font-size: 12px; opacity: 0.8;">Correct answers</div>
                        </div>
                        
                        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(79, 172, 254, 0.2);">
                            <div style="font-size: 14px; opacity: 0.9; margin-bottom: 10px;">TOTAL QUESTIONS</div>
                            <div style="font-size: 42px; font-weight: bold; margin-bottom: 10px;">${stats.total_questions || 0}</div>
                            <div style="font-size: 12px; opacity: 0.8;">Questions answered</div>
                        </div>
                        
                        <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(250, 112, 154, 0.2);">
                            <div style="font-size: 14px; opacity: 0.9; margin-bottom: 10px;">ENGAGEMENT</div>
                            <div style="font-size: 42px; font-weight: bold; margin-bottom: 10px;">${stats.recent_engagement_score ? (stats.recent_engagement_score * 100).toFixed(0) : 'N/A'}%</div>
                            <div style="font-size: 12px; opacity: 0.8;">Recent activity</div>
                        </div>
                    </div>
                    
                    <div style="background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 25px; border-radius: 12px; margin-bottom: 20px;">
                        <h3 style="color: #333; margin: 0 0 15px 0; font-size: 16px; font-weight: 600;">📥 Export Learning Data for Research</h3>
                        <p style="color: #666; margin: 0 0 15px 0; font-size: 13px;">Download your complete learning and facial expression data for analysis and documentation.</p>
                        <div style="display: flex; gap: 12px; flex-wrap: wrap;">
                            <button type="button" onclick="exportAllStudentData('${currentStudent.id}')" style="padding: 12px 20px; font-size: 14px; font-weight: 600; cursor: pointer; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; transition: all 0.2s;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 15px rgba(102, 126, 234, 0.3)'" onmouseout="this.style.transform='none'; this.style.boxShadow='none';">📊 Export All Data (JSON)</button>
                            <button type="button" onclick="exportAsCSV('${currentStudent.id}')" style="padding: 12px 20px; font-size: 14px; font-weight: 600; cursor: pointer; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; border: none; border-radius: 8px; transition: all 0.2s;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 15px rgba(79, 172, 254, 0.3)'" onmouseout="this.style.transform='none'; this.style.boxShadow='none';">📈 Export as CSV</button>
                            <button type="button" onclick="alert('Facial data is exported with session data. Use the JSON export and filter for engagement_metrics.')" style="padding: 12px 20px; font-size: 14px; font-weight: 600; cursor: pointer; background: white; border: 2px solid #667eea; color: #667eea; border-radius: 8px; transition: all 0.2s;" onmouseover="this.style.background='#f0f5ff'" onmouseout="this.style.background='white';">💡 Help</button>
                        </div>
                    </div>
                    
                    <div style="background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); text-align: center;">
                        <p style="color: #666; margin: 0 0 20px 0; font-size: 16px;">Ready to continue learning?</p>
                        <button type="button" onclick="showTestPage()" style="padding: 16px 40px; font-size: 16px; font-weight: 600; cursor: pointer; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; transition: all 0.2s;" onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 8px 20px rgba(102, 126, 234, 0.3)'" onmouseout="this.style.transform='none'; this.style.boxShadow='none';">Start a New Test</button>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
        alert('Failed to load dashboard');
    }
}

// ============================================================================
// FACIAL EXPRESSION MONITORING WITH FACE.JS
// ============================================================================

let facialCapture = null;
let facialMonitoringEnabled = false;

class WebcamFacialCapture {
    constructor(videoElementId) {
        this.video = document.getElementById(videoElementId);
        this.stream = null;
        this.isRunning = false;
        this.detectionInterval = null;
        this.modelsLoaded = false;
        this.lastEmotion = 'neutral';
    }
    
    async loadModels() {
        if (this.modelsLoaded) return;
        console.log('Loading facial detection models...');
        
        try {
            await Promise.all([
                faceapi.nets.tinyFaceDetector.loadFromUri('https://cdn.jsdelivr.net/npm/@vladmandic/face-api/model/'),
                faceapi.nets.faceExpressionNet.loadFromUri('https://cdn.jsdelivr.net/npm/@vladmandic/face-api/model/')
            ]);
            
            this.modelsLoaded = true;
            console.log('✅ Facial detection models loaded');
        } catch (error) {
            console.error('❌ Failed to load facial models:', error);
            throw error;
        }
    }
    
    async initialize() {
        try {
            // Load models first
            await this.loadModels();
            
            // Request camera access
            this.stream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user'
                },
                audio: false 
            });
            
            this.video.srcObject = this.stream;
            this.video.onloadedmetadata = () => {
                this.video.play().catch(e => console.error('Video play error:', e));
            };
            
            console.log('✅ Webcam initialized');
            return true;
        } catch (error) {
            console.error('❌ Webcam initialization failed:', error);
            if (error.name === 'NotAllowedError') {
                alert('Camera access denied. Please enable camera permissions to use facial monitoring.');
            } else if (error.name === 'NotFoundError') {
                alert('No camera found. Facial monitoring requires a webcam.');
            }
            return false;
        }
    }
    
    async startDetection(sessionId) {
        if (!this.modelsLoaded || !this.stream) {
            console.error('Models not loaded or webcam not initialized');
            return;
        }
        
        this.isRunning = true;
        console.log('🟢 Facial detection started for session:', sessionId);
        
        // Update camera status indicator
        const statusIndicator = document.getElementById('camera-status');
        const feedbackText = document.getElementById('feedback-text');
        if (statusIndicator) statusIndicator.style.background = '#10b981';  // Green
        if (feedbackText) feedbackText.textContent = '✅ Camera working';
        
        this.detectionInterval = setInterval(async () => {
            if (!this.isRunning || !this.video.srcObject) return;
            
            try {
                const options = new faceapi.TinyFaceDetectorOptions({
                    inputSize: 416,
                    scoreThreshold: 0.5
                });
                
                const detections = await faceapi
                    .detectAllFaces(this.video, options)
                    .withFaceExpressions();
                
                if (detections.length > 0) {
                    // Update status - face detected
                    if (statusIndicator) statusIndicator.style.background = '#10b981';  // Green
                    if (feedbackText) feedbackText.textContent = '✅ Face detected';
                    
                    const expressions = detections[0].expressions;
                    
                    // Find dominant emotion
                    const emotions = {
                        'happy': expressions.happy,
                        'sad': expressions.sad,
                        'angry': expressions.angry,
                        'fearful': expressions.fearful,
                        'disgusted': expressions.disgusted,
                        'neutral': expressions.neutral,
                        'surprised': expressions.surprised
                    };
                    
                    const emotion = Object.keys(emotions).reduce((a, b) =>
                        emotions[a] > emotions[b] ? a : b
                    );
                    const confidence = Math.max(...Object.values(expressions));
                    
                    // CRITICAL: Record facial metrics to current question state
                    if (currentQuestionState.facial_data) {
                        currentQuestionState.facial_data.face_detected_count = (currentQuestionState.facial_data.face_detected_count || 0) + 1;
                        currentQuestionState.facial_data.attention_scores.push(confidence);
                        currentQuestionState.facial_data.emotions_detected.push({
                            emotion: emotion,
                            confidence: confidence,
                            timestamp: Date.now()
                        });
                    }
                    
                    // Update UI with emotion and confidence
                    const emotionDisplay = document.getElementById('emotion-display');
                    const confidenceDisplay = document.getElementById('emotion-confidence');
                    
                    if (emotionDisplay) {
                        emotionDisplay.textContent = emotion.charAt(0).toUpperCase() + emotion.slice(1);
                    }
                    if (confidenceDisplay) {
                        confidenceDisplay.textContent = `${Math.round(confidence * 100)}% confidence`;
                    }
                    
                    // Draw face rectangle on canvas
                    this.drawFaceRectangle(detections[0]);
                    
                    // Send to backend
                    try {
                        const response = await fetch(`${API_BASE_URL}/analytics/affective/record-facial`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                student_id: currentStudent?.id || 'anonymous',
                                session_id: sessionId,
                                question_id: currentQuestionState?.questionId,
                                emotion: emotion,
                                confidence: confidence
                            })
                        });
                        
                        if (!response.ok) {
                            console.warn('Backend response:', response.status);
                        }
                    } catch (error) {
                        console.error('Error sending facial data:', error);
                    }
                } else {
                    // Face not detected
                    if (currentQuestionState.facial_data) {
                        currentQuestionState.facial_data.face_lost_count = (currentQuestionState.facial_data.face_lost_count || 0) + 1;
                    }
                    
                    const emotionDisplay = document.getElementById('emotion-display');
                    const confidenceDisplay = document.getElementById('emotion-confidence');
                    const feedbackText = document.getElementById('feedback-text');
                    const statusIndicator = document.getElementById('camera-status');
                    
                    if (emotionDisplay) emotionDisplay.textContent = '--';
                    if (confidenceDisplay) confidenceDisplay.textContent = 'no face';
                    if (feedbackText) feedbackText.textContent = '⚠️ Adjust lighting or position';
                    if (statusIndicator) statusIndicator.style.background = '#f59e0b';  // Amber
                }
            } catch (error) {
                console.error('Facial detection error:', error);
                const feedbackText = document.getElementById('feedback-text');
                if (feedbackText) feedbackText.textContent = '❌ Detection error';
            }
        }, 500); // Detect every 500ms (2 FPS)
    }
    
    stopDetection() {
        if (this.detectionInterval) {
            clearInterval(this.detectionInterval);
        }
        this.isRunning = false;
        
        // Reset status indicator
        const statusIndicator = document.getElementById('camera-status');
        const feedbackText = document.getElementById('feedback-text');
        if (statusIndicator) statusIndicator.style.background = '#ddd';
        if (feedbackText) feedbackText.textContent = 'Monitoring disabled';
        
        console.log('🔴 Facial detection stopped');
    }
    
    async stop() {
        this.stopDetection();;
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }
    }
    
    drawFaceRectangle(detection) {
        /**
         * Draw a rectangle around detected face on canvas overlay
         */
        const canvas = document.getElementById('face-canvas');
        const video = this.video;
        
        if (!canvas || !video || !detection) {
            console.warn('[Canvas] Missing element:', {canvas: !!canvas, video: !!video, detection: !!detection});
            return;
        }
        
        console.log('[Canvas] Drawing face rectangle', {canvasDisplay: canvas.style.display, offsetWidth: canvas.offsetWidth, offsetHeight: canvas.offsetHeight});
        
        // Set canvas size to match video
        // Use offsetWidth/offsetHeight for displayed size, fallback to computed style
        let canvasWidth = canvas.offsetWidth;
        let canvasHeight = canvas.offsetHeight;
        
        // If offsetWidth is 0, get the parent size
        if (canvasWidth === 0 || canvasHeight === 0) {
            const parent = canvas.parentElement;
            if (parent) {
                canvasWidth = canvasWidth || parent.offsetWidth;
                canvasHeight = canvasHeight || parent.offsetHeight;
            }
        }
        
        // Fallback to fixed dimensions
        if (canvasWidth === 0 || canvasHeight === 0) {
            canvasWidth = canvasWidth || 220;
            canvasHeight = canvasHeight || 150;
        }
        
        canvas.width = canvasWidth;
        canvas.height = canvasHeight;
        
        console.log('[Canvas] Canvas dimensions set to:', canvas.width, 'x', canvas.height, 'from video:', video.videoWidth, 'x', video.videoHeight);
        
        const ctx = canvas.getContext('2d');
        if (!ctx) {
            console.error('[Canvas] Failed to get 2D context');
            return;
        }
        
        // Clear canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Get detection box
        const { x, y, width, height } = detection.detection.box;
        
        // Calculate scale from actual video size to displayed size
        const scaleX = canvas.width / video.videoWidth;
        const scaleY = canvas.height / video.videoHeight;
        
        // Draw rectangle
        const scaledX = x * scaleX;
        const scaledY = y * scaleY;
        const scaledWidth = width * scaleX;
        const scaledHeight = height * scaleY;
        
        // Green glowing rectangle style
        ctx.strokeStyle = '#10b981';
        ctx.lineWidth = 3;
        ctx.shadowColor = 'rgba(16, 185, 129, 0.8)';
        ctx.shadowBlur = 15;
        ctx.shadowOffsetX = 0;
        ctx.shadowOffsetY = 0;
        
        // Draw rectangle
        ctx.strokeRect(scaledX, scaledY, scaledWidth, scaledHeight);
        
        // Draw corner markers
        const cornerSize = 10;
        ctx.fillStyle = '#10b981';
        
        // Top-left
        ctx.fillRect(scaledX, scaledY, cornerSize, 3);
        ctx.fillRect(scaledX, scaledY, 3, cornerSize);
        
        // Top-right
        ctx.fillRect(scaledX + scaledWidth - cornerSize, scaledY, cornerSize, 3);
        ctx.fillRect(scaledX + scaledWidth - 3, scaledY, 3, cornerSize);
        
        // Bottom-left
        ctx.fillRect(scaledX, scaledY + scaledHeight - 3, cornerSize, 3);
        ctx.fillRect(scaledX, scaledY + scaledHeight - cornerSize, 3, cornerSize);
        
        // Bottom-right
        ctx.fillRect(scaledX + scaledWidth - cornerSize, scaledY + scaledHeight - 3, cornerSize, 3);
        ctx.fillRect(scaledX + scaledWidth - 3, scaledY + scaledHeight - cornerSize, 3, cornerSize);
        
        console.log('[Canvas] Face rectangle drawn successfully at:', {x: scaledX, y: scaledY, width: scaledWidth, height: scaledHeight});
    }
}

// Initialize facial monitoring UI
function setupFacialMonitoring() {
    const checkbox = document.getElementById('facial-enabled');
    const container = document.getElementById('facial-monitoring-container');
    
    if (!checkbox || !container) {
        console.warn('Facial monitoring elements not found in DOM');
        return;
    }
    
    // Show container when page loads
    container.style.display = 'block';
    
    // Handle checkbox changes
    checkbox.addEventListener('change', async (e) => {
        if (e.target.checked) {
            // Enable facial monitoring
            console.log('Enabling facial monitoring...');
            facialCapture = new WebcamFacialCapture('webcam-video');
            const initialized = await facialCapture.initialize();
            
            if (initialized) {
                const sessionId = currentSession?.id || new Date().getTime().toString();
                const video = document.getElementById('webcam-video');
                const canvas = document.getElementById('face-canvas');
                
                console.log('[Facial] Video element:', !!video, 'Canvas element:', !!canvas);
                
                if (video) {
                    video.style.display = 'block';
                    console.log('[Facial] Video display set to block');
                }
                if (canvas) {
                    canvas.style.display = 'block';
                    console.log('[Facial] Canvas display set to block');
                }
                
                facialCapture.startDetection(sessionId);
                facialMonitoringEnabled = true;
                console.log('✅ Facial monitoring enabled');
            } else {
                e.target.checked = false;
                facialMonitoringEnabled = false;
                console.error('Failed to initialize facial monitoring');
            }
        } else {
            // Disable facial monitoring
            console.log('Disabling facial monitoring...');
            if (facialCapture) {
                await facialCapture.stop();
            }
            const video = document.getElementById('webcam-video');
            const canvas = document.getElementById('face-canvas');
            video.style.display = 'none';
            if (canvas) canvas.style.display = 'none';
            facialMonitoringEnabled = false;
            console.log('✅ Facial monitoring disabled');
        }
    });
}

// Call setup when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupFacialMonitoring);
} else {
    setupFacialMonitoring();
}

// Make sure to stop facial monitoring when page unloads
window.addEventListener('beforeunload', () => {
    if (facialCapture && facialMonitoringEnabled) {
        facialCapture.stop();
    }
});
