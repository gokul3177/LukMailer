import React, { useState, useEffect } from 'react';
import { Edit3, Eye, RotateCcw } from 'lucide-react';
import { apiUrl } from '../api';

export default function TemplateEditor({ customSubject, setCustomSubject, customBody, setCustomBody }) {
  const [activeTab, setActiveTab] = useState('edit');
  const [preview, setPreview] = useState({ subject: '', body: '' });

  const defaultSubject = "Application for [Role] – [Your Name]";
  const defaultBody = `Dear Hiring Team,

I am writing to express my strong interest in engineering opportunities at {company}. I am excited about {company}'s innovative work in the industry.

[Write your introduction here — mention your current status, the role you are targeting, and your availability.]

Key Highlights:
- [Achievement 1 — e.g., a certification, award, or academic distinction]
- [Achievement 2 — e.g., a project you built and its impact]
- [Achievement 3 — e.g., your core technical skills]

I would love the opportunity to discuss how my background aligns with your team's goals. My resume is attached for your review.

Best regards,
[Your Name]
Phone    : [Your Phone Number]
LinkedIn : [Your LinkedIn URL]
GitHub   : [Your GitHub URL]
Email    : [Your Email Address]`;

  useEffect(() => {
    fetchPreview();
  }, [customSubject, customBody]);

  const fetchPreview = async () => {
    try {
      const res = await fetch(apiUrl('/api/preview-email'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company: 'Amazon',
          hr_name: 'John Doe',
          custom_subject: customSubject || null,
          custom_body: customBody || null,
        }),
      });
      const data = await res.json();
      setPreview(data);
    } catch (e) {
      console.error(e);
    }
  };

  const handleReset = () => {
    setCustomSubject('');
    setCustomBody('');
  };

  return (
    <div className="card">
      <div className="card-header" style={{ marginBottom: '1rem' }}>
        <div className="card-title">
          <div className="card-title-icon">
            <Edit3 size={18} />
          </div>
          <span>Email Template Preview & Customization</span>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            className={`btn btn-sm ${activeTab === 'edit' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('edit')}
          >
            <Edit3 size={14} /> Edit Template
          </button>
          <button
            className={`btn btn-sm ${activeTab === 'preview' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('preview')}
          >
            <Eye size={14} /> Preview (Amazon)
          </button>
          <button
            className="btn btn-sm btn-secondary"
            onClick={handleReset}
          >
            <RotateCcw size={14} /> Reset
          </button>
        </div>
      </div>

      {activeTab === 'edit' ? (
        <div>
          <div className="form-group">
            <label className="form-label">Subject Line Template</label>
            <input
              type="text"
              className="form-input"
              value={customSubject !== null && customSubject !== undefined ? customSubject : defaultSubject}
              onChange={(e) => setCustomSubject(e.target.value)}
              placeholder="Application for Backend Engineering – {sender_name}"
            />
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label className="form-label">Email Body Template</label>
            <textarea
              className="form-input"
              rows={8}
              value={customBody !== null && customBody !== undefined ? customBody : defaultBody}
              onChange={(e) => setCustomBody(e.target.value)}
              placeholder="Use placeholders like {greeting}, {company}, etc."
            />
          </div>
        </div>
      ) : (
        <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', padding: '1.25rem', borderRadius: '8px', fontSize: '0.875rem' }}>
          <div style={{ fontWeight: 700, color: '#0f172a', marginBottom: '0.75rem', paddingBottom: '0.625rem', borderBottom: '1px solid #e2e8f0' }}>
            SUBJECT: {preview.subject}
          </div>
          <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit', color: '#334155', lineHeight: '1.6' }}>
            {preview.body}
          </pre>
        </div>
      )}
    </div>
  );
}
