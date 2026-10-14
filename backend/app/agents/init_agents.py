from app.agents.company_research import CompanyResearchAgent
from app.agents.lead_discovery import LeadDiscoveryAgent
from app.agents.lead_scoring import LeadScoringAgent
from app.agents.meeting_intelligence.intelligence import MeetingIntelligenceAgent
from app.agents.registry import agent_registry


def initialize_agents():
    """
    Registers the 4 active AI Agents in the NEXORA Pursuit Engine:
    1. Company Research Agent (Firmographics, Why Now, Project Signals)
    2. Opportunity Qualification Agent (ICP Fit, Service Matching, PURSUE/REVIEW/REJECT)
    3. Contact Discovery & Ranking Agent (Decision Maker Ranking & Source Links)
    4. Meeting Intelligence Agent (Transcript Analysis, Pain Points, Buying Intent)
    """
    agent_registry.register(CompanyResearchAgent())
    agent_registry.register(LeadScoringAgent())
    agent_registry.register(LeadDiscoveryAgent())
    agent_registry.register(MeetingIntelligenceAgent())
