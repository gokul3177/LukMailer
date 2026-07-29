"""
backend/config.py — Configuration and constants for LukMailer backend.
"""

import os
from pathlib import Path

# SMTP Settings
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))  # SSL

# Sending Rate Limits & Retries
DELAY_MIN = float(os.getenv("DELAY_MIN", 8.0))
DELAY_MAX = float(os.getenv("DELAY_MAX", 18.0))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))

# Verifier Settings
SMTP_PROBE_TIMEOUT = int(os.getenv("SMTP_PROBE_TIMEOUT", 10))
PROBE_FROM = "verify@lukmailer.local"

# Logging Settings
DEFAULT_LOG_FILE = Path("send_log.txt")

# Standard Sender Fallback Defaults (intentionally blank — filled by user via UI)
DEFAULT_SENDER_NAME = ""
DEFAULT_SENDER_PHONE = ""
DEFAULT_SENDER_LINKEDIN = ""
DEFAULT_SENDER_GITHUB = ""
DEFAULT_SENDER_LEETCODE = ""
