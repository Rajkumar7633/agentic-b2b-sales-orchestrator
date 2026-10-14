import asyncio
import logging
import random
from collections.abc import Awaitable, Callable

from app.events.schemas import DomainEvent

logger = logging.getLogger(__name__)

EventHandler = Callable[[DomainEvent], Awaitable[None]]


class EventBus:
    """Abstract EventBus interface for decoupling agent communications."""
    async def publish(self, event: DomainEvent) -> None:
        raise NotImplementedError

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        raise NotImplementedError


class InMemoryEventBus(EventBus):
    """
    In-memory async event bus implementation with idempotency check,
    retry handling, and dead-letter logging.
    """
    def __init__(self, max_retries: int = 3):
        self._subscribers: dict[str, list[EventHandler]] = {}
        self._processed_events: set[str] = set()
        self.dead_letter_queue: list[DomainEvent] = []
        self.max_retries = max_retries

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.info(f"Subscribed handler {handler.__name__} to event topic '{event_type}'")

    async def publish(self, event: DomainEvent) -> None:
        # Idempotency check: prevent processing duplicate events
        if event.event_id in self._processed_events:
            logger.warning(f"Duplicate event ignored: {event.event_id} ({event.event_type})")
            return

        self._processed_events.add(event.event_id)
        logger.info(f"[EVENT BUS] Published {event.event_type} (Correlation ID: {event.correlation_id})")

        handlers = self._subscribers.get(event.event_type, [])
        for handler in handlers:
            retries = 0
            success = False
            while retries <= self.max_retries and not success:
                try:
                    await handler(event)
                    success = True
                except Exception as exc:
                    retries += 1
                    logger.error(
                        f"Error in handler {handler.__name__} for event {event.event_id} "
                        f"(Attempt {retries}/{self.max_retries + 1}): {exc!s}"
                    )
                    if retries <= self.max_retries:
                        backoff = (0.1 * (2 ** retries)) + random.uniform(0, 0.05)
                        await asyncio.sleep(backoff)
                    else:
                        logger.critical(f"Moving event {event.event_id} to Dead Letter Queue")
                        self.dead_letter_queue.append(event)


# Global singleton instance for local MVP execution
global_event_bus = InMemoryEventBus()
