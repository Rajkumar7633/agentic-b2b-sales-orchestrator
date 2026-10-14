import pytest

from app.agents.lead_scoring import LeadScoringAgent


@pytest.mark.asyncio
async def test_deterministic_scoring_high_fit():
    agent = LeadScoringAgent()
    payload = {
        "company_research": {
            "industry": "Enterprise Construction & Engineering",
            "size": "1,000 - 5,000 employees",
            "why_now_signal": "Secured $85M Series C funding",
            "recommended_service": "NEXORA Pursuit Engine",
            "projects": [{"project_name": "Data Center Expansion"}],
            "signals": [{"signal_type": "FUNDING"}]
        },
        "contact": {
            "seniority": "VP",
            "title": "VP Procurement"
        }
    }

    result = await agent.execute(payload)
    assert result["fit_score"] >= 80
    assert result["fit_classification"] == "HIGH"
    assert len(result["positive_signals"]) >= 3
    assert result["confidence"] > 0.8
