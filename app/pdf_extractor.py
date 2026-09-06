import os
import re
import logging
from typing import List, Tuple, Dict
import pdfplumber
import fitz  # PyMuPDF
from app.models import Contact

logger = logging.getLogger(__name__)

# Phone regex rules
# Indian phones: Optional +91 / 91 / 0, followed by 10 digits starting with 6-9
INDIAN_PHONE_REGEX = re.compile(r"(?:(?:\+?91[\s\-]?)?|0)?([6-9]\d{9})\b")
# General E.164 / International regex for fallback
INTL_PHONE_REGEX = re.compile(r"\+?\d{1,4}[\s\-]?\(?\d{2,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{3,4}")

# Name extraction regex patterns near phone numbers
NAME_PATTERNS = [
    re.compile(r"(?:Name|Employee|Contact|Person|User|Staff)\s*[:\-]\s*([A-Za-z\s\.]{2,30})", re.IGNORECASE),
    re.compile(r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)", re.MULTILINE),
    re.compile(r"([A-Za-z\s\.]{3,25})\s*[:\-]?\s*(?:\+?91[\s\-]?)?[6-9]\d{9}")
]

def clean_and_normalize_phone(raw_phone: str) -> Tuple[str, bool]:
    """
    Cleans raw phone string to E.164 +91 format for Indian numbers.
    Returns (normalized_phone, is_valid).
    """
    digits = re.sub(r"\D", "", raw_phone)
    if len(digits) == 10 and digits[0] in "6789":
        return f"+91{digits}", True
    elif len(digits) == 12 and digits.startswith("91") and digits[2] in "6789":
        return f"+{digits}", True
    elif len(digits) == 11 and digits.startswith("0") and digits[1] in "6789":
        return f"+91{digits[1:]}", True
    elif len(digits) >= 10 and len(digits) <= 15:
        # Generic international format fallback
        return f"+{digits}", True
    else:
        return raw_phone, False

def extract_name_near_text(text: str, phone_raw: str) -> str:
    """
    Attempts to extract name from context surrounding phone number.
    """
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if phone_raw in line or re.sub(r"\D", "", phone_raw) in re.sub(r"\D", "", line):
            # Check for pattern in current line
            for pattern in NAME_PATTERNS:
                match = pattern.search(line)
                if match:
                    extracted = match.group(1).strip()
                    if extracted and len(extracted) > 1 and not any(char.isdigit() for char in extracted):
                        return extracted
            # Check preceding line if current line only had phone
            if i > 0:
                prev_line = lines[i-1].strip()
                if prev_line and not any(char.isdigit() for char in prev_line) and len(prev_line) < 40:
                    return prev_line
    return "Unknown"

def extract_from_text_pdf(pdf_path: str) -> List[Tuple[str, str, int, float]]:
    """
    Extracts text using pdfplumber and PyMuPDF.
    Returns list of tuples: (raw_phone, name, page_num, confidence)
    """
    extracted_data = []

    # Primary attempt with pdfplumber
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_idx, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text() or ""
                if len(page_text.strip()) >= 20:
                    matches = INDIAN_PHONE_REGEX.findall(page_text)
                    for m in matches:
                        phone_digits = m if isinstance(m, str) else m[0]
                        name = extract_name_near_text(page_text, phone_digits)
                        extracted_data.append((phone_digits, name, page_idx, 1.0))
    except Exception as e:
        logger.warning(f"pdfplumber failed for {pdf_path}: {e}")

    # Fallback or secondary check using PyMuPDF if pdfplumber found nothing
    if not extracted_data:
        try:
            doc = fitz.open(pdf_path)
            for page_idx in range(len(doc)):
                page = doc[page_idx]
                page_text = page.get_text() or ""
                if len(page_text.strip()) >= 20:
                    matches = INDIAN_PHONE_REGEX.findall(page_text)
                    for m in matches:
                        phone_digits = m if isinstance(m, str) else m[0]
                        name = extract_name_near_text(page_text, phone_digits)
                        extracted_data.append((phone_digits, name, page_idx + 1, 1.0))
            doc.close()
        except Exception as e:
            logger.warning(f"PyMuPDF failed for {pdf_path}: {e}")

    return extracted_data

def extract_from_scanned_pdf_ocr(pdf_path: str) -> List[Tuple[str, str, int, float]]:
    """
    OCR Fallback using pdf2image and pytesseract for scanned PDFs.
    Returns list of tuples: (raw_phone, name, page_num, confidence)
    """
    extracted_data = []
    try:
        from pdf2image import convert_from_path
        import pytesseract

        images = convert_from_path(pdf_path)
        for page_idx, img in enumerate(images, start=1):
            ocr_text = pytesseract.image_to_string(img)
            matches = INDIAN_PHONE_REGEX.findall(ocr_text)
            for m in matches:
                phone_digits = m if isinstance(m, str) else m[0]
                name = extract_name_near_text(ocr_text, phone_digits)
                extracted_data.append((phone_digits, name, page_idx, 0.95))
    except Exception as e:
        logger.error(f"OCR processing failed for {pdf_path}: {e}")

    return extracted_data

def extract_contacts_from_pdf(pdf_path: str) -> List[Contact]:
    """
    Main extraction orchestrator for a single PDF file.
    Applies text extraction first, falls back to OCR if text length < 20,
    normalizes phone numbers to E.164, deduplicates, and returns Contact models.
    """
    pdf_name = os.path.basename(pdf_path)
    raw_contacts = extract_from_text_pdf(pdf_path)

    # If text extraction produced no results or file seems scanned, perform OCR fallback
    if not raw_contacts:
        logger.info(f"No text contacts found in {pdf_name}. Attempting OCR fallback...")
        raw_contacts = extract_from_scanned_pdf_ocr(pdf_path)

    contacts_dict: Dict[str, Contact] = {}

    for raw_phone, name, page_num, confidence in raw_contacts:
        norm_phone, is_valid = clean_and_normalize_phone(raw_phone)
        if norm_phone not in contacts_dict or (is_valid and not contacts_dict[norm_phone].is_valid):
            contacts_dict[norm_phone] = Contact(
                phone=norm_phone,
                name=name if name != "Unknown" else "Contact",
                source_pdf=pdf_name,
                status="pending",
                confidence=confidence,
                page_num=page_num,
                is_valid=is_valid
            )

    return list(contacts_dict.values())
