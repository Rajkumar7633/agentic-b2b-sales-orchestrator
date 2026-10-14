from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.agents.company_research import CompanyResearchAgent
from app.agents.supervisor import SupervisorAgent
from app.core.database import get_db
from app.core.security import UserContext, get_current_user
from app.domain.models.models import Approval, AuditLog, Company, Contact, Lead, OutreachMessage
from app.domain.schemas.schemas import CompanyPursueRequest, CompanyResponse

router = APIRouter(prefix="/accounts", tags=["Accounts & Companies"])
supervisor = SupervisorAgent()
research_agent = CompanyResearchAgent()


@router.get("", response_model=list[CompanyResponse])
async def list_accounts(
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(get_current_user)
):
    # Enforce tenant isolation with eager loading of projects and signals
    result = await db.execute(
        select(Company)
        .where(Company.tenant_id == user.tenant_id)
        .options(selectinload(Company.projects), selectinload(Company.signals))
    )
    companies = result.scalars().all()
    return companies


@router.get("/{account_id}", response_model=CompanyResponse)
async def get_account(
    account_id: str,
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(get_current_user)
):
    result = await db.execute(
        select(Company)
        .where(Company.id == account_id, Company.tenant_id == user.tenant_id)
        .options(selectinload(Company.projects), selectinload(Company.signals))
    )
    company = result.scalars().first()
    if not company:
        raise HTTPException(status_code=404, detail="Account not found")
    return company


@router.post("/{account_id}/research")
async def research_account(
    account_id: str,
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(get_current_user)
):
    result = await db.execute(
        select(Company).where(Company.id == account_id, Company.tenant_id == user.tenant_id)
    )
    company = result.scalars().first()
    if not company:
        raise HTTPException(status_code=404, detail="Account not found")

    research = await research_agent.execute({"company_name": company.name})

    company.why_now_signal = research.get("why_now_signal")
    company.recommended_service = research.get("recommended_service")
    company.research_summary = research.get("research_summary")
    company.research_confidence = research.get("confidence", 0.9)
    company.pipeline_stage = "RESEARCHED"

    await db.commit()
    return research


@router.post("/pursue")
async def pursue_account(
    body: CompanyPursueRequest,
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(get_current_user)
):
    company_name = body.company_name or "Acme Construction"

    result = await db.execute(
        select(Company).where(Company.name == company_name, Company.tenant_id == user.tenant_id)
    )
    company = result.scalars().first()
    if not company:
        company = Company(
            tenant_id=user.tenant_id,
            name=company_name,
            domain=body.domain or f"{company_name.lower().replace(' ', '')}.com",
            pipeline_stage="TARGET"
        )
        db.add(company)
        await db.commit()
        await db.refresh(company)
        # Audit: new account created
        db.add(AuditLog(
            tenant_id=user.tenant_id,
            user_id=user.user_id,
            action="ACCOUNT_CREATED",
            resource_type="Company",
            resource_id=company.id,
            details={"name": company_name}
        ))
        await db.commit()

    # Stage 1: mark as RESEARCHING before orchestration starts
    company.pipeline_stage = "RESEARCHING"
    await db.commit()

    orchestration_result = await supervisor.execute({
        "company_name": company.name,
        "tenant_id": user.tenant_id
    })

    # Audit: pursuit triggered
    db.add(AuditLog(
        tenant_id=user.tenant_id,
        user_id=user.user_id,
        action="PURSUIT_TRIGGERED",
        resource_type="Company",
        resource_id=company.id,
        details={"company_name": company_name, "correlation_id": orchestration_result.get("correlation_id")}
    ))

    # ─────────────────────────────────────────────────────────────
    # BUG FIX 1: Persist discovered contacts to the DB
    # ─────────────────────────────────────────────────────────────
    discovered_contacts = orchestration_result.get("discovered_contacts", [])
    persisted_contacts = []
    for c in discovered_contacts:
        # Avoid duplicate contacts for the same company + email
        existing = await db.execute(
            select(Contact).where(
                Contact.company_id == company.id,
                Contact.email == c.get("email")
            )
        )
        if existing.scalars().first():
            continue
        contact_row = Contact(
            tenant_id=user.tenant_id,
            company_id=company.id,
            first_name=c.get("first_name", "Unknown"),
            last_name=c.get("last_name", ""),
            title=c.get("title", "Executive"),
            email=c.get("email"),
            linkedin_url=c.get("linkedin_url"),
            seniority=c.get("seniority"),
            influence_score=float(c.get("influence_score", 0.5)),
            relationship_status=c.get("relationship_status", "NEW"),
            source=c.get("source", "LeadDiscoveryAgent"),
        )
        db.add(contact_row)
        persisted_contacts.append(contact_row)

    await db.flush()  # get IDs for contacts before creating leads

    # ─────────────────────────────────────────────────────────────
    # BUG FIX 3: Persist Lead + OutreachMessage rows to DB
    # ─────────────────────────────────────────────────────────────
    scoring = orchestration_result.get("scoring", {})
    outreach_draft = orchestration_result.get("outreach_draft", {})

    # Create a Lead record for the top scored contact
    top_contact_row = persisted_contacts[0] if persisted_contacts else None
    lead_row = Lead(
        tenant_id=user.tenant_id,
        company_id=company.id,
        contact_id=top_contact_row.id if top_contact_row else None,
        pipeline_stage="CONTACT_IDENTIFIED",
        fit_score=int(scoring.get("fit_score", 0)),
        fit_classification=scoring.get("fit_classification", "LOW"),
        score_reasoning=scoring.get("reasoning", ""),
        positive_signals=scoring.get("positive_signals", []),
        negative_signals=scoring.get("negative_signals", []),
        score_confidence=float(scoring.get("score_confidence", 0.0)),
    )
    db.add(lead_row)
    await db.flush()  # get lead ID

    # Persist the outreach message draft
    if outreach_draft:
        outreach_row = OutreachMessage(
            tenant_id=user.tenant_id,
            lead_id=lead_row.id,
            contact_id=top_contact_row.id if top_contact_row else None,
            channel=outreach_draft.get("channel", "LINKEDIN"),
            subject=outreach_draft.get("subject"),
            body_text=outreach_draft.get("body_text", ""),
            reasoning=outreach_draft.get("reasoning", ""),
            approval_status="PENDING",
        )
        db.add(outreach_row)
        await db.flush()

    # ─────────────────────────────────────────────────────────────
    # Pipeline stage progression
    # ─────────────────────────────────────────────────────────────
    company.pipeline_stage = "QUALIFIED"
    lead_row.pipeline_stage = "OUTREACH_SENT"

    # Persist pending HITL Approval record to Database
    approval_req = orchestration_result.get("approval_required")
    if approval_req:
        appr_obj = Approval(
            tenant_id=user.tenant_id,
            entity_type=approval_req.get("entity_type", "OUTREACH"),
            entity_id=approval_req.get("entity_id", "out_default"),
            action_type=approval_req.get("action_type", "SEND_LINKEDIN"),
            draft_payload=approval_req.get("draft_payload", {}),
            risk_level=approval_req.get("risk_level", "MEDIUM"),
            status="PENDING",
            requested_by_agent=approval_req.get("requested_by_agent", "supervisor_agent")
        )
        db.add(appr_obj)

    await db.commit()
    return orchestration_result
