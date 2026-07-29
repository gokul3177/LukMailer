import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import ResumeUpload from './components/ResumeUpload';
import ContactUpload from './components/ContactUpload';
import CredentialsForm from './components/CredentialsForm';
import TemplateEditor from './components/TemplateEditor';
import LiveLogPanel from './components/LiveLogPanel';
import ProgressBar from './components/ProgressBar';
import SummaryModal from './components/SummaryModal';
import { Play, Square, AlertCircle, Rocket } from 'lucide-react';
import { apiUrl, sseUrl } from './api';

export default function App() {
  const [apiConnected, setApiConnected] = useState(false);
  const [resumeData, setResumeData] = useState(null);
  const [resumeFile, setResumeFile] = useState(null);
  const [contacts, setContacts] = useState([]);
  const [contactsStats, setContactsStats] = useState(null);

  const [gmailAddress, setGmailAddress] = useState('');
  const [appPassword, setAppPassword] = useState('');

  const [customSubject, setCustomSubject] = useState(null);
  const [customBody, setCustomBody] = useState(null);

  const [dryRun, setDryRun] = useState(false);
  const [isSending, setIsSending] = useState(false);

  const [logs, setLogs] = useState([]);
  const [autoScroll, setAutoScroll] = useState(true);

  const [progressStats, setProgressStats] = useState({
    processed: 0,
    total: 0,
    sent: 0,
    failed: 0,
    skipped: 0,
    remaining: 0,
  });

  const [summaryData, setSummaryData] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');

  // Connect to backend SSE Log Stream
  useEffect(() => {
    checkHealth();
    const eventSource = new EventSource(sseUrl('/api/stream-logs'));

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'connected') {
          setApiConnected(true);
        } else {
          setLogs((prev) => [...prev, data]);
          
          if (data.type === 'item_completed' || data.type === 'item_skipped') {
            setProgressStats((prev) => ({
              ...prev,
              processed: data.processed_count || prev.processed + 1,
              total: data.total || prev.total,
              sent: data.sent_count || prev.sent,
              failed: data.failed_count || prev.failed,
              skipped: data.skipped_count || prev.skipped,
              remaining: data.remaining_count !== undefined ? data.remaining_count : prev.remaining - 1,
            }));
          }

          if (data.type === 'campaign_finished') {
            setIsSending(false);
            setSummaryData(data.summary);
          }

          if (data.type === 'campaign_cancelled') {
            setIsSending(false);
          }
        }
      } catch (e) {
        console.error('SSE Error:', e);
      }
    };

    return () => {
      eventSource.close();
    };
  }, []);

  const checkHealth = async () => {
    try {
      const res = await fetch(apiUrl('/api/health'));
      if (res.ok) setApiConnected(true);
    } catch {
      setApiConnected(false);
    }
  };

  const handleResumeParsed = (data, file) => {
    setResumeData(data);
    setResumeFile(file);
    addLog(`Resume PDF loaded: ${file.name}`);
  };

  const handleContactsParsed = (contactsList, stats) => {
    setContacts(contactsList);
    setContactsStats(stats);
    setProgressStats((prev) => ({ ...prev, total: contactsList.length, remaining: contactsList.length }));
    addLog(`HR Contact file parsed: ${stats.total_found} total emails found, ${stats.valid_count} valid, ${stats.invalid_count} skipped.`);
  };

  const addLog = (msg) => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs((prev) => [...prev, { timestamp, message: msg, type: 'info' }]);
  };

  const handleStartCampaign = async () => {
    if (!contacts || contacts.length === 0) {
      setErrorMessage('Please upload a valid HR Email list (.csv or .docx) first.');
      return;
    }

    if (!gmailAddress || !gmailAddress.trim().toLowerCase().endsWith('@gmail.com')) {
      setErrorMessage('Please enter a valid @gmail.com email address.');
      return;
    }

    if (!appPassword || !appPassword.trim()) {
      setErrorMessage('Please enter your 16-character Gmail App Password.');
      return;
    }

    setErrorMessage('');
    setIsSending(true);
    setSummaryData(null);
    setProgressStats({
      processed: 0,
      total: contacts.length,
      sent: 0,
      failed: 0,
      skipped: 0,
      remaining: contacts.length,
    });

    const formData = new FormData();
    formData.append('gmail_address', gmailAddress.trim());
    formData.append('gmail_app_password', appPassword.trim());
    formData.append('contacts_json', JSON.stringify(contacts));
    if (resumeFile) {
      formData.append('resume_file', resumeFile);
      formData.append('resume_filename', resumeFile.name);
    }
    if (customSubject) formData.append('custom_subject', customSubject);
    if (customBody) formData.append('custom_body', customBody);
    formData.append('dry_run', dryRun);

    try {
      const res = await fetch(apiUrl('/api/start-campaign'), {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to start campaign');
      }
      addLog(`Campaign launched for ${data.recipient_count} recipients.`);
    } catch (err) {
      setIsSending(false);
      setErrorMessage(err.message);
    }
  };

  const handleStopCampaign = async () => {
    try {
      await fetch(apiUrl('/api/stop-campaign'), { method: 'POST' });
      addLog('Cancellation requested by user...');
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="app-container">
      <Header apiConnected={apiConnected} />

      <div className="grid-container">
        {/* Step 1 & Step 2 Row */}
        <div className="grid-2col">
          <ResumeUpload onResumeParsed={handleResumeParsed} />
          <ContactUpload onContactsParsed={handleContactsParsed} />
        </div>

        {/* Step 3 & Step 4 Row */}
        <div className="grid-2col">
          <CredentialsForm
            gmailAddress={gmailAddress}
            setGmailAddress={setGmailAddress}
            appPassword={appPassword}
            setAppPassword={setAppPassword}
          />

          <div className="card">
            <div className="card-header">
              <div className="card-title">
                <div className="card-title-icon">
                  <Rocket size={18} />
                </div>
                <span>Launch Campaign</span>
              </div>
              {contacts && contacts.length > 0 && (
                <span style={{ fontSize: '0.8rem', fontWeight: 600, background: '#eff6ff', color: '#2563eb', border: '1px solid #bfdbfe', borderRadius: '20px', padding: '0.2rem 0.75rem' }}>
                  {contacts.length} recipients ready
                </span>
              )}
            </div>

            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: '1rem' }}>

              {/* Dry Run Toggle */}
              <label htmlFor="dryrun-check" style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem', background: dryRun ? '#fefce8' : '#f8fafc', padding: '0.875rem 1rem', borderRadius: '8px', border: `1px solid ${dryRun ? '#fde68a' : '#e2e8f0'}`, cursor: 'pointer', transition: 'all 0.2s' }}>
                <input
                  type="checkbox"
                  id="dryrun-check"
                  checked={dryRun}
                  onChange={(e) => setDryRun(e.target.checked)}
                  disabled={isSending}
                  style={{ cursor: 'pointer', marginTop: '2px', flexShrink: 0 }}
                />
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.875rem', color: '#1e293b' }}>
                    🧪 Test Mode (no emails sent)
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.2rem' }}>
                    Runs everything — but skips the actual sending. Use this first to make sure it all works.
                  </div>
                </div>
              </label>

              {/* Action Button */}
              {!isSending ? (
                <button
                  className="btn btn-primary"
                  style={{ width: '100%', padding: '0.875rem', fontSize: '1rem' }}
                  onClick={handleStartCampaign}
                  disabled={!contacts || contacts.length === 0}
                >
                  <Play size={20} />
                  {dryRun ? 'Run Test Campaign' : 'Start Sending Emails'}
                </button>
              ) : (
                <button
                  className="btn btn-danger"
                  style={{ width: '100%', padding: '0.875rem', fontSize: '1rem' }}
                  onClick={handleStopCampaign}
                >
                  <Square size={20} /> Stop Campaign
                </button>
              )}

              {!contacts || contacts.length === 0 ? (
                <p style={{ fontSize: '0.78rem', color: '#94a3b8', textAlign: 'center', margin: 0 }}>
                  ⬆ Upload your HR contact list first to enable sending
                </p>
              ) : null}

              {errorMessage && (
                <div style={{ color: '#dc2626', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.375rem', background: '#fef2f2', padding: '0.625rem', borderRadius: '8px', border: '1px solid #fecaca' }}>
                  <AlertCircle size={16} />
                  <span>{errorMessage}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Email Template Customizer */}
        <TemplateEditor
          customSubject={customSubject}
          setCustomSubject={setCustomSubject}
          customBody={customBody}
          setCustomBody={setCustomBody}
        />

        {/* Campaign Progress Bar */}
        <ProgressBar stats={progressStats} />

        {/* Real-time Activity Log Terminal */}
        <LiveLogPanel
          logs={logs}
          onClearLogs={() => setLogs([])}
          autoScroll={autoScroll}
          setAutoScroll={setAutoScroll}
        />
      </div>

      <SummaryModal summary={summaryData} onClose={() => setSummaryData(null)} />
    </div>
  );
}
