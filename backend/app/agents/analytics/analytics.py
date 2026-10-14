import collections
from typing import Any

from sqlalchemy import func, select

from app.agents.base import BaseAgent
from app.core.database import AsyncSessionLocal
from app.domain.models.models import Approval, Company, Contact, Meeting, OutreachMessage
from app.domain.schemas.schemas import AnalyticsResponse


class AnalyticsAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="analytics_agent",
            name="Analytics Agent",
            version="2.0.0",
            capabilities=["kpi_computation", "conversion_forecasting", "weekly_recommendations"],
            supported_tasks=["compute_analytics"]
        )

    async def _query_stats(self, db, tenant_id: str) -> dict:
        """Run all DB queries against the provided session."""
        # ── Accounts ──────────────────────────────────────────────────
        companies_result = await db.execute(
            select(Company).where(Company.tenant_id == tenant_id)
        )
        companies = companies_result.scalars().all()
        total_accounts = len(companies)

        # Pipeline stage distribution
        stage_dist: dict[str, int] = dict(collections.Counter(
            (c.pipeline_stage or "IDENTIFIED") for c in companies
        ))

        # Industry breakdown – normalise compound strings ("Developer / Residential" → "Developer")
        industry_counter: collections.Counter = collections.Counter()
        for c in companies:
            raw = (c.industry or "Enterprise").strip()
            primary = raw.split("/")[0].strip() if "/" in raw else raw
            industry_counter[primary] += 1
        top_industries = dict(industry_counter.most_common(10))

        qualified_leads = stage_dist.get("QUALIFIED", 0) + stage_dist.get("RESEARCHED", 0)
        high_value_leads = stage_dist.get("RESEARCHED", 0)

        # ── Contacts ─────────────────────────────────────────────────
        contacts_result = await db.execute(
            select(func.count(Contact.id)).where(Contact.tenant_id == tenant_id)
        )
        total_contacts = contacts_result.scalar() or 0

        # ── Outreach ─────────────────────────────────────────────────
        outreach_result = await db.execute(
            select(func.count(OutreachMessage.id)).where(OutreachMessage.tenant_id == tenant_id)
        )
        outreach_sent = outreach_result.scalar() or 0

        # ── Approvals ────────────────────────────────────────────────
        approvals_result = await db.execute(
            select(func.count(Approval.id)).where(
                Approval.tenant_id == tenant_id,
                Approval.status == "PENDING"
            )
        )
        approvals_pending = approvals_result.scalar() or 0

        # ── Meetings ─────────────────────────────────────────────────
        meetings_result = await db.execute(
            select(func.count(Meeting.id)).where(Meeting.tenant_id == tenant_id)
        )
        meetings_booked = meetings_result.scalar() or 0

        return dict(
            total_accounts=total_accounts,
            stage_dist=stage_dist,
            top_industries=top_industries,
            qualified_leads=qualified_leads,
            high_value_leads=high_value_leads,
            total_contacts=total_contacts,
            outreach_sent=outreach_sent,
            approvals_pending=approvals_pending,
            meetings_booked=meetings_booked,
        )

    async def run(self, payload: dict[str, Any]) -> dict[str, Any]:
        tenant_id = payload.get("tenant_id", "tenant_nexora_default")

        # Tests can inject a db session via "_db_session" to avoid event-loop conflicts
        injected_db = payload.get("_db_session")
        if injected_db is not None:
            stats = await self._query_stats(injected_db, tenant_id)
        else:
            async with AsyncSessionLocal() as db:
                stats = await self._query_stats(db, tenant_id)

        total_accounts = stats["total_accounts"]
        outreach_sent = stats["outreach_sent"]
        meetings_booked = stats["meetings_booked"]
        approvals_pending = stats["approvals_pending"]
        total_contacts = stats["total_contacts"]
        qualified_leads = stats["qualified_leads"]
        high_value_leads = stats["high_value_leads"]
        top_industries = stats["top_industries"]
        stage_dist = stats["stage_dist"]

        # ── Derived KPIs ─────────────────────────────────────────────────
        response_rate = round((outreach_sent / max(total_accounts, 1)) * 100, 1)
        meeting_conversion_rate = round((meetings_booked / max(outreach_sent, 1)) * 100, 1)
        pipeline_value_usd = total_accounts * 75_000.0  # estimated avg deal size

        # ── Weekly Recommendations (dynamic) ─────────────────────────────
        recs: list[str] = []
        if total_accounts == 0:
            recs.append("Upload your pursuit workbook to begin tracking target accounts.")
        else:
            recs.append(
                f"You have {total_accounts} target accounts imported — "
                f"{qualified_leads} have been qualified via AI pipeline."
            )
        if total_contacts > 0:
            recs.append(
                f"{total_contacts} decision-maker contacts tracked across your target portfolio."
            )
        if approvals_pending > 0:
            recs.append(
                f"Review {approvals_pending} pending outreach drafts in the Approval Center before dispatching."
            )
        if outreach_sent > 0:
            recs.append(
                f"{outreach_sent} outreach messages sent with a {response_rate}% estimated response rate."
            )
        if len(recs) < 3:
            recs.append("Run Deep Research on a target account to generate AI-ranked contacts and outreach drafts.")

        output = AnalyticsResponse(
            total_target_accounts=total_accounts,
            qualified_leads=qualified_leads,
            high_value_leads=high_value_leads,
            outreach_sent=outreach_sent,
            approvals_pending=approvals_pending,
            followups_due=0,
            response_rate=response_rate,
            meeting_conversion_rate=meeting_conversion_rate,
            meetings_booked=meetings_booked,
            pipeline_value_usd=pipeline_value_usd,
            total_contacts=total_contacts,
            industry_breakdown=top_industries,
            pipeline_stage_distribution=stage_dist,
            weekly_recommendations=recs,
        )
        return output.model_dump()
