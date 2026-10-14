from datetime import datetime, timezone
from typing import Any

from app.agents.base import BaseAgent
from app.integrations.calendar.provider import MockCalendarProvider


class MeetingSchedulerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="meeting_scheduler_agent",
            name="Meeting Scheduler Agent",
            version="1.0.0",
            capabilities=["calendar_availability", "slot_proposal", "meeting_booking"],
            supported_tasks=["propose_meeting", "book_meeting"]
        )
        self.calendar = MockCalendarProvider()

    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        lead_id = payload.get("lead_id", "lead_001")
        company_name = payload.get("company_name", "Target Account")

        action = payload.get("action", "propose")
        if action == "book":
            selected_slot = payload.get("selected_slot", "2026-08-15 14:00 PST")
            attendee_email = payload.get("attendee_email", "prospect@acme.com")
            booked = await self.calendar.create_meeting(
                title=f"NEXORA Pursuit Introduction - {company_name}",
                selected_slot=selected_slot,
                attendee_email=attendee_email
            )
            return booked

        # Default action: propose slots
        slots = await self.calendar.get_availability()
        output = {
            "id": f"mtg_{lead_id[:6]}",
            "tenant_id": payload.get("tenant_id", "tenant_nexora_default"),
            "lead_id": lead_id,
            "title": f"NEXORA Pursuit Introduction - {company_name}",
            "description": "Executive alignment on expansion projects and enterprise pursuit automation.",
            "proposed_slots": slots,
            "selected_slot": None,
            "status": "PROPOSED",
            "calendar_provider": "MockCalendarProvider",
            "meeting_link": None,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        return output
