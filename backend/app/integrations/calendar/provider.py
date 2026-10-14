import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

logger = logging.getLogger(__name__)

class CalendarProvider:
    async def get_availability(self) -> list[str]:
        raise NotImplementedError

    async def create_meeting(self, title: str, selected_slot: str, attendee_email: str) -> dict[str, Any]:
        raise NotImplementedError


class MockCalendarProvider(CalendarProvider):
    """
    Mock Calendar provider returning available meeting slots and scheduling events.
    """
    async def get_availability(self) -> list[str]:
        now = datetime.now(timezone.utc)
        slot1 = (now + timedelta(days=2)).replace(hour=14, minute=0, second=0).strftime("%Y-%m-%d %H:%M PST")
        slot2 = (now + timedelta(days=3)).replace(hour=10, minute=30, second=0).strftime("%Y-%m-%d %H:%M PST")
        slot3 = (now + timedelta(days=4)).replace(hour=15, minute=0, second=0).strftime("%Y-%m-%d %H:%M PST")
        return [slot1, slot2, slot3]

    async def create_meeting(self, title: str, selected_slot: str, attendee_email: str) -> dict[str, Any]:
        event_id = f"cal_evt_{uuid.uuid4().hex[:8]}"
        meeting_link = f"https://meet.nexora.ai/room-{event_id}"
        logger.info(f"[MOCK CALENDAR] Scheduled '{title}' at {selected_slot} with {attendee_email}")
        return {
            "status": "BOOKED",
            "provider_event_id": event_id,
            "meeting_link": meeting_link,
            "selected_slot": selected_slot,
            "attendee_email": attendee_email,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
