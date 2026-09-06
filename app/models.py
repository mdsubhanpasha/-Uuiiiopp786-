from typing import List, Optional
from pydantic import BaseModel, Field

class Contact(BaseModel):
    phone: str = Field(..., description="E.164 formatted phone number (+91XXXXXXXXXX)")
    name: str = Field(default="Unknown", description="Extracted or edited contact name")
    source_pdf: str = Field(..., description="Source PDF filename from which contact was extracted")
    status: str = Field(default="pending", description="Status: pending, delivered, failed, or invalid")
    confidence: float = Field(default=1.0, description="Extraction confidence score (1.0 for text, 0.95 for OCR)")
    page_num: Optional[int] = Field(default=1, description="PDF page number")
    is_valid: bool = Field(default=True, description="Whether phone number meets validation rules")

class ExtractResponse(BaseModel):
    status: str = "success"
    pdf_count: int
    total_contacts: int
    contacts: List[Contact]

class SendMessageRequest(BaseModel):
    message: str = Field(..., description="Message template with optional {{name}} or {{phone}} placeholders")
    channel: str = Field(..., description="Messaging channel: sms, whatsapp, fast2sms, or telegram")
    contacts: List[Contact]
    fast2sms_api_key: Optional[str] = None
    twilio_sid: Optional[str] = None
    twilio_token: Optional[str] = None
    twilio_whatsapp_from: Optional[str] = None
    telegram_bot_token: Optional[str] = None

class MessageResult(BaseModel):
    phone: str
    name: str
    source_pdf: str
    status: str  # delivered, failed, invalid
    channel: str
    error: Optional[str] = None

class DeliveryReport(BaseModel):
    total: int
    delivered: int
    failed: int
    invalid: int
    results: List[MessageResult]
