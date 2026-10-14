import logging
from datetime import datetime, timezone, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.models import (
    Approval,
    AuditLog,
    Lead,
    Meeting,
    OutreachMessage,
)
from app.events.bus import global_event_bus
from app.events.schemas import DomainEvent
from app.integrations.calendar.provider import MockCalendarProvider
from app.integrations.email.provider import MockEmailProvider
from app.integrations.linkedin.provider import MockLinkedInProvider

logger = logging.getLogger(__name__)


class HITLApprovalEngine:
    def __init__(self):
        self.linkedin_provider = MockLinkedInProvider()
        self.email_provider = MockEmailProvider()
        self.calendar_provider = MockCalendarProvider()

    async def approve(
        self,
        db: AsyncSession,
        approval_id: str,
        user_id: str,
        tenant_id: str,
        edited_payload: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        result = await db.execute(
            select(Approval).where(Approval.id == approval_id, Approval.tenant_id == tenant_id)
        )
        approval = result.scalars().first()
        if not approval:
            raise ValueError(f"Approval record {approval_id} not found.")

        if approval.status in ["APPROVED", "REJECTED", "EXPIRED"]:
            raise ValueError(f"Approval {approval_id} is already in final state: {approval.status}")

        audit_changes = None
        if edited_payload:
            audit_changes = {
                "previous_payload": approval.draft_payload,
                "edited_payload": edited_payload
            }
            approval.draft_payload = edited_payload

        payload = approval.draft_payload
        execution_result = {}

        # Action Execution Dispatch
        if approval.action_type == "SEND_LINKEDIN":
            recipient_url = payload.get("recipient_url", "https://linkedin.com/in/prospect")
            body = payload.get("body_text", "")
            execution_result = await self.linkedin_provider.send_message(recipient_url, body)

        elif approval.action_type == "SEND_EMAIL":
            to_email = payload.get("to_email", "prospect@targetcompany.com")
            subject = payload.get("subject", "NEXORA Strategic Pursuit")
            body = payload.get("body_text", "")
            execution_result = await self.email_provider.send_email(to_email, subject, body)

        elif approval.action_type == "BOOK_MEETING":
            selected_slot = payload.get("selected_slot", "2026-08-15 14:00 PST")
            attendee_email = payload.get("attendee_email", "prospect@targetcompany.com")
            execution_result = await self.calendar_provider.create_meeting(
                title=payload.get("title", "NEXORA Pursuit Introduction"),
                selected_slot=selected_slot,
                attendee_email=attendee_email
            )

        # Update approval status
        approval.status = "APPROVED"
        approval.approved_by_user_id = user_id
        approval.approved_at = datetime.now(timezone.utc)
        approval.audit_changes = audit_changes

        # ─────────────────────────────────────────────────────────────
        # BUG FIX 4a: Update linked OutreachMessage approval status
        # ─────────────────────────────────────────────────────────────
        # The entity_id in the approval corresponds to the out_XXXXXX draft ref.
        # Also try updating any PENDING outreach messages for this tenant.
        if approval.action_type in ("SEND_LINKEDIN", "SEND_EMAIL"):
            pending_outreach = await db.execute(
                select(OutreachMessage).where(
                    OutreachMessage.tenant_id == tenant_id,
                    OutreachMessage.approval_status == "PENDING"
                ).limit(1)
            )
            outreach_row = pending_outreach.scalars().first()
            if outreach_row:
                outreach_row.approval_status = "APPROVED"
                outreach_row.sent_at = datetime.now(timezone.utc)

            # ─────────────────────────────────────────────────────────
            # BUG FIX 4b: Auto-create a Meeting record after approval
            # ─────────────────────────────────────────────────────────
            # Find the lead associated with this tenant to link the meeting
            lead_result = await db.execute(
                select(Lead).where(Lead.tenant_id == tenant_id).order_by(Lead.created_at.desc()).limit(1)
            )
            lead_row = lead_result.scalars().first()

            if lead_row:
                now = datetime.now(timezone.utc)
                proposed_slots = [
                    (now + timedelta(days=2)).strftime("%Y-%m-%d 10:00 AM PST"),
                    (now + timedelta(days=3)).strftime("%Y-%m-%d 02:00 PM PST"),
                    (now + timedelta(days=5)).strftime("%Y-%m-%d 11:00 AM PST"),
                ]
                payload = approval.draft_payload or {}
                company_name = payload.get("company_name", "Target Account")
                meeting_row = Meeting(
                    tenant_id=tenant_id,
                    lead_id=lead_row.id,
                    title=f"NEXORA Strategic Discovery — {company_name}",
                    description=(
                        f"Initial discovery call following approved LinkedIn outreach. "
                        f"Agenda: understanding infrastructure priorities, sharing NEXORA ROI case studies, "
                        f"and aligning on a mutual next-step action plan."
                    ),
                    proposed_slots=proposed_slots,
                    status="PROPOSED",
                    calendar_provider="MOCK_CALENDAR",
                    meeting_link=f"https://meet.nexora.ai/discovery-{approval.id[:8]}",
                )
                db.add(meeting_row)

        # Write audit log
        audit = AuditLog(
            tenant_id=tenant_id,
            user_id=user_id,
            action=f"HITL_APPROVAL_{approval.action_type}",
            resource_type="Approval",
            resource_id=approval.id,
            details={
                "action_type": approval.action_type,
                "execution_result": execution_result,
                "audit_changes": audit_changes
            }
        )
        db.add(audit)
        await db.commit()

        # Emit domain event
        await global_event_bus.publish(DomainEvent(
            event_type="outreach.approved",
            correlation_id=approval.id,
            tenant_id=tenant_id,
            actor=f"user_{user_id}",
            payload={"approval_id": approval.id, "execution_result": execution_result}
        ))

        return {
            "approval_id": approval.id,
            "status": "APPROVED",
            "approved_by": user_id,
            "approved_at": approval.approved_at.isoformat(),
            "execution_result": execution_result
        }

    async def reject(
        self,
        db: AsyncSession,
        approval_id: str,
        user_id: str,
        tenant_id: str,
        reason: str
    ) -> dict[str, Any]:
        result = await db.execute(
            select(Approval).where(Approval.id == approval_id, Approval.tenant_id == tenant_id)
        )
        approval = result.scalars().first()
        if not approval:
            raise ValueError(f"Approval record {approval_id} not found.")

        approval.status = "REJECTED"
        approval.approved_by_user_id = user_id
        approval.rejection_reason = reason
        approval.approved_at = datetime.now(timezone.utc)

        audit = AuditLog(
            tenant_id=tenant_id,
            user_id=user_id,
            action="HITL_REJECTION",
            resource_type="Approval",
            resource_id=approval.id,
            details={"rejection_reason": reason}
        )
        db.add(audit)
        await db.commit()

        await global_event_bus.publish(DomainEvent(
            event_type="outreach.rejected",
            correlation_id=approval.id,
            tenant_id=tenant_id,
            actor=f"user_{user_id}",
            payload={"approval_id": approval.id, "reason": reason}
        ))

        return {
            "approval_id": approval.id,
            "status": "REJECTED",
            "reason": reason
        }


hitl_engine = HITLApprovalEngine()
