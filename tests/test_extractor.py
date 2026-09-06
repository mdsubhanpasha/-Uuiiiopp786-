import os
import pytest
from app.pdf_extractor import clean_and_normalize_phone, extract_contacts_from_pdf
from scripts.test_pdfs.generate_sample_pdfs import generate_samples

def test_clean_and_normalize_phone():
    # 10 digit Indian number
    p1, v1 = clean_and_normalize_phone("9876543210")
    assert p1 == "+919876543210"
    assert v1 is True

    # +91 prefix with space
    p2, v2 = clean_and_normalize_phone("+91 9876543211")
    assert p2 == "+919876543211"
    assert v2 is True

    # Leading 0
    p3, v3 = clean_and_normalize_phone("09876543212")
    assert p3 == "+919876543212"
    assert v3 is True

    # Invalid phone
    p4, v4 = clean_and_normalize_phone("12345")
    assert v4 is False

def test_extract_contacts_from_sample_pdf():
    generate_samples()
    pdf_path = "/tmp/sample_pdfs_gen/engineering_team.pdf"
    assert os.path.exists(pdf_path)

    contacts = extract_contacts_from_pdf(pdf_path)
    assert len(contacts) == 4
    for c in contacts:
        assert c.is_valid is True
        assert c.phone.startswith("+91")
        assert len(c.phone) == 13
        assert c.confidence == 1.0
