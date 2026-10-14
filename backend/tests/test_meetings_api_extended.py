"""
Meetings API — Extended Integration Tests
Covers list_meetings, create_human_meeting (all fallback branches),
analyze_meeting_transcript (error & success), propose_meeting_slots.
"""
import pytest

from app.domain.models.models import Company, Lead, Meeting, Tenant


@pytest.mark.asyncio
async def test_list_meetings_with_data(client, db_session, auth_headers):
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    co = Company(tenant_id="tenant_nexora_default", name="Meeting Co", pipeline_stage="QUALIFIED")
    db_session.add_all([tenant, co])
    await db_session.commit()
    await db_session.refresh(co)

    lead = Lead(tenant_id="tenant_nexora_default", company_id=co.id, pipeline_stage="QUALIFIED", fit_score=85)
    db_session.add(lead)
    await db_session.commit()
    await db_session.refresh(lead)

    mtg = Meeting(
        tenant_id="tenant_nexora_default",
        lead_id=lead.id,
        title="Strategy Sync",
        status="SCHEDULED",
        calendar_provider="HUMAN_CALENDAR",
        meeting_link="https://meet.google.com/test-link",
        meeting_date="Tomorrow"
    )
    db_session.add(mtg)
    await db_session.commit()

    res = await client.get("/api/v1/meetings", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert data[0]["title"] == "Strategy Sync"
    assert data[0]["company_name"] == "Meeting Co"


@pytest.mark.asyncio
async def test_create_human_meeting_with_existing_lead(client, db_session, auth_headers):
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    co = Company(tenant_id="tenant_nexora_default", name="Lead Co", pipeline_stage="TARGET")
    db_session.add_all([tenant, co])
    await db_session.commit()
    await db_session.refresh(co)

    lead = Lead(tenant_id="tenant_nexora_default", company_id=co.id, pipeline_stage="TARGET", fit_score=70)
    db_session.add(lead)
    await db_session.commit()
    await db_session.refresh(lead)

    payload = {
        "title": "Discovery Session",
        "lead_id": lead.id,
        "meeting_link": "https://meet.google.com/disco",
        "meeting_date": "Friday 3pm"
    }
    res = await client.post("/api/v1/meetings", json=payload, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["title"] == "Discovery Session"
    assert data["status"] == "SCHEDULED"


@pytest.mark.asyncio
async def test_create_human_meeting_fallback_company(client, db_session, auth_headers):
    """When lead_id is not provided, fall back to existing company or create one."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    co = Company(tenant_id="tenant_nexora_default", name="Fallback Co", pipeline_stage="TARGET")
    db_session.add_all([tenant, co])
    await db_session.commit()

    res = await client.post("/api/v1/meetings", json={"title": "Auto Lead Meeting"}, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["title"] == "Auto Lead Meeting"


@pytest.mark.asyncio
async def test_create_human_meeting_no_company_or_lead(client, db_session, auth_headers):
    """When no company or lead exists in tenant, auto-create company & lead."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    res = await client.post("/api/v1/meetings", json={"title": "Scratch Account Call"}, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["title"] == "Scratch Account Call"


@pytest.mark.asyncio
async def test_analyze_transcript_empty_error(client, db_session, auth_headers):
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    res = await client.post("/api/v1/meetings/transcript", json={"transcript": ""}, headers=auth_headers)
    assert res.status_code == 400
    assert "Transcript text is required" in res.json()["detail"]


@pytest.mark.asyncio
async def test_analyze_transcript_success(client, db_session, auth_headers):
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    co = Company(tenant_id="tenant_nexora_default", name="Analysis Co", pipeline_stage="TARGET")
    db_session.add_all([tenant, co])
    await db_session.commit()
    await db_session.refresh(co)

    lead = Lead(tenant_id="tenant_nexora_default", company_id=co.id, pipeline_stage="TARGET", fit_score=80)
    db_session.add(lead)
    await db_session.commit()
    await db_session.refresh(lead)

    mtg = Meeting(tenant_id="tenant_nexora_default", lead_id=lead.id, title="Call", status="SCHEDULED")
    db_session.add(mtg)
    await db_session.commit()
    await db_session.refresh(mtg)

    payload = {
        "meeting_id": mtg.id,
        "transcript": "Speaker A: We want to expand our data center infrastructure in Q3. Budget is $5M."
    }
    res = await client.post("/api/v1/meetings/transcript", json=payload, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert "analysis" in data


@pytest.mark.asyncio
async def test_propose_meeting_slots(client, auth_headers):
    res = await client.post(
        "/api/v1/meetings/propose",
        json={"proposed_slots": ["Monday 10am EST", "Tuesday 2pm EST"]},
        headers=auth_headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert len(data["proposed_slots"]) == 2
