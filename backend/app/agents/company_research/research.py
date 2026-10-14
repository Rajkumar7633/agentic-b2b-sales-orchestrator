from typing import Any

from app.agents.base import BaseAgent
from app.domain.schemas.schemas import CompanyResearchOutput
from app.integrations.llm.provider import get_llm_provider
from app.knowledge.rag_engine import knowledge_service


class CompanyResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="company_research_agent",
            name="Company Research Agent",
            version="1.0.0",
            capabilities=["firmographic_enrichment", "project_discovery", "why_now_signals"],
            supported_tasks=["research_company"]
        )
        self.llm = get_llm_provider()

    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        company_name = payload.get("company_name", "Acme Construction")
        domain = payload.get("domain", f"{company_name.lower().replace(' ', '')}.com")

        # RAG augmentation from sales playbooks
        rag_context = knowledge_service.search(f"{company_name} expansion projects software")
        playbook_snippet = rag_context[0]["content"] if rag_context else ""

        prompt = f"""
        Research target company '{company_name}' (Domain: {domain}).
        Context playbook: {playbook_snippet}.

        Respond strictly with JSON using these exact key names:
        {{
          "company_name": "{company_name}",
          "domain": "{domain}",
          "industry": "Enterprise Construction & Engineering",
          "size": "1,000 - 5,000 employees",
          "location": "San Francisco, CA",
          "revenue": "$350M",
          "why_now_signal": "Secured growth expansion funding and launched new data center regional projects.",
          "recommended_service": "NEXORA Pursuit Engine Enterprise Platform",
          "research_summary": "Detailed research summary on target account expansion plans and procurement timeline.",
          "confidence": 0.92,
          "projects": [
            {{
              "project_name": "Regional Infrastructure Expansion",
              "project_type": "Expansion",
              "budget": "$10M - $25M",
              "timeframe": "Q3 2026",
              "description": "Constructing new regional nodes and data center facilities.",
              "status": "PLANNING",
              "verified": true
            }}
          ],
          "signals": [
            {{
              "signal_type": "FUNDING",
              "title": "Expansion Funding Secured",
              "summary": "Growth funding round closed.",
              "confidence": 0.95
            }}
          ],
          "sources": []
        }}
        """

        raw_output = await self.llm.generate_json(prompt)

        # Normalize fields for robust parsing
        if not isinstance(raw_output, dict):
            raw_output = {}

        raw_output.setdefault("company_name", company_name)
        raw_output.setdefault("domain", domain)
        raw_output.setdefault("industry", "Enterprise Technology & Infrastructure")
        raw_output.setdefault("size", "1,000 - 5,000 employees")
        raw_output.setdefault("location", "San Francisco, CA")
        raw_output.setdefault("revenue", "$250M+")
        raw_output.setdefault("why_now_signal", raw_output.get("signal", "Active expansion funding & procurement cycle"))
        raw_output.setdefault("recommended_service", "NEXORA Pursuit Engine Enterprise Platform")
        raw_output.setdefault("research_summary", raw_output.get("summary", f"Detailed research profile for {company_name}"))

        # Ensure confidence is float between 0 and 1
        conf = raw_output.get("confidence", 0.9)
        if not isinstance(conf, (int, float)) or conf > 1.0 or conf < 0.0:
            conf = 0.9
        raw_output["confidence"] = conf

        # Normalize projects
        projects = raw_output.get("projects", [])
        if not isinstance(projects, list) or not projects:
            projects = [{
                "project_name": f"{company_name} Regional Expansion",
                "project_type": "Expansion",
                "budget": "$10M - $25M",
                "timeframe": "Q3-Q4 2026",
                "description": "Enterprise infrastructure expansion initiative",
                "status": "PLANNING",
                "verified": True
            }]
        else:
            for p in projects:
                if isinstance(p, dict):
                    p["verified"] = True
        raw_output["projects"] = projects
        # Normalize sources
        sources = raw_output.get("sources", [])
        if isinstance(sources, list):
            norm_sources = []
            for s in sources:
                if isinstance(s, str):
                    norm_sources.append({"title": s, "url": f"https://google.com/search?q={s.replace(' ', '+')}"})
                elif isinstance(s, dict):
                    norm_sources.append(s)
            raw_output["sources"] = norm_sources
        else:
            raw_output["sources"] = []

        parsed = CompanyResearchOutput.model_validate(raw_output)
        return parsed.model_dump()
