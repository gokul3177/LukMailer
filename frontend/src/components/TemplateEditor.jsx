import React, { useState, useEffect } from 'react';
import { Edit3, Eye, RotateCcw } from 'lucide-react';
import { apiUrl } from '../api';

export default function TemplateEditor({ customSubject, setCustomSubject, customBody, setCustomBody }) {
  const [activeTab, setActiveTab] = useState('edit');
  const [preview, setPreview] = useState({ subject: '', body: '' });

  const defaultSubject = "Application for Backend Engineering / AI-ML Role – Gokulakannan B S";
  const defaultBody = `Dear Hiring Team,

I am a final-year Computer Science undergraduate at SASTRA University looking for Backend Engineering or AI/ML roles at Amazon (available from Jan 2027 for internship / full-time).

Key Highlights:
- Amazon ML Summer School 2025: Selected nationally for advanced GenAI, LLM/RAG, and System Design training.
- Core Projects: Engineered LukMatch (LLM semantic matching), LukBill (NLP medical invoice automation), and LukWealth (PostgreSQL, Docker, CI/CD).
- Technical Core: Python, REST APIs, SQL (PostgreSQL, MySQL), NoSQL (MongoDB), Docker, AWS, Git.
- Problem Solving: Solved 250+ DSA problems on LeetCode; Core Member of SASTRA Robotics Club.

I would love the opportunity to discuss how my technical skills align with engineering opportunities at Amazon. My resume is attached for your review.

Best regards,
Gokulakannan B S
Phone    : +91 9444520998
LinkedIn : https://www.linkedin.com/in/bsgk/
GitHub   : https://github.com/gokul3177
LeetCode : https://leetcode.com/u/gokul3177/
Email    : gokulakannanbs31@gmail.com`;

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
