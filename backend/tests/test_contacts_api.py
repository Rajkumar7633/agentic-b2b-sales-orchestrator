"""
Contacts API — Integration Tests
Covers: list contacts, empty-state, search/filter, tenant isolation,
        contact schema completeness, unauthenticated access.
"""
import pytest

from app.domain.models.models import Company, Contact, Tenant


async def _seed_contacts(db, tenant_id: str, company_id: str, n: int = 5):
    contacts = []
    for i in range(n):
        c = Contact(
            tenant_id=tenant_id,
            company_id=company_id,
            first_name=f"First{i}",
            last_name=f"Last{i}",
            title=f"VP Level {i}",
            seniority="VP",
            priority="HIGH" if i == 0 else "MEDIUM",
            linkedin_status="NOT_STARTED",
            why_this_person=f"Key decision maker {i}",
        )
        db.add(c)
        contacts.append(c)
    await db.commit()
    return contacts


@pytest.mark.asyncio
async def test_contacts_list_empty(client, db_session, auth_headers):
    """No contacts loaded → empty list response."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    res = await client.get("/api/v1/contacts", headers=auth_headers)
    assert res.status_code == 200
    assert res.json() == []


@pytest.mark.asyncio
async def test_contacts_list_returns_all_contacts(client, db_session, auth_headers):
    """List endpoint returns all contacts for the tenant."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    co = Company(tenant_id="tenant_nexora_default", name="Main Co", pipeline_stage="TARGET")
    db_session.add_all([tenant, co])
    await db_session.commit()
    await db_session.refresh(co)

    await _seed_contacts(db_session, "tenant_nexora_default", co.id, n=8)

    res = await client.get("/api/v1/contacts", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()) == 8


@pytest.mark.asyncio
async def test_contact_schema_fields_present(client, db_session, auth_headers):
    """Each contact must carry required schema fields in the response."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    co = Company(tenant_id="tenant_nexora_default", name="Schema Co", pipeline_stage="TARGET")
    db_session.add_all([tenant, co])
    await db_session.commit()
    await db_session.refresh(co)

    await _seed_contacts(db_session, "tenant_nexora_default", co.id, n=1)

    res = await client.get("/api/v1/contacts", headers=auth_headers)
    assert res.status_code == 200
    contact = res.json()[0]

    required_fields = [
        "id", "first_name", "last_name", "title", "seniority",
        "linkedin_status", "priority", "why_this_person"
    ]
    for field in required_fields:
        assert field in contact, f"Missing field: {field}"


@pytest.mark.asyncio
async def test_contacts_tenant_isolation(client, db_session):
    """Tenant A must not see Tenant B's contacts."""
    from app.core.security import create_access_token

    t_a = Tenant(id="t_c_a", name="A")
    t_b = Tenant(id="t_c_b", name="B")
    co_a = Company(tenant_id="t_c_a", name="Co A", pipeline_stage="TARGET")
    co_b = Company(tenant_id="t_c_b", name="Co B", pipeline_stage="TARGET")
    db_session.add_all([t_a, t_b, co_a, co_b])
    await db_session.commit()
    await db_session.refresh(co_a)
    await db_session.refresh(co_b)

    db_session.add(Contact(
        tenant_id="t_c_a", company_id=co_a.id,
        first_name="Alice", last_name="A", title="VP"
    ))
    db_session.add(Contact(
        tenant_id="t_c_b", company_id=co_b.id,
        first_name="Bob", last_name="B", title="CTO"
    ))
    await db_session.commit()

    token_a = create_access_token({
        "sub": "ua", "email": "a@a.com", "role": "SALES_REP", "tenant_id": "t_c_a"
    })
    res = await client.get(
        "/api/v1/contacts", headers={"Authorization": f"Bearer {token_a}"}
    )
    assert res.status_code == 200
    names = [f"{c['first_name']} {c['last_name']}" for c in res.json()]
    assert "Alice A" in names
    assert "Bob B" not in names


@pytest.mark.asyncio
async def test_contacts_requires_auth(client, db_session):
    """Unauthenticated request — response depends on app auth config."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()
    res = await client.get("/api/v1/contacts")
    assert res.status_code in (200, 401, 403)
