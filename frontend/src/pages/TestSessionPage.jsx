/**
 * Comprehensive Test Session Page Component
 * 
 * Full integration of:
 * - Question presentation
 * - Real-time difficulty tracking
 * - Live engagement monitoring
 * - Session history and timeline
 * - Adaptation feedback
 * - User testing with temporary overrides
 */

import React, { useState, useEffect, useRef } from 'react';
import AdaptiveQuestion from './AdaptiveQuestion';
import SessionTimeline from './SessionTimeline';
import EngagementIndicators from './EngagementIndicators';
import '../styles/TestSession.css';

const TestSessionPage = ({ studentId, sessionId, subject = 'Mathematics' }) => {
  // Core Session State
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [session, setSession] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Tracking
  const [responses, setResponses] = useState([]);
  const [engagementHistory, setEngagementHistory] = useState([]);
  const [adaptationHistory, setAdaptationHistory] = useState([]);
  const [currentEngagement, setCurrentEngagement] = useState({});

  // UI State
  const [showTimeline, setShowTimeline] = useState(false);
  const [showDebug, setShowDebug] = useState(false);
  const [engagementOverride, setEngagementOverride] = useState(null);
  const timelineRef = useRef(null);

  // Initialize session
  useEffect(() => {
    const initSession = async () => {
      try {
        setIsLoading(true);
        
        // Start session
        const sessionResponse = await fetch(
          `http://localhost:5000/api/cbt/session/start`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              student_id: studentId,
              num_questions: 10,
              subject: subject
            })
          }
        );

        if (!sessionResponse.ok) throw new Error('Failed to start session');
        const sessionData = await sessionResponse.json();

        if (sessionData.success) {
          setSession(sessionData.session);

          // Fetch first question
          await fetchNextQuestion(sessionData.session.id);
        } else {
          setError(sessionData.error || 'Failed to initialize session');
        }
      } catch (err) {
        setError(err.message);
        console.error('Init error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    initSession();
  }, [studentId, subject]);

  // Fetch next question
  const fetchNextQuestion = async (sId) => {
    try {
      const response = await fetch(
        `http://localhost:5000/api/cbt/question/next/${sId}`
      );

      if (!response.ok) throw new Error('Failed to fetch question');
      const data = await response.json();

      if (data.success && data.question) {
        setCurrentQuestion(data.question);
      } else if (data.status === 'completed') {
        // Session finished
        setCurrentQuestion(null);
      } else {
        setError(data.error || 'Failed to load question');
      }
    } catch (err) {
      setError(err.message);
      console.error('Question fetch error:', err);
    }
  };

  // Handle answer submission
  const handleAnswerSubmit = async (responseData) => {
    try {
      // Track response
      const newResponse = {
        question_id: currentQuestion.question_id,
        is_correct: responseData.is_correct,
        student_answer: responseData.student_answer,
        correct_answer: responseData.correct_answer,
        response_time_seconds: responseData.response_time,
        difficulty: responseData.current_difficulty || session?.current_difficulty
      };

      setResponses(prev => [...prev, newResponse]);

      // Fetch engagement data
      try {
        const engageResponse = await fetch(
          `http://localhost:5000/api/engagement/last/${session.id}`
        );
        if (engageResponse.ok) {
          const engageData = await engageResponse.json();
          setCurrentEngagement(engageData.engagement || {});
          setEngagementHistory(prev => [
            ...prev,
            engageData.engagement || {}
          ]);
        }
      } catch (err) {
        console.warn('Could not fetch engagement:', err);
      }

      // Track adaptation decision if available
      if (responseData.adaptation) {
        setAdaptationHistory(prev => [...prev, responseData.adaptation]);
      }

      // Fetch next question
      setTimeout(() => {
        fetchNextQuestion(session.id);
      }, 2000); // Small delay for user feedback
    } catch (err) {
      console.error('Submission error:', err);
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="test-session-loading">
        <div className="loading-spinner" />
        <p>Initializing your test session...</p>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="test-session-error">
        <h2>❌ Error</h2>
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>
          Retry
        </button>
      </div>
    );
  }

  // Completed state
  if (!currentQuestion && responses.length > 0) {
    return <TestCompleteView responses={responses} session={session} />;
  }

  // Main test interface
  return (
    <div className="test-session-container">
      {/* Header */}
      <div className="test-header">
        <div className="test-info">
          <h1>{subject} Test</h1>
          <p>Question {responses.length + 1} of {session?.num_questions || 10}</p>
        </div>
        <div className="test-controls">
          <button
            className="control-btn timeline-btn"
            onClick={() => setShowTimeline(!showTimeline)}
            title="Toggle question history"
          >
            📋 History
          </button>
          <button
            className="control-btn debug-btn"
            onClick={() => setShowDebug(!showDebug)}
            title="Show adaptation policy debug"
          >
            🔧 Debug
          </button>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="test-content-grid">
        {/* Left: Question Panel */}
        <div className="question-panel">
          {currentQuestion && (
            <AdaptiveQuestion
              question={currentQuestion}
              session={session}
              onSubmit={handleAnswerSubmit}
              isLoading={isLoading}
            />
          )}
        </div>

        {/* Right: Engagement & Progress Panels */}
        <div className="right-panels">
          {/* Live Engagement Indicator */}
          <div className="engagement-panel">
            <EngagementIndicators
              currentEngagement={currentEngagement}
              sessionData={{
                correct_answers: responses.filter(r => r.is_correct).length,
                total_answered: responses.length,
                avg_response_time: responses.length > 0
                  ? responses.reduce((sum, r) => sum + r.response_time_seconds, 0) / responses.length
                  : 0,
                current_difficulty: session?.current_difficulty || 0.5
              }}
              policyDebug={showDebug}
            />
          </div>

          {/* Quick Stats */}
          <div className="quick-stats">
            <StatRow
              label="Correct"
              value={responses.filter(r => r.is_correct).length}
              total={responses.length}
            />
            <StatRow
              label="Difficulty"
              value={`${(session?.current_difficulty * 100 || 50).toFixed(0)}%`}
              color={getDifficultyColor(session?.current_difficulty)}
            />
            <StatRow
              label="Avg Response"
              value={responses.length > 0
                ? `${(responses.reduce((sum, r) => sum + r.response_time_seconds, 0) / responses.length).toFixed(1)}s`
                : '—'
              }
            />
          </div>

          {/* Testing Controls (Optional) */}
          {showDebug && (
            <div className="testing-controls">
              <h4>Testing Overrides</h4>
              <div className="override-input">
                <label>Engagement Override (0-1):</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={engagementOverride || 0.5}
                  onChange={(e) => setEngagementOverride(parseFloat(e.target.value))}
                />
                <span>{(engagementOverride || 0.5).toFixed(1)}</span>
              </div>
              <p className="override-note">
                (Dev: Engagement used for adaptation if set)
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Timeline Panel (Expandable) */}
      {showTimeline && (
        <div className="timeline-panel" ref={timelineRef}>
          <SessionTimeline
            session={session}
            responses={responses}
            engagementHistory={engagementHistory}
            adaptationHistory={adaptationHistory}
          />
        </div>
      )}

      {/* Progress Bar */}
      <div className="progress-footer">
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{
              width: `${((responses.length) / (session?.num_questions || 10)) * 100}%`
            }}
          />
        </div>
        <p className="progress-text">
          {responses.length} / {session?.num_questions || 10} completed
        </p>
      </div>
    </div>
  );
};

/**
 * Test Completion View
 */
const TestCompleteView = ({ responses, session }) => {
  const correctCount = responses.filter(r => r.is_correct).length;
  const accuracy = (correctCount / responses.length) * 100;
  const avgResponseTime = responses.reduce((sum, r) => sum + r.response_time_seconds, 0) / responses.length;

  return (
    <div className="test-complete">
      <div className="complete-header">
        <h1>🎉 Test Complete!</h1>
        <p>Great job! Let's review your performance.</p>
      </div>

      <div className="complete-stats">
        <StatCard
          icon="✓"
          label="Final Score"
          value={`${accuracy.toFixed(0)}%`}
          color="#48bb78"
        />
        <StatCard
          icon="📊"
          label="Correct Answers"
          value={`${correctCount}/${responses.length}`}
          color="#667eea"
        />
        <StatCard
          icon="⏱️"
          label="Avg Response Time"
          value={`${avgResponseTime.toFixed(1)}s`}
          color="#f6ad55"
        />
        <StatCard
          icon="📈"
          label="Difficulty Range"
          value={`${(Math.min(...responses.map(r => r.difficulty)) * 100).toFixed(0)}% - ${(Math.max(...responses.map(r => r.difficulty)) * 100).toFixed(0)}%`}
          color="#f5576c"
        />
      </div>

      <div className="complete-timeline">
        <h2>Question Review</h2>
        <SessionTimeline
          session={session}
          responses={responses}
        />
      </div>

      <div className="complete-actions">
        <button className="action-btn primary" onClick={() => window.location.href = '/dashboard'}>
          📊 View Dashboard
        </button>
        <button className="action-btn secondary" onClick={() => window.location.reload()}>
          🔄 Start New Test
        </button>
      </div>
    </div>
  );
};

/**
 * Stat Row Component
 */
const StatRow = ({ label, value, color, total }) => (
  <div className="stat-row">
    <span className="stat-label">{label}</span>
    <span
      className="stat-value"
      style={color ? { color } : {}}
    >
      {total ? `${value}/${total}` : value}
    </span>
  </div>
);

/**
 * Stat Card Component
 */
const StatCard = ({ icon, label, value, color }) => (
  <div className="stat-card" style={{ borderLeftColor: color }}>
    <div className="card-icon" style={{ color }}>{icon}</div>
    <div className="card-content">
      <div className="card-label">{label}</div>
      <div className="card-value">{value}</div>
    </div>
  </div>
);

/**
 * Helper Functions
 */
const getDifficultyColor = (difficulty) => {
  if (difficulty < 0.33) return '#48bb78';
  if (difficulty < 0.67) return '#f6ad55';
  return '#f56565';
};

export default TestSessionPage;
