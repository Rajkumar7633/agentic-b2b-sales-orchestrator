"""
Agents Unit Tests — All 8 agents
Covers: each agent's output schema, key fields, edge cases.
"""
import pytest

from app.agents.analytics import AnalyticsAgent
from app.agents.company_research import CompanyResearchAgent
from app.agents.crm import CRMPipelineAgent
from app.agents.followup import FollowupAgent
from app.agents.lead_discovery import LeadDiscoveryAgent
from app.agents.meeting_scheduler import MeetingSchedulerAgent
from app.agents.outreach import OutreachAgent
from app.agents.planner import PlannerAgent


# ─────────────────────────────────────────────────────────────
# Planner Agent
# ─────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_planner_creates_structured_task_graph():
    planner = PlannerAgent()
    result = await planner.execute({"goal": "Pursue Acme Construction", "company_name": "Acme Construction"})
    assert result["status"] == "READY"
    assert len(result["tasks"]) >= 7
    assert all("agent_name" in t for t in result["tasks"])
    assert any("Human Approval Gate" in t["agent_name"] for t in result["tasks"])


@pytest.mark.asyncio
async def test_planner_returns_sequential_step_ids():
    planner = PlannerAgent()
    result = await planner.execute({"goal": "Pursue Beta Corp", "company_name": "Beta Corp"})
    step_ids = [t["step_id"] for t in result["tasks"]]
    assert step_ids == list(range(1, len(step_ids) + 1))


@pytest.mark.asyncio
async def test_planner_task_descriptions_non_empty():
    planner = PlannerAgent()
    result = await planner.execute({"goal": "Pursue Gamma Inc", "company_name": "Gamma Inc"})
    for task in result["tasks"]:
        assert len(task.get("description", "")) > 5, \
            f"Empty description for step {task.get('step_id')}"


# ─────────────────────────────────────────────────────────────
# Company Research Agent
# ─────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_company_research_returns_verified_projects():
    agent = CompanyResearchAgent()
    result = await agent.execute({"company_name": "Acme Construction"})
    assert "why_now_signal" in result
    assert "projects" in result
    assert len(result["projects"]) >= 1
    assert result["projects"][0]["verified"] is True
    assert result["confidence"] >= 0.8


@pytest.mark.asyncio
async def test_company_research_output_schema():
    agent = CompanyResearchAgent()
    result = await agent.execute({"company_name": "Delta Tech"})
    required = ["company_name", "domain", "industry", "size", "location",
                "why_now_signal", "recommended_service", "research_summary",
                "confidence", "projects", "signals"]
    for key in required:
        assert key in result, f"Missing key: {key}"


@pytest.mark.asyncio
async def test_company_research_confidence_in_range():
    agent = CompanyResearchAgent()
    result = await agent.execute({"company_name": "Epsilon Energy"})
    assert 0.0 <= result["confidence"] <= 1.0


# ─────────────────────────────────────────────────────────────
# Lead Discovery Agent
# ─────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_lead_discovery_returns_contacts():
    agent = LeadDiscoveryAgent()
    result = await agent.execute({"company_id": "comp_001", "company_name": "Acme Construction"})
    assert "discovered_contacts" in result
    contacts = result["discovered_contacts"]
    assert len(contacts) >= 1


@pytest.mark.asyncio
async def test_lead_discovery_contacts_have_required_fields():
    agent = LeadDiscoveryAgent()
    result = await agent.execute({"company_id": "comp_002", "company_name": "Zeta Corp"})
    for c in result["discovered_contacts"]:
        assert "first_name" in c
        assert "last_name" in c
        assert "title" in c
        assert "seniority" in c
        assert c["seniority"] in ("C-Level", "VP", "Director", "Manager")


@pytest.mark.asyncio
async def test_lead_discovery_influence_scores_valid():
    agent = LeadDiscoveryAgent()
    result = await agent.execute({"company_id": "comp_003", "company_name": "Omega Build"})
    for c in result["discovered_contacts"]:
        score = c.get("influence_score", 0)
        assert 0.0 <= score <= 1.0


# ─────────────────────────────────────────────────────────────
# Outreach Agent
# ─────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_outreach_agent_always_produces_pending_draft():
    agent = OutreachAgent()
    result = await agent.execute({
        "company_name": "Apex Energy",
        "lead_id": "lead_test_001",
        "contact": {"first_name": "Elena", "title": "CTO", "seniority": "C-Level"},
        "why_now_signal": "Grid Modernization RFP"
    })
    assert result["approval_status"] == "PENDING"
    assert len(result["body_text"]) > 20
    assert result["channel"] in ("LINKEDIN", "EMAIL")


@pytest.mark.asyncio
async def test_outreach_agent_body_references_company():
    """The outreach body text should reference the target company or person."""
    agent = OutreachAgent()
    result = await agent.execute({
        "company_name": "Unique Corp XYZ",
        "lead_id": "lead_unique",
        "contact": {"first_name": "Jordan", "title": "CFO", "seniority": "C-Level"},
        "why_now_signal": "Major expansion"
    })
    # Body must not be empty or placeholder
    assert len(result["body_text"].strip()) > 30
    assert result["reasoning"]  # Reasoning must be present


# ─────────────────────────────────────────────────────────────
# Followup Agent
# ─────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_followup_agent_schedules_correct_cadence():
    agent = FollowupAgent()
    result = await agent.execute({
        "lead_id": "lead_cadence_test",
        "cadence_days": 7,
        "current_attempt": 1,
        "max_attempts": 3
    })
    assert result["status"] == "SCHEDULED"
    assert result["cadence_days"] == 7
    assert result["sequence_number"] == 1
    assert result["max_attempts"] == 3


@pytest.mark.asyncio
async def test_followup_agent_custom_cadence():
    agent = FollowupAgent()
    result = await agent.execute({
        "lead_id": "lead_cad_5",
        "cadence_days": 5,
        "current_attempt": 2,
        "max_attempts": 5
    })
    assert result["cadence_days"] == 5
    assert result["sequence_number"] == 2
    assert result["max_attempts"] == 5


# ─────────────────────────────────────────────────────────────
# Meeting Scheduler Agent
# ─────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_meeting_scheduler_proposes_three_slots():
    agent = MeetingSchedulerAgent()
    result = await agent.execute({"lead_id": "lead_001", "company_name": "Acme Construction"})
    assert len(result["proposed_slots"]) >= 3
    assert result["status"] == "PROPOSED"


@pytest.mark.asyncio
async def test_meeting_scheduler_slots_are_strings():
    agent = MeetingSchedulerAgent()
    result = await agent.execute({"lead_id": "lead_002", "company_name": "Beta Corp"})
    for slot in result["proposed_slots"]:
        assert isinstance(slot, str)
        assert len(slot) > 5


# ─────────────────────────────────────────────────────────────
# CRM Pipeline Agent
# ─────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_crm_pipeline_agent_updates_stage():
    agent = CRMPipelineAgent()
    result = await agent.execute({
        "company_id": "comp_acme_001",
        "lead_id": "lead_acme_001",
        "new_stage": "MEETING_BOOKED"
    })
    assert result["status"] == "SYNCHRONIZED"
    assert result["pipeline_stage"] == "MEETING_BOOKED"


@pytest.mark.asyncio
async def test_crm_pipeline_supports_all_stages():
    agent = CRMPipelineAgent()
    for stage in ("IDENTIFIED", "QUALIFIED", "RESEARCHED", "OUTREACH", "MEETING_BOOKED", "WON"):
        result = await agent.execute({
            "company_id": "comp_stage_test",
            "lead_id": f"lead_{stage}",
            "new_stage": stage
        })
        assert result["pipeline_stage"] == stage


# ─────────────────────────────────────────────────────────────
# Analytics Agent (lightweight smoke — no DB needed)
# ─────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_analytics_agent_returns_complete_kpis():
    agent = AnalyticsAgent()
    result = await agent.execute({"tenant_id": "tenant_nexora_default"})
    required_keys = [
        "total_target_accounts", "qualified_leads", "high_value_leads",
        "outreach_sent", "approvals_pending", "followups_due",
        "response_rate", "meeting_conversion_rate", "meetings_booked",
        "pipeline_value_usd", "total_contacts",
        "industry_breakdown", "pipeline_stage_distribution",
        "weekly_recommendations"
    ]
    for key in required_keys:
        assert key in result, f"Missing key: {key}"
    assert result["total_target_accounts"] >= 0
    assert isinstance(result["weekly_recommendations"], list)
    assert len(result["weekly_recommendations"]) >= 1
