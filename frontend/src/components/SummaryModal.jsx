import React from 'react';
import { CheckCircle2, X } from 'lucide-react';

export default function SummaryModal({ summary, onClose }) {
  if (!summary) return null;

  const formatTime = (sec) => {
    if (!sec) return '0 sec';
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return m > 0 ? `${m} min ${s} sec` : `${s} sec`;
  };

  return (
    <div className="modal-overlay">
      <div className="modal-card">
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '1rem', color: '#16a34a' }}>
          <CheckCircle2 size={48} />
        </div>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.25rem', color: '#0f172a' }}>
          Campaign Execution Complete
        </h2>
        <p style={{ fontSize: '0.875rem', color: '#64748b', marginBottom: '1.5rem' }}>
          All target recruiter emails have been processed.
        </p>

        <div style={{ background: '#f8fafc', borderRadius: '8px', padding: '1rem', marginBottom: '1.5rem', textAlign: 'left' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.375rem 0', borderBottom: '1px solid #e2e8f0' }}>
            <span style={{ color: '#64748b' }}>Emails Found:</span>
            <span style={{ fontWeight: 600 }}>{summary.total_found}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.375rem 0', borderBottom: '1px solid #e2e8f0' }}>
            <span style={{ color: '#16a34a' }}>Sent Successfully:</span>
            <span style={{ fontWeight: 600, color: '#16a34a' }}>{summary.sent_count}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.375rem 0', borderBottom: '1px solid #e2e8f0' }}>
            <span style={{ color: '#dc2626' }}>Failed:</span>
            <span style={{ fontWeight: 600, color: '#dc2626' }}>{summary.failed_count}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.375rem 0', borderBottom: '1px solid #e2e8f0' }}>
            <span style={{ color: '#d97706' }}>Skipped:</span>
            <span style={{ fontWeight: 600, color: '#d97706' }}>{summary.skipped_count}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.375rem 0', borderBottom: '1px solid #e2e8f0' }}>
            <span style={{ color: '#64748b' }}>Total Time:</span>
            <span style={{ fontWeight: 600 }}>{formatTime(summary.total_time)}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.375rem 0' }}>
            <span style={{ color: '#64748b' }}>Average Send Time:</span>
            <span style={{ fontWeight: 600 }}>{summary.avg_send_time} sec</span>
          </div>
        </div>

        <button className="btn btn-primary" style={{ width: '100%' }} onClick={onClose}>
          Close Summary
        </button>
      </div>
    </div>
  );
}
