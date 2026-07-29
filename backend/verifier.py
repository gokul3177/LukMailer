"""
backend/verifier.py — Deep receiver email verifier (MX lookup + SMTP probe).

Determines whether the recipient email actually exists on the target server:
  - VALID   : MX record found and SMTP RCPT TO confirmed mailbox existence.
  - RISKY   : MX record found, but SMTP probe was inconclusive/blocked (catch-all server or anti-spam firewall).
  - INVALID : Domain has no MX record or SMTP server explicitly rejected the address (550 / 551 / 554).
"""

import smtplib
import socket
import dns.resolver
from typing import Literal
from backend.config import SMTP_PROBE_TIMEOUT, PROBE_FROM
from backend.validators import validate_email_syntax

Status = Literal["VALID", "RISKY", "INVALID"]

class VerifyResult:
    def __init__(self, company: str, email: str, status: Status, reason: str, mx_host: str = ""):
        self.company = company
        self.email = email
        self.status = status
        self.reason = reason
        self.mx_host = mx_host

    def to_dict(self):
        return {
            "company": self.company,
            "email": self.email,
            "status": self.status,
            "reason": self.reason,
            "mx_host": self.mx_host,
        }

def get_mx_record(domain: str) -> str | None:
    """Return the highest priority MX hostname for a domain, or None if DNS query fails."""
    try:
        resolver = dns.resolver.Resolver()
        resolver.lifetime = 5.0  # 5 sec timeout
        records = resolver.resolve(domain, "MX")
        best = sorted(records, key=lambda r: r.preference)[0]
        return str(best.exchange).rstrip(".")
    except Exception:
        return None

def smtp_probe(mx_host: str, email: str) -> tuple[bool | None, str]:
    """
    Perform SMTP RCPT TO probe.
    Returns:
        (True, reason)  -> Mailbox confirmed
        (False, reason) -> Mailbox hard-rejected (5xx error)
        (None, reason)  -> Inconclusive / blocked
    """
    try:
        with smtplib.SMTP(timeout=SMTP_PROBE_TIMEOUT) as s:
            s.connect(mx_host, 25)
            s.ehlo_or_helo_if_needed()
            code, _ = s.mail(PROBE_FROM)
            if code != 250:
                return None, f"MAIL FROM rejected ({code})"
            code, msg = s.rcpt(email)
            if code == 250:
                return True, "Mailbox confirmed by destination server"
            if code in (550, 551, 553, 554):
                return False, f"Mailbox rejected ({code}): {msg.decode(errors='replace')}"
            return None, f"Inconclusive server response ({code})"
    except smtplib.SMTPConnectError as e:
        return None, f"SMTP connect error: {e}"
    except smtplib.SMTPServerDisconnected:
        return None, "Server disconnected probe (firewall/rate-limit)"
    except socket.timeout:
        return None, "Connection timed out"
    except OSError as e:
        return None, f"Network error: {e}"
    except Exception as e:
        return None, f"Probe error: {e}"

def verify_email_existence(company: str, email: str) -> VerifyResult:
    """
    Main verifier routine for an email address.
    """
    clean_email = (email or "").strip()
    if not validate_email_syntax(clean_email):
        return VerifyResult(company, clean_email, "INVALID", "Malformed email syntax")

    domain = clean_email.split("@")[1].lower()
    mx = get_mx_record(domain)
    if not mx:
        return VerifyResult(company, clean_email, "INVALID", f"No MX record found for domain '{domain}'")

    confirmed, reason = smtp_probe(mx, clean_email)
    if confirmed is True:
        return VerifyResult(company, clean_email, "VALID", reason, mx)
    elif confirmed is False:
        return VerifyResult(company, clean_email, "INVALID", reason, mx)
    else:
        # Inconclusive (firewall / catch-all) -> RISKY (still safe to attempt send)
        return VerifyResult(company, clean_email, "RISKY", reason, mx)
