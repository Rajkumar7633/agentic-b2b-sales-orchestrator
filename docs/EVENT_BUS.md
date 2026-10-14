# Event Bus Specification (`docs/EVENT_BUS.md`)

## 1. Overview

Communication between agents in NEXORA is event-driven. Agents publish domain events to the **`InMemoryEventBus`** rather than invoking each other synchronously.

## 2. Event Schema (`DomainEvent`)

```python
class DomainEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:8]}")
    event_type: str
    correlation_id: str
    tenant_id: str
    payload: Dict[str, Any]
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
```

## 3. Registered Event Topics

| Topic | Publisher | Subscribers | Payload Keys |
| :--- | :--- | :--- | :--- |
| `pursuit.initiated` | API Router | Supervisor | `company_name`, `domain`, `tenant_id` |
| `company.research.requested` | Supervisor | Company Research Agent | `company_name`, `domain` |
| `company.research.completed` | Company Research Agent | Lead Discovery Agent | `company_name`, `why_now_signal`, `projects` |
| `leads.discovered` | Lead Discovery Agent | Lead Scoring Agent | `company_id`, `contacts` |
| `lead.scoring.completed` | Lead Scoring Agent | Outreach Agent | `fit_score`, `fit_classification`, `signals` |
| `outreach.approval.requested` | Outreach Agent | HITL Approval Engine | `lead_id`, `channel`, `body_text`, `subject` |
| `outreach.approved` | HITL Approval Engine | Follow-up Agent, CRM Agent | `approval_id`, `execution_result` |
| `outreach.rejected` | HITL Approval Engine | Outreach Agent | `approval_id`, `rejection_reason` |

## 4. Reliability, Retries & Dead Letter Queue (DLQ)

- **Idempotency**: The event bus tracks `processed_event_ids: Set[str]`. Duplicate events are automatically dropped.
- **Retries**: When a subscriber handler raises an exception, the event bus retries up to `max_retries = 3` with exponential backoff (0.1s, 0.2s, 0.4s).
- **Dead Letter Queue (DLQ)**: If an event fails all retries, it is moved to `bus.dead_letter_queue` for audit inspection and manual replay.
