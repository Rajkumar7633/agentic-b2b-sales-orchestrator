import logging
import uuid
from typing import Any

from app.agents.base import BaseAgent
from app.agents.company_research import CompanyResearchAgent
from app.agents.crm import CRMPipelineAgent
from app.agents.followup import FollowupAgent
from app.agents.lead_discovery import LeadDiscoveryAgent
from app.agents.lead_scoring import LeadScoringAgent
from app.agents.meeting_scheduler import MeetingSchedulerAgent
from app.agents.outreach import OutreachAgent
from app.agents.planner import PlannerAgent
from app.events.bus import global_event_bus
from app.events.schemas import DomainEvent

logger = logging.getLogger(__name__)


class SupervisorAgent(BaseAgent):
    """
    Supervisor Agent orchestrates multi-agent goal execution, state tracking,
    event bus publishing, retry logic, and strict HITL Approval policy enforcement.
    """
    def __init__(self):
        super().__init__(
            agent_id="supervisor_agent",
            name="Supervisor Agent",
            version="1.0.0",
            capabilities=["agent_orchestration", "policy_enforcement", "hitl_gatekeeper"],
            supported_tasks=["pursue_account", "orchestrate_goal"]
        )
        self.planner = PlannerAgent()
        self.research_agent = CompanyResearchAgent()
        self.discovery_agent = LeadDiscoveryAgent()
        self.scoring_agent = LeadScoringAgent()
        self.outreach_agent = OutreachAgent()
        self.followup_agent = FollowupAgent()
        self.meeting_agent = MeetingSchedulerAgent()
        self.crm_agent = CRMPipelineAgent()

    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        company_name = payload.get("company_name", "Acme Construction")
        tenant_id = payload.get("tenant_id", "tenant_nexora_default")
        correlation_id = payload.get("correlation_id", f"corr_{uuid.uuid4().hex[:8]}")

        logger.info(f"[SUPERVISOR] Initiating pursuit workflow for '{company_name}' (Correlation: {correlation_id})")

        # Step 1: Planning
        plan = await self.planner.execute({"goal": f"Pursue account {company_name}", "company_name": company_name})

        # Step 2: Company Research
        await global_event_bus.publish(DomainEvent(
            event_type="company.research.requested",
            correlation_id=correlation_id,
            tenant_id=tenant_id,
            actor="supervisor_agent",
            payload={"company_name": company_name}
        ))
        research_res = await self.research_agent.execute({"company_name": company_name})

        await global_event_bus.publish(DomainEvent(
            event_type="company.research.completed",
            correlation_id=correlation_id,
            tenant_id=tenant_id,
            actor="company_research_agent",
            payload=research_res
        ))

        # Step 3: Lead Discovery
        discovery_res = await self.discovery_agent.execute({
            "company_name": company_name,
            "company_id": f"comp_{uuid.uuid4().hex[:6]}"
        })

        top_contact = discovery_res["discovered_contacts"][0] if discovery_res.get("discovered_contacts") else {}

        # Step 4: Lead Scoring
        scoring_res = await self.scoring_agent.execute({
            "company_research": research_res,
            "contact": top_contact
        })

        await global_event_bus.publish(DomainEvent(
            event_type="lead.scoring.completed",
            correlation_id=correlation_id,
            tenant_id=tenant_id,
            actor="lead_scoring_agent",
            payload=scoring_res
        ))

        # Step 5: Outreach Draft
        outreach_res = await self.outreach_agent.execute({
            "company_name": company_name,
            "contact": top_contact,
            "why_now_signal": research_res.get("why_now_signal")
        })

        # Step 6: Enforcement of HITL Gate
        approval_req = {
            "entity_type": "OUTREACH",
            "entity_id": f"out_{uuid.uuid4().hex[:6]}",
            "action_type": "SEND_LINKEDIN",
            "draft_payload": outreach_res,
            "risk_level": "MEDIUM",
            "status": "PENDING",
            "requested_by_agent": "supervisor_agent"
        }

        await global_event_bus.publish(DomainEvent(
            event_type="outreach.approval.requested",
            correlation_id=correlation_id,
            tenant_id=tenant_id,
            actor="supervisor_agent",
            payload=approval_req
        ))

        return {
            "status": "APPROVAL_REQUIRED",
            "correlation_id": correlation_id,
            "plan": plan,
            "research": research_res,
            "discovered_contacts": discovery_res.get("discovered_contacts", []),
            "scoring": scoring_res,
            "outreach_draft": outreach_res,
            "approval_required": approval_req
        }
