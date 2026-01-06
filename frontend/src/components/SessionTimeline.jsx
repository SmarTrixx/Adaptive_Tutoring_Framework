/**
 * SessionTimeline Component
 * 
 * Displays progression through test with:
 * - Question history
 * - Correctness indicators
 * - Difficulty at each step
 * - Engagement metrics
 * - Decision rationale
 */

import React from 'react';
import '../styles/SessionTimeline.css';

const SessionTimeline = ({ 
  session, 
  responses = [], 
  engagementHistory = [],
  adaptationHistory = [] 
}) => {
  if (!responses || responses.length === 0) {
    return (
      <div className="timeline-empty">
        <p>No questions answered yet. Answer your first question to see progression.</p>
      </div>
    );
  }

  return (
    <div className="session-timeline">
      <div className="timeline-header">
        <h3>📋 Question History</h3>
        <p className="timeline-subtitle">
          Track your progress, difficulty changes, and adaptive adjustments
        </p>
      </div>

      <div className="timeline-stats">
        <div className="stat-item">
          <span className="stat-label">Questions Answered</span>
          <span className="stat-value">{responses.length}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Correct</span>
          <span className="stat-value correct">
            {responses.filter(r => r.is_correct).length}
          </span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Accuracy</span>
          <span className="stat-value">
            {responses.length > 0 
              ? Math.round((responses.filter(r => r.is_correct).length / responses.length) * 100)
              : 0}%
          </span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Avg Response Time</span>
          <span className="stat-value">
            {responses.length > 0
              ? (responses.reduce((sum, r) => sum + (r.response_time_seconds || 0), 0) / responses.length).toFixed(1)
              : 0}s
          </span>
        </div>
      </div>

      <div className="timeline-entries">
        {responses.map((response, index) => {
          const adaptation = adaptationHistory[index];
          const engagement = engagementHistory[index];

          return (
            <TimelineEntry
              key={index}
              questionNumber={index + 1}
              response={response}
              adaptation={adaptation}
              engagement={engagement}
              previousDifficulty={index > 0 ? responses[index - 1].difficulty : 0.5}
            />
          );
        })}
      </div>

      {/* Difficulty Trajectory */}
      <DifficultyTrajectory responses={responses} />

      {/* Engagement Over Time */}
      <EngagementTrajectory engagementHistory={engagementHistory} />
    </div>
  );
};

/**
 * Individual Timeline Entry
 */
const TimelineEntry = ({ 
  questionNumber, 
  response, 
  adaptation, 
  engagement,
  previousDifficulty 
}) => {
  const difficultyDelta = (response.difficulty || 0) - previousDifficulty;
  const difficultyColor = getDifficultyColor(response.difficulty);

  return (
    <div className="timeline-entry">
      {/* Question Number and Correctness */}
      <div className="entry-marker">
        <div className={`marker-circle ${response.is_correct ? 'correct' : 'incorrect'}`}>
          {response.is_correct ? '✓' : '✗'}
        </div>
        <div className="marker-line" />
      </div>

      {/* Entry Content */}
      <div className="entry-content">
        <div className="entry-header">
          <span className="question-num">Question {questionNumber}</span>
          <span className="correctness-badge">
            {response.is_correct ? '✓ Correct' : '✗ Incorrect'}
          </span>
        </div>

        <div className="entry-details">
          <DetailRow 
            label="Difficulty"
            value={`${(response.difficulty * 100).toFixed(0)}%`}
            color={difficultyColor}
          />

          <DetailRow 
            label="Change"
            value={`${difficultyDelta > 0 ? '+' : ''}${(difficultyDelta * 100).toFixed(1)}%`}
            className={difficultyDelta > 0 ? 'increase' : difficultyDelta < 0 ? 'decrease' : 'stable'}
          />

          <DetailRow 
            label="Response Time"
            value={`${response.response_time_seconds?.toFixed(1) || '0.0'}s`}
          />

          {engagement && (
            <DetailRow 
              label="Engagement"
              value={`${(engagement.engagement_score * 100).toFixed(0)}%`}
              color={getEngagementColor(engagement.engagement_score)}
            />
          )}
        </div>

        {/* Adaptation Rationale */}
        {adaptation && (
          <div className="adaptation-rationale">
            <strong>Policy Decision:</strong>
            <p>{adaptation.rationale || 'Difficulty adjusted based on performance and engagement.'}</p>
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * Detail Row Component
 */
const DetailRow = ({ label, value, color, className = '' }) => (
  <div className={`detail-row ${className}`}>
    <span className="detail-label">{label}:</span>
    <span 
      className="detail-value"
      style={color ? { color: color } : {}}
    >
      {value}
    </span>
  </div>
);

/**
 * Difficulty Trajectory Chart
 * Simple visualization of difficulty progression
 */
const DifficultyTrajectory = ({ responses }) => {
  if (!responses || responses.length < 2) return null;

  const maxDifficulty = Math.max(...responses.map(r => r.difficulty || 0), 1);
  const minDifficulty = Math.min(...responses.map(r => r.difficulty || 0), 0);
  const range = maxDifficulty - minDifficulty || 1;

  return (
    <div className="trajectory-chart">
      <h4>Difficulty Progression</h4>
      <div className="chart-container">
        {responses.map((response, index) => {
          const normalized = ((response.difficulty - minDifficulty) / range) * 100;
          return (
            <div 
              key={index}
              className="chart-bar"
              style={{ height: `${normalized}%` }}
              title={`Q${index + 1}: ${(response.difficulty * 100).toFixed(0)}%`}
            />
          );
        })}
      </div>
      <div className="chart-labels">
        <span>Easy</span>
        <span>Hard</span>
      </div>
    </div>
  );
};

/**
 * Engagement Trajectory Chart
 */
const EngagementTrajectory = ({ engagementHistory }) => {
  if (!engagementHistory || engagementHistory.length < 2) return null;

  const validScores = engagementHistory.filter(e => e?.engagement_score !== undefined);
  if (validScores.length < 2) return null;

  const maxScore = Math.max(...validScores.map(e => e.engagement_score), 1);
  const minScore = Math.min(...validScores.map(e => e.engagement_score), 0);
  const range = maxScore - minScore || 1;

  return (
    <div className="trajectory-chart engagement-chart">
      <h4>Engagement Over Time</h4>
      <div className="chart-container">
        {engagementHistory.map((engagement, index) => {
          const score = engagement?.engagement_score || 0;
          const normalized = ((score - minScore) / range) * 100;
          return (
            <div 
              key={index}
              className="chart-bar engagement-bar"
              style={{ 
                height: `${normalized}%`,
                backgroundColor: getEngagementColor(score)
              }}
              title={`Q${index + 1}: ${(score * 100).toFixed(0)}%`}
            />
          );
        })}
      </div>
      <div className="chart-labels">
        <span>Low</span>
        <span>High</span>
      </div>
    </div>
  );
};

/**
 * Helper Functions
 */
const getDifficultyColor = (difficulty) => {
  if (difficulty < 0.33) return '#48bb78'; // Green - Easy
  if (difficulty < 0.67) return '#f6ad55'; // Orange - Medium
  return '#f56565'; // Red - Hard
};

const getEngagementColor = (engagement) => {
  if (engagement < 0.33) return '#fc8181'; // Red - Low
  if (engagement < 0.67) return '#fbd38d'; // Yellow - Medium
  return '#9ae6b4'; // Green - High
};

export default SessionTimeline;
