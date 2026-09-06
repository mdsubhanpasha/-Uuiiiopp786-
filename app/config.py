import os
from pydantic import BaseModel

class Settings(BaseModel):
    APP_NAME: str = "Org Messenger Agent"
    DEBUG: bool = True
    UPLOAD_DIR: str = "/tmp/pdfs"
    OUTPUT_DIR: str = "/tmp/org_messenger"

    # Messaging API Keys / Config
    FAST2SMS_API_KEY: str = os.getenv("FAST2SMS_API_KEY", "")
    TWILIO_SID: str = os.getenv("TWILIO_SID", "")
    TWILIO_TOKEN: str = os.getenv("TWILIO_TOKEN", "")
    TWILIO_WHATSAPP_FROM: str = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
    TWILIO_SMS_FROM: str = os.getenv("TWILIO_SMS_FROM", "")
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

settings = Settings()
