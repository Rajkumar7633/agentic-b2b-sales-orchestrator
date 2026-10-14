"""
Analytics Agent — Unit Tests
Covers: KPI computation, industry normalisation, stage distribution,
        recommendations, empty-DB edge case, db-session injection.
"""
import pytest

from app.agents.analytics import AnalyticsAgent
from app.domain.models.models import Approval, Company, Contact, Meeting, OutreachMessage, Tenant


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
async def _seed_company(db, tenant_id: str, name: str,
                        industry: str = "Construction",
                        stage: str = "IDENTIFIED") -> Company:
    c = Company(tenant_id=tenant_id, name=name,
                industry=industry, pipeline_stage=stage)
    db.add(c)
    await db.flush()
    return c


# ─────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_analytics_returns_zero_counts_on_empty_db(db_session):
    """With no data in the DB the agent should return zeroes gracefully."""
    tenant = Tenant(id="t_empty", name="Empty Org")
    db_session.add(tenant)
    await db_session.commit()

    agent = AnalyticsAgent()
    result = await agent.execute({"tenant_id": "t_empty", "_db_session": db_session})

    assert result["total_target_accounts"] == 0
    assert result["total_contacts"] == 0
    assert result["outreach_sent"] == 0
    assert result["meetings_booked"] == 0
    assert result["approvals_pending"] == 0
    assert result["pipeline_value_usd"] == 0.0
    assert isinstance(result["weekly_recommendations"], list)
    assert len(result["weekly_recommendations"]) >= 1


@pytest.mark.asyncio
async def test_analytics_counts_real_companies(db_session):
    """Agent must count all companies belonging to the tenant."""
    tenant = Tenant(id="t_accts", name="Test Org")
    db_session.add(tenant)
    await db_session.commit()

    for i in range(5):
        await _seed_company(db_session, "t_accts", f"Company {i}", stage="IDENTIFIED")
    await _seed_company(db_session, "t_accts", "Qualified Co", stage="QUALIFIED")
    await _seed_company(db_session, "t_accts", "Researched Co", stage="RESEARCHED")
    await db_session.commit()

    agent = AnalyticsAgent()
    result = await agent.execute({"tenant_id": "t_accts", "_db_session": db_session})

    assert result["total_target_accounts"] == 7
    assert result["pipeline_stage_distribution"]["IDENTIFIED"] == 5
    assert result["pipeline_stage_distribution"]["QUALIFIED"] == 1
    assert result["pipeline_stage_distribution"]["RESEARCHED"] == 1
    assert result["qualified_leads"] == 2   # QUALIFIED + RESEARCHED
    assert result["high_value_leads"] == 1  # RESEARCHED only


@pytest.mark.asyncio
async def test_analytics_pipeline_value_scales_with_accounts(db_session):
    """Pipeline value = accounts × $75,000."""
    tenant = Tenant(id="t_val", name="Val Org")
    db_session.add(tenant)
    await db_session.commit()

    for i in range(4):
        await _seed_company(db_session, "t_val", f"Co {i}")
    await db_session.commit()

    agent = AnalyticsAgent()
    result = await agent.execute({"tenant_id": "t_val", "_db_session": db_session})

    assert result["pipeline_value_usd"] == 4 * 75_000.0


@pytest.mark.asyncio
async def test_analytics_industry_normalisation(db_session):
    """'Developer / Residential / Hospitality' should collapse to 'Developer'."""
    tenant = Tenant(id="t_ind", name="Ind Org")
    db_session.add(tenant)
    await db_session.commit()

    await _seed_company(db_session, "t_ind", "Alpha", industry="Developer / Residential")
    await _seed_company(db_session, "t_ind", "Beta",  industry="Developer / Luxury Residential")
    await _seed_company(db_session, "t_ind", "Gamma", industry="Healthcare")
    await db_session.commit()

    agent = AnalyticsAgent()
    result = await agent.execute({"tenant_id": "t_ind", "_db_session": db_session})

    breakdown = result["industry_breakdown"]
    assert breakdown.get("Developer") == 2
    assert breakdown.get("Healthcare") == 1
    # No compound key should appear
    assert all("/" not in k for k in breakdown)


@pytest.mark.asyncio
async def test_analytics_counts_contacts(db_session):
    """Contact count must match rows inserted for the tenant."""
    tenant = Tenant(id="t_contacts", name="Contact Org")
    db_session.add(tenant)
    await db_session.commit()

    co = await _seed_company(db_session, "t_contacts", "Main Co")
    for i in range(10):
        c = Contact(
            tenant_id="t_contacts",
            company_id=co.id,
            first_name=f"First{i}",
            last_name=f"Last{i}",
            title="VP"
        )
        db_session.add(c)
    await db_session.commit()

    agent = AnalyticsAgent()
    result = await agent.execute({"tenant_id": "t_contacts", "_db_session": db_session})

    assert result["total_contacts"] == 10


@pytest.mark.asyncio
async def test_analytics_counts_pending_approvals_only(db_session):
    """Only PENDING approvals should be counted — APPROVED ones are excluded."""
    tenant = Tenant(id="t_appr", name="Appr Org")
    db_session.add(tenant)
    await db_session.commit()

    for status in ("PENDING", "PENDING", "APPROVED", "REJECTED"):
        a = Approval(
            tenant_id="t_appr",
            entity_type="OUTREACH",
            entity_id=f"msg_{status}",
            action_type="SEND_LINKEDIN",
            draft_payload={"body_text": "hi"},
            risk_level="LOW",
            status=status,
            requested_by_agent="supervisor_agent"
        )
        db_session.add(a)
    await db_session.commit()

    agent = AnalyticsAgent()
    result = await agent.execute({"tenant_id": "t_appr", "_db_session": db_session})

    assert result["approvals_pending"] == 2


@pytest.mark.asyncio
async def test_analytics_response_rate_calculation(db_session):
    """response_rate = outreach / accounts × 100, capped to 1 decimal place."""
    tenant = Tenant(id="t_rr", name="RR Org")
    co = Company(tenant_id="t_rr", name="Co", pipeline_stage="IDENTIFIED")
    db_session.add_all([tenant, co])
    await db_session.flush()

    # 2 accounts (co already added) — add 1 more
    co2 = Company(tenant_id="t_rr", name="Co2", pipeline_stage="IDENTIFIED")
    db_session.add(co2)

    # 1 outreach message
    om = OutreachMessage(
        tenant_id="t_rr",
        lead_id="lead_rr_01",
        channel="LINKEDIN",
        body_text="Hello",
        approval_status="APPROVED"
    )
    db_session.add(om)
    await db_session.commit()

    agent = AnalyticsAgent()
    result = await agent.execute({"tenant_id": "t_rr", "_db_session": db_session})

    # 1 outreach / 2 accounts × 100 = 50.0
    assert result["outreach_sent"] == 1
    assert result["total_target_accounts"] == 2
    assert result["response_rate"] == 50.0


@pytest.mark.asyncio
async def test_analytics_weekly_recommendations_are_dynamic(db_session):
    """Recommendations must reference actual data counts, not hardcoded strings."""
    tenant = Tenant(id="t_recs", name="Recs Org")
    db_session.add(tenant)
    await db_session.commit()

    for i in range(3):
        await _seed_company(db_session, "t_recs", f"Co {i}")

    appr = Approval(
        tenant_id="t_recs",
        entity_type="OUTREACH",
        entity_id="msg_p",
        action_type="SEND_LINKEDIN",
        draft_payload={"body_text": "hello"},
        risk_level="LOW",
        status="PENDING",
        requested_by_agent="supervisor_agent"
    )
    db_session.add(appr)
    await db_session.commit()

    agent = AnalyticsAgent()
    result = await agent.execute({"tenant_id": "t_recs", "_db_session": db_session})

    recs = result["weekly_recommendations"]
    full_text = " ".join(recs)
    # Should mention real numbers
    assert "3" in full_text          # 3 accounts
    assert "1" in full_text          # 1 pending approval
    assert len(recs) >= 2


@pytest.mark.asyncio
async def test_analytics_tenant_isolation(db_session):
    """Analytics must NOT bleed data between tenants."""
    t1 = Tenant(id="t_iso_1", name="Org 1")
    t2 = Tenant(id="t_iso_2", name="Org 2")
    db_session.add_all([t1, t2])
    await db_session.commit()

    # 5 companies for tenant 1, 2 for tenant 2
    for i in range(5):
        await _seed_company(db_session, "t_iso_1", f"T1 Co {i}")
    for i in range(2):
        await _seed_company(db_session, "t_iso_2", f"T2 Co {i}")
    await db_session.commit()

    agent = AnalyticsAgent()
    r1 = await agent.execute({"tenant_id": "t_iso_1", "_db_session": db_session})
    r2 = await agent.execute({"tenant_id": "t_iso_2", "_db_session": db_session})

    assert r1["total_target_accounts"] == 5
    assert r2["total_target_accounts"] == 2


@pytest.mark.asyncio
async def test_analytics_agent_returns_complete_kpis(db_session):
    """Smoke test: agent must return all required keys."""
    tenant = Tenant(id="tenant_nexora_default", name="Default Org")
    db_session.add(tenant)
    await db_session.commit()

    from app.agents.analytics.analytics import AnalyticsAgent as _AnalyticsAgent
    agent = _AnalyticsAgent()
    result = await agent.execute({"tenant_id": "tenant_nexora_default", "_db_session": db_session})

    required_keys = [
        "total_target_accounts", "qualified_leads", "high_value_leads",
        "outreach_sent", "approvals_pending", "followups_due",
        "response_rate", "meeting_conversion_rate", "meetings_booked",
        "pipeline_value_usd", "total_contacts",
        "industry_breakdown", "pipeline_stage_distribution",
        "weekly_recommendations"
    ]
    for key in required_keys:
        assert key in result, f"Missing key: {key}"

    assert result["total_target_accounts"] >= 0
    assert result["response_rate"] >= 0.0
    assert isinstance(result["industry_breakdown"], dict)
    assert isinstance(result["pipeline_stage_distribution"], dict)
    assert isinstance(result["weekly_recommendations"], list)
    assert len(result["weekly_recommendations"]) >= 1
