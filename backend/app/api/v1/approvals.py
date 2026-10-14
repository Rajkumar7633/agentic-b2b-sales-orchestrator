from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.approvals.engine import hitl_engine
from app.core.database import get_db
from app.core.rbac import require_reviewer
from app.core.security import UserContext, get_current_user
from app.domain.models.models import Approval
from app.domain.schemas.schemas import ApprovalActionRequest, ApprovalResponse

router = APIRouter(prefix="/approvals", tags=["HITL Approvals"])

APPROVAL_EXPIRY_HOURS = 48


async def _expire_stale_approvals(db: AsyncSession, tenant_id: str) -> None:
    """
    Mark any PENDING approvals older than APPROVAL_EXPIRY_HOURS as EXPIRED.
    Called lazily on every list request — lightweight, no background task needed for MVP.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=APPROVAL_EXPIRY_HOURS)
    result = await db.execute(
        select(Approval).where(
            Approval.tenant_id == tenant_id,
            Approval.status == "PENDING",
            Approval.created_at < cutoff
        )
    )
    stale = result.scalars().all()
    for appr in stale:
        appr.status = "EXPIRED"
    if stale:
        await db.commit()


@router.get("", response_model=list[ApprovalResponse])
async def list_approvals(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(get_current_user)
):
    # Lazily expire stale approvals before returning list
    await _expire_stale_approvals(db, user.tenant_id)

    query = select(Approval).where(Approval.tenant_id == user.tenant_id)
    if status:
        query = query.where(Approval.status == status.upper())
    query = query.order_by(Approval.created_at.desc())

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/{approval_id}/approve")
async def approve_action(
    approval_id: str,
    body: ApprovalActionRequest | None = None,
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(require_reviewer)
):
    try:
        edited_payload = body.edited_payload if body else None
        res = await hitl_engine.approve(
            db=db,
            approval_id=approval_id,
            user_id=user.user_id,
            tenant_id=user.tenant_id,
            edited_payload=edited_payload
        )
        return res
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))


@router.post("/{approval_id}/reject")
async def reject_action(
    approval_id: str,
    body: ApprovalActionRequest,
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(require_reviewer)
):
    reason = body.rejection_reason or "Rejected by human reviewer"
    try:
        res = await hitl_engine.reject(
            db=db,
            approval_id=approval_id,
            user_id=user.user_id,
            tenant_id=user.tenant_id,
            reason=reason
        )
        return res
    except ValueError as val_err:
        raise HTTPException(status_code=400, detail=str(val_err))


@router.post("/patch-stale-bodies")
async def patch_stale_approval_bodies(
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(get_current_user)
):
    """
    Retroactively patch all Approval records for this tenant that still have
    the old generic 'Hello, reaching out regarding alignment.' placeholder body.
    Replaces it with a rich, personalized fallback using context stored in the payload.
    """
    STALE_BODY = "Hello, reaching out regarding alignment."
    result = await db.execute(
        select(Approval).where(Approval.tenant_id == user.tenant_id)
    )
    all_approvals = result.scalars().all()

    patched = 0
    for appr in all_approvals:
        payload = dict(appr.draft_payload or {})
        body = payload.get("body_text", "")
        if not body or body.strip() == STALE_BODY:
            first_name = payload.get("first_name", "Marcus")
            company = payload.get("company_name", "your organization")
            title = payload.get("title", "VP of Procurement")
            why_now = payload.get("why_now_signal", "recent expansion and strategic growth initiatives")
            company_abbrev = company[:4].upper() if company else "ACME"

            rich_body = (
                f"Hi {first_name},\n\n"
                f"Congratulations on {company}'s recent {why_now} — this signals exactly the kind of "
                f"infrastructure and procurement momentum where NEXORA's Pursuit Engine has driven measurable outcomes "
                f"for peer engineering leaders.\n\n"
                f"As {title}, you're likely navigating the challenge of aligning vendor capability with delivery speed "
                f"under tight capital timelines. NEXORA's platform has helped similar leaders streamline pursuit "
                f"workflows while maintaining full human approval control at every critical decision gate.\n\n"
                f"Would you be open to a 15-minute discovery call next Tuesday or Wednesday? I'd love to share how "
                f"two comparable {company_abbrev}-scale teams reduced pursuit cycle time by 40%.\n\n"
                f"Best regards,\n"
                f"Alex Vance | NEXORA Enterprise Team\n"
                f"alex.vance@nexora.ai | Strategic Partnerships"
            )
            payload["body_text"] = rich_body
            if not payload.get("subject"):
                payload["subject"] = f"Strategic Alignment: {company}'s {why_now}"
            appr.draft_payload = payload
            patched += 1

    if patched > 0:
        await db.commit()

    return {"patched": patched, "message": f"Successfully patched {patched} stale approval bodies."}
