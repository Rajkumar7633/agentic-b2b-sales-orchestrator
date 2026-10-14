from app.agents.analytics import AnalyticsAgent, analytics
from app.agents.company_research import CompanyResearchAgent, research
from app.agents.crm import CRMPipelineAgent, crm
from app.agents.followup import FollowupAgent, followup
from app.agents.lead_discovery import LeadDiscoveryAgent, discovery
from app.agents.lead_scoring import LeadScoringAgent, scoring
from app.agents.meeting_scheduler import MeetingSchedulerAgent, meeting
from app.agents.outreach import OutreachAgent, outreach
from app.agents.planner import PlannerAgent, planner

# Re-export module aliases for backward compatibility with tests
from app.agents.supervisor import SupervisorAgent, supervisor

__all__ = [
    "AnalyticsAgent",
    "CRMPipelineAgent",
    "CompanyResearchAgent",
    "FollowupAgent",
    "LeadDiscoveryAgent",
    "LeadScoringAgent",
    "MeetingSchedulerAgent",
    "OutreachAgent",
    "PlannerAgent",
    "SupervisorAgent",
    "analytics",
    "crm",
    "discovery",
    "followup",
    "meeting",
    "outreach",
    "planner",
    "research",
    "scoring",
    "supervisor"
]
