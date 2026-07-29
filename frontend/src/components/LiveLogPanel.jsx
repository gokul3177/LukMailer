import React, { useEffect, useRef } from 'react';
import { Terminal, Trash2 } from 'lucide-react';

export default function LiveLogPanel({ logs, onClearLogs, autoScroll, setAutoScroll }) {
  const logEndRef = useRef(null);

  useEffect(() => {
    if (autoScroll && logEndRef.current) {
      logEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll]);

  const formatEta = (seconds) => {
    if (!seconds || seconds <= 0) return '0 sec';
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return m > 0 ? `${m} min ${s} sec` : `${s} sec`;
  };

  return (
    <div className="terminal-card">
      <div className="terminal-header">
        <div className="terminal-title">
          <Terminal size={18} color="#38bdf8" />
          <span>REAL-TIME ACTIVITY LOG</span>
        </div>
        <div className="terminal-controls">
          <label style={{ fontSize: '0.8rem', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '0.375rem', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={autoScroll}
              onChange={(e) => setAutoScroll(e.target.checked)}
            />
            <span>Auto-Scroll</span>
          </label>
          <button
            className="btn btn-sm btn-secondary"
            style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem', background: '#334155', color: '#f8fafc', borderColor: '#475569' }}
            onClick={onClearLogs}
          >
            <Trash2 size={12} /> Clear Logs
          </button>
        </div>
      </div>

      <div className="terminal-body">
        {logs.length === 0 ? (
          <div style={{ color: '#64748b', fontStyle: 'italic', textAlign: 'center', marginTop: '3rem' }}>
            Ready. Click "Start Sending" to watch real-time activity logs.
          </div>
        ) : (
          logs.map((log, i) => {
            const time = log.timestamp || new Date().toLocaleTimeString();

            if (log.type === 'item_processing') {
              return (
                <div key={i} className="log-entry">
                  <span className="log-time">[{time}]</span>
                  <span className="log-info">Sending email to:</span>{' '}
                  <span style={{ color: '#ffffff', fontWeight: 600 }}>{log.email}</span> ({log.company})
                </div>
              );
            }

            if (log.type === 'item_completed') {
              const isOk = log.status === 'SUCCESS';
              return (
                <div key={i} className="log-entry" style={{ borderLeft: `3px solid ${isOk ? '#4ade80' : '#f87171'}`, paddingLeft: '0.625rem', margin: '0.625rem 0', background: 'rgba(255,255,255,0.02)', padding: '0.5rem 0.625rem', borderRadius: '0 6px 6px 0' }}>
                  <div>
                    <span className="log-time">[{time}]</span>
                    <span>Status: </span>
                    <span className={isOk ? 'log-success' : 'log-fail'}>{log.status}</span>
                    <span style={{ color: '#94a3b8', marginLeft: '0.875rem' }}>Time: {log.duration} seconds</span>
                  </div>
                  {log.message && !isOk && (
                    <div style={{ color: '#fca5a5', fontSize: '0.78rem', marginTop: '0.15rem' }}>Reason: {log.message}</div>
                  )}
                  <div style={{ color: '#94a3b8', fontSize: '0.78rem', marginTop: '0.25rem' }}>
                    Current Progress: {log.processed_count} / {log.total} | Average Time: {log.avg_time}s | Estimated Time Remaining: {formatEta(log.eta_seconds)}
                  </div>
                </div>
              );
            }

            if (log.type === 'item_skipped') {
              return (
                <div key={i} className="log-entry" style={{ color: '#fbbf24' }}>
                  <span className="log-time">[{time}]</span>
                  <span>Skipped address: {log.email} ({log.reason})</span>
                </div>
              );
            }

            return (
              <div key={i} className="log-entry">
                <span className="log-time">[{time}]</span>
                <span>{log.message || JSON.stringify(log)}</span>
              </div>
            );
          })
        )}
        <div ref={logEndRef} />
      </div>
    </div>
  );
}
