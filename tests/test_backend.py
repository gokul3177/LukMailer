"""
Unit tests for LukMailer backend modules.
"""

import pytest
from backend.validators import validate_gmail_address, validate_email_syntax, validate_file_extension
from backend.verifier import verify_email_existence
from backend.email_generator import build_email_template, COMPANY_HIGHLIGHTS
from backend.parser import parse_csv_file, parse_docx_file

def test_validators():
    assert validate_email_syntax("user@example.com") is True
    assert validate_email_syntax("invalid-email") is False

    valid, _ = validate_gmail_address("test@gmail.com")
    assert valid is True
    valid, _ = validate_gmail_address("test@yahoo.com")
    assert valid is False

    valid, _ = validate_file_extension("resume.pdf", {".pdf"})
    assert valid is True
    valid, _ = validate_file_extension("list.docx", {".csv", ".docx"})
    assert valid is True
    valid, _ = validate_file_extension("list.txt", {".csv", ".docx"})
    assert valid is False

def test_email_generator():
    # Verify no duplicate Broadridge key in highlights dictionary
    assert "Broadridge" in COMPANY_HIGHLIGHTS

    subject, body = build_email_template(company="Amazon", hr_name="John Doe")
    assert "Dear John," in body
    assert "Amazon" in body
    assert "Application for Backend Engineering" in subject

    # Verify partial sender info does not raise KeyError
    subj2, body2 = build_email_template(company="Uber", hr_name="Jane", sender_info={"name": "Gokul"})
    assert "Gokul" in subj2 or "Gokul" in body2
    assert "Phone" in body2

def test_csv_parser():
    raw_csv = b"Company|HR Name|Email\nAmazon|Jane Doe|jane@amazon.com\nUber|John Smith|john@uber.com\n"
    contacts = parse_csv_file(raw_csv)
    assert len(contacts) == 2
    assert contacts[0][0] == "Amazon"
    assert contacts[0][2] == "jane@amazon.com"
