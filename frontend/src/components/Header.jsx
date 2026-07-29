import React from 'react';
import { Mail } from 'lucide-react';

export default function Header({ apiConnected }) {
  return (
    <header className="app-header">
      <div className="brand">
        <div className="brand-icon">
          <Mail size={24} />
        </div>
        <div className="brand-title">
          <h1>LukMailer</h1>
          <p>Personalized Recruiter Email Automation Platform</p>
        </div>
      </div>
      
      <div className={`status-badge ${apiConnected ? 'status-online' : 'status-offline'}`}>
        <span className="status-dot"></span>
        <span>{apiConnected ? 'Backend Connected' : 'Connecting to Server...'}</span>
      </div>
    </header>
  );
}
