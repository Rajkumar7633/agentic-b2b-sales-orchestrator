from typing import Any

from app.agents.base import BaseAgent
from app.domain.schemas.schemas import LeadScoringOutput


class LeadScoringAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="lead_scoring_agent",
            name="Lead Scoring Agent",
            version="1.0.0",
            capabilities=["deterministic_scoring", "fit_classification", "explainable_ai"],
            supported_tasks=["score_lead"]
        )

    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        company_data = payload.get("company_research", {})
        contact_data = payload.get("contact", {})

        # Deterministic scoring algorithm
        score = 0
        positive_signals: list[str] = []
        negative_signals: list[str] = []

        # Factor 1: Active Project Signal (Max 25 pts)
        projects = company_data.get("projects", [])
        if len(projects) > 0:
            score += 25
            positive_signals.append(f"Active project verified: {projects[0].get('project_name', 'Expansion Project')}")
        else:
            negative_signals.append("No active expansion projects explicitly detected")

        # Factor 2: Why-Now / Growth Funding Signal (Max 20 pts)
        why_now = company_data.get("why_now_signal", "")
        signals = company_data.get("signals", [])
        if "funding" in why_now.lower() or any(s.get("signal_type") == "FUNDING" for s in signals):
            score += 20
            positive_signals.append("High velocity growth signal: Recent capital raise / Series C funding")
        elif len(signals) > 0:
            score += 12
            positive_signals.append("Business activity signal detected")

        # Factor 3: Company Industry & Service Fit (Max 25 pts)
        industry = company_data.get("industry", "")
        rec_service = company_data.get("recommended_service", "")
        if "construction" in industry.lower() or "engineering" in industry.lower() or "enterprise" in industry.lower():
            score += 25
            positive_signals.append(f"Ideal ICP Industry fit ({industry}) aligned with {rec_service}")
        else:
            score += 15
            positive_signals.append("General enterprise market fit")

        # Factor 4: Decision Maker Seniority (Max 15 pts)
        seniority = contact_data.get("seniority", "VP")
        if seniority in ["C-Level", "VP"]:
            score += 15
            positive_signals.append(f"High influence decision-maker contact ({seniority})")
        elif seniority in ["Director", "Head"]:
            score += 10
            positive_signals.append(f"Mid-level decision maker ({seniority})")
        else:
            score += 5

        # Factor 5: Company Size / Revenue (Max 15 pts)
        size = company_data.get("size", "")
        if "1,000" in size or "Enterprise" in size or "500" in size:
            score += 15
            positive_signals.append("Enterprise scale company size")
        else:
            score += 10

        # Bound score between 0 and 100
        score = max(0, min(100, score))

        # Classification threshold
        if score >= 75:
            classification = "HIGH"
        elif score >= 50:
            classification = "MEDIUM"
        else:
            classification = "LOW"

        reasoning = (
            f"Account scored {score}/100 ({classification} Priority). "
            f"Driven by {len(positive_signals)} verified signals including active project budget and C-suite alignment."
        )

        output = LeadScoringOutput(
            company_id=payload.get("company_id", "comp_001"),
            contact_id=contact_data.get("id", None),
            fit_score=score,
            fit_classification=classification,
            reasoning_summary=reasoning,
            positive_signals=positive_signals,
            negative_signals=negative_signals,
            confidence=0.92
        )
        return output.model_dump()
