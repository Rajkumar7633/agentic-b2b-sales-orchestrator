"""
Audit API & Database Seeder Unit Tests
Covers audit log retrieval/sample auto-seeding, log_audit_event core helper,
and seed_database function (idempotency check).
"""
import pytest

from app.core.audit import record_audit_log
from app.domain.models.models import AuditLog, Tenant
from app.seeds.seed import seed_database


@pytest.mark.asyncio
async def test_audit_logs_api_sample_seeding(client, db_session, auth_headers):
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    res = await client.get("/api/v1/audit-logs", headers=auth_headers)
    assert res.status_code == 200
    logs = res.json()
    assert len(logs) >= 5
    actions = [entry["action"] for entry in logs]
    assert "USER_LOGIN_SUCCESS" in actions
    assert "PURSUIT_TRIGGERED" in actions


@pytest.mark.asyncio
async def test_audit_logs_api_existing_logs(client, db_session, auth_headers):
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    log_item = AuditLog(
        tenant_id="tenant_nexora_default",
        user_id="usr_admin_001",
        action="CUSTOM_ACTION",
        resource_type="TestResource",
        resource_id="res_001"
    )
    db_session.add_all([tenant, log_item])
    await db_session.commit()

    res = await client.get("/api/v1/audit-logs", headers=auth_headers)
    assert res.status_code == 200
    logs = res.json()
    assert len(logs) == 1
    assert logs[0]["action"] == "CUSTOM_ACTION"


@pytest.mark.asyncio
async def test_record_audit_log_helper(db_session):
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    entry = await record_audit_log(
        db=db_session,
        tenant_id="tenant_nexora_default",
        action="CORE_AUDIT_LOGGED",
        user_id="usr_core",
        resource_type="System",
        resource_id="sys_1",
        details={"note": "audit helper test", "password": "my_secret_password"}
    )
    assert entry.action == "CORE_AUDIT_LOGGED"
    assert entry.details["note"] == "audit helper test"
    assert entry.details["password"] == "[REDACTED]"


@pytest.mark.asyncio
async def test_seed_database_execution(db_session):
    """Verify seed_database runs without error and is idempotent."""
    await seed_database(session=db_session)
    # Second run should log skipping message and exit cleanly
    await seed_database(session=db_session)
