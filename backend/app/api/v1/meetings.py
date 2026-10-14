from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.meeting_intelligence.intelligence import meeting_intelligence_agent
from app.core.database import get_db
from app.core.security import UserContext, get_current_user
from app.domain.models.models import Company, Lead, Meeting


router = APIRouter(prefix="/meetings", tags=["Meetings & Intelligence"])


@router.get("")
async def list_meetings(
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(get_current_user)
):
    result = await db.execute(select(Meeting).where(Meeting.tenant_id == user.tenant_id))
    meetings = result.scalars().all()
    out = []
    for m in meetings:
        res_lead = await db.execute(select(Lead).where(Lead.id == m.lead_id))
        lead = res_lead.scalars().first()
        comp_name = "Target Company"
        if lead:
            res_c = await db.execute(select(Company).where(Company.id == lead.company_id))
            comp = res_c.scalars().first()
            if comp:
                comp_name = comp.name

        out.append({
            "id": m.id,
            "title": m.title,
            "company_name": comp_name,
            "status": m.status,
            "meeting_link": m.meeting_link,
            "meeting_date": m.meeting_date,
            "transcript_text": m.transcript_text,
            "transcript_analysis": m.transcript_analysis,
            "created_at": m.created_at.isoformat() if m.created_at else None
        })
    return out


@router.post("")
async def create_human_meeting(
    payload: dict[str, Any],
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(get_current_user)
):
    title = payload.get("title", "Executive Discovery Call")
    lead_id = payload.get("lead_id")
    meeting_link = payload.get("meeting_link", "https://meet.google.com/abc-defg-hij")
    meeting_date = payload.get("meeting_date", "Tomorrow at 2:00 PM")

    if not lead_id:
        res_lead = await db.execute(select(Lead).where(Lead.tenant_id == user.tenant_id).limit(1))
        lead = res_lead.scalars().first()
        if not lead:
            # Check if any company exists to attach a Lead
            res_comp = await db.execute(select(Company).where(Company.tenant_id == user.tenant_id).limit(1))
            comp = res_comp.scalars().first()
            if comp:
                lead = Lead(
                    tenant_id=user.tenant_id,
                    company_id=comp.id,
                    pipeline_stage="IDENTIFIED",
                    fit_score=75,
                    fit_classification="MEDIUM",
                    score_reasoning="Auto-created for human scheduled meeting",
                    positive_signals=["Human initiated Google Meet scheduling"]
                )
                db.add(lead)
                await db.flush()
                lead_id = lead.id
            else:
                # Create default company & lead so scheduling never crashes
                comp = Company(
                    tenant_id=user.tenant_id,
                    name="Target Pursuit Account",
                    pipeline_stage="IDENTIFIED"
                )
                db.add(comp)
                await db.flush()
                lead = Lead(
                    tenant_id=user.tenant_id,
                    company_id=comp.id,
                    pipeline_stage="IDENTIFIED",
                    fit_score=80
                )
                db.add(lead)
                await db.flush()
                lead_id = lead.id
        else:
            lead_id = lead.id

    mtg = Meeting(
        tenant_id=user.tenant_id,
        lead_id=lead_id,
        title=title,
        status="SCHEDULED",
        calendar_provider="HUMAN_CALENDAR",
        meeting_link=meeting_link,
        meeting_date=meeting_date
    )
    db.add(mtg)

    # Update Lead status
    res_lead = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = res_lead.scalars().first()
    if lead:
        lead.meeting_status = "SCHEDULED"
        lead.meeting_link = meeting_link
        lead.meeting_date = meeting_date
        lead.pipeline_stage = "MEETING_SCHEDULED"

    await db.commit()
    await db.refresh(mtg)
    return mtg


@router.post("/transcript")
async def analyze_meeting_transcript(
    payload: dict[str, Any],
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(get_current_user)
):
    meeting_id = payload.get("meeting_id")
    transcript_text = payload.get("transcript", "").strip()

    if not transcript_text:
        raise HTTPException(status_code=400, detail="Transcript text is required for AI analysis.")

    # Find meeting or use latest
    mtg = None
    if meeting_id:
        res_m = await db.execute(select(Meeting).where(Meeting.id == meeting_id, Meeting.tenant_id == user.tenant_id))
        mtg = res_m.scalars().first()

    if not mtg:
        res_m = await db.execute(select(Meeting).where(Meeting.tenant_id == user.tenant_id).order_by(Meeting.created_at.desc()).limit(1))
        mtg = res_m.scalars().first()

    comp_name = "Target Company"
    lead = None
    if mtg:
        res_l = await db.execute(select(Lead).where(Lead.id == mtg.lead_id))
        lead = res_l.scalars().first()
        if lead:
            res_c = await db.execute(select(Company).where(Company.id == lead.company_id))
            comp = res_c.scalars().first()
            if comp:
                comp_name = comp.name

    # Execute Meeting Intelligence Agent
    analysis = await meeting_intelligence_agent.run({
        "transcript": transcript_text,
        "company_name": comp_name
    })

    if mtg:
        mtg.transcript_text = transcript_text
        mtg.transcript_analysis = analysis
        mtg.status = "ANALYZED"

    if lead:
        lead.transcript_text = transcript_text
        lead.transcript_analysis = analysis
        lead.meeting_status = "ANALYZED"
        lead.pipeline_stage = "TRANSCRIPT_ANALYZED"
        if analysis.get("next_actions"):
            lead.score_reasoning = f"Meeting Analysis: {analysis.get('summary')}"

        res_c = await db.execute(select(Company).where(Company.id == lead.company_id))
        comp = res_c.scalars().first()
        if comp and analysis.get("next_actions"):
            comp.recommended_next_action = str(analysis["next_actions"][0])
            comp.pipeline_stage = "TRANSCRIPT_ANALYZED"

    await db.commit()

    return {
        "status": "SUCCESS",
        "meeting_id": mtg.id if mtg else None,
        "company_name": comp_name,
        "analysis": analysis
    }


@router.post("/propose")
async def propose_meeting_slots(
    payload: dict[str, Any],
    user: UserContext = Depends(get_current_user)
):
    return {
        "status": "SUCCESS",
        "proposed_slots": payload.get("proposed_slots", ["Tomorrow at 2:00 PM EST"]),
        "calendar_provider": "HUMAN_CALENDAR"
    }

