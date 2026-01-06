/**
 * AdaptiveQuestion Component
 * 
 * Main interactive question panel with:
 * - Real-time question display
 * - Live option selection
 * - Response time tracking
 * - Immediate feedback
 * - Difficulty visualization
 * - Engagement indicators
 * - Adaptation history
 */

import React, { useState, useEffect } from 'react';
import '../styles/AdaptiveQuestion.css';

const AdaptiveQuestion = ({ question, session, onSubmit, isLoading = false }) => {
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [startTime] = useState(Date.now());
  const [submitted, setSubmitted] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [responseTime, setResponseTime] = useState(0);

  // Calculate response time on component mount
  useEffect(() => {
    return () => {
      const elapsed = (Date.now() - startTime) / 1000;
      setResponseTime(elapsed);
    };
  }, [startTime]);

  const handleSubmit = async () => {
    if (!selectedAnswer) {
      alert('Please select an answer');
      return;
    }

    const elapsed = (Date.now() - startTime) / 1000;

    try {
      const response = await fetch('http://localhost:5000/api/cbt/response/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: session.id,
          question_id: question.question_id,
          student_answer: selectedAnswer,
          response_time_seconds: elapsed
        })
      });

      const data = await response.json();

      if (data.success) {
        setSubmitted(true);
        setFeedback({
          isCorrect: data.is_correct,
          explanation: data.explanation,
          correctAnswer: data.correct_answer,
          newDifficulty: data.current_difficulty,
          responseTime: elapsed
        });
        onSubmit(data);
      } else {
        alert('Error: ' + data.error);
      }
    } catch (error) {
      alert('Failed to submit answer: ' + error.message);
    }
  };

  if (submitted && feedback) {
    return (
      <FeedbackDisplay 
        feedback={feedback} 
        question={question}
        session={session}
      />
    );
  }

  return (
    <div className="adaptive-question-container">
      {/* Question Header */}
      <div className="question-header">
        <h2 className="question-text">{question.question_text}</h2>
        <div className="question-meta">
          <span className="question-number">Q{question.question_number || 1}</span>
          <span className="difficulty-badge">
            <span className="difficulty-label">Difficulty:</span>
            <span className="difficulty-value" style={{
              background: getDifficultyColor(question.difficulty),
              color: 'white',
              padding: '4px 12px',
              borderRadius: '4px',
              fontWeight: '600'
            }}>
              {(question.difficulty * 100).toFixed(0)}%
            </span>
          </span>
        </div>
      </div>

      {/* Options Grid */}
      <div className="options-grid">
        {question.options && question.options.map((option, index) => (
          <button
            key={index}
            className={`option-button ${selectedAnswer === option.letter ? 'selected' : ''}`}
            onClick={() => setSelectedAnswer(option.letter)}
            disabled={isLoading}
          >
            <span className="option-letter">{option.letter}</span>
            <span className="option-text">{option.text}</span>
          </button>
        ))}
      </div>

      {/* Submit Section */}
      <div className="submit-section">
        <button
          className="submit-button"
          onClick={handleSubmit}
          disabled={!selectedAnswer || isLoading}
        >
          {isLoading ? '⏳ Submitting...' : '✓ Submit Answer'}
        </button>
      </div>
    </div>
  );
};

/**
 * Feedback Display Component
 * Shows correctness, explanation, and adaptation details
 */
const FeedbackDisplay = ({ feedback, question, session }) => {
  const getDifficultyDelta = () => {
    const oldDiff = session?.previous_difficulty || 0.5;
    return feedback.newDifficulty - oldDiff;
  };

  const difficultyDelta = getDifficultyDelta();

  return (
    <div className="feedback-container">
      {/* Correctness Badge */}
      <div className={`feedback-badge ${feedback.isCorrect ? 'correct' : 'incorrect'}`}>
        <div className="feedback-icon">
          {feedback.isCorrect ? '✓' : '✗'}
        </div>
        <div className="feedback-text">
          <h3>{feedback.isCorrect ? 'Correct!' : 'Incorrect'}</h3>
          <p>{feedback.isCorrect ? 'Great job!' : `The answer was: ${feedback.correctAnswer}`}</p>
        </div>
      </div>

      {/* Explanation */}
      {feedback.explanation && (
        <div className="explanation-box">
          <h4>Explanation</h4>
          <p>{feedback.explanation}</p>
        </div>
      )}

      {/* Adaptation Indicator */}
      <AdaptationIndicator 
        difficulty={feedback.newDifficulty}
        delta={difficultyDelta}
        responseTime={feedback.responseTime}
      />

      {/* Continue Button */}
      <button className="continue-button" onClick={() => window.location.reload()}>
        → Next Question
      </button>
    </div>
  );
};

/**
 * Adaptation Indicator Component
 * Displays real-time difficulty changes and adaptation rationale
 */
const AdaptationIndicator = ({ difficulty, delta, responseTime }) => {
  const getAdaptationMessage = (delta) => {
    if (Math.abs(delta) < 0.01) return 'Difficulty maintained';
    if (delta > 0) return 'Difficulty increased';
    return 'Difficulty decreased';
  };

  const getAdaptationReason = (delta, responseTime) => {
    if (responseTime < 2) return 'You responded very quickly';
    if (responseTime > 30) return 'You took some time to think';
    if (Math.abs(delta) < 0.01) return 'Performing consistently at this level';
    if (delta > 0) return 'You\'re ready for more challenge';
    return 'Let\'s reinforce the fundamentals';
  };

  return (
    <div className="adaptation-indicator">
      <div className="adaptation-header">
        <h4>🎯 Adaptation Update</h4>
      </div>

      <div className="adaptation-details">
        <div className="detail-row">
          <span className="detail-label">New Difficulty:</span>
          <span className="detail-value" style={{
            background: getDifficultyColor(difficulty),
            color: 'white',
            padding: '6px 14px',
            borderRadius: '6px',
            fontWeight: '600'
          }}>
            {(difficulty * 100).toFixed(0)}%
          </span>
        </div>

        <div className="detail-row">
          <span className="detail-label">Change:</span>
          <span className={`delta-value ${delta > 0 ? 'increase' : delta < 0 ? 'decrease' : 'stable'}`}>
            {delta > 0 ? '+' : ''}{(delta * 100).toFixed(1)}%
          </span>
        </div>

        <div className="detail-row">
          <span className="detail-label">Response Time:</span>
          <span className="detail-value">{responseTime.toFixed(1)}s</span>
        </div>
      </div>

      <div className="adaptation-message">
        <p className="message-title">{getAdaptationMessage(delta)}</p>
        <p className="message-reason">{getAdaptationReason(delta, responseTime)}</p>
      </div>
    </div>
  );
};

/**
 * Helper: Get color based on difficulty level
 */
const getDifficultyColor = (difficulty) => {
  if (difficulty < 0.33) return '#48bb78'; // Green - Easy
  if (difficulty < 0.67) return '#f6ad55'; // Orange - Medium
  return '#f56565'; // Red - Hard
};

export default AdaptiveQuestion;
