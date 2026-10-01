"""
ChurnGuard Zero-Trust PII Protection Module for JobSentinel.
Hashes and masks personal identifiable information (PII) to ensure privacy compliance.
"""

import hashlib
import re
from typing import Dict, Any, Optional
from job_sentinel.config import HASH_SALT


class PIIProtector:
    """Zero-Trust PII protection engine inspired by ChurnGuard architecture."""

    def __init__(self, salt: Optional[str] = None):
        self.salt = salt or HASH_SALT

    def hash_value(self, raw_value: str) -> str:
        """Computes salted SHA-256 hash of a string."""
        if not raw_value:
            return ""
        salted = f"{self.salt}:{raw_value.strip().lower()}"
        return hashlib.sha256(salted.encode("utf-8")).hexdigest()

    def mask_email(self, email: str) -> str:
        """Masks email address, e.g., 'john.doe@example.com' -> 'j***e@example.com'."""
        if not email or "@" not in email:
            return "*****"
        local_part, domain = email.split("@", 1)
        if len(local_part) <= 2:
            masked_local = local_part[0] + "*"
        else:
            masked_local = local_part[0] + "*" * (len(local_part) - 2) + local_part[-1]
        return f"{masked_local}@{domain}"

    def mask_phone(self, phone: str) -> str:
        """Masks phone number leaving only last 4 digits visible."""
        digits = re.sub(r"\D", "", phone)
        if len(digits) < 4:
            return "****"
        return "*" * (len(digits) - 4) + digits[-4:]

    def sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitizes sensitive fields in a dictionary."""
        sanitized = data.copy()
        pii_fields = ["email", "phone", "candidate_name", "ssn", "address"]
        for field in pii_fields:
            if field in sanitized and isinstance(sanitized[field], str):
                if field == "email":
                    sanitized[field] = self.mask_email(sanitized[field])
                elif field == "phone":
                    sanitized[field] = self.mask_phone(sanitized[field])
                else:
                    sanitized[field] = f"[HASHED_{self.hash_value(sanitized[field])[:8]}]"
        return sanitized
