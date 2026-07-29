import React, { useState } from 'react';
import { FileUp, FileText, CheckCircle, AlertTriangle } from 'lucide-react';

export default function ResumeUpload({ onResumeParsed }) {
  const [loading, setLoading] = useState(false);
  const [resumeData, setResumeData] = useState(null);
  const [error, setError] = useState('');

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Only PDF files are allowed for resume upload.');
      return;
    }

    setError('');
    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/parse-resume', {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to parse resume');
      }

      setResumeData(data);
      if (onResumeParsed) onResumeParsed(data, file);
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
            <FileText size={18} />
          </div>
          <span>Step 1: Resume Upload</span>
        </div>
      </div>

      <label className="dropzone" htmlFor="resume-file-input">
        <FileUp size={32} className="dropzone-icon" />
        <div className="dropzone-text">
          <strong>Click to upload PDF resume</strong> or drag & drop file
        </div>
        <div className="dropzone-hint">
          Accepts .pdf files only
        </div>
        <input
          id="resume-file-input"
          type="file"
          accept=".pdf"
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />
      </label>

      {loading && (
        <div style={{ marginTop: '0.875rem', fontSize: '0.85rem', color: '#2563eb', fontWeight: 500 }}>
          Processing and extracting resume text...
        </div>
      )}

      {error && (
        <div style={{ marginTop: '0.875rem', color: '#dc2626', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.375rem', background: '#fef2f2', padding: '0.625rem', borderRadius: '8px', border: '1px solid #fecaca' }}>
          <AlertTriangle size={16} />
          <span>{error}</span>
        </div>
      )}

      {resumeData && (
        <div style={{ marginTop: '0.875rem', padding: '0.75rem 1rem', background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px', fontSize: '0.85rem', color: '#166534' }}>
          <div style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
            <CheckCircle size={16} />
            <span>{resumeData.filename}</span>
          </div>
          <div style={{ marginTop: '0.25rem', fontSize: '0.8rem', color: '#15803d' }}>
            {resumeData.metadata.page_count} Page(s) • {resumeData.metadata.word_count} Words Extracted
          </div>
        </div>
      )}
    </div>
  );
}
