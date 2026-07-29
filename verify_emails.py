"""
verify_emails.py — Pre-send email verifier for LukMailer.

Checks each contact's email address in two stages:
  1. MX record lookup  — confirms the domain accepts mail
  2. SMTP RCPT TO probe — confirms the specific mailbox exists

Usage:
    python verify_emails.py              → verify all contacts (contacts.py)
    python verify_emails.py --wave2      → verify 2ndWave contacts
    python verify_emails.py --report     → print report only (no colour)

Results:
    ✅ VALID   — MX found + SMTP confirmed mailbox exists
    ⚠️  RISKY   — MX found but server blocked SMTP probe (catch-all / firewall)
    ❌ INVALID  — No MX record or SMTP hard-rejected the address

IMPORTANT: Many large providers (Gmail, Yahoo, Outlook, some corporates) block
SMTP probing. Those will show RISKY — still safe to send, just unconfirmed.
"""

import smtplib
import socket
import sys
import argparse
import dns.resolver                     # pip install dnspython
from dataclasses import dataclass, field
from typing import Literal

# ──────────────────────────────────────────────────────────────
PROBE_FROM   = "verify@lukmailer.local"   # dummy sender for SMTP probe
SMTP_TIMEOUT = 10                         # seconds per connection
# ──────────────────────────────────────────────────────────────


Status = Literal["VALID", "RISKY", "INVALID"]


@dataclass
class VerifyResult:
    company:  str
    email:    str
    status:   Status
    reason:   str
    mx_host:  str = ""


# ──────────────────────────────────────────────────────────────
# Step 1 — MX lookup
# ──────────────────────────────────────────────────────────────
def get_mx(domain: str) -> str | None:
    """Return the highest-priority MX hostname, or None if not found."""
    try:
        records = dns.resolver.resolve(domain, "MX", lifetime=8)
        # sort by preference (lower = higher priority)
        best = sorted(records, key=lambda r: r.preference)[0]
        return str(best.exchange).rstrip(".")
    except Exception:
        return None


# ──────────────────────────────────────────────────────────────
# Step 2 — SMTP RCPT TO probe
# ──────────────────────────────────────────────────────────────
def smtp_probe(mx_host: str, email: str) -> tuple[bool | None, str]:
    """
    Returns:
        (True,  reason)  → mailbox confirmed
        (False, reason)  → mailbox rejected (hard bounce)
        (None,  reason)  → inconclusive (server refused probe / timeout)
    """
    try:
        with smtplib.SMTP(timeout=SMTP_TIMEOUT) as s:
            s.connect(mx_host, 25)
            s.ehlo_or_helo_if_needed()
            code, _ = s.mail(PROBE_FROM)
            if code != 250:
                return None, f"MAIL FROM rejected ({code})"
            code, msg = s.rcpt(email)
            if code == 250:
                return True, "Mailbox confirmed by server"
            if code in (550, 551, 553, 554):
                return False, f"Mailbox rejected ({code}): {msg.decode(errors='replace')}"
            # 452, 421, 450, 451 etc. — inconclusive
            return None, f"Inconclusive response ({code})"
    except smtplib.SMTPConnectError as e:
        return None, f"SMTP connect error: {e}"
    except smtplib.SMTPServerDisconnected:
        return None, "Server disconnected early (probe blocked)"
    except socket.timeout:
        return None, "Connection timed out"
    except OSError as e:
        return None, f"Network error: {e}"
    except Exception as e:
        return None, f"Unexpected error: {e}"


# ──────────────────────────────────────────────────────────────
# Main verify function
# ──────────────────────────────────────────────────────────────
def verify(company: str, email: str) -> VerifyResult:
    email = email.strip()

    # Basic format check
    if "@" not in email or "." not in email.split("@")[-1]:
        return VerifyResult(company, email, "INVALID", "Malformed email address")

    domain = email.split("@")[1].lower()

    # Stage 1 — MX
    mx = get_mx(domain)
    if not mx:
        return VerifyResult(company, email, "INVALID", f"No MX record for domain '{domain}'")

    # Stage 2 — SMTP probe
    confirmed, reason = smtp_probe(mx, email)

    if confirmed is True:
        return VerifyResult(company, email, "VALID",   reason, mx)
    elif confirmed is False:
        return VerifyResult(company, email, "INVALID", reason, mx)
    else:
        # Inconclusive — mark RISKY (still sendable, just unconfirmed)
        return VerifyResult(company, email, "RISKY",   reason, mx)


# ──────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────



def run_verification(contacts: list[tuple[str, str | None, str]]) -> list[VerifyResult]:
    results = []
    total = len(contacts)
    print(f"\nVerifying {total} email addresses ...\n")

    for i, (company, _hr, email) in enumerate(contacts, 1):
        result = verify(company, email)
        icon   = {"VALID": "[OK]  ", "RISKY": "[RISKY]", "INVALID": "[SKIP] "}[result.status]
        print(f"  [{i:>3}/{total}]  {icon}  {result.status:<7}  {email:<45}  {result.reason}")
        results.append(result)

    return results


def print_summary(results: list[VerifyResult]) -> None:
    valid   = [r for r in results if r.status == "VALID"]
    risky   = [r for r in results if r.status == "RISKY"]
    invalid = [r for r in results if r.status == "INVALID"]

    print("\n" + "=" * 65)
    print(f"  [OK]   VALID   (safe to send)          : {len(valid)}")
    print(f"  [RISKY] RISKY  (unconfirmed, but ok)   : {len(risky)}")
    print(f"  [SKIP] INVALID (skip - likely bad addr): {len(invalid)}")
    print("=" * 65)

    if invalid:
        print("\n  These addresses will be SKIPPED when you send:\n")
        for r in invalid:
            print(f"       - {r.email}  ({r.company})  -- {r.reason}")

    print()


def save_report(results: list[VerifyResult], path: str = "verify_report.txt") -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{'STATUS':<8}  {'EMAIL':<45}  {'COMPANY':<35}  REASON\n")
        f.write("-" * 120 + "\n")
        for r in results:
            f.write(f"{r.status:<8}  {r.email:<45}  {r.company:<35}  {r.reason}\n")
    print(f"  Full report saved -> {path}\n")


# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LukMailer — Email verifier")
    parser.add_argument("--wave2", action="store_true", help="Verify 2ndWave contacts instead of contacts.py")
    args = parser.parse_args()

    if args.wave2:
        # Import will be wired once 2ndWave contacts module is ready
        try:
            from contacts_wave2 import RECRUITERS
            report_file = "verify_report_wave2.txt"
        except ImportError:
            print("❌  contacts_wave2.py not found yet. Paste your contacts first!")
            sys.exit(1)
    else:
        from contacts import RECRUITERS
        report_file = "verify_report.txt"

    results = run_verification(RECRUITERS)
    print_summary(results)
    save_report(results, report_file)
