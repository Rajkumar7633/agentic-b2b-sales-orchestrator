import pytest

from app.core.audit import record_audit_log
from app.domain.models.models import Tenant


@pytest.mark.asyncio
async def test_audit_logging_sanitizes_secrets(db_session):
    tenant = Tenant(id="tenant_audit_test", name="Audit Test Org")
    db_session.add(tenant)
    await db_session.commit()

    entry = await record_audit_log(
        db=db_session,
        tenant_id="tenant_audit_test",
        action="TEST_ACTION",
        resource_type="COMPANY",
        resource_id="comp_123",
        user_id="usr_admin_001",
        details={"api_key": "secret_key_123", "company_name": "Acme Corp"}
    )
    await db_session.commit()

    assert entry.id is not None
    assert entry.details["api_key"] == "[REDACTED]"
    assert entry.details["company_name"] == "Acme Corp"
