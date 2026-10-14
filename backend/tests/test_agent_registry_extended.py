"""
Agent Registry Extended Unit Tests
Covers get(), list_agents(), and sync_to_db() (create, update, delete obsolete).
"""
import pytest

from app.agents.init_agents import initialize_agents
from app.agents.registry import AgentRegistry, agent_registry
from app.domain.models.models import AgentRegistryItem, Tenant


@pytest.mark.asyncio
async def test_agent_registry_get_and_sync_to_db(db_session):
    initialize_agents()

    # 1. Test get()
    agent = agent_registry.get("company_research_agent")
    assert agent is not None
    assert agent.name == "Company Research Agent"

    assert agent_registry.get("non_existent_agent") is None

    # 2. Test sync_to_db() (inserts new items)
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    await agent_registry.sync_to_db(db_session)

    # Verify items created in DB
    result = await db_session.execute(
        AgentRegistryItem.__table__.select()
    )
    items = result.fetchall()
    assert len(items) >= 4

    # 3. Test sync_to_db() update branch
    agent.total_invocations += 5
    await agent_registry.sync_to_db(db_session)

    # 4. Test obsolete agent deletion
    custom_registry = AgentRegistry()
    custom_registry.register(agent)  # register only 1 agent
    await custom_registry.sync_to_db(db_session)

    res_obsolete = await db_session.execute(
        AgentRegistryItem.__table__.select()
    )
    assert len(res_obsolete.fetchall()) == 1
