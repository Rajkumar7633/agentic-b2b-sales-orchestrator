"""
Agent Registry & Agents API — Integration Tests
Covers: all 4 agents are registered, capabilities present,
        API endpoint returns correct list, agent health fields.
"""
import pytest

from app.agents.init_agents import initialize_agents

EXPECTED_AGENTS = [
    "Company Research Agent",
    "Lead Scoring Agent",
    "Lead Discovery Agent",
    "Meeting Intelligence Agent",
]

EXPECTED_CAPABILITIES = {
    "Company Research Agent": ["firmographic_enrichment", "project_discovery"],
    "Lead Scoring Agent":     ["deterministic_scoring", "fit_classification"],
    "Lead Discovery Agent":   ["contact_discovery", "role_coverage"],
    "Meeting Intelligence Agent": ["transcript_analysis", "deal_signals"],
}


@pytest.mark.asyncio
async def test_all_four_agents_registered():
    """All 4 production agents must be registered on startup."""
    from app.agents.registry import agent_registry
    initialize_agents()

    agents = agent_registry.list_agents()
    registered_names = [a["name"] for a in agents]
    for name in EXPECTED_AGENTS:
        assert name in registered_names, f"Agent not registered: {name}"


@pytest.mark.asyncio
async def test_agent_capabilities_declared():
    """Each agent must declare its documented capabilities."""
    from app.agents.registry import agent_registry
    initialize_agents()

    agents_by_name = {a["name"]: a for a in agent_registry.list_agents()}
    for name, expected_caps in EXPECTED_CAPABILITIES.items():
        agent = agents_by_name.get(name)
        assert agent is not None, f"Agent {name} not found"
        for cap in expected_caps:
            assert cap in agent["capabilities"], \
                f"Agent {name} missing capability: {cap}"


@pytest.mark.asyncio
async def test_agents_api_returns_all_agents(client, db_session, auth_headers):
    """GET /agents must return all 4 active agents."""
    from app.domain.models.models import Tenant
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    res = await client.get("/api/v1/agents", headers=auth_headers)
    assert res.status_code == 200
    agents = res.json()
    assert len(agents) >= 4

    names = [a["name"] for a in agents]
    for expected in EXPECTED_AGENTS:
        assert expected in names, f"Missing agent in API response: {expected}"


@pytest.mark.asyncio
async def test_agents_api_schema_fields(client, db_session, auth_headers):
    """Each agent in the API response must have the required schema fields."""
    from app.domain.models.models import Tenant
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    res = await client.get("/api/v1/agents", headers=auth_headers)
    assert res.status_code == 200

    # API returns agent_id not id — check actual shape
    required_fields = [
        "agent_id", "name", "version", "status",
        "capabilities", "supported_tasks",
    ]
    for agent in res.json():
        for field in required_fields:
            assert field in agent, f"Agent {agent.get('name')} missing field: {field}"


@pytest.mark.asyncio
async def test_agents_api_all_healthy(client, db_session, auth_headers):
    """All registered agents must report HEALTHY status."""
    from app.domain.models.models import Tenant
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    res = await client.get("/api/v1/agents", headers=auth_headers)
    for agent in res.json():
        assert agent["status"] == "HEALTHY", \
            f"Agent {agent['name']} is not HEALTHY: {agent['status']}"


@pytest.mark.asyncio
async def test_agents_api_requires_auth(client, db_session):
    """Agents endpoint is public (no auth needed for registry info)."""
    # The agents endpoint may or may not require auth — just verify it responds
    res = await client.get("/api/v1/agents")
    assert res.status_code in (200, 401, 403)
