import pytest
from app.models import Contact
from app.sms_sender import send_fast2sms, send_twilio_sms, send_whatsapp_twilio, send_bulk

def test_sms_sender_validation():
    contacts = [
        Contact(phone="+919876543210", name="Valid User", source_pdf="test.pdf", is_valid=True),
        Contact(phone="12345", name="Invalid User", source_pdf="test.pdf", is_valid=False)
    ]

    report = send_bulk(
        contacts=contacts,
        template_msg="Hello {{name}}",
        channel="sms",
        config={}
    )

    assert report.total == 2
    assert report.delivered == 1
    assert report.invalid == 1
    assert report.results[0].status == "delivered"
    assert report.results[1].status == "invalid"
