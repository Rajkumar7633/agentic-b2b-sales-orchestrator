from fastapi import APIRouter

from app.agents.registry import agent_registry

router = APIRouter(prefix="/agents", tags=["Agent Registry"])


@router.get("")
async def list_registered_agents():
    return agent_registry.list_agents()
