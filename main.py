"""
main.py — Main Entry point for LukMailer.

Usage:
    python main.py                     → Launch GUI Web Interface (http://localhost:8000)
    python main.py --gui               → Launch GUI Web Interface
    python main.py --send              → Run legacy CLI send
    python main.py --verify            → Run legacy CLI email verification
    python main.py --preview 3         → Print 3 email previews
"""

import argparse
import os
import sys
import webbrowser
import uvicorn
from dotenv import load_dotenv

from backend.config import DEFAULT_LOG_FILE
from backend.logger import log
from backend.validators import validate_gmail_address
from backend.verifier import verify_email_existence
from backend.email_generator import build_email_template
from backend.mailer import GmailSender

load_dotenv()

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS", "gokulakannanbs31@gmail.com")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")

def find_default_resume() -> str | None:
    candidates = [
        "Gokul_resume_.pdf",
        "Gokul_resume.pdf",
        "resume.pdf",
    ]
    for c in candidates:
        if os.path.exists(c):
            return os.path.abspath(c)
    return None

def parse_args():
    p = argparse.ArgumentParser(description="LukMailer — Recruiter Email Automation System")
    p.add_argument("--gui", action="store_true", help="Start Web GUI server (default behavior if no mode specified)")
    p.add_argument("--host", type=str, default="127.0.0.1", help="Host address for GUI server (default: 127.0.0.1)")
    p.add_argument("--port", type=int, default=8000, help="Port for GUI server (default: 8000)")
    p.add_argument("--send", action="store_true", help="CLI Mode: Send email campaign")
    p.add_argument("--dry-run", action="store_true", help="CLI Mode: Dry run without sending")
    p.add_argument("--preview", type=int, default=0, metavar="N", help="CLI Mode: Preview N emails and exit")
    p.add_argument("--verify", action="store_true", help="CLI Mode: Verify contact list mailbox existence")
    p.add_argument("--contacts-file", type=str, default="", help="Path to contacts file (.csv or .docx)")
    return p.parse_args()

def run_gui(host: str, port: int):
    log.info("=" * 65)
    log.info("  🚀 Launching LukMailer Modern Web GUI")
    log.info(f"  URL: http://{host}:{port}")
    log.info("=" * 65)
    
    # Try opening browser automatically
    try:
        webbrowser.open(f"http://{host}:{port}")
    except Exception:
        pass

    uvicorn.run("backend.api:app", host=host, port=port, reload=False)

def main():
    args = parse_args()

    # Default to GUI if no CLI mode flags provided
    if not (args.send or args.verify or args.preview > 0 or args.dry_run):
        run_gui(args.host, args.port)
        return

    if args.gui:
        run_gui(args.host, args.port)
        return

    # CLI Workflow
    log.info("Running in CLI Mode...")
    
    # Load contacts
    if os.path.exists("contacts.py"):
        from contacts import RECRUITERS
        contacts = [{"company": c[0], "hr_name": c[1], "email": c[2]} for c in RECRUITERS]
    else:
        log.error("No contacts found for CLI mode. Specify contacts file or run GUI.")
        sys.exit(1)

    if args.preview > 0:
        for c in contacts[:args.preview]:
            subj, body = build_email_template(c["company"], c["hr_name"])
            print("=" * 70)
            print(f"TO      : {c['email']}")
            print(f"COMPANY : {c['company']}")
            print(f"SUBJECT : {subj}")
            print("-" * 70)
            print(body)
            print("=" * 70)
        return

    if args.verify and not args.send:
        log.info(f"Verifying {len(contacts)} contacts...")
        for c in contacts:
            res = verify_email_existence(c["company"], c["email"])
            print(f"[{res.status:<7}] {c['email']:<40} {c['company']} -> {res.reason}")
        return

    # Send Workflow
    dry_run = args.dry_run or not args.send
    if not dry_run and not GMAIL_APP_PASSWORD:
        log.error("GMAIL_APP_PASSWORD not set in environment or .env file.")
        sys.exit(1)

    resume_path = find_default_resume()
    attachments = []
    if resume_path:
        with open(resume_path, "rb") as f:
            attachments.append({"filename": os.path.basename(resume_path), "content": f.read()})

    sender = GmailSender(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
    result = sender.send_campaign(
        recipients=contacts,
        email_builder=build_email_template,
        attachments=attachments,
        dry_run=dry_run
    )

    log.info(f"CLI Campaign finished. Summary: {result}")

if __name__ == "__main__":
    main()
