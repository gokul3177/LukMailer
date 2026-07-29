"""
mailer.py — Gmail SMTP sender with rate-limiting, retry, and detailed logging.

Uses App Password (recommended) — no OAuth needed.
Set GMAIL_ADDRESS and GMAIL_APP_PASSWORD in .env or as environment variables.
Set LOG_FILE in .env to write logs to a custom file (default: send_log.txt).
"""

import os
import smtplib
import ssl
import time
import logging
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────────────────────────────────────────
# Logging  (LOG_FILE env var selects the ledger file)
# ──────────────────────────────────────────────────────────────
_log_file = os.getenv("LOG_FILE", "send_log.txt")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(_log_file, encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────
SMTP_HOST    = "smtp.gmail.com"
SMTP_PORT    = 465          # SSL
DELAY_MIN    = 8            # seconds between sends (lower = faster but riskier)
DELAY_MAX    = 18
MAX_RETRIES  = 3


class GmailSender:
    def __init__(self, address: str, app_password: str):
        self.address      = address
        self.app_password = app_password

    # ----------------------------------------------------------
    def _build_message(
        self,
        to_email: str,
        subject:  str,
        body:     str,
        attachments: list[str] | None = None,
    ) -> MIMEMultipart:
        msg = MIMEMultipart()
        msg["From"]    = f"Gokulakannan B S <{self.address}>"
        msg["To"]      = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        for path_str in (attachments or []):
            path = Path(path_str)
            if not path.exists():
                log.warning(f"Attachment not found, skipping: {path}")
                continue
            part = MIMEBase("application", "octet-stream")
            part.set_payload(path.read_bytes())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{path.name}"',
            )
            msg.attach(part)

        return msg

    # ----------------------------------------------------------
    def send_one(
        self,
        to_email:    str,
        subject:     str,
        body:        str,
        attachments: list[str] | None = None,
        dry_run:     bool = False,
    ) -> bool:
        """
        Send a single email. Returns True on success, False on failure.
        """
        msg = self._build_message(to_email, subject, body, attachments)

        if dry_run:
            log.info(f"[DRY RUN] Would send → {to_email}")
            return True

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                ctx = ssl.create_default_context()
                with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx) as server:
                    server.login(self.address, self.app_password)
                    server.sendmail(self.address, to_email, msg.as_string())
                log.info(f"[OK]  Sent -> {to_email}")
                return True
            except smtplib.SMTPRecipientsRefused as e:
                log.error(f"❌  Recipient refused {to_email}: {e}")
                return False          # no point retrying
            except Exception as e:
                log.warning(f"[WARN] Attempt {attempt}/{MAX_RETRIES} failed for {to_email}: {e}")
                if attempt < MAX_RETRIES:
                    time.sleep(5 * attempt)

        log.error(f"[FAIL] Giving up on {to_email} after {MAX_RETRIES} attempts.")
        return False

    # ----------------------------------------------------------
    def send_bulk(
        self,
        recipients:  list[tuple[str, str, str]],   # (company, hr_name, email)
        build_email,                                 # callable(company, hr_name) -> (subject, body)
        attachments: list[str] | None = None,
        dry_run:     bool = False,
        start_from:  int  = 0,                      # resume from index
    ) -> dict:
        """
        Send emails to all recipients with polite rate-limiting.

        Returns a summary dict:
            {
                "sent":   [...],
                "failed": [...],
                "skipped": [...],
            }
        """
        sent, failed, skipped = [], [], []

        total = len(recipients)
        for idx, (company, hr_name, email) in enumerate(recipients):
            if idx < start_from:
                log.info(f"[{idx+1}/{total}] Skipping (resume) -> {email}")
                skipped.append(email)
                continue

            subject, body = build_email(company, hr_name)

            log.info(f"[{idx+1}/{total}] Sending to {company} ({email}) ...")
            ok = self.send_one(email, subject, body, attachments, dry_run=dry_run)

            if ok:
                sent.append(email)
            else:
                failed.append(email)

            # Polite delay between sends (skip in dry_run or after last email)
            if not dry_run and idx < total - 1:
                delay = random.uniform(DELAY_MIN, DELAY_MAX)
                log.info(f"    Waiting {delay:.1f}s before next send ...")
                time.sleep(delay)

        return {"sent": sent, "failed": failed, "skipped": skipped}
