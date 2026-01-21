import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/Chat.css';

const Chat = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const [sessionId, setSessionId] = useState(null);
  const [userData, setUserData] = useState({
    name: 'Guest',
    height: null,
    weight: null,
    bmi: null,
    bmi_category: null,
    goal: null,
    age: null
  });
  const [isInitialized, setIsInitialized] = useState(false);
  const [fitnessData, setFitnessData] = useState({
    caloriesTarget: 2200,
    caloriesConsumed: 360,
    steps: 8432,
    activeMinutes: 42,
    protein: { current: 120, target: 150 },
    carbs: { current: 180, target: 300 },
    fats: { current: 60, target: 150 },
    hydration: { current: 1.8, target: 2.5 }
  });

  // Calculate dynamic calorie target based on BMI and goal
  const calculateCalorieTarget = () => {
    if (!userData.weight || !userData.height) return 2200;
    const bmr = userData.weight * 24; // Simplified BMR
    if (userData.goal?.toLowerCase().includes('loss')) return Math.round(bmr - 500);
    if (userData.goal?.toLowerCase().includes('gain')) return Math.round(bmr + 500);
    return Math.round(bmr);
  };

  const getFlexaInsight = () => {
    const caloriesLeft = fitnessData.caloriesTarget - fitnessData.caloriesConsumed;
    
    if (!userData.bmi) {
      return "Complete your profile to get personalized insights from Flexa AI!";
    }
    
    if (userData.bmi < 18.5) {
      return `You're underweight (BMI: ${userData.bmi}). Focus on high-protein meals and aim for ${Math.round(caloriesLeft)} more calories today.`;
    } else if (userData.bmi > 25) {
      if (caloriesLeft < 500) {
        return `Great job! You're ${caloriesLeft} kcal under target. A protein-rich snack would optimize recovery.`;
      }
      return `You're on track for weight management. Keep your protein intake high and stay active!`;
    } else {
      if (fitnessData.activeMinutes < 30) {
        return "You're doing well! Try to add 15 more active minutes to hit your daily goal.";
      }
      return `Excellent progress! Your balanced approach is working. Keep it up! 💪`;
    }
  };

  // Update calorie target when user data changes
  useEffect(() => {
    if (userData.weight && userData.height) {
      const newTarget = calculateCalorieTarget();
      setFitnessData(prev => ({ ...prev, caloriesTarget: newTarget }));
    }
  }, [userData.weight, userData.height, userData.goal]);

  // Initialize chat session
  useEffect(() => {
    if (isInitialized) return;
    
    const initChat = async () => {
      try {
        const response = await fetch('http://localhost:5000/chat/start');
        const data = await response.json();
        setSessionId(data.session_id);
        setMessages([{
          id: 1,
          type: 'ai',
          content: data.message,
          timestamp: new Date()
        }]);
        setIsInitialized(true);
      } catch (error) {
        console.error('Error initializing chat:', error);
        setMessages([{
          id: 1,
          type: 'ai',
          content: 'Hi! I\'m Flexa 👋 What\'s your name?',
          timestamp: new Date()
        }]);
        setIsInitialized(true);
      }
    };
    initChat();
  }, [isInitialized]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const addMessage = (message) => {
    setMessages((prev) => [
      ...prev,
      {
        id: prev.length + 1,
        timestamp: new Date(),
        ...message
      }
    ]);
  };

  const formatMLResponse = (content) => {
    // Replace escaped newlines with actual newlines
    const cleanContent = content.replace(/\\n/g, '\n');
    
    // Check if this is an ML recommendation response or video list
    if (cleanContent.includes('personalized plan') || cleanContent.includes('ML-based') || cleanContent.includes('WORKOUT VIDEOS') || cleanContent.includes('🔗 Watch:')) {
      const lines = cleanContent.split('\n');
      let formatted = [];
      
      lines.forEach((line, idx) => {
        const trimmed = line.trim();
        if (!trimmed) return;
        
        // Check for YouTube links
        if (trimmed.includes('🔗 Watch:') || (trimmed.includes('youtube.com') || trimmed.includes('youtu.be'))) {
          const urlMatch = trimmed.match(/(https?:\/\/[^\s]+)/);
          if (urlMatch) {
            const url = urlMatch[1];
            const label = trimmed.replace(url, '').replace('🔗 Watch:', '').trim() || 'Watch Video';
            formatted.push({ type: 'video-link', content: label, url: url, key: idx });
            return;
          }
        }
        
        if (trimmed.startsWith('⚠️')) {
          formatted.push({ type: 'warning', content: trimmed, key: idx });
        } else if (trimmed.startsWith('✅')) {
          formatted.push({ type: 'header', content: trimmed, key: idx });
        } else if (trimmed.startsWith('📊') || trimmed.startsWith('▶️')) {
          formatted.push({ type: 'section-header', content: trimmed, key: idx });
        } else if (trimmed.startsWith('🏋️') || trimmed.startsWith('🧰') || trimmed.startsWith('🥗') || trimmed.startsWith('📌')) {
          formatted.push({ type: 'info-item', content: trimmed, key: idx });
        } else if (trimmed.startsWith('•')) {
          formatted.push({ type: 'bullet', content: trimmed.substring(1).trim(), key: idx });
        } else if (trimmed.match(/^\d+\./)) {
          // Numbered list item (for video titles)
          formatted.push({ type: 'numbered', content: trimmed, key: idx });
        } else if (trimmed.startsWith('⏱')) {
          formatted.push({ type: 'meta', content: trimmed, key: idx });
        } else if (trimmed.includes('YouTube') || trimmed.includes('videos')) {
          formatted.push({ type: 'question', content: trimmed, key: idx });
        } else if (trimmed.length > 0) {
          formatted.push({ type: 'text', content: trimmed, key: idx });
        }
      });
      
      return formatted;
    }
    return null;
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || !sessionId) return;

    const text = inputValue.trim();
    addMessage({ type: 'user', content: text });
    setInputValue('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:5000/chat/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          user_message: text
        })
      });

      const data = await response.json();

      addMessage({
        type: 'ai',
        content: data.message || 'I encountered an issue. Please try again.'
      });

      // Update user data if provided by backend
      if (data.user_data) {
        setUserData(prev => ({
          ...prev,
          ...data.user_data
        }));
      }
      
      // Update from data_collected if available
      if (data.data_collected) {
        const collected = data.data_collected;
        setUserData(prev => ({
          ...prev,
          name: collected.name || prev.name,
          height: collected.height_m ? Math.round(collected.height_m * 100) : prev.height,
          weight: collected.weight_kg || prev.weight,
          bmi: collected.bmi || prev.bmi,
          bmi_category: collected.bmi_category || prev.bmi_category,
          goal: collected.problem || prev.goal,
          age: collected.age || prev.age
        }));
      }
    } catch (error) {
      console.error('Error:', error);
      addMessage({
        type: 'ai',
        content: 'Sorry, I couldn\'t process your request. Please try again.'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleNewChat = async () => {
    setIsInitialized(false);
    setMessages([]);
    setSessionId(null);
    setUserData({
      name: 'Guest',
      height: null,
      weight: null,
      bmi: null,
      bmi_category: null
    });
    
    // Initialize new session
    try {
      const response = await fetch('http://localhost:5000/chat/start');
      const data = await response.json();
      setSessionId(data.session_id);
      setMessages([{
        id: 1,
        type: 'ai',
        content: data.message,
        timestamp: new Date()
      }]);
      setIsInitialized(true);
    } catch (error) {
      console.error('Error starting new chat:', error);
      setMessages([{
        id: 1,
        type: 'ai',
        content: 'Hi! I\'m Flexa 👋 What\'s your name?',
        timestamp: new Date()
      }]);
      setIsInitialized(true);
    }
  };

  const handleLogoClick = () => {
    navigate('/');
  };

  return (
    <div className="chat-container">
      {/* Sidebar */}
      <aside className="chat-sidebar">
        <div className="sidebar-header">
          <div className="flexa-logo" onClick={handleLogoClick} style={{ cursor: 'pointer' }}>
            <video autoPlay loop muted playsInline style={{ width: '100%', height: '100%', borderRadius: '0.75rem', objectFit: 'cover' }}>
              <source src="/Bot1.mp4" type="video/mp4" />
            </video>
          </div>
          <h2 onClick={handleLogoClick} style={{ cursor: 'pointer' }}>Flexa AI</h2>
        </div>
        <button className="new-chat-btn" onClick={handleNewChat}>

          New Chat
        </button>
        <nav className="chat-history">
          <p className="history-title">Chat History</p>
          <a href="#" className="history-item active">

            <span>Current Chat</span>
          </a>
          <a href="#" className="history-item">

            <span>Previous Chat</span>
          </a>
          <a href="#" className="history-item">

            <span>Older Chat</span>
          </a>
        </nav>
      </aside>

      {/* Main Chat */}
      <main className="chat-main">
        {/* Header */}
        <header className="chat-header">
          <div className="header-left">
            <div className="status-dot"></div>
            <h3>Chat with Flexa AI</h3>
          </div>
          <div className="header-actions">
            <button><span className="material-symbols-outlined">search</span></button>
            <button><span className="material-symbols-outlined">Login</span></button>
          </div>
        </header>

        {/* Messages */}
        <div className="messages-container">
          {messages.map((msg) => (
            <div key={msg.id} className={`message ${msg.type}`}>
              {msg.type === 'ai' && (
                <div className="ai-avatar">
                  <video autoPlay loop muted playsInline style={{ width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover' }}>
                    <source src="/Bot1.mp4" type="video/mp4" />
                  </video>
                </div>
              )}
              <div className="message-content">
                {msg.type === 'ai' && <p className="message-label">FLEXA AI</p>}
                {msg.type === 'user' && <p className="message-label">YOU</p>}
                <div className="message-bubble">
                  {(() => {
                    const formatted = msg.type === 'ai' ? formatMLResponse(msg.content) : null;
                    if (formatted) {
                      return (
                        <div className="ml-recommendation">
                          {formatted.map((item) => {
                            switch (item.type) {
                              case 'warning':
                                return <div key={item.key} style={{ backgroundColor: 'rgba(255, 243, 205, 0.2)', padding: '14px', borderRadius: '8px', marginBottom: '16px', color: '#fff', fontWeight: '500', fontSize: '14px', border: '1px solid rgba(255, 255, 255, 0.3)' }}>{item.content}</div>;
                              case 'header':
                                return <div key={item.key} style={{ fontSize: '18px', fontWeight: '700', marginBottom: '20px', color: '#fff', lineHeight: '1.4' }}>{item.content}</div>;
                              case 'section-header':
                                return <div key={item.key} style={{ fontSize: '16px', fontWeight: '700', marginTop: '16px', marginBottom: '10px', color: '#fff', borderBottom: '2px solid rgba(255, 255, 255, 0.5)', paddingBottom: '6px' }}>{item.content}</div>;
                              case 'bullet':
                                return <div key={item.key} style={{ paddingLeft: '24px', marginBottom: '8px', color: '#fff', fontSize: '14px', lineHeight: '1.6' }}>• {item.content}</div>;
                              case 'numbered':
                                return <div key={item.key} style={{ marginBottom: '8px', color: '#fff', fontSize: '14px', fontWeight: '600', lineHeight: '1.6' }}>{item.content}</div>;
                              case 'meta':
                                return <div key={item.key} style={{ paddingLeft: '24px', marginBottom: '6px', color: 'rgba(255, 255, 255, 0.9)', fontSize: '13px', lineHeight: '1.5' }}>{item.content}</div>;
                              case 'video-link':
                                return <div key={item.key} style={{ paddingLeft: '24px', marginBottom: '8px' }}>
                                  <a href={item.url} target="_blank" rel="noopener noreferrer" style={{ color: '#fff', textDecoration: 'underline', fontSize: '14px', fontWeight: '500', display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                                    🔗 {item.content}
                                  </a>
                                </div>;
                              case 'info-item':
                                return <div key={item.key} style={{ marginBottom: '14px', padding: '12px 14px', backgroundColor: 'rgba(255, 255, 255, 0.15)', borderRadius: '8px', borderLeft: '4px solid #fff', color: '#fff', fontSize: '14px', fontWeight: '500', lineHeight: '1.6' }}>{item.content}</div>;
                              case 'question':
                                return <div key={item.key} style={{ marginTop: '20px', fontWeight: '600', color: '#fff', fontSize: '15px' }}>{item.content}</div>;
                              default:
                                return <div key={item.key} style={{ marginBottom: '10px', color: '#fff', fontSize: '14px', lineHeight: '1.6' }}>{item.content}</div>;
                            }
                          })}
                        </div>
                      );
                    }
                    // For user messages, use black text; for AI messages, use white
                    // Replace escaped newlines with actual newlines
                    const cleanContent = msg.content.replace(/\\n/g, '\n');
                    const textColor = msg.type === 'user' ? '#000' : '#fff';
                    return <div style={{ whiteSpace: 'pre-wrap', color: textColor }}>{cleanContent}</div>;
                  })()}
                </div>
                {msg.metadata && (
                  <div className="message-metadata">
                    {msg.metadata.type === 'workout' && (
                      <div className="metadata-card">
                        <span className="material-symbols-outlined">timer</span>
                        <div>
                          <p>{msg.metadata.title}</p>
                          <span>{msg.metadata.duration} • {msg.metadata.intensity}</span>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
              {msg.type === 'user' && (
                <div className="user-avatar">
                  <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuBo5Q_YJZol5yqqQwfkBIFcVS_17DIvf95eVOCPoZTanv_L4_gxowvCpnQ0e1ij3T-rzgUIkNaMMvT2cmo9-QEclBiQ2EJet01qOS6USzIIomJ_oNCDRt2gbP6dWeMWmG9suE5g_lNinhf7cFyyxIuKXHM-RQtkyuC6nhccyZ-Ws2PTG4yRUPQPqvM0wf0_KNvwfK_uYwowGlMm1kst22jsJ5-qRoA_dPr3hf_DbL5rxX6UxLq9p5RAQZiJb1A2XG0INeTdzNsMkO1W" alt="User" />
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="message ai">
              <div className="ai-avatar">
                <video autoPlay loop muted playsInline style={{ width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover' }}>
                  <source src="/Bot1.mp4" type="video/mp4" />
                </video>
              </div>
              <div className="loading-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <footer className="chat-footer">
          <div className="input-container">
            <button className="input-action">
              <img src="/attachment.png" alt="attachment" style={{ width: '24px', height: '24px' }} />
            </button>
            <input
              type="text"
              placeholder="Ask Flexa about your fitness journey..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={loading}
            />
            <button onClick={sendMessage} disabled={loading} className="send-btn">
              <img src="/send2.png" alt="send" style={{ width: '24px', height: '24px' }} />
            </button>
          </div>
          <p className="chat-disclaimer">Flexa may provide suggestions based on AI. Consult a doctor before starting new routines.</p>
        </footer>
      </main>

      {/* Right Sidebar - Dashboard */}
      <aside className="chat-dashboard">
        <h2>Fitness Dashboard</h2>

        {/* User Profile Card */}
        <div className="user-profile-card">
          <div className="profile-header">
            <div className="profile-avatar">
              <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuBo5Q_YJZol5yqqQwfkBIFcVS_17DIvf95eVOCPoZTanv_L4_gxowvCpnQ0e1ij3T-rzgUIkNaMMvT2cmo9-QEclBiQ2EJet01qOS6USzIIomJ_oNCDRt2gbP6dWeMWmG9suE5g_lNinhf7cFyyxIuKXHM-RQtkyuC6nhccyZ-Ws2PTG4yRUPQPqvM0wf0_KNvwfK_uYwowGlMm1kst22jsJ5-qRoA_dPr3hf_DbL5rxX6UxLq9p5RAQZiJb1A2XG0INeTdzNsMkO1W" alt="Profile" />
            </div>
            <div className="profile-info">
              <h3>{userData.name}</h3>
              <p className="profile-status">Active</p>
            </div>
          </div>

          {/* User Metrics */}
          <div className="profile-metrics">
            <div className="metric-item">
              <span className="metric-label">Height</span>
              <span className="metric-value">{userData.height ? `${userData.height} cm` : '-'}</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Weight</span>
              <span className="metric-value">{userData.weight ? `${userData.weight} kg` : '-'}</span>
            </div>
            {userData.bmi && (
              <div className="metric-item">
                <span className="metric-label">BMI</span>
                <div className="bmi-display">
                  <span className="bmi-value">{userData.bmi}</span>
                  <span className="bmi-category">{userData.bmi_category}</span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Calorie Ring */}
        <div className="calorie-card">
          <p className="card-title">Daily Calorie Goal</p>
          <div className="calorie-ring">
            <svg viewBox="0 0 160 160">
              <circle cx="80" cy="80" r="70" fill="none" stroke="currentColor" strokeWidth="8" className="ring-background" />
              <circle cx="80" cy="80" r="70" fill="none" stroke="currentColor" strokeWidth="12" strokeDasharray="440" strokeDashoffset={440 - (440 * (fitnessData.caloriesConsumed / fitnessData.caloriesTarget))} strokeLinecap="round" className="ring-progress" />
            </svg>
            <div className="ring-text">
              <span className="ring-value">{fitnessData.caloriesTarget - fitnessData.caloriesConsumed}</span>
              <span className="ring-label">kcal left</span>
            </div>
          </div>
        </div>

        {/* Macronutrient Breakdown */}
        <div className="macro-card">
          <p className="card-title">Macro nutrients</p>
          <div className="macro-item">
            <div className="macro-header">
              <span className="macro-label">🍗 Protein</span>
              <span className="macro-value">{fitnessData.protein.current}g / {fitnessData.protein.target}g</span>
            </div>
            <div className="macro-bar">
              <div className="macro-progress" style={{width: `${Math.min((fitnessData.protein.current / fitnessData.protein.target) * 100, 100)}%`, backgroundColor: '#ff6b6b'}}></div>
            </div>
          </div>
          <div className="macro-item">
            <div className="macro-header">
              <span className="macro-label">🍞 Carbs</span>
              <span className="macro-value">{fitnessData.carbs.current}g / {fitnessData.carbs.target}g</span>
            </div>
            <div className="macro-bar">
              <div className="macro-progress" style={{width: `${Math.min((fitnessData.carbs.current / fitnessData.carbs.target) * 100, 100)}%`, backgroundColor: '#4ecdc4'}}></div>
            </div>
          </div>
          <div className="macro-item">
            <div className="macro-header">
              <span className="macro-label">🥑 Fats</span>
              <span className="macro-value">{fitnessData.fats.current}g / {fitnessData.fats.target}g</span>
            </div>
            <div className="macro-bar">
              <div className="macro-progress" style={{width: `${Math.min((fitnessData.fats.current / fitnessData.fats.target) * 100, 100)}%`, backgroundColor: '#ffd93d'}}></div>
            </div>
          </div>
        </div>

        {/* Flexa Insight Card */}
        <div className="insight-card">
          <div className="insight-header">
            <span className="insight-icon">🤖</span>
            <span className="insight-title">Flexa Insight</span>
          </div>
          <p className="insight-text">
            {getFlexaInsight()}
          </p>
        </div>

        {/* Hydration Tracker */}
        <div className="hydration-card">
          <p className="card-title">Hydration</p>
          <div className="hydration-content">
            <div className="hydration-ring">
              <svg viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="40" fill="none" stroke="#e5e7eb" strokeWidth="8" />
                <circle cx="50" cy="50" r="40" fill="none" stroke="#3b82f6" strokeWidth="8" strokeDasharray="251.2" strokeDashoffset={251.2 - (251.2 * (fitnessData.hydration.current / fitnessData.hydration.target))} strokeLinecap="round" transform="rotate(-90 50 50)" />
              </svg>
              <div className="hydration-text">
                <span className="hydration-icon">💧</span>
              </div>
            </div>
            <div className="hydration-info">
              <span className="hydration-value">{fitnessData.hydration.current} / {fitnessData.hydration.target} L</span>
              <span className="hydration-label">{Math.round((fitnessData.hydration.current / fitnessData.hydration.target) * 100)}% of daily goal</span>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">
              <span className="material-symbols-outlined">footprint</span>
            </div>
            <p className="stat-label">Steps</p>
            <p className="stat-value">{fitnessData.steps.toLocaleString()}</p>
            <div className="stat-bar"><div style={{width: `${Math.min((fitnessData.steps / 10000) * 100, 100)}%`}}></div></div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">
              <span className="material-symbols-outlined">schedule</span>
            </div>
            <p className="stat-label">Active</p>
            <p className="stat-value">{fitnessData.activeMinutes}m</p>
            <div className="stat-bar"><div style={{width: `${Math.min((fitnessData.activeMinutes / 60) * 100, 100)}%`}}></div></div>
          </div>
        </div>

        {/* Next Workout */}
        <div className="next-workout">
          <p className="card-title">Next Workout</p>
          <div className="workout-card">
            <div className="workout-badge">Today at 5:00 PM</div>
            <h4>HIIT & Core Blast</h4>
            <p>Focus on explosive power and abdominal stability.</p>
            <button className="workout-btn">Prepare Gear</button>
          </div>
        </div>
      </aside>
    </div>
  );
};

export default Chat;
