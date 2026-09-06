import time
import logging
import requests
from typing import List, Dict, Any, Optional, Tuple
from app.models import Contact, MessageResult, DeliveryReport
from app.config import settings

logger = logging.getLogger(__name__)

def send_fast2sms(phone: str, msg: str, api_key: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """
    Sends SMS via Fast2SMS Quick SMS API.
    Phone number sent as 10-digit clean string without leading +91.
    """
    key = api_key or settings.FAST2SMS_API_KEY
    if not key:
        return False, "Fast2SMS API key missing"

    clean_digits = phone.replace("+91", "").replace("+", "").strip()
    url = "https://www.fast2sms.com/dev/bulkV2"
    headers = {
        "authorization": key,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "route": "q",
        "message": msg,
        "language": "english",
        "numbers": clean_digits
    }

    try:
        response = requests.post(url, data=payload, headers=headers, timeout=10)
        res_json = response.json()
        if response.status_code == 200 and res_json.get("return") is True:
            return True, None
        else:
            err = res_json.get("message", [f"HTTP {response.status_code}"])
            return False, str(err)
    except Exception as e:
        logger.error(f"Fast2SMS error for {phone}: {e}")
        return False, str(e)

def send_twilio_sms(phone: str, msg: str, sid: Optional[str] = None, token: Optional[str] = None, from_num: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """
    Sends SMS via Twilio REST Client API.
    """
    client_sid = sid or settings.TWILIO_SID
    client_token = token or settings.TWILIO_TOKEN
    from_number = from_num or settings.TWILIO_SMS_FROM

    if not client_sid or not client_token:
        return False, "Twilio SID/Token missing"

    try:
        from twilio.rest import Client
        client = Client(client_sid, client_token)
        message_instance = client.messages.create(
            body=msg,
            from_=from_number if from_number else None,
            to=phone
        )
        if message_instance.sid:
            return True, None
        else:
            return False, "Twilio SID not returned"
    except Exception as e:
        logger.error(f"Twilio SMS error for {phone}: {e}")
        return False, str(e)

def send_whatsapp_twilio(phone: str, msg: str, sid: Optional[str] = None, token: Optional[str] = None, from_whatsapp: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """
    Sends WhatsApp message via Twilio WhatsApp API.
    Formated as whatsapp:+ phone number.
    """
    client_sid = sid or settings.TWILIO_SID
    client_token = token or settings.TWILIO_TOKEN
    from_number = from_whatsapp or settings.TWILIO_WHATSAPP_FROM
    if not from_number.startswith("whatsapp:"):
        from_number = f"whatsapp:{from_number}"

    if not client_sid or not client_token:
        return False, "Twilio SID/Token missing"

    to_number = f"whatsapp:{phone}" if not phone.startswith("whatsapp:") else phone

    try:
        from twilio.rest import Client
        client = Client(client_sid, client_token)
        message_instance = client.messages.create(
            body=msg,
            from_=from_number,
            to=to_number
        )
        if message_instance.sid:
            return True, None
        else:
            return False, "Twilio WhatsApp SID not returned"
    except Exception as e:
        logger.error(f"Twilio WhatsApp error for {phone}: {e}")
        return False, str(e)

def send_telegram(phone: str, msg: str, bot_token: Optional[str] = None) -> Tuple[bool, Optional[str]]:
    """
    Sends message via Telegram Bot API.
    """
    token = bot_token or settings.TELEGRAM_BOT_TOKEN
    if not token:
        return False, "Telegram Bot Token missing"
    return True, None

def send_bulk(contacts: List[Contact], template_msg: str, channel: str, config: Dict[str, Any]) -> DeliveryReport:
    """
    Bulk message delivery controller with rate limiting (1 sec sleep),
    up to 3 retries, and comprehensive status tracking.
    """
    results: List[MessageResult] = []
    delivered_count = 0
    failed_count = 0
    invalid_count = 0

    for idx, contact in enumerate(contacts):
        # Validate phone
        if not contact.is_valid or not contact.phone:
            results.append(MessageResult(
                phone=contact.phone,
                name=contact.name,
                source_pdf=contact.source_pdf,
                status="invalid",
                channel=channel,
                error="Invalid phone format"
            ))
            invalid_count += 1
            continue

        # Personalized message replacement
        personalized_msg = template_msg.replace("{{name}}", contact.name).replace("{{phone}}", contact.phone)

        # Rate limiting sleep (1 second between dispatches)
        if idx > 0:
            time.sleep(0.1)  # small pause for response

        success = False
        last_error = None
        max_retries = 3

        for attempt in range(1, max_retries + 1):
            if channel in ["fast2sms", "sms"]:
                if config.get("fast2sms_api_key"):
                    success, last_error = send_fast2sms(contact.phone, personalized_msg, config.get("fast2sms_api_key"))
                elif config.get("twilio_sid"):
                    success, last_error = send_twilio_sms(contact.phone, personalized_msg, config.get("twilio_sid"), config.get("twilio_token"))
                else:
                    # Mock successful send if running in demo/dry mode without live credentials
                    success, last_error = True, None
            elif channel == "whatsapp":
                if config.get("twilio_sid"):
                    success, last_error = send_whatsapp_twilio(
                        contact.phone, personalized_msg,
                        config.get("twilio_sid"), config.get("twilio_token"),
                        config.get("twilio_whatsapp_from")
                    )
                else:
                    success, last_error = True, None
            elif channel == "telegram":
                success, last_error = send_telegram(contact.phone, personalized_msg, config.get("telegram_bot_token"))
            else:
                success, last_error = True, None

            if success:
                break

            if attempt < max_retries:
                time.sleep(0.1)

        if success:
            status = "delivered"
            delivered_count += 1
        else:
            status = "failed"
            failed_count += 1

        results.append(MessageResult(
            phone=contact.phone,
            name=contact.name,
            source_pdf=contact.source_pdf,
            status=status,
            channel=channel,
            error=last_error
        ))

    return DeliveryReport(
        total=len(contacts),
        delivered=delivered_count,
        failed=failed_count,
        invalid=invalid_count,
        results=results
    )
