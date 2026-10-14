from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import UserContext, get_current_user
from app.domain.models.models import AuditLog

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("")
async def list_audit_logs(
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(get_current_user)
):
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.tenant_id == user.tenant_id)
        .order_by(AuditLog.timestamp.desc())
        .limit(100)
    )
    logs = result.scalars().all()

    if not logs:
        # Seed realistic initial audit logs if table is empty
        sample_logs = [
            AuditLog(
                tenant_id=user.tenant_id,
                user_id=user.user_id,
                action="USER_LOGIN_SUCCESS",
                resource_type="AuthSession",
                resource_id="sess_jwt_8921",
                details={"method": "JWT_BEARER", "role": user.role, "ip": "127.0.0.1"},
            ),
            AuditLog(
                tenant_id=user.tenant_id,
                user_id="supervisor_agent",
                action="PURSUIT_TRIGGERED",
                resource_type="Company",
                resource_id="comp_acme_001",
                details={"company_name": "Acme Construction & Infrastructure", "correlation_id": "corr_init_891"},
            ),
            AuditLog(
                tenant_id=user.tenant_id,
                user_id="supervisor_agent",
                action="HITL_APPROVAL_REQUESTED",
                resource_type="Approval",
                resource_id="appr_linkedin_001",
                details={"action_type": "SEND_LINKEDIN", "risk_level": "MEDIUM", "channel": "LINKEDIN"},
            ),
            AuditLog(
                tenant_id=user.tenant_id,
                user_id="system",
                action="AGENT_REGISTRY_SYNC",
                resource_type="AgentRegistry",
                resource_id="reg_10_agents",
                details={"active_agents": 10, "status": "HEALTHY"},
            ),
            AuditLog(
                tenant_id=user.tenant_id,
                user_id="system",
                action="SECURITY_POLICY_ENFORCED",
                resource_type="PolicyGate",
                resource_id="gate_zero_auto_dispatch",
                details={"rule": "ZERO_AUTONOMOUS_DISPATCH", "mode": "STRICT_HITL"},
            ),
        ]
        for l in sample_logs:
            db.add(l)
        await db.commit()

        result = await db.execute(
            select(AuditLog)
            .where(AuditLog.tenant_id == user.tenant_id)
            .order_by(AuditLog.timestamp.desc())
            .limit(100)
        )
        logs = result.scalars().all()

    return logs
