"""
backend/mailer.py — Gmail SMTP email sender with rate-limiting, retry, live metrics & event callbacks.
"""

import os
import ssl
import time
import random
import smtplib
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from backend.config import SMTP_HOST, SMTP_PORT, DELAY_MIN, DELAY_MAX, MAX_RETRIES
from backend.logger import log

class CampaignCancelledException(Exception):
    """Raised when campaign execution is stopped by user."""
    pass

class GmailSender:
    def __init__(self, address: str, app_password: str, sender_name: str = ""):
        self.address = address.strip()
        self.app_password = app_password.strip()
        self.sender_name = sender_name.strip()
        self.cancel_requested = False

    def request_cancel(self):
        self.cancel_requested = True

    def _build_message(
        self,
        to_email: str,
        subject: str,
        body: str,
        attachments: list[dict] | None = None, # [{filename: str, content: bytes}]
    ) -> MIMEMultipart:
        msg = MIMEMultipart()
        msg["From"] = f"{self.sender_name} <{self.address}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        for att in (attachments or []):
            fname = att.get("filename", "attachment.pdf")
            content = att.get("content", b"")
            if not content:
                continue
            part = MIMEBase("application", "octet-stream")
            part.set_payload(content)
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f'attachment; filename="{fname}"')
            msg.attach(part)

        return msg

    def send_one(
        self,
        to_email: str,
        subject: str,
        body: str,
        attachments: list[dict] | None = None,
        dry_run: bool = False,
    ) -> tuple[bool, str]:
        """
        Send a single email. Returns (success_bool, status_message).
        """
        msg = self._build_message(to_email, subject, body, attachments)

        if dry_run:
            log.info(f"[DRY RUN] Would send email to -> {to_email}")
            return True, "Dry run simulated success"

        for attempt in range(1, MAX_RETRIES + 1):
            if self.cancel_requested:
                raise CampaignCancelledException("Campaign cancelled by user.")
                
            try:
                ctx = ssl.create_default_context()
                with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx, timeout=20) as server:
                    server.login(self.address, self.app_password)
                    server.sendmail(self.address, to_email, msg.as_string())
                return True, "SUCCESS"
            except smtplib.SMTPAuthenticationError as e:
                err_msg = "Authentication failed: Invalid Gmail address or App Password."
                log.error(f"❌ SMTP Auth Error: {err_msg}")
                return False, err_msg
            except smtplib.SMTPRecipientsRefused as e:
                err_msg = f"Recipient refused by server: {e}"
                log.error(f"❌ Recipient Refused {to_email}: {e}")
                return False, err_msg
            except Exception as e:
                log.warning(f"⚠️ Attempt {attempt}/{MAX_RETRIES} failed for {to_email}: {e}")
                if attempt < MAX_RETRIES:
                    time.sleep(3 * attempt)

        return False, f"Failed after {MAX_RETRIES} attempts"

    def send_campaign(
        self,
        recipients: list[dict], # [{"company": ..., "hr_name": ..., "email": ...}]
        email_builder,          # callable(company, hr_name) -> (subject, body)
        attachments: list[dict] | None = None,
        dry_run: bool = False,
        progress_callback = None, # callback(event_dict)
    ) -> dict:
        """
        Execute bulk sending with rate-limiting, timing metrics, and progress callbacks.
        """
        self.cancel_requested = False
        sent = []
        failed = []
        skipped = []
        
        total = len(recipients)
        start_time_all = time.time()
        send_durations = []

        log.info(f"Starting campaign: Total {total} recipients | Sender: {self.address}")
        if progress_callback:
            progress_callback({
                "type": "campaign_start",
                "total": total,
                "sender": self.address,
                "dry_run": dry_run,
            })

        for idx, item in enumerate(recipients, start=1):
            if self.cancel_requested:
                log.warning("⚠️ Campaign execution cancelled by user.")
                if progress_callback:
                    progress_callback({
                        "type": "campaign_cancelled",
                        "processed": idx - 1,
                        "total": total,
                    })
                break

            email = item["email"]
            company = item.get("company", "Company")
            hr_name = item.get("hr_name")
            status_prev = item.get("status")

            if status_prev == "INVALID":
                log.info(f"[{idx}/{total}] Skipping hard invalid address -> {email}")
                skipped.append({"email": email, "reason": "Hard invalid / non-existent address"})
                if progress_callback:
                    progress_callback({
                        "type": "item_skipped",
                        "index": idx,
                        "total": total,
                        "email": email,
                        "company": company,
                        "reason": "Hard invalid address",
                    })
                continue

            subject, body = email_builder(company, hr_name)
            
            # Log action start
            log.info(f"[{idx}/{total}] Processing email to {company} ({email})...")
            if progress_callback:
                progress_callback({
                    "type": "item_processing",
                    "index": idx,
                    "total": total,
                    "email": email,
                    "company": company,
                })

            item_start = time.time()
            success = False
            message = ""

            try:
                success, message = self.send_one(
                    to_email=email,
                    subject=subject,
                    body=body,
                    attachments=attachments,
                    dry_run=dry_run,
                )
            except CampaignCancelledException:
                break
            except Exception as e:
                success = False
                message = str(e)

            item_duration = time.time() - item_start
            send_durations.append(item_duration)

            # Compute running statistics
            avg_time = sum(send_durations) / len(send_durations) if send_durations else 0.0
            remaining_count = total - idx
            eta_seconds = remaining_count * (avg_time + (0 if dry_run else (DELAY_MIN + DELAY_MAX) / 2.0))

            if success:
                sent.append(email)
                log.info(f"[{idx}/{total}] SUCCESS -> {email} in {item_duration:.2f}s")
            else:
                failed.append({"email": email, "reason": message})
                log.error(f"[{idx}/{total}] FAILURE -> {email} | Error: {message}")

            if progress_callback:
                progress_callback({
                    "type": "item_completed",
                    "index": idx,
                    "total": total,
                    "email": email,
                    "company": company,
                    "status": "SUCCESS" if success else "FAILED",
                    "message": message,
                    "duration": round(item_duration, 2),
                    "avg_time": round(avg_time, 2),
                    "eta_seconds": round(eta_seconds, 1),
                    "processed_count": idx,
                    "sent_count": len(sent),
                    "failed_count": len(failed),
                    "skipped_count": len(skipped),
                    "remaining_count": remaining_count,
                })

            # Rate limit delay between emails
            if not dry_run and idx < total and not self.cancel_requested:
                delay = random.uniform(DELAY_MIN, DELAY_MAX)
                log.info(f"Waiting {delay:.1f}s before next send to respect Gmail limits...")
                
                # Sleep in short increments to allow fast cancellation
                slept = 0.0
                while slept < delay and not self.cancel_requested:
                    time.sleep(0.5)
                    slept += 0.5

        total_time = time.time() - start_time_all
        summary = {
            "total_found": total,
            "processed": len(sent) + len(failed) + len(skipped),
            "sent_count": len(sent),
            "failed_count": len(failed),
            "skipped_count": len(skipped),
            "sent": sent,
            "failed": failed,
            "skipped": skipped,
            "total_time": round(total_time, 2),
            "avg_send_time": round(sum(send_durations) / len(send_durations), 2) if send_durations else 0.0,
        }

        log.info(f"Campaign finished in {total_time:.2f}s | Sent: {len(sent)} | Failed: {len(failed)} | Skipped: {len(skipped)}")
        if progress_callback:
            progress_callback({
                "type": "campaign_finished",
                "summary": summary,
            })

        return summary
