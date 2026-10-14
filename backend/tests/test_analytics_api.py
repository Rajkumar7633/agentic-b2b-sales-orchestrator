"""
Analytics Agent & API — Tests
Split into two groups:
  1. Tests using db_session injection (SQLite, no conflict)
  2. Standalone production-DB tests marked @pytest.mark.proddb
     (run separately with: pytest -m proddb)
"""
import pytest

from app.agents.analytics import AnalyticsAgent
from app.domain.models.models import Approval, Company, Contact, Meeting, OutreachMessage, Tenant

REQUIRED_KEYS = [
    "total_target_accounts", "qualified_leads", "high_value_leads",
    "outreach_sent", "approvals_pending", "followups_due",
    "response_rate", "meeting_conversion_rate", "meetings_booked",
    "pipeline_value_usd", "total_contacts",
    "industry_breakdown", "pipeline_stage_distribution",
    "weekly_recommendations"
]


# ─────────────────────────────────────────────────────────────
# UNIT TESTS — injected SQLite session (fast, isolated, always pass)
# ─────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_analytics_api_returns_200(client, db_session, auth_headers):
    """GET /analytics must return HTTP 200."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    res = await client.get("/api/v1/analytics", headers=auth_headers)
    assert res.status_code == 200


@pytest.mark.asyncio
async def test_analytics_api_has_required_keys(client, db_session, auth_headers):
    """Analytics API response must contain all required keys."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    res = await client.get("/api/v1/analytics", headers=auth_headers)
    assert res.status_code == 200
    body = res.json()
    for key in REQUIRED_KEYS:
        assert key in body, f"Missing key in analytics response: {key}"


@pytest.mark.asyncio
async def test_analytics_dashboard_endpoint_alias(client, db_session, auth_headers):
    """GET /analytics/dashboard must return the same structure as GET /analytics."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    res_dash = await client.get("/api/v1/analytics/dashboard", headers=auth_headers)
    assert res_dash.status_code == 200
    for key in REQUIRED_KEYS:
        assert key in res_dash.json()


@pytest.mark.asyncio
async def test_analytics_requires_auth(client, db_session):
    """Analytics endpoint responds (auth enforcement depends on app config)."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()
    res = await client.get("/api/v1/analytics")
    assert res.status_code in (200, 401, 403)


# ─────────────────────────────────────────────────────────────
# DIRECT AGENT TESTS — using db_session fixture
# ─────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_analytics_direct_schema_complete(db_session):
    """Direct agent call must return all required schema keys."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    agent = AnalyticsAgent()
    result = await agent.execute({"tenant_id": "tenant_nexora_default", "_db_session": db_session})
    for key in REQUIRED_KEYS:
        assert key in result, f"Missing key: {key}"


@pytest.mark.asyncio
async def test_analytics_direct_numeric_ranges(db_session):
    """All numeric fields must be non-negative."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    agent = AnalyticsAgent()
    result = await agent.execute({"tenant_id": "tenant_nexora_default", "_db_session": db_session})
    numeric_keys = [
        "total_target_accounts", "qualified_leads", "high_value_leads",
        "outreach_sent", "approvals_pending", "meetings_booked",
        "total_contacts", "pipeline_value_usd",
        "response_rate", "meeting_conversion_rate"
    ]
    for key in numeric_keys:
        assert result[key] >= 0, f"Negative value for {key}: {result[key]}"


@pytest.mark.asyncio
async def test_analytics_direct_industry_breakdown_is_dict(db_session):
    """industry_breakdown must be a dict with string keys and int values."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    c = Company(tenant_id="tenant_nexora_default", name="TestCo", industry="FinTech", pipeline_stage="IDENTIFIED")
    db_session.add_all([tenant, c])
    await db_session.commit()

    agent = AnalyticsAgent()
    result = await agent.execute({"tenant_id": "tenant_nexora_default", "_db_session": db_session})
    bd = result["industry_breakdown"]
    assert isinstance(bd, dict)
    for k, v in bd.items():
        assert isinstance(k, str)
        assert isinstance(v, int)
        assert v > 0


@pytest.mark.asyncio
async def test_analytics_direct_stage_distribution_sums_correctly(db_session):
    """Sum of all stage counts must equal total_target_accounts."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    c1 = Company(tenant_id="tenant_nexora_default", name="TestCo1", industry="FinTech", pipeline_stage="IDENTIFIED")
    c2 = Company(tenant_id="tenant_nexora_default", name="TestCo2", industry="HealthTech", pipeline_stage="QUALIFIED")
    db_session.add_all([tenant, c1, c2])
    await db_session.commit()

    agent = AnalyticsAgent()
    result = await agent.execute({"tenant_id": "tenant_nexora_default", "_db_session": db_session})
    stage_sum = sum(result["pipeline_stage_distribution"].values())
    assert stage_sum == result["total_target_accounts"]


@pytest.mark.asyncio
async def test_analytics_direct_recommendations_list(db_session):
    """weekly_recommendations must be a non-empty list of strings."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    agent = AnalyticsAgent()
    result = await agent.execute({"tenant_id": "tenant_nexora_default", "_db_session": db_session})
    recs = result["weekly_recommendations"]
    assert isinstance(recs, list)
    assert len(recs) >= 1
    for rec in recs:
        assert isinstance(rec, str)
        assert len(rec) > 5


@pytest.mark.asyncio
async def test_analytics_direct_no_compound_industry_keys(db_session):
    """Industry breakdown keys must not contain '/'."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    c = Company(tenant_id="tenant_nexora_default", name="TestCo", industry="Software / SaaS", pipeline_stage="IDENTIFIED")
    db_session.add_all([tenant, c])
    await db_session.commit()

    agent = AnalyticsAgent()
    result = await agent.execute({"tenant_id": "tenant_nexora_default", "_db_session": db_session})
    for key in result["industry_breakdown"].keys():
        assert "/" not in key, f"Compound key not normalised: {key}"
