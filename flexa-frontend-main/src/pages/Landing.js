import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/Landing.css';

const Landing = () => {
  const navigate = useNavigate();

  return (
    <div className="landing-page">
      {/* Navigation */}
      <header className="landing-nav">
        <div className="nav-container">
          <div className="nav-logo">
            <div className="logo-icon">
              <video autoPlay loop muted playsInline style={{ width: '100%', height: '100%', borderRadius: '0.5rem', objectFit: 'cover' }}>
                <source src="/Bot1.mp4" type="video/mp4" />
              </video>
            </div>
            <h1>Flexa</h1>
          </div>
          <nav className="nav-links">
            <a href="#how">How it Works</a>
            <a href="#features">Features</a>
            <a href="#sign up">Sign up</a>
          </nav>
          <div className="nav-actions">
            <button className="login-btn">Login</button>
            <button onClick={() => navigate('/chat')} className="cta-btn">Start Chatting</button>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="hero">
        <div className="hero-content">
          <h2 className="hero-title">
            Your Personal Trainer, <br />
            <span className="gradient-text">Powered by AI.</span>
          </h2>
          <p className="hero-description">
            Meet Flexa. The AI coach that builds your workouts, tracks your meals, and keeps you motivated 24/7 with hyper-personalized logic.
          </p>
          <div className="hero-cta">
            <button onClick={() => navigate('/chat')} className="cta-primary">Get Started Free</button>
          </div>
        </div>

        <div className="hero-preview">
          <div className="preview-card">
            <div className="preview-header">
              <div className="preview-avatar">
                <video autoPlay loop muted playsInline style={{ width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover' }}>
                  <source src="/Bot1.mp4" type="video/mp4" />
                </video>
              </div>
              <div>
                <h4>Flexa AI</h4>
                <div className="online-status">
                  <div className="status-dot"></div>
                  <span>Online</span>
                </div>
              </div>
            </div>
            <div className="preview-messages">
              <div className="msg-ai">Hey Alex! Ready to crush today's workout? Let's do it!</div>
              <div className="msg-user">Absolutely! What's the plan?</div>
              <div className="msg-ai">Perfect! Starting with a 10-minute warm-up...</div>
            </div>
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section id="how" className="how-it-works">
        <h2>How it Works</h2>
        <p>Three simple steps to transform your fitness journey with AI intelligence.</p>
        <div className="steps-grid">
          <div className="step-card">
            <div className="step-icon">
              <span className="material-symbols-outlined">target</span>
            </div>
            <h3>Set Goals</h3>
            <p>Define your fitness path and what you want to achieve.</p>
          </div>
          <div className="step-card">
            <div className="step-icon">
              <span className="material-symbols-outlined">chat</span>
            </div>
            <h3>Chat Daily</h3>
            <p>Get real-time adjustments and daily motivation.</p>
          </div>
          <div className="step-card">
            <div className="step-icon">
              <span className="material-symbols-outlined">monitoring</span>
            </div>
            <h3>Track Progress</h3>
            <p>Visualize your gains with AI-driven insights.</p>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="features">
        <h2>Smart Features</h2>
        <p>Hyper-Personalized tools that actually understand your body.</p>
        <div className="features-grid">
          <div className="feature-card large">
            <div className="feature-bg" style={{backgroundImage: 'url(https://lh3.googleusercontent.com/aida-public/AB6AXuAM1d803E80l6DsZWJ3vCDsitloriXAsVbyG1JwMus-0lXa-_PzseGrESYMSORPy0aO8AxGKTof5dtTQQgqNAzr0fkCoSizcujsbcXliT1nCWNlSES0xWIOLN9uo0-5VFn_jRVBQJg-kLreFxRxTbDjm9_-lXqNKHKBUs2JZw-dZn-eHpdyYtnHUS4AfqTy5_JcG3rGHPdZJHQyN4w0tqb8efKRMHljyC3MCB4LinZ2_3VtkJy-6gH8ClCkZvI8S_nbPxWPsr4EFIMi)'}}></div>
            <div className="feature-content">
              <h3>Hyper-Personalized Routines</h3>
              <p>Workouts tailored to your physiology and equipment.</p>
            </div>
          </div>
          <div className="feature-card large">
            <div className="feature-bg" style={{backgroundImage: 'url(https://lh3.googleusercontent.com/aida-public/AB6AXuC7MzT1Yiaq2AmNfNXvGmG7rQ7a5FRnk_KmFGmROKkd2SQHl4CDr3MGyf0jlXZQ8889bvyGurtxsmFlGEXzaPaKQ5u48yaGWfxlkPydbbpSgA-zXRjVdubSoMghSylYkLUr3pA859bXgQvDu_Ksq96L0MEztHKk06phIZUZQtdDifBVTvodeUEuURv-cLpwuvx3WOuOsmxWpWsH9btvowmu5VP68f9vEn6mjTTA9M_80-2xJDxKxG8FH67lXCz3oopbqBQUplVHSTuW)'}}></div>
            <div className="feature-content">
              <h3>Smart Nutrition Planning</h3>
              <p>Meal plans that adapt to your cravings and schedule.</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="cta-section">
        <h2>Stop Guessing. Start Transforming.</h2>
        <p>Join thousands who have optimized their lives with Flexa.</p>
        <button onClick={() => navigate('/chat')} className="cta-primary">Claim My Free Week</button>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="footer-content">
          <div className="footer-col">
            <h4>Flexa</h4>
            <p>Your personal AI fitness coach.</p>
          </div>
          <div className="footer-col">
            <h5>Product</h5>
            <ul>
              <li><a href="#how">How it works</a></li>
              <li><a href="#features">Features</a></li>
            </ul>
          </div>
          <div className="footer-col">
            <h5>Company</h5>
            <ul>
              <li><a href="/about">About</a></li>
              <li><a href="/privacy">Privacy</a></li>
              <li><a href="/terms">Terms</a></li>
            </ul>
          </div>
        </div>
        <p className="footer-copyright">© 2026 Flexa AI. All rights reserved.</p>
      </footer>

      {/* Floating Chatbot Button */}
      <button className="floating-chatbot" onClick={() => navigate('/chat')} title="Chat with Flexa">
        <video autoPlay loop muted playsInline style={{ width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover' }}>
          <source src="/Bot1.mp4" type="video/mp4" />
        </video>
      </button>
    </div>
  );
};

export default Landing;
