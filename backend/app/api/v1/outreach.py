from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.outreach import OutreachAgent
from app.core.database import get_db
from app.core.security import UserContext, get_current_user
from app.domain.models.models import OutreachMessage
from app.domain.schemas.schemas import OutreachResponse

router = APIRouter(prefix="/outreach", tags=["Outreach & Messages"])
outreach_agent = OutreachAgent()


@router.get("", response_model=list[OutreachResponse])
async def list_outreach_messages(
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(get_current_user)
):
    result = await db.execute(select(OutreachMessage).where(OutreachMessage.tenant_id == user.tenant_id))
    return result.scalars().all()


@router.post("/draft")
async def create_outreach_draft(
    payload: dict[str, Any],
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(get_current_user)
):
    draft = await outreach_agent.execute(payload)
    return draft
