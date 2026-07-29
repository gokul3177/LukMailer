"""
backend/resume_reader.py — Resume text & metadata extractor (PDF format).
"""

from pathlib import Path
import fitz  # PyMuPDF

def extract_resume_text(pdf_bytes: bytes | None = None, pdf_path: str | Path | None = None) -> tuple[str, dict]:
    """
    Extract text and metadata from a PDF resume file.
    
    Returns:
        (extracted_text, metadata_dict)
    """
    doc = None
    try:
        if pdf_bytes:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        elif pdf_path:
            doc = fitz.open(str(pdf_path))
        else:
            raise ValueError("Either pdf_bytes or pdf_path must be provided.")

        full_text = []
        for page in doc:
            full_text.append(page.get_text())

        text_content = "\n".join(full_text).strip()
        metadata = {
            "page_count": len(doc),
            "char_count": len(text_content),
            "word_count": len(text_content.split()),
            "is_valid": len(text_content) > 0,
        }
        return text_content, metadata
    except Exception as e:
        return "", {
            "page_count": 0,
            "char_count": 0,
            "word_count": 0,
            "is_valid": False,
            "error": str(e),
        }
    finally:
        if doc:
            doc.close()
