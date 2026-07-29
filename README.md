---
title: LukMailer Backend
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8000
pinned: false
---

# LukMailer — Personalized Recruiter Email Automation Platform

**LukMailer** is a modern, lightweight bulk emailing platform built for job seekers to reach recruiters with personalized emails, PDF resume attachments, deep receiver email verification, and real-time live activity logging.

---

## Key Features

1. **Modern React + Vite Frontend**: Clean, minimal white theme with subtle blue accents.
2. **Real-Time Live Activity Log**: Streamed in real-time via Server-Sent Events (SSE). Watch timestamped execution events, send durations, average speed, and estimated time remaining (ETA).
3. **Deep Receiver Email Verification**:
   - Syntax validation
   - Domain MX DNS lookup
   - SMTP `RCPT TO` mailbox existence probe (checks whether the receiver email address actually exists on the target mail server!)
4. **Flexible Contact File Parsing**:
   - Supports `.csv` and `.docx` HR contact lists.
   - Automatically extracts valid emails, filters invalid or non-existent mailboxes, and displays statistical metrics (Total found, Valid/Risky, Invalid skipped).
5. **PDF Resume Attachment**: Accepts PDF resume uploads and validates text content.
6. **Customizable Email Templates**: Interactive preview with options to customize subject line & body templates before sending.
7. **Secure Credential Handling**: Gmail App Passwords are kept strictly in-memory during execution and are never saved to disk or written to logs.
8. **Rate Limiting & Safety**: Includes polite delay intervals (8–18s) to comply with Gmail SMTP limits and prevent account restrictions.

---

## Directory Structure

```
LukMailer/
├── backend/
│   ├── config.py           # Settings and configuration constants
│   ├── validators.py       # Syntax and file extension validators
│   ├── verifier.py         # MX lookup & SMTP existence probe
│   ├── logger.py           # File logger & live SSE broadcaster
│   ├── resume_reader.py    # PDF text & metadata extractor
│   ├── parser.py           # CSV and DOCX HR contact list parser
│   ├── email_generator.py  # Personalized email builder with highlights
│   ├── mailer.py           # Gmail SMTP sender with rate-limiting & cancellation
│   └── api.py              # FastAPI server (REST endpoints + SSE live logs)
├── frontend/
│   ├── src/
│   │   ├── components/     # Header, ResumeUpload, ContactUpload, CredentialsForm, etc.
│   │   ├── App.jsx         # Main application controller & state
│   │   └── index.css       # Clean design system
│   └── dist/               # Built static frontend bundle
├── tests/
│   └── test_backend.py     # Pytest unit tests for backend modules
├── main.py                 # Unified launcher (GUI server & legacy CLI)
├── requirements.txt        # Python dependencies
└── README.md               # Documentation
```

---

## Quick Start Guide

### 1. Install Dependencies

```bash
# Python dependencies
pip install -r requirements.txt

# Install frontend dependencies (optional if running pre-built frontend)
cd frontend
npm install
npm run build
cd ..
```

### 2. Launch the Application

Run the unified launcher:

```bash
python main.py
```

Or explicitly start the Web GUI:

```bash
python main.py --gui
```

Open your browser and navigate to:  
👉 **http://localhost:8000**

---

## How to Use the Web Interface

1. **Upload Resume**: Click or drag-and-drop your resume (`.pdf` only).
2. **Upload HR Email List**: Upload your recruiter contact list (`.csv` or `.docx`).
   - Enable **Deep Verify Email Mailbox Existence** to check whether recipient mailboxes actually exist.
   - Inspect the extracted metrics (Total Found, Valid Emails, Invalid Skipped).
3. **Enter Gmail Credentials**:
   - Enter your `@gmail.com` address.
   - Enter your 16-character **Gmail App Password** (generate from [Google Account App Passwords](https://myaccount.google.com/apppasswords)).
4. **Preview & Edit Template**:
   - Inspect the generated email subject and body.
   - Customize placeholders or text as desired.
5. **Start Campaign**:
   - Click **Start Sending** (or select **Dry Run Mode** to simulate sending without emailing).
   - Watch real-time updates in the **Live Activity Log** panel and monitor the **Progress Bar**.

---

## CLI Mode

For command-line users:

```bash
# Preview 3 emails
python main.py --preview 3

# Verify contact list
python main.py --verify

# Dry run campaign
python main.py --dry-run

# Live send campaign
python main.py --send
```

---

## Deployment

> ⚠️ **Vercel is NOT supported** for this app. LukMailer uses Server-Sent Events (SSE), background tasks, and long-running SMTP connections — none of which work on Vercel's 10-second serverless functions.

### 🚀 Deploy on Railway (Recommended — Free)

1. Push your repo to GitHub (already done!)
2. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub**
3. Select `gokul3177/LukMailer`
4. Railway auto-detects the `railway.toml` and runs the build + start commands
5. Add environment variables if needed (optional — credentials are entered via the UI)
6. Your app will be live at `https://lukmailer-production.up.railway.app`

### 🌐 Deploy on Render (Alternative — Free)

1. Go to [render.com](https://render.com) → **New Web Service**
2. Connect GitHub repo `gokul3177/LukMailer`
3. Render auto-detects `render.yaml`
4. Click **Deploy** — done!

### 💻 Run Locally

```bash
# Install Python dependencies
pip install -r requirements.txt

# Build the frontend
cd frontend && npm install && npm run build && cd ..

# Start the server
uvicorn backend.api:app --host 0.0.0.0 --port 8000 --reload
```

Open: **http://localhost:8000**

---

## Testing

Run unit tests using pytest:

```bash
pytest tests/test_backend.py
```
