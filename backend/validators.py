"""
backend/validators.py — Input validation routines for email addresses, files, and credentials.
"""

import re
from pathlib import Path

# Standard RFC 5322 regex pattern for email addresses
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)

def validate_email_syntax(email: str) -> bool:
    """Return True if email string matches standard email format."""
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email.strip()))

def validate_gmail_address(email: str) -> tuple[bool, str]:
    """
    Validates that the email is non-empty, matches valid email syntax,
    and is a @gmail.com address (or Google Workspace equivalent if specified).
    """
    if not email or not email.strip():
        return False, "Gmail address is required."
    
    clean_email = email.strip().lower()
    if not validate_email_syntax(clean_email):
        return False, "Invalid email format."
    
    if not clean_email.endswith("@gmail.com"):
        return False, "Email must be a valid @gmail.com address."
        
    return True, "Valid Gmail address."

def validate_file_extension(filename: str, allowed_extensions: set[str]) -> tuple[bool, str]:
    """
    Check if a filename has an allowed extension (e.g., {'.pdf'}, {'.csv', '.docx'}).
    """
    if not filename:
        return False, "No file provided."
    
    ext = Path(filename).suffix.lower()
    if ext not in allowed_extensions:
        allowed_str = ", ".join(sorted(allowed_extensions))
        return False, f"Invalid file extension '{ext}'. Only {allowed_str} allowed."
        
    return True, "File extension allowed."
