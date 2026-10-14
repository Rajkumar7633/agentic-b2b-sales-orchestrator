from datetime import datetime, timedelta, timezone
from typing import Any

from app.agents.base import BaseAgent


class FollowupAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="followup_agent",
            name="Follow-up Agent",
            version="1.0.0",
            capabilities=["cadence_management", "followup_state_machine"],
            supported_tasks=["schedule_followup", "check_followups"]
        )

    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        lead_id = payload.get("lead_id", "lead_001")
        cadence_days = payload.get("cadence_days", 5)
        current_attempt = payload.get("current_attempt", 1)
        max_attempts = payload.get("max_attempts", 3)

        due_at = datetime.now(timezone.utc) + timedelta(days=cadence_days)

        output = {
            "id": f"flw_{lead_id[:6]}_{current_attempt}",
            "tenant_id": payload.get("tenant_id", "tenant_nexora_default"),
            "lead_id": lead_id,
            "sequence_number": current_attempt,
            "status": "SCHEDULED",
            "due_at": due_at.isoformat(),
            "current_attempt": current_attempt,
            "max_attempts": max_attempts,
            "cadence_days": cadence_days
        }
        return output
