import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from scripts.test_pdfs.generate_sample_pdfs import generate_samples

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Org Messenger Agent" in response.text

def test_upload_zip_and_extract():
    generate_samples()
    zip_path = "data/sample_contacts.zip"
    assert os.path.exists(zip_path)

    with open(zip_path, "rb") as f:
        response = client.post("/upload-zip", files={"file": ("sample_contacts.zip", f, "application/zip")})

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["count"] == 3

    # Test extract contacts
    ext_response = client.post("/extract-contacts")
    assert ext_response.status_code == 200
    ext_data = ext_response.json()
    assert ext_data["status"] == "success"
    assert ext_data["total_contacts"] == 10

def test_send_messages_api():
    contacts_payload = [
        {"phone": "+919876543210", "name": "Aarav Sharma", "source_pdf": "test.pdf", "status": "pending", "confidence": 1.0, "is_valid": True},
        {"phone": "+919876543211", "name": "Priya Patel", "source_pdf": "test.pdf", "status": "pending", "confidence": 1.0, "is_valid": True}
    ]

    payload = {
        "message": "Hello {{name}}, test alert",
        "channel": "sms",
        "contacts": contacts_payload
    }

    response = client.post("/send-messages", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["delivered"] == 2
