"""
backend/api.py — FastAPI Web Application Server for LukMailer GUI.

Provides REST endpoints for parsing HR lists, PDF resumes, generating email previews,
and managing live email campaigns with SSE real-time log streaming.
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from pydantic import BaseModel

from backend.validators import validate_gmail_address, validate_file_extension
from backend.resume_reader import extract_resume_text
from backend.parser import parse_hr_email_list
from backend.email_generator import build_email_template
from backend.mailer import GmailSender
from backend.logger import log, broadcaster

app = FastAPI(title="LukMailer API", version="2.0.0")

# Enable CORS for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global active campaign state
current_sender: Optional[GmailSender] = None

class PreviewRequest(BaseModel):
    company: str = "Amazon"
    hr_name: Optional[str] = "Hiring Manager"
    custom_subject: Optional[str] = None
    custom_body: Optional[str] = None
    sender_name: Optional[str] = None

class StartCampaignRequest(BaseModel):
    gmail_address: str
    gmail_app_password: str
    contacts: list[dict]
    resume_text: Optional[str] = ""
    resume_filename: Optional[str] = "resume.pdf"
    custom_subject: Optional[str] = None
    custom_body: Optional[str] = None
    dry_run: bool = False

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "LukMailer API"}

@app.post("/api/parse-resume")
async def api_parse_resume(file: UploadFile = File(...)):
    """Upload and parse PDF resume."""
    valid, err_msg = validate_file_extension(file.filename, {".pdf"})
    if not valid:
        raise HTTPException(status_code=400, detail=err_msg)

    content = await file.read()
    text, meta = extract_resume_text(pdf_bytes=content)

    if not meta.get("is_valid"):
        raise HTTPException(status_code=400, detail=f"Failed to read PDF: {meta.get('error', 'Invalid PDF format')}")

    log.info(f"Resume uploaded: {file.filename} ({meta['word_count']} words, {meta['page_count']} pages)")
    return {
        "filename": file.filename,
        "text": text,
        "metadata": meta
    }

@app.post("/api/parse-hr-list")
async def api_parse_hr_list(
    file: UploadFile = File(...),
    verify_existence: bool = Form(True)
):
    """Upload and parse .csv or .docx HR email list."""
    valid, err_msg = validate_file_extension(file.filename, {".csv", ".docx"})
    if not valid:
        raise HTTPException(status_code=400, detail=err_msg)

    content = await file.read()
    log.info(f"Parsing HR email file: {file.filename}...")

    try:
        contacts, stats = parse_hr_email_list(
            filename=file.filename,
            file_content=content,
            verify_existence=verify_existence
        )
        log.info(f"HR file parsed successfully: Found {stats['total_found']}, Valid {stats['valid_count']}, Skipped {stats['invalid_count']}")
        return {
            "filename": file.filename,
            "stats": stats,
            "contacts": contacts
        }
    except Exception as e:
        log.error(f"Error parsing HR list: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/preview-email")
async def api_preview_email(req: PreviewRequest):
    """Generate email preview for user inspection/editing."""
    sender_info = {"name": req.sender_name or "Gokulakannan B S"}
    subject, body = build_email_template(
        company=req.company,
        hr_name=req.hr_name,
        sender_info=sender_info,
        custom_subject=req.custom_subject,
        custom_body=req.custom_body
    )
    return {
        "company": req.company,
        "hr_name": req.hr_name,
        "subject": subject,
        "body": body
    }

@app.get("/api/stream-logs")
async def stream_logs():
    """SSE endpoint for live log streaming to the React UI."""
    async def event_generator():
        q = broadcaster.subscribe()
        try:
            # Yield initial connection message
            yield f"data: {json.dumps({'type': 'connected', 'message': 'Live log stream active'})}\n\n"
            while True:
                try:
                    data = await asyncio.wait_for(q.get(), timeout=30.0)
                    yield f"data: {json.dumps(data)}\n\n"
                except asyncio.TimeoutError:
                    # Send a heartbeat comment to keep the connection alive
                    yield ": heartbeat\n\n"
        except (asyncio.CancelledError, GeneratorExit):
            # Must re-raise CancelledError for anyio/starlette task group cleanup
            raise
        finally:
            # Always clean up the subscriber queue on disconnect
            broadcaster.unsubscribe(q)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

def _run_campaign_task(
    sender: GmailSender,
    contacts: list[dict],
    attachments: list[dict],
    custom_subject: Optional[str],
    custom_body: Optional[str],
    dry_run: bool
):
    def email_builder(company, hr_name):
        return build_email_template(
            company=company,
            hr_name=hr_name,
            custom_subject=custom_subject,
            custom_body=custom_body
        )

    def progress_callback(event_dict):
        broadcaster.publish(event_dict)

    try:
        sender.send_campaign(
            recipients=contacts,
            email_builder=email_builder,
            attachments=attachments,
            dry_run=dry_run,
            progress_callback=progress_callback
        )
    except Exception as e:
        log.error(f"Unhandled error in campaign task: {e}")
        broadcaster.publish({
            "type": "campaign_error",
            "error": str(e)
        })

@app.post("/api/start-campaign")
async def start_campaign(
    background_tasks: BackgroundTasks,
    gmail_address: str = Form(...),
    gmail_app_password: str = Form(...),
    contacts_json: str = Form(...),
    resume_filename: Optional[str] = Form("resume.pdf"),
    resume_file: Optional[UploadFile] = File(None),
    custom_subject: Optional[str] = Form(None),
    custom_body: Optional[str] = Form(None),
    dry_run: bool = Form(False)
):
    """Start campaign background sending process."""
    global current_sender

    # Validate Gmail Address
    valid_gmail, err_msg = validate_gmail_address(gmail_address)
    if not valid_gmail:
        raise HTTPException(status_code=400, detail=err_msg)

    if not gmail_app_password or not gmail_app_password.strip():
        raise HTTPException(status_code=400, detail="Gmail App Password is required.")

    try:
        contacts = json.loads(contacts_json)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid contacts JSON payload.")

    if not contacts:
        raise HTTPException(status_code=400, detail="No contacts provided for campaign.")

    attachments = []
    if resume_file:
        content = await resume_file.read()
        attachments.append({
            "filename": resume_file.filename or resume_filename or "resume.pdf",
            "content": content
        })

    sender = GmailSender(address=gmail_address, app_password=gmail_app_password)
    current_sender = sender

    background_tasks.add_task(
        _run_campaign_task,
        sender=sender,
        contacts=contacts,
        attachments=attachments,
        custom_subject=custom_subject,
        custom_body=custom_body,
        dry_run=dry_run
    )

    return {"status": "started", "recipient_count": len(contacts)}

@app.post("/api/stop-campaign")
async def stop_campaign():
    """Cancel currently running campaign."""
    global current_sender
    if current_sender:
        current_sender.request_cancel()
        log.warning("Stop campaign signal sent.")
        return {"status": "stopping"}
    return {"status": "no_active_campaign"}

# Mount frontend dist folder if compiled
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        target = frontend_dist / full_path
        if target.exists() and target.is_file():
            return FileResponse(target)
        return FileResponse(frontend_dist / "index.html")

