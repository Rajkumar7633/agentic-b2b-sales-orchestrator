import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.models import AuditLog

logger = logging.getLogger(__name__)


async def record_audit_log(
    db: AsyncSession,
    tenant_id: str,
    action: str,
    resource_type: str,
    resource_id: str,
    user_id: str | None = None,
    details: dict[str, Any] | None = None,
    ip_address: str | None = None
) -> AuditLog:
    """
    Centralized helper for recording audit trail events.
    Enforces tenant isolation and sanitizes sensitive data.
    """
    # Sanitize details (never log password, token, or secret)
    sanitized_details = None
    if details:
        sanitized_details = {
            k: ("[REDACTED]" if k.lower() in ["password", "token", "jwt", "secret", "api_key", "groq_api_key"] else v)
            for k, v in details.items()
        }

    audit_entry = AuditLog(
        tenant_id=tenant_id,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=sanitized_details,
        ip_address=ip_address
    )
    db.add(audit_entry)
    logger.info(f"[AUDIT LOG] Tenant: {tenant_id} | Action: {action} | Resource: {resource_type}/{resource_id} | User: {user_id or 'system'}")
    return audit_entry
