from typing import Any


class LeadProvider:
    async def discover_leads(self, company_name: str, domain: str = None) -> list[dict[str, Any]]:
        raise NotImplementedError


class MockLeadProvider(LeadProvider):
    """
    Mock Lead Provider identifying key executive decision makers for target accounts.
    """
    async def discover_leads(self, company_name: str, domain: str = None) -> list[dict[str, Any]]:
        domain_name = domain or f"{company_name.lower().replace(' ', '')}.com"

        return [
            {
                "first_name": "Marcus",
                "last_name": "Vance",
                "title": "Vice President of Infrastructure & Procurement",
                "email": f"marcus.vance@{domain_name}",
                "linkedin_url": f"https://linkedin.com/in/marcus-vance-{company_name.lower()[:4]}",
                "seniority": "VP",
                "influence_score": 0.92,
                "relationship_status": "NEW",
                "source": "MockLeadProvider"
            },
            {
                "first_name": "Elena",
                "last_name": "Rostova",
                "title": "Chief Technology Officer (CTO)",
                "email": f"elena.rostova@{domain_name}",
                "linkedin_url": "https://linkedin.com/in/elena-rostova-cto",
                "seniority": "C-Level",
                "influence_score": 0.98,
                "relationship_status": "NEW",
                "source": "MockLeadProvider"
            },
            {
                "first_name": "David",
                "last_name": "Chen",
                "title": "Director of Project Execution",
                "email": f"david.chen@{domain_name}",
                "linkedin_url": "https://linkedin.com/in/david-chen-dir",
                "seniority": "Director",
                "influence_score": 0.81,
                "relationship_status": "NEW",
                "source": "MockLeadProvider"
            }
        ]
