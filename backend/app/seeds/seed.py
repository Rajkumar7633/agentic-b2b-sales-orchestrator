import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.init_agents import initialize_agents
from app.agents.registry import agent_registry
from app.core.database import AsyncSessionLocal, Base, engine
from app.core.security import hash_password
from app.domain.models.models import (
    AgentRegistryItem,
    Tenant,
    User,
)

logger = logging.getLogger(__name__)


async def seed_database(session: AsyncSession | None = None):
    """
    Initializes database tables, default system tenant, workspace users, and active AI Agent Registry items.
    Does NOT hardcode any demo business records (Acme, Tesla, Apex, etc.).
    Production business records are populated 100% dynamically from user-uploaded workbooks.
    """
    initialize_agents()

    async def _do_seed(db: AsyncSession):
        # Check if already seeded (use admin user as sentinel)
        res = await db.execute(select(User).where(User.id == "usr_admin_001"))
        existing_user = res.scalars().first()
        if existing_user:
            logger.info("Database system schema already initialized. Skipping.")
            return

        logger.info("Initializing clean NEXORA database workspace (0 hardcoded business data)...")

        # 1. Tenant (default tenant)
        existing_tenant = await db.get(Tenant, "tenant_nexora_default")
        if not existing_tenant:
            tenant = Tenant(id="tenant_nexora_default", name="NEXORA Sales Pursuit Workspace")
            db.add(tenant)

        # 2. Workspace Users
        admin = User(
            id="usr_admin_001",
            tenant_id="tenant_nexora_default",
            email="admin@nexora.ai",
            full_name="Raj Kumar (Admin)",
            hashed_password=hash_password("password123"),
            role="ADMIN"
        )
        reviewer = User(
            id="usr_reviewer_001",
            tenant_id="tenant_nexora_default",
            email="reviewer@nexora.ai",
            full_name="Sarah Jenkins (Reviewer)",
            hashed_password=hash_password("password123"),
            role="REVIEWER"
        )
        rep = User(
            id="usr_rep_001",
            tenant_id="tenant_nexora_default",
            email="rep@nexora.ai",
            full_name="Alex Vance (Sales Rep)",
            hashed_password=hash_password("password123"),
            role="SALES_REP"
        )
        db.add_all([admin, reviewer, rep])

        # 3. Agent Registry Items for 4 Active AI Agents
        for agent in agent_registry.list_all():
            item = AgentRegistryItem(
                id=agent.agent_id,
                name=agent.name,
                version=agent.version,
                status="HEALTHY",
                capabilities=agent.capabilities,
                supported_tasks=agent.supported_tasks,
                model="grok-beta",
                total_invocations=0,
                total_tokens_used=0,
                estimated_cost_usd=0.0
            )
            db.add(item)

        await db.commit()
        logger.info("Clean workspace initialization complete. Ready for workbook upload.")

    if session is not None:
        await _do_seed(session)
    else:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with AsyncSessionLocal() as db:
            await _do_seed(db)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed_database())
