
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import UserContext, get_current_user
from app.domain.models.models import Lead
from app.domain.schemas.schemas import LeadResponse

router = APIRouter(prefix="/leads", tags=["Leads & Pipeline"])


@router.get("", response_model=list[LeadResponse])
async def list_leads(
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(get_current_user)
):
    result = await db.execute(select(Lead).where(Lead.tenant_id == user.tenant_id))
    return result.scalars().all()


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: str,
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(get_current_user)
):
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id, Lead.tenant_id == user.tenant_id)
    )
    lead = result.scalars().first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead
