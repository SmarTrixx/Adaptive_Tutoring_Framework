/**
 * API Service Utilities
 * 
 * Provides abstracted API calls for backend integration
 * Handles all communication with adaptive tutoring backend
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

/**
 * Session Management
 */
export const SessionAPI = {
  /**
   * Start a new test session
   */
  startSession: async (studentId, numQuestions, subject) => {
    const response = await fetch(`${API_BASE_URL}/cbt/session/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        student_id: studentId,
        num_questions: numQuestions,
        subject: subject
      })
    });

    if (!response.ok) throw new Error('Failed to start session');
    return response.json();
  },

  /**
   * Get next question in session
   */
  getNextQuestion: async (sessionId) => {
    const response = await fetch(
      `${API_BASE_URL}/cbt/question/next/${sessionId}`
    );

    if (!response.ok) throw new Error('Failed to fetch question');
    return response.json();
  },

  /**
   * Get session summary
   */
  getSessionSummary: async (sessionId) => {
    const response = await fetch(
      `${API_BASE_URL}/cbt/session/${sessionId}`
    );

    if (!response.ok) throw new Error('Failed to fetch session summary');
    return response.json();
  },

  /**
   * End the session
   */
  endSession: async (sessionId) => {
    const response = await fetch(
      `${API_BASE_URL}/cbt/session/end/${sessionId}`,
      { method: 'POST' }
    );

    if (!response.ok) throw new Error('Failed to end session');
    return response.json();
  }
};

/**
 * Response Submission
 */
export const ResponseAPI = {
  /**
   * Submit answer to a question
   * Returns: is_correct, current_difficulty, explanation, engagement data
   */
  submitResponse: async (sessionId, questionId, studentAnswer, responseTime) => {
    const response = await fetch(`${API_BASE_URL}/cbt/response/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        question_id: questionId,
        student_answer: studentAnswer,
        response_time_seconds: responseTime
      })
    });

    if (!response.ok) throw new Error('Failed to submit response');
    const data = await response.json();

    return {
      isCorrect: data.is_correct,
      explanation: data.explanation,
      correctAnswer: data.correct_answer,
      currentDifficulty: data.current_difficulty,
      score: data.current_score,
      totalAnswered: data.total_answered,
      correctCount: data.correct_count
    };
  },

  /**
   * Get hint for a question
   */
  getHint: async (sessionId, questionId, hintIndex = 0) => {
    const response = await fetch(
      `${API_BASE_URL}/cbt/hint/${sessionId}/${questionId}?hint_index=${hintIndex}`
    );

    if (!response.ok) throw new Error('Failed to fetch hint');
    return response.json();
  }
};

/**
 * Engagement Tracking
 */
export const EngagementAPI = {
  /**
   * Get latest engagement data for session
   */
  getLastEngagement: async (sessionId) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/engagement/last/${sessionId}`
      );

      if (!response.ok) return null;
      return response.json();
    } catch (error) {
      console.warn('Engagement fetch failed:', error);
      return null;
    }
  },

  /**
   * Track engagement manually (optional)
   */
  trackEngagement: async (studentId, sessionId, responseData) => {
    try {
      await fetch(`${API_BASE_URL}/engagement/track`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: studentId,
          session_id: sessionId,
          response_data: responseData
        })
      });
    } catch (error) {
      console.warn('Engagement tracking failed:', error);
    }
  }
};

/**
 * Adaptation & Policy
 */
export const AdaptationAPI = {
  /**
   * Get adaptation logs for session
   */
  getAdaptationLogs: async (sessionId) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/adaptation/logs/${sessionId}`
      );

      if (!response.ok) return [];
      return response.json();
    } catch (error) {
      console.warn('Adaptation logs fetch failed:', error);
      return [];
    }
  },

  /**
   * Get adaptation effectiveness analysis
   */
  getEffectiveness: async (sessionId) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/adaptation/effectiveness/${sessionId}`
      );

      if (!response.ok) return null;
      return response.json();
    } catch (error) {
      console.warn('Effectiveness fetch failed:', error);
      return null;
    }
  }
};

/**
 * Analytics
 */
export const AnalyticsAPI = {
  /**
   * Get student analytics
   */
  getStudentAnalytics: async (studentId) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/analytics/student/${studentId}`
      );

      if (!response.ok) return null;
      return response.json();
    } catch (error) {
      console.warn('Analytics fetch failed:', error);
      return null;
    }
  },

  /**
   * Evaluate adaptation effectiveness
   */
  evaluateAdaptation: async (studentId, sessionId) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/analytics/eval-adaptation/${studentId}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ session_id: sessionId })
        }
      );

      if (!response.ok) return null;
      return response.json();
    } catch (error) {
      console.warn('Adaptation evaluation failed:', error);
      return null;
    }
  }
};

/**
 * Error Handler
 * Provides consistent error handling across API calls
 */
export const handleAPIError = (error, context = '') => {
  console.error(`API Error [${context}]:`, error);

  if (error.message.includes('Failed')) {
    return {
      error: true,
      message: error.message,
      context: context
    };
  }

  if (error.statusCode === 401) {
    return {
      error: true,
      message: 'Not authenticated. Please log in.',
      context: context
    };
  }

  if (error.statusCode === 404) {
    return {
      error: true,
      message: 'Resource not found.',
      context: context
    };
  }

  return {
    error: true,
    message: 'An unexpected error occurred. Please try again.',
    context: context
  };
};

/**
 * Utility: Calculate response time from timestamp
 */
export const calculateResponseTime = (startTime, endTime = null) => {
  const end = endTime || Date.now();
  return (end - startTime) / 1000; // seconds
};

/**
 * Utility: Format difficulty as percentage
 */
export const formatDifficulty = (difficulty) => {
  return `${(difficulty * 100).toFixed(0)}%`;
};

/**
 * Utility: Get difficulty color
 */
export const getDifficultyColor = (difficulty) => {
  if (difficulty < 0.33) return '#48bb78'; // Green
  if (difficulty < 0.67) return '#f6ad55'; // Orange
  return '#f56565'; // Red
};

/**
 * Utility: Get engagement color
 */
export const getEngagementColor = (score) => {
  if (score < 0.33) return '#f56565'; // Red
  if (score < 0.67) return '#f6ad55'; // Orange
  return '#48bb78'; // Green
};

export default {
  SessionAPI,
  ResponseAPI,
  EngagementAPI,
  AdaptationAPI,
  AnalyticsAPI,
  handleAPIError,
  calculateResponseTime,
  formatDifficulty,
  getDifficultyColor,
  getEngagementColor
};
