import asyncio
import json
import logging
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SystemEventBroadcaster:
    """In-memory async broadcast channel for Server-Sent Events (SSE)."""

    def __init__(self):
        self._subscribers: list[asyncio.Queue] = []

    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._subscribers.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        if q in self._subscribers:
            self._subscribers.remove(q)

    async def broadcast(self, event_type: str, data: dict[str, Any]) -> None:
        payload = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "data": data,
            "timestamp": _now_iso(),
        }
        raw = f"data: {json.dumps(payload)}\n\n"
        dead = []
        for q in self._subscribers:
            try:
                q.put_nowait(raw)
            except Exception:
                dead.append(q)
        for q in dead:
            self.unsubscribe(q)


broadcaster = SystemEventBroadcaster()


async def stream_agent_execution(
    company_name: str,
    tenant_id: str = "tenant_nexora_default",
    speed: float = 0.05,
) -> AsyncGenerator[str, None]:
    """
    Streams realistic, structured multi-agent execution steps via SSE.
    Simulates reasoning, tool execution, ICP fit scoring, outreach synthesis, and HITL gate.
    """
    correlation_id = f"corr_{uuid.uuid4().hex[:8]}"

    steps = [
        {
            "step": 1,
            "total_steps": 6,
            "phase": "INIT",
            "agent_id": "supervisor_agent",
            "agent_name": "Supervisor Agent",
            "thought": f"Decomposing sales pursuit workflow for '{company_name}' into autonomous sub-tasks.",
            "data": {"status": "INITIALIZED", "correlation_id": correlation_id},
            "progress": 15,
        },
        {
            "step": 2,
            "total_steps": 6,
            "phase": "DISCOVERY",
            "agent_id": "lead_discovery_agent",
            "agent_name": "Lead Discovery Agent",
            "thought": f"Scanning business registries, domain DNS, and key decision-maker signals for {company_name}.",
            "data": {
                "discovered_contacts": 3,
                "primary_decision_maker": "VP of Operations / Managing Director",
                "verified_domain": f"{company_name.lower().replace(' ', '')}.com",
            },
            "progress": 35,
        },
        {
            "step": 3,
            "total_steps": 6,
            "phase": "RESEARCH",
            "agent_id": "company_research_agent",
            "agent_name": "Company Research Agent",
            "thought": "Ingesting recent news, infrastructure hiring spikes, and technographic footprint.",
            "data": {
                "why_now_signal": "Active multi-million capital expansion & hiring spree",
                "estimated_budget": "$2.5M - $5.0M",
                "technographic_stack": ["AWS", "Kubernetes", "PostgreSQL", "Salesforce"],
            },
            "progress": 55,
        },
        {
            "step": 4,
            "total_steps": 6,
            "phase": "SCORING",
            "agent_id": "lead_scoring_agent",
            "agent_name": "Lead Scoring Agent",
            "thought": "Calculating deterministic ICP fit score based on firmographic, revenue, and intent weights.",
            "data": {
                "icp_fit_score": 92.5,
                "tier": "TIER_1",
                "recommendation": "Priority outbound outreach with executive briefing copy",
            },
            "progress": 75,
        },
        {
            "step": 5,
            "total_steps": 6,
            "phase": "SYNTHESIS",
            "agent_id": "outreach_agent",
            "agent_name": "Outreach Generator Agent",
            "thought": "Drafting personalized multichannel value propositions (LinkedIn + Direct Email).",
            "data": {
                "channels": ["LINKEDIN", "EMAIL"],
                "subject": f"Strategic Partnership & Scale Optimization for {company_name}",
                "preview_text": "Noticed your recent expansion into regional projects. Our enterprise engine accelerates delivery...",
            },
            "progress": 90,
        },
        {
            "step": 6,
            "total_steps": 6,
            "phase": "GOVERNANCE",
            "agent_id": "hitl_approval_agent",
            "agent_name": "Approval Governance Agent",
            "thought": "Evaluating outreach risk against brand compliance rules. Staging at Human-in-the-Loop gate.",
            "data": {
                "approval_ticket_id": f"appr_{uuid.uuid4().hex[:10]}",
                "risk_rating": "MEDIUM",
                "requires_review": True,
                "status": "PENDING_APPROVAL",
            },
            "progress": 100,
        },
    ]

    for item in steps:
        payload = {
            "event_id": str(uuid.uuid4()),
            "tenant_id": tenant_id,
            "company_name": company_name,
            "timestamp": _now_iso(),
            **item,
        }
        yield f"data: {json.dumps(payload)}\n\n"
        if speed > 0:
            await asyncio.sleep(speed)
