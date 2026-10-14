import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


def generate_event_id() -> str:
    return f"evt_{uuid.uuid4().hex}"


class DomainEvent(BaseModel):
    event_id: str = Field(default_factory=generate_event_id)
    event_type: str  # e.g., company.research.completed, outreach.approval.requested
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    correlation_id: str
    causation_id: str | None = None
    actor: str = "system"
    tenant_id: str
    payload: dict[str, Any]
    schema_version: str = "1.0"
