/**
 * Quick-Start Example: Complete TestSession Integration
 * 
 * This shows how to use all components together in a real application
 * Copy and adapt for your specific needs
 */

import React, { useState, useEffect } from 'react';
import TestSessionPage from './pages/TestSessionPage';
import { SessionAPI } from './utils/api';

/**
 * Main App Component
 * Handles login and session routing
 */
function App() {
  const [currentStudent, setCurrentStudent] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Check if student is stored in localStorage
  useEffect(() => {
    const stored = localStorage.getItem('currentStudent');
    if (stored) {
      setCurrentStudent(JSON.parse(stored));
    }
  }, []);

  const handleLogin = async (email, name) => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/cbt/student', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, name })
      });

      const data = await response.json();
      if (data.success && data.student) {
        setCurrentStudent(data.student);
        localStorage.setItem('currentStudent', JSON.stringify(data.student));
      } else {
        setError(data.error || 'Login failed');
      }
    } catch (err) {
      setError('Failed to connect to server');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    setCurrentStudent(null);
    localStorage.removeItem('currentStudent');
  };

  if (!currentStudent) {
    return (
      <LoginForm
        onLogin={handleLogin}
        isLoading={isLoading}
        error={error}
      />
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: '#f7fafc' }}>
      <MainInterface
        student={currentStudent}
        onLogout={handleLogout}
      />
    </div>
  );
}

/**
 * Login Form Component
 */
function LoginForm({ onLogin, isLoading, error }) {
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onLogin(email, name);
  };

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }}>
      <div style={{
        background: 'white',
        padding: '50px',
        borderRadius: '12px',
        boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
        maxWidth: '400px',
        width: '100%'
      }}>
        <h1 style={{ textAlign: 'center', color: '#667eea', marginBottom: '30px' }}>
          🎓 Learning Platform
        </h1>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600' }}>
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              required
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '6px',
                fontSize: '16px'
              }}
            />
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600' }}>
              Full Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="John Doe"
              required
              style={{
                width: '100%',
                padding: '12px',
                border: '1px solid #ddd',
                borderRadius: '6px',
                fontSize: '16px'
              }}
            />
          </div>

          {error && (
            <div style={{
              background: '#fee2e2',
              color: '#c53030',
              padding: '12px',
              borderRadius: '6px',
              marginBottom: '20px',
              fontSize: '14px'
            }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            style={{
              width: '100%',
              padding: '12px',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              opacity: isLoading ? 0.6 : 1
            }}
          >
            {isLoading ? 'Signing In...' : 'Sign In / Register'}
          </button>
        </form>
      </div>
    </div>
  );
}

/**
 * Main Interface: Dashboard with Subject Selection
 */
function MainInterface({ student, onLogout }) {
  const [activeTest, setActiveTest] = useState(null);

  const subjects = [
    { name: 'Mathematics', emoji: '📐', color: '#667eea' },
    { name: 'Science', emoji: '🔬', color: '#f5576c' },
    { name: 'English', emoji: '📚', color: '#4facfe' },
    { name: 'History', emoji: '🏛️', color: '#fa709a' }
  ];

  if (activeTest) {
    return (
      <TestSessionPage
        studentId={student.id}
        subject={activeTest}
      />
    );
  }

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '40px 20px' }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '40px'
      }}>
        <div>
          <h1 style={{ margin: '0 0 10px 0', color: '#1a202c' }}>
            Welcome back, {student.name}! 👋
          </h1>
          <p style={{ margin: '0', color: '#4a5568' }}>
            Choose a subject to begin your adaptive learning session
          </p>
        </div>
        <button
          onClick={onLogout}
          style={{
            padding: '10px 20px',
            background: '#e53e3e',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontWeight: '600'
          }}
        >
          Logout
        </button>
      </div>

      {/* Subject Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '20px'
      }}>
        {subjects.map((subject) => (
          <SubjectCard
            key={subject.name}
            {...subject}
            onStart={() => setActiveTest(subject.name)}
          />
        ))}
      </div>

      {/* Info Section */}
      <div style={{
        marginTop: '40px',
        background: 'white',
        padding: '30px',
        borderRadius: '12px',
        boxShadow: '0 2px 12px rgba(0,0,0,0.08)'
      }}>
        <h2 style={{ margin: '0 0 20px 0', color: '#1a202c' }}>
          How Adaptive Learning Works
        </h2>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '20px'
        }}>
          <InfoBox
            icon="🎯"
            title="Personalized Difficulty"
            description="Questions adjust to your skill level in real-time"
          />
          <InfoBox
            icon="📊"
            title="Live Feedback"
            description="See why the difficulty changed and track your progress"
          />
          <InfoBox
            icon="⚡"
            title="Engagement Aware"
            description="System monitors your engagement and adjusts accordingly"
          />
          <InfoBox
            icon="📈"
            title="Learning Optimized"
            description="Find the right balance between challenge and success"
          />
        </div>
      </div>
    </div>
  );
}

/**
 * Subject Selection Card
 */
function SubjectCard({ name, emoji, color, onStart }) {
  return (
    <button
      onClick={onStart}
      style={{
        background: `linear-gradient(135deg, ${color} 0%, ${shadeColor(color, -20)} 100%)`,
        color: 'white',
        border: 'none',
        borderRadius: '12px',
        padding: '40px 20px',
        cursor: 'pointer',
        fontSize: '48px',
        fontWeight: '600',
        textAlign: 'center',
        transition: 'all 0.2s',
        transform: 'scale(1)'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'scale(1.05)';
        e.currentTarget.style.boxShadow = `0 8px 24px rgba(0,0,0,0.15)`;
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'scale(1)';
        e.currentTarget.style.boxShadow = 'none';
      }}
    >
      <div style={{ fontSize: '48px', marginBottom: '10px' }}>
        {emoji}
      </div>
      <div>{name}</div>
      <div style={{ fontSize: '12px', opacity: 0.9, marginTop: '8px' }}>
        Start Test
      </div>
    </button>
  );
}

/**
 * Info Box Component
 */
function InfoBox({ icon, title, description }) {
  return (
    <div style={{
      background: 'linear-gradient(135deg, #f7fafc 0%, #eef2ff 100%)',
      padding: '20px',
      borderRadius: '8px',
      borderLeft: '4px solid #667eea'
    }}>
      <div style={{ fontSize: '28px', marginBottom: '10px' }}>
        {icon}
      </div>
      <h3 style={{ margin: '0 0 8px 0', color: '#1a202c' }}>
        {title}
      </h3>
      <p style={{ margin: '0', color: '#4a5568', fontSize: '14px' }}>
        {description}
      </p>
    </div>
  );
}

/**
 * Utility: Shade color for gradient
 */
function shadeColor(color, percent) {
  const num = parseInt(color.replace('#', ''), 16);
  const amt = Math.round(2.55 * percent);
  const R = (num >> 16) + amt;
  const G = (num >> 8 & 0x00FF) + amt;
  const B = (num & 0x0000FF) + amt;
  return '#' + (
    0x1000000 + (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
    (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
    (B < 255 ? B < 1 ? 0 : B : 255)
  ).toString(16).slice(1);
}

export default App;
