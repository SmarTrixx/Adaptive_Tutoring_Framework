/**
 * EngagementIndicators Component
 * 
 * Real-time display of engagement signals:
 * - Behavioral: response time, hints, navigation
 * - Cognitive: accuracy, progress, confidence
 * - Affective: frustration, interest
 * - Composite engagement score
 */

import React, { useState } from 'react';
import '../styles/EngagementIndicators.css';

const EngagementIndicators = ({ 
  currentEngagement = {}, 
  sessionData = {},
  policyDebug = false 
}) => {
  const [expandedSection, setExpandedSection] = useState('overview');

  const engagement = {
    score: currentEngagement.engagement_score || 0.5,
    level: currentEngagement.engagement_level || 'moderate',
    behavioral: currentEngagement.behavioral || {},
    cognitive: currentEngagement.cognitive || {},
    affective: currentEngagement.affective || {},
    ...currentEngagement
  };

  return (
    <div className="engagement-indicators-panel">
      {/* Main Engagement Score */}
      <EngagementScoreDisplay engagement={engagement} />

      {/* Detailed Indicators */}
      <div className="indicators-grid">
        <IndicatorSection
          title="⚡ Behavioral"
          expanded={expandedSection === 'behavioral'}
          onToggle={() => setExpandedSection(
            expandedSection === 'behavioral' ? 'overview' : 'behavioral'
          )}
        >
          <BehavioralIndicators data={engagement.behavioral || sessionData} />
        </IndicatorSection>

        <IndicatorSection
          title="🧠 Cognitive"
          expanded={expandedSection === 'cognitive'}
          onToggle={() => setExpandedSection(
            expandedSection === 'cognitive' ? 'overview' : 'cognitive'
          )}
        >
          <CognitiveIndicators data={engagement.cognitive || sessionData} />
        </IndicatorSection>

        <IndicatorSection
          title="😊 Affective"
          expanded={expandedSection === 'affective'}
          onToggle={() => setExpandedSection(
            expandedSection === 'affective' ? 'overview' : 'affective'
          )}
        >
          <AffectiveIndicators data={engagement.affective || {}} />
        </IndicatorSection>
      </div>

      {/* Policy Debug Info (Optional) */}
      {policyDebug && (
        <PolicyDebugPanel engagement={engagement} sessionData={sessionData} />
      )}

      {/* Adaptation Recommendations */}
      <AdaptationRecommendation 
        engagement={engagement}
        sessionData={sessionData}
      />
    </div>
  );
};

/**
 * Main Engagement Score Circle
 */
const EngagementScoreDisplay = ({ engagement }) => {
  const score = engagement.score || 0.5;
  const circumference = 2 * Math.PI * 45; // radius = 45
  const offset = circumference * (1 - score);

  return (
    <div className="engagement-score-display">
      <div className="score-circle-container">
        <svg viewBox="0 0 100 100" className="score-circle">
          <circle
            cx="50"
            cy="50"
            r="45"
            className="score-bg"
          />
          <circle
            cx="50"
            cy="50"
            r="45"
            className="score-fill"
            style={{
              strokeDasharray: circumference,
              strokeDashoffset: offset,
              stroke: getEngagementColor(score)
            }}
          />
        </svg>
        <div className="score-text">
          <div className="score-value">{(score * 100).toFixed(0)}%</div>
          <div className="score-label">{getEngagementLabel(score)}</div>
        </div>
      </div>

      <div className="engagement-status">
        <p className="status-message">
          {getEngagementMessage(score)}
        </p>
      </div>
    </div>
  );
};

/**
 * Behavioral Indicators Section
 */
const BehavioralIndicators = ({ data }) => {
  const responseTime = data.response_time_seconds || data.avg_response_time || 5;
  const hintsUsed = data.hints_used || data.hints_requested || 0;
  const navigationFreq = data.navigation_frequency || 0;
  const attempts = data.attempts_count || 1;

  // Response time analysis
  const rtStatus = responseTime < 2 
    ? { label: '⚡ Very Fast', color: '#f56565' }
    : responseTime < 5 
    ? { label: '✓ Normal', color: '#48bb78' }
    : responseTime < 10
    ? { label: '⏳ Thoughtful', color: '#f6ad55' }
    : { label: '⏱️ Slow', color: '#ed8936' };

  return (
    <div className="indicator-group">
      <IndicatorItem
        label="Response Time"
        value={`${responseTime.toFixed(1)}s`}
        status={rtStatus.label}
        color={rtStatus.color}
      />
      <IndicatorItem
        label="Hints Used"
        value={hintsUsed}
        status={hintsUsed === 0 ? 'Independent' : `Asked ${hintsUsed}`}
        color={hintsUsed === 0 ? '#48bb78' : '#f6ad55'}
      />
      <IndicatorItem
        label="Attempts"
        value={attempts}
        status={attempts === 1 ? 'First try' : `Retry ${attempts}`}
        color={attempts === 1 ? '#48bb78' : '#f6ad55'}
      />
      <IndicatorItem
        label="Navigation"
        value={navigationFreq}
        status="page switches"
        color={navigationFreq > 5 ? '#f56565' : '#48bb78'}
      />
    </div>
  );
};

/**
 * Cognitive Indicators Section
 */
const CognitiveIndicators = ({ data }) => {
  const accuracy = (data.accuracy !== undefined 
    ? data.accuracy 
    : data.correct_answers / Math.max(data.total_answered || 1, 1)) || 0;
  
  const progress = data.learning_progress || 0;
  const questionsAnswered = data.total_answered || data.questions_completed || 0;

  return (
    <div className="indicator-group">
      <IndicatorItem
        label="Accuracy"
        value={`${(accuracy * 100).toFixed(0)}%`}
        status={getAccuracyLabel(accuracy)}
        color={getAccuracyColor(accuracy)}
      />
      <IndicatorItem
        label="Progress"
        value={`${(progress * 100).toFixed(0)}%`}
        status="learning trajectory"
        color={progress > 0 ? '#48bb78' : '#f6ad55'}
      />
      <IndicatorItem
        label="Questions Answered"
        value={questionsAnswered}
        status={questionsAnswered < 3 ? 'warming up' : 'in progress'}
        color={questionsAnswered >= 3 ? '#48bb78' : '#f6ad55'}
      />
      <ProgressBar
        label="Knowledge Retention"
        value={Math.min((questionsAnswered / 5) * 100, 100)}
      />
    </div>
  );
};

/**
 * Affective Indicators Section
 */
const AffectiveIndicators = ({ data }) => {
  const frustration = data.frustration_level || 'neutral';
  const interest = data.interest_level || 'moderate';
  const confidence = data.confidence_level || 'moderate';

  const emotionMap = {
    low: '😔',
    neutral: '😐',
    moderate: '🙂',
    high: '😊',
    very_high: '😄'
  };

  return (
    <div className="indicator-group">
      <EmotionIndicator
        label="Frustration"
        level={frustration}
        emoji={emotionMap[frustration] || '😐'}
        negative={true}
      />
      <EmotionIndicator
        label="Interest"
        level={interest}
        emoji={emotionMap[interest] || '🙂'}
        negative={false}
      />
      <EmotionIndicator
        label="Confidence"
        level={confidence}
        emoji={emotionMap[confidence] || '🙂'}
        negative={false}
      />
    </div>
  );
};

/**
 * Indicator Item Component
 */
const IndicatorItem = ({ label, value, status, color }) => (
  <div className="indicator-item">
    <div className="indicator-top">
      <span className="indicator-label">{label}</span>
      <span 
        className="indicator-value"
        style={{ color: color || '#667eea' }}
      >
        {value}
      </span>
    </div>
    <span className="indicator-status">{status}</span>
  </div>
);

/**
 * Emotion Indicator Component
 */
const EmotionIndicator = ({ label, level, emoji, negative = false }) => {
  const levelMap = {
    low: { color: '#48bb78', width: '20%' },
    neutral: { color: '#f6ad55', width: '40%' },
    moderate: { color: '#f6ad55', width: '60%' },
    high: { color: '#667eea', width: '80%' },
    very_high: { color: '#667eea', width: '100%' }
  };

  const config = levelMap[level] || levelMap.moderate;
  
  if (negative) {
    config.color = level === 'low' 
      ? '#48bb78' 
      : level === 'neutral' || level === 'moderate'
      ? '#f6ad55'
      : '#f56565';
  }

  return (
    <div className="emotion-indicator">
      <div className="emotion-header">
        <span className="emotion-emoji">{emoji}</span>
        <span className="emotion-label">{label}</span>
        <span className="emotion-level">{level.toUpperCase()}</span>
      </div>
      <div className="emotion-bar">
        <div 
          className="emotion-fill"
          style={{
            width: config.width,
            backgroundColor: config.color
          }}
        />
      </div>
    </div>
  );
};

/**
 * Progress Bar Component
 */
const ProgressBar = ({ label, value }) => (
  <div className="progress-bar-item">
    <span className="progress-label">{label}</span>
    <div className="progress-bar">
      <div 
        className="progress-fill"
        style={{ width: `${value}%` }}
      />
    </div>
    <span className="progress-value">{value.toFixed(0)}%</span>
  </div>
);

/**
 * Indicator Section (Collapsible)
 */
const IndicatorSection = ({ title, expanded, onToggle, children }) => (
  <div className={`indicator-section ${expanded ? 'expanded' : ''}`}>
    <div 
      className="section-header"
      onClick={onToggle}
    >
      <span>{title}</span>
      <span className="toggle-arrow">{expanded ? '▼' : '▶'}</span>
    </div>
    {expanded && (
      <div className="section-content">
        {children}
      </div>
    )}
  </div>
);

/**
 * Policy Debug Panel
 */
const PolicyDebugPanel = ({ engagement, sessionData }) => {
  return (
    <div className="policy-debug-panel">
      <h4>🔧 Policy Debug (Dev Only)</h4>
      <div className="debug-grid">
        <DebugItem 
          label="Window Size" 
          value="5 questions" 
        />
        <DebugItem 
          label="Current Window Acc" 
          value={`${(engagement.accuracy || 0).toFixed(1)}%`}
        />
        <DebugItem 
          label="Engagement Fused" 
          value={`${(engagement.score * 100).toFixed(0)}%`}
        />
        <DebugItem 
          label="Rushing Detected" 
          value={engagement.behavioral?.response_time_seconds < 2 ? 'YES' : 'NO'}
        />
        <DebugItem 
          label="Oscillation Check" 
          value="monitoring"
        />
        <DebugItem 
          label="Momentum Tracking" 
          value="active"
        />
      </div>
    </div>
  );
};

const DebugItem = ({ label, value }) => (
  <div className="debug-item">
    <span className="debug-label">{label}:</span>
    <span className="debug-value">{value}</span>
  </div>
);

/**
 * Adaptation Recommendation
 */
const AdaptationRecommendation = ({ engagement, sessionData }) => {
  const getRecommendation = () => {
    const score = engagement.score || 0.5;
    const accuracy = engagement.cognitive?.accuracy || 0;
    const frustration = engagement.affective?.frustration_level || 'neutral';

    if (frustration === 'high') {
      return {
        icon: '⚠️',
        message: 'Student appears frustrated. Consider reducing difficulty or providing hints.',
        color: '#f56565'
      };
    }

    if (score < 0.3) {
      return {
        icon: '📉',
        message: 'Low engagement detected. Difficulty will decrease to re-engage.',
        color: '#ed8936'
      };
    }

    if (accuracy > 0.85 && engagement.behavioral?.response_time_seconds > 8) {
      return {
        icon: '✓',
        message: 'High performance with thoughtful responses. Difficulty may increase.',
        color: '#48bb78'
      };
    }

    if (accuracy > 0.85 && engagement.behavioral?.response_time_seconds < 2) {
      return {
        icon: '⚡',
        message: 'Excellent accuracy but very fast. System is cautious about advancing.',
        color: '#667eea'
      };
    }

    return {
      icon: '😊',
      message: 'Engaged and performing well. Continuing at current difficulty.',
      color: '#48bb78'
    };
  };

  const rec = getRecommendation();

  return (
    <div className="adaptation-recommendation" style={{ borderLeftColor: rec.color }}>
      <span className="rec-icon">{rec.icon}</span>
      <p className="rec-message">{rec.message}</p>
    </div>
  );
};

/**
 * Helper Functions
 */
const getEngagementColor = (score) => {
  if (score < 0.33) return '#f56565';
  if (score < 0.67) return '#f6ad55';
  return '#48bb78';
};

const getEngagementLabel = (score) => {
  if (score < 0.33) return 'Low';
  if (score < 0.67) return 'Moderate';
  return 'High';
};

const getEngagementMessage = (score) => {
  if (score < 0.2) return 'Very low engagement. Consider taking a break.';
  if (score < 0.4) return 'Low engagement. Difficulty adjusting to re-engage.';
  if (score < 0.6) return 'Moderate engagement. Finding the right level.';
  if (score < 0.8) return 'Good engagement. Keep up the momentum!';
  return 'Excellent engagement! You\'re in the zone.';
};

const getAccuracyLabel = (accuracy) => {
  if (accuracy >= 0.9) return 'Excellent';
  if (accuracy >= 0.7) return 'Good';
  if (accuracy >= 0.5) return 'Fair';
  return 'Needs improvement';
};

const getAccuracyColor = (accuracy) => {
  if (accuracy >= 0.9) return '#48bb78';
  if (accuracy >= 0.7) return '#667eea';
  if (accuracy >= 0.5) return '#f6ad55';
  return '#f56565';
};

export default EngagementIndicators;
