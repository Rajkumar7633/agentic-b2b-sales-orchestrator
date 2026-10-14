from typing import Any

from app.agents.base import BaseAgent
from app.domain.schemas.schemas import ContactSchema, LeadDiscoveryOutput
from app.integrations.lead.provider import MockLeadProvider


class LeadDiscoveryAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="lead_discovery_agent",
            name="Lead Discovery Agent",
            version="1.0.0",
            capabilities=["contact_discovery", "role_coverage", "decision_maker_mapping"],
            supported_tasks=["discover_leads"]
        )
        self.provider = MockLeadProvider()

    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        company_id = payload.get("company_id", "comp_001")
        company_name = payload.get("company_name", "Acme Construction")
        domain = payload.get("domain", None)

        contacts_raw = await self.provider.discover_leads(company_name, domain)
        contacts = [ContactSchema.model_validate({**c, "company_id": company_id}) for c in contacts_raw]

        output = LeadDiscoveryOutput(
            company_id=company_id,
            company_name=company_name,
            discovered_contacts=contacts
        )
        return output.model_dump()
