import React, { useState } from 'react';
import { Users, FileSpreadsheet, AlertCircle } from 'lucide-react';

export default function ContactUpload({ onContactsParsed }) {
  const [loading, setLoading] = useState(false);
  const [parsedData, setParsedData] = useState(null);
  const [error, setError] = useState('');
  const [verifyExistence, setVerifyExistence] = useState(true);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const fileName = file.name.toLowerCase();
    if (!fileName.endsWith('.csv') && !fileName.endsWith('.docx')) {
      setError('Only .csv and .docx files are allowed.');
      return;
    }

    setError('');
    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('verify_existence', verifyExistence);

    try {
      const res = await fetch('http://localhost:8000/api/parse-hr-list', {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to parse HR contacts file');
      }

      setParsedData(data);
      if (onContactsParsed) onContactsParsed(data.contacts, data.stats);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title">
          <div className="card-title-icon">
            <Users size={18} />
          </div>
          <span>Step 2: HR Email List Upload</span>
        </div>
      </div>

      <div style={{ marginBottom: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
        <input
          type="checkbox"
          id="verify-check"
          checked={verifyExistence}
          onChange={(e) => setVerifyExistence(e.target.checked)}
          style={{ cursor: 'pointer' }}
        />
        <label htmlFor="verify-check" style={{ color: '#475569', cursor: 'pointer', fontWeight: 500 }}>
          Verify Mailbox Existence (MX + SMTP Probe)
        </label>
      </div>

      <label className="dropzone" htmlFor="hr-file-input">
        <FileSpreadsheet size={32} className="dropzone-icon" />
        <div className="dropzone-text">
          <strong>Click to upload HR contact list</strong> (.csv or .docx)
        </div>
        <div className="dropzone-hint">
          Supports .csv and .docx files only
        </div>
        <input
          id="hr-file-input"
          type="file"
          accept=".csv, .docx"
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />
      </label>

      {loading && (
        <div style={{ marginTop: '0.875rem', fontSize: '0.85rem', color: '#2563eb', fontWeight: 500 }}>
          Extracting emails & probing MX/SMTP mailbox existence...
        </div>
      )}

      {error && (
        <div style={{ marginTop: '0.875rem', color: '#dc2626', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.375rem', background: '#fef2f2', padding: '0.625rem', borderRadius: '8px', border: '1px solid #fecaca' }}>
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}

      {parsedData && (
        <div style={{ marginTop: '1rem' }}>
          <div style={{ fontWeight: 600, fontSize: '0.875rem', marginBottom: '0.625rem', color: '#0f172a' }}>
            File: {parsedData.filename}
          </div>
          <div className="stats-grid">
            <div className="stat-box">
              <div className="stat-val" style={{ color: '#2563eb' }}>{parsedData.stats.total_found}</div>
              <div className="stat-lbl">Total Found</div>
            </div>
            <div className="stat-box">
              <div className="stat-val" style={{ color: '#16a34a' }}>{parsedData.stats.valid_count}</div>
              <div className="stat-lbl">Valid Emails</div>
            </div>
            <div className="stat-box">
              <div className="stat-val" style={{ color: '#dc2626' }}>{parsedData.stats.invalid_count}</div>
              <div className="stat-lbl">Skipped</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
