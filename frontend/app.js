// Main Application JavaScript

const API_BASE_URL = 'http://localhost:5000/api';

// Student and Session Management
let currentStudent = null;
let currentSession = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    setupUI();
});

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
        // Logged in - show dashboard, start test, and logout
        navLinks.innerHTML = `
            <a href="#" onclick="showDashboard()" style="padding: 10px 20px; cursor: pointer; text-decoration: none; color: #667eea; font-weight: 600; border-radius: 6px; transition: all 0.2s;" onmouseover="this.style.background='#f0f5ff'" onmouseout="this.style.background='transparent';">Dashboard</a>
            <a href="#" onclick="showTestPage()" style="padding: 10px 20px; cursor: pointer; text-decoration: none; color: #667eea; font-weight: 600; border-radius: 6px; transition: all 0.2s;" onmouseover="this.style.background='#f0f5ff'" onmouseout="this.style.background='transparent';">Start Test</a>
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
        console.log('Submitting answer:', { questionId, answer, responseTime });
        
        const response = await fetch(`${API_BASE_URL}/cbt/response/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: currentSession.id,
                question_id: questionId,
                student_answer: answer,
                response_time_seconds: responseTime
            })
        });
        
        const data = await response.json();
        console.log('Submit response:', data);
        
        if (data.success) {
            // Update session with response data
            if (data.session) {
                currentSession = data.session;
                localStorage.setItem('session', JSON.stringify(currentSession));
            } else {
                // Update local session counters
                currentSession.questions_completed = (currentSession.questions_completed || 0) + 1;
                if (data.is_correct) {
                    currentSession.correct_answers = (currentSession.correct_answers || 0) + 1;
                }
            }
            
            // Show feedback
            const correctAnswer = data.correct_answer || 'Unknown';
            alert(data.is_correct ? '✓ Correct!' : '✗ Incorrect! Answer: ' + correctAnswer);
            
            // Track engagement
            await trackEngagement(data);
            
            // Check if session is complete
            if (currentSession.questions_completed >= currentSession.num_questions) {
                alert('Test completed!\nCorrect: ' + currentSession.correct_answers + '/' + currentSession.num_questions);
                showDashboard();
            } else {
                showQuestion();
            }
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

async function showQuestion() {
    if (!currentSession || !currentSession.id) {
        console.error('No active session. Session:', currentSession);
        alert('No active session. Please start a test first.');
        showTestPage();
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
            
            const content = document.getElementById('content');
            
            const progressPercent = currentSession.num_questions > 0 
                ? ((currentSession.questions_completed || 0) / currentSession.num_questions) * 100 
                : 0;
            
            content.innerHTML = `
                <div style="max-width: 800px; margin: 0 auto; padding: 30px 20px;">
                    <div style="margin-bottom: 30px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                            <span style="font-size: 14px; color: #999;">Progress</span>
                            <span style="font-size: 14px; color: #667eea; font-weight: 600;">
                                ${(currentSession.questions_completed || 0) + 1} of ${currentSession.num_questions}
                            </span>
                        </div>
                        <div style="background: #e8eaf6; height: 8px; border-radius: 10px; overflow: hidden;">
                            <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); height: 100%; width: ${progressPercent}%; transition: width 0.3s;"></div>
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 30px;">
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 16px; border-radius: 8px; text-align: center; color: white;">
                            <div style="font-size: 11px; opacity: 0.9; margin-bottom: 6px;">CORRECT</div>
                            <div style="font-size: 28px; font-weight: bold;">${currentSession.correct_answers || 0}</div>
                        </div>
                        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 16px; border-radius: 8px; text-align: center; color: white;">
                            <div style="font-size: 11px; opacity: 0.9; margin-bottom: 6px;">DIFFICULTY</div>
                            <div style="font-size: 28px; font-weight: bold;">${(question.difficulty * 100).toFixed(0)}%</div>
                        </div>
                        <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 16px; border-radius: 8px; text-align: center; color: white;">
                            <div style="font-size: 11px; opacity: 0.9; margin-bottom: 6px;">SUBJECT</div>
                            <div style="font-size: 28px; font-weight: bold;">${currentSession.subject}</div>
                        </div>
                    </div>
                    
                    <div style="background: white; padding: 35px; border-radius: 12px; box-shadow: 0 2px 15px rgba(0,0,0,0.1); margin-bottom: 35px;">
                        <h3 style="margin: 0 0 30px 0; font-size: 22px; line-height: 1.7; color: #222; font-weight: 600;">${question.question_text}</h3>
                        
                        <div id="options" style="margin-bottom: 25px;"></div>
                    </div>
                    
                    <div style="display: flex; gap: 15px;">
                        <button onclick="submitSelectedAnswer('${question.question_id}', 30)" style="flex: 1; padding: 16px; font-size: 16px; font-weight: 600; cursor: pointer; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; transition: all 0.2s; box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 8px 20px rgba(102, 126, 234, 0.4)'" onmouseout="this.style.transform='none'; this.style.boxShadow='0 2px 8px rgba(102, 126, 234, 0.2)';">✓ Submit Answer</button>
                        ${question.hints_available > 0 ? 
                            `<button onclick="getHint('${currentSession.id}', '${question.question_id}')" style="flex: 1; padding: 16px; font-size: 16px; font-weight: 600; cursor: pointer; background: white; border: 2px solid #e0e0e0; border-radius: 8px; transition: all 0.2s; color: #555; font-weight: 600;" onmouseover="this.style.borderColor='#667eea'; this.style.color='#667eea'; this.style.background='#f0f5ff';" onmouseout="this.style.borderColor='#e0e0e0'; this.style.color='#555'; this.style.background='white';">💡 Get Hint (${question.hints_available})</button>` 
                            : ''}
                    </div>
                </div>
            `;
            
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
                button.onclick = () => selectOption(button, key);
                optionsDiv.appendChild(button);
            }
        } else {
            throw new Error(data.error || 'Failed to load question');
        }
    } catch (error) {
        console.error('Error fetching question:', error);
        alert('Failed to load question: ' + error.message);
    }
}

function selectOption(element, value) {
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

function submitSelectedAnswer(questionId, responseTime) {
    const selectedOption = document.querySelector('.option-button.selected');
    const selectedAnswer = selectedOption ? selectedOption.dataset.value : null;

    if (!selectedAnswer) {
        alert('Please select an answer before submitting');
        return;
    }

    submitAnswer(questionId, selectedAnswer, responseTime);
}

async function getHint(sessionId, questionId) {
    try {
        const response = await fetch(
            `${API_BASE_URL}/cbt/hint/${sessionId}/${questionId}`
        );
        const data = await response.json();
        
        if (data.success) {
            alert('Hint: ' + data.hint_data.hint);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error getting hint:', error);
        alert('Failed to get hint');
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
