
import pytest

from app.events.bus import InMemoryEventBus
from app.events.schemas import DomainEvent


@pytest.mark.asyncio
async def test_event_bus_dead_letter_on_persistent_failure():
    """Events that fail all retries must go to the Dead Letter Queue."""
    bus = InMemoryEventBus(max_retries=2)
    failures = 0

    async def always_failing_handler(event: DomainEvent):
        nonlocal failures
        failures += 1
        raise RuntimeError("Simulated handler failure for DLQ test")

    bus.subscribe("agent.failed", always_failing_handler)

    event = DomainEvent(
        event_id="evt_dlq_test_001",
        event_type="agent.failed",
        correlation_id="corr_dlq_001",
        tenant_id="tenant_nexora_default",
        payload={"agent_id": "company_research_agent", "reason": "LLM timeout"}
    )

    await bus.publish(event)

    # Handler should have been retried max_retries+1 times
    assert failures == bus.max_retries + 1
    # Event should appear in DLQ
    assert len(bus.dead_letter_queue) == 1
    assert bus.dead_letter_queue[0].event_id == "evt_dlq_test_001"


@pytest.mark.asyncio
async def test_multiple_subscribers_receive_same_event():
    """Multiple handlers subscribed to the same event type must all fire."""
    bus = InMemoryEventBus()
    received_by_handler_a = []
    received_by_handler_b = []

    async def handler_a(event: DomainEvent):
        received_by_handler_a.append(event.event_id)

    async def handler_b(event: DomainEvent):
        received_by_handler_b.append(event.event_id)

    bus.subscribe("lead.scoring.completed", handler_a)
    bus.subscribe("lead.scoring.completed", handler_b)

    event = DomainEvent(
        event_id="evt_multi_sub_001",
        event_type="lead.scoring.completed",
        correlation_id="corr_multi_001",
        tenant_id="tenant_nexora_default",
        payload={"fit_score": 88, "fit_classification": "HIGH"}
    )
    await bus.publish(event)

    assert "evt_multi_sub_001" in received_by_handler_a
    assert "evt_multi_sub_001" in received_by_handler_b
