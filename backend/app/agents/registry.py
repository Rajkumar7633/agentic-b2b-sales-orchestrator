import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import BaseAgent
from app.domain.models.models import AgentRegistryItem

logger = logging.getLogger(__name__)


class AgentRegistry:
    """
    Agent Registry maintaining health status, capabilities, versioning,
    and runtime performance of all registered platform agents.
    Syncs in-memory registry status with DB persistence layer.
    """
    def __init__(self):
        self._agents: dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        self._agents[agent.agent_id] = agent
        logger.info(f"Registered agent '{agent.name}' (ID: {agent.agent_id}, Version: {agent.version})")

    def get(self, agent_id: str) -> BaseAgent | None:
        return self._agents.get(agent_id)

    def list_agents(self) -> list[dict]:
        return [agent.get_info() for agent in self._agents.values()]

    def list_all(self) -> list[BaseAgent]:
        return list(self._agents.values())

    async def sync_to_db(self, db: AsyncSession) -> None:
        """Syncs all registered in-memory agent statuses and metrics to the DB AgentRegistryItem table."""
        active_ids = set(self._agents.keys())

        # Remove obsolete agents not in active list
        from sqlalchemy import delete
        await db.execute(delete(AgentRegistryItem).where(AgentRegistryItem.id.not_in(active_ids)))

        for agent in self._agents.values():
            result = await db.execute(select(AgentRegistryItem).where(AgentRegistryItem.id == agent.agent_id))
            item = result.scalars().first()
            if not item:
                item = AgentRegistryItem(
                    id=agent.agent_id,
                    name=agent.name,
                    version=agent.version,
                    status=agent.status,
                    capabilities=agent.capabilities,
                    supported_tasks=agent.supported_tasks,
                    total_invocations=agent.total_invocations,
                    total_tokens_used=agent.total_tokens_used,
                    estimated_cost_usd=agent.estimated_cost_usd,
                    last_heartbeat=agent.last_heartbeat
                )
                db.add(item)
            else:
                item.status = agent.status
                item.total_invocations = agent.total_invocations
                item.total_tokens_used = agent.total_tokens_used
                item.estimated_cost_usd = agent.estimated_cost_usd
                item.last_heartbeat = agent.last_heartbeat
        await db.commit()


agent_registry = AgentRegistry()
