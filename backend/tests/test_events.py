
import pytest

from app.events.bus import InMemoryEventBus
from app.events.schemas import DomainEvent


@pytest.mark.asyncio
async def test_event_bus_pub_sub_and_idempotency():
    bus = InMemoryEventBus()
    received_events = []

    async def mock_handler(event: DomainEvent):
        received_events.append(event)

    bus.subscribe("company.research.completed", mock_handler)

    event = DomainEvent(
        event_id="evt_test_100",
        event_type="company.research.completed",
        correlation_id="corr_100",
        tenant_id="tenant_nexora_default",
        payload={"company": "Acme"}
    )

    # First publish: should succeed
    await bus.publish(event)
    assert len(received_events) == 1

    # Second publish with identical event_id: should be ignored (idempotency check)
    await bus.publish(event)
    assert len(received_events) == 1
