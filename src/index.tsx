import React from 'react';
import ReactDOM from 'react-dom';
import SettingsPage from './components/settings/SettingsPage';
import './styles.css';

// Import component-specific styles
import './components/settings/settings.css';
import './components/tokens/tokens.css';

const App: React.FC = () => {
  return (
    <div className="app-container">
      <header className="app-header">
        <div className="logo">
          <img src="/logo.svg" alt="Tembo Logo" />
        </div>
        <nav className="main-nav">
          <ul>
            <li><a href="/">Dashboard</a></li>
            <li><a href="/integrations">Integrations</a></li>
            <li><a href="/ai">AI Tasks</a></li>
            <li className="active"><a href="/settings">Settings</a></li>
          </ul>
        </nav>
        <div className="user-menu">
          <button className="user-button">
            <span className="user-avatar">JD</span>
            <span className="user-name">John Doe</span>
          </button>
        </div>
      </header>

      <main className="app-content">
        <SettingsPage />
      </main>

      <footer className="app-footer">
        <div className="footer-content">
          <div className="copyright">© {new Date().getFullYear()} Tembo, Inc. All rights reserved.</div>
          <div className="footer-links">
            <a href="https://docs.tembo.io" target="_blank" rel="noopener noreferrer">Documentation</a>
            <a href="https://tembo.io/support" target="_blank" rel="noopener noreferrer">Support</a>
            <a href="https://tembo.io/privacy" target="_blank" rel="noopener noreferrer">Privacy Policy</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);