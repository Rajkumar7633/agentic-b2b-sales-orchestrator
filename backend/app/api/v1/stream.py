import asyncio
import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core.security import UserContext, get_current_user
from app.core.streaming import broadcaster, stream_agent_execution

router = APIRouter(prefix="/stream", tags=["Real-Time Streaming & Telemetry"])


class BroadcastEventRequest(BaseModel):
    event_type: str
    data: dict


@router.get("/pursuit")
async def stream_pursuit_execution(
    company_name: str = Query("Acme Corporation", description="Company target name"),
    speed: float = Query(0.05, description="Inter-step delay in seconds"),
    current_user: UserContext = Depends(get_current_user),
):
    """
    Server-Sent Events (SSE) endpoint streaming real-time multi-agent reasoning,
    tool execution, ICP fit scoring, and HITL gate creation.
    """
    return StreamingResponse(
        stream_agent_execution(company_name=company_name, tenant_id=current_user.tenant_id, speed=speed),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/events")
async def stream_system_events(
    current_user: UserContext = Depends(get_current_user),
):
    """
    Server-Sent Events (SSE) broadcast channel for live platform events (pipeline updates, approvals, agents).
    """
    queue = broadcaster.subscribe()

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            # Yield initial connection heartbeat
            init_msg = {
                "event_type": "CONNECTED",
                "message": "Connected to NEXORA Live Event Stream",
                "tenant_id": current_user.tenant_id,
            }
            yield f"data: {json.dumps(init_msg)}\n\n"

            while True:
                # Wait for broadcasted message or send periodic keepalive
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield data
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            broadcaster.unsubscribe(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/broadcast")
async def broadcast_event(
    payload: BroadcastEventRequest,
    current_user: UserContext = Depends(get_current_user),
):
    """
    Broadcasts a custom event to all active real-time dashboard listeners.
    """
    data = {"tenant_id": current_user.tenant_id, "user_id": current_user.user_id, **payload.data}
    await broadcaster.broadcast(payload.event_type, data)
    return {"status": "BROADCASTED", "event_type": payload.event_type}
