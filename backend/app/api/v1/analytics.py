from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.analytics import AnalyticsAgent
from app.core.database import get_db
from app.core.security import UserContext, get_current_user
from app.domain.schemas.schemas import AnalyticsResponse

router = APIRouter(prefix="/analytics", tags=["Analytics & Reporting"])
analytics_agent = AnalyticsAgent()


@router.get("", response_model=AnalyticsResponse)
async def get_analytics(
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(get_current_user)
):
    # Pass the request-scoped DB session so the agent doesn't open a second connection
    res = await analytics_agent.execute({
        "tenant_id": user.tenant_id,
        "_db_session": db
    })
    return res


@router.get("/dashboard")
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(get_current_user)
):
    res = await analytics_agent.execute({
        "tenant_id": user.tenant_id,
        "_db_session": db
    })
    return res
