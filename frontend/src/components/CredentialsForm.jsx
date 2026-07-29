import React from 'react';
import { Lock, ShieldCheck } from 'lucide-react';

export default function CredentialsForm({
  gmailAddress,
  setGmailAddress,
  appPassword,
  setAppPassword,
}) {
  const isValidGmail = (email) => {
    return !email || email.trim().toLowerCase().endsWith('@gmail.com');
  };

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">
          <div className="card-title-icon">
            <Lock size={18} />
          </div>
          <span>Step 3: Gmail Credentials</span>
        </div>
      </div>

      <div className="form-group">
        <label className="form-label" htmlFor="gmail-input">Gmail Address</label>
        <input
          id="gmail-input"
          type="email"
          className="form-input"
          placeholder="name@gmail.com"
          value={gmailAddress}
          onChange={(e) => setGmailAddress(e.target.value)}
        />
        {gmailAddress && !isValidGmail(gmailAddress) && (
          <div style={{ color: '#dc2626', fontSize: '0.75rem', marginTop: '0.375rem' }}>
            Must be a valid @gmail.com address format
          </div>
        )}
      </div>

      <div className="form-group" style={{ marginBottom: '0.75rem' }}>
        <label className="form-label" htmlFor="password-input">Gmail App Password</label>
        <input
          id="password-input"
          type="password"
          className="form-input"
          placeholder="•••• •••• •••• ••••"
          value={appPassword}
          onChange={(e) => setAppPassword(e.target.value)}
        />
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.775rem', color: '#64748b', background: '#f8fafc', padding: '0.5rem 0.75rem', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
        <ShieldCheck size={16} color="#2563eb" />
        <span>App Password is kept strictly in RAM memory during execution. Never saved to disk or logged.</span>
      </div>
    </div>
  );
}
