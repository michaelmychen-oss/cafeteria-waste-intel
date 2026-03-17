"""
Document parsing service: extracts raw text from PDF, CSV, Excel, and images.
"""

import io
from pathlib import Path

import fitz  # pymupdf
import pandas as pd
from PIL import Image

try:
    import pytesseract
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False


def parse_file(file_path: str, file_type: str) -> str:
    """Route to the correct parser based on file type."""
    parsers = {
        "pdf": _parse_pdf,
        "csv": _parse_csv,
        "xlsx": _parse_excel,
        "xls": _parse_excel,
        "png": _parse_image,
        "jpg": _parse_image,
        "jpeg": _parse_image,
    }
    parser = parsers.get(file_type.lower())
    if not parser:
        raise ValueError(f"Unsupported file type: {file_type}")
    return parser(file_path)


def _parse_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    text_parts = []
    for page in doc:
        text = page.get_text()
        if text.strip():
            text_parts.append(text)
        else:
            # Fallback to OCR for scanned pages
            if OCR_AVAILABLE:
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                text_parts.append(pytesseract.image_to_string(img))
    doc.close()
    return "\n\n".join(text_parts)


def _parse_csv(file_path: str) -> str:
    df = pd.read_csv(file_path)
    return _dataframe_to_text(df)


def _parse_excel(file_path: str) -> str:
    df = pd.read_excel(file_path)
    return _dataframe_to_text(df)


def _parse_image(file_path: str) -> str:
    if not OCR_AVAILABLE:
        raise RuntimeError("pytesseract is not available for OCR processing")
    img = Image.open(file_path)
    return pytesseract.image_to_string(img)


def _dataframe_to_text(df: pd.DataFrame) -> str:
    """Convert a DataFrame to a readable text representation for AI processing."""
    lines = []
    lines.append(f"Columns: {', '.join(df.columns.tolist())}")
    lines.append(f"Rows: {len(df)}")
    lines.append("")
    lines.append(df.to_string(index=False, max_rows=200))
    return "\n".join(lines)
