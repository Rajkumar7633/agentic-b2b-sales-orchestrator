import logging
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

class EmailProvider:
    async def send_email(self, to_email: str, subject: str, body: str) -> dict[str, Any]:
        raise NotImplementedError


class MockEmailProvider(EmailProvider):
    """
    Mock Email provider for simulated outbound email delivery.
    """
    async def send_email(self, to_email: str, subject: str, body: str) -> dict[str, Any]:
        msg_id = f"email_{uuid.uuid4().hex[:8]}"
        logger.info(f"[MOCK EMAIL] Sent email to {to_email} with subject '{subject}' (ID: {msg_id})")
        return {
            "status": "SENT",
            "provider": "MockEmailProvider",
            "provider_message_id": msg_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "to_email": to_email,
            "subject": subject
        }
