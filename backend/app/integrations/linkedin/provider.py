import logging
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

class LinkedInProvider:
    async def send_message(self, recipient_url: str, message: str) -> dict[str, Any]:
        raise NotImplementedError


class MockLinkedInProvider(LinkedInProvider):
    """
    Mock LinkedIn adapter recording simulated LinkedIn outreach delivery.
    """
    async def send_message(self, recipient_url: str, message: str) -> dict[str, Any]:
        msg_id = f"ln_msg_{uuid.uuid4().hex[:8]}"
        logger.info(f"[MOCK LINKEDIN] Successfully dispatched outreach to {recipient_url} (ID: {msg_id})")
        return {
            "status": "DELIVERED",
            "provider": "MockLinkedInProvider",
            "provider_message_id": msg_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "recipient_url": recipient_url
        }
