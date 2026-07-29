import React from 'react';
import { Activity } from 'lucide-react';

export default function ProgressBar({ stats }) {
  const { processed = 0, total = 0, sent = 0, failed = 0, skipped = 0, remaining = 0 } = stats;
  const percentage = total > 0 ? Math.round((processed / total) * 100) : 0;

  return (
    <div className="card">
      <div className="card-header" style={{ marginBottom: '0.5rem' }}>
        <div className="card-title">
          <div className="card-title-icon">
            <Activity size={18} />
          </div>
          <span>Campaign Progress</span>
        </div>
        <span style={{ fontWeight: 700, fontSize: '1.15rem', color: '#2563eb' }}>{percentage}%</span>
      </div>

      <div className="progress-track">
        <div className="progress-bar-fill" style={{ width: `${percentage}%` }} />
      </div>

      <div className="stats-grid">
        <div className="stat-box">
          <div className="stat-val">{processed} / {total}</div>
          <div className="stat-lbl">Processed</div>
        </div>
        <div className="stat-box">
          <div className="stat-val" style={{ color: '#16a34a' }}>{sent}</div>
          <div className="stat-lbl">Successful</div>
        </div>
        <div className="stat-box">
          <div className="stat-val" style={{ color: '#dc2626' }}>{failed}</div>
          <div className="stat-lbl">Failed</div>
        </div>
        <div className="stat-box">
          <div className="stat-val" style={{ color: '#d97706' }}>{skipped}</div>
          <div className="stat-lbl">Skipped</div>
        </div>
        <div className="stat-box">
          <div className="stat-val" style={{ color: '#64748b' }}>{remaining}</div>
          <div className="stat-lbl">Remaining</div>
        </div>
      </div>
    </div>
  );
}
