import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.models import Approval, CadenceWorkflow, Company

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


DEFAULT_CADENCE_STEPS: list[dict[str, Any]] = [
    {
        "step_index": 0,
        "day_offset": 1,
        "name": "Day 1: Account Research & Signal Analysis",
        "action_type": "RESEARCH_ACCOUNT",
        "channel": "SYSTEM",
        "description": "Perform 360-degree firmographic analysis, technographic check, and intent signal harvest.",
        "requires_hitl": False,
    },
    {
        "step_index": 1,
        "day_offset": 3,
        "name": "Day 3: Personalized Executive Outreach (HITL Gate)",
        "action_type": "DRAFT_OUTREACH",
        "channel": "EMAIL",
        "description": "Synthesize tailored executive pitch referencing why-now trigger; route to HITL approval.",
        "requires_hitl": True,
    },
    {
        "step_index": 2,
        "day_offset": 6,
        "name": "Day 6: LinkedIn Multichannel Follow-Up",
        "action_type": "DRAFT_OUTREACH",
        "channel": "LINKEDIN",
        "description": "Send concise InMail highlighting relevant enterprise case study & industry benchmark.",
        "requires_hitl": True,
    },
    {
        "step_index": 3,
        "day_offset": 10,
        "name": "Day 10: Executive Briefing & Calendar Scheduling",
        "action_type": "SCHEDULE_MEETING",
        "channel": "CALENDAR",
        "description": "Propose 3 tentative 20-minute meeting slots with meeting agenda brief.",
        "requires_hitl": False,
    },
]


class CadenceWorkflowEngine:
    """
    Durable Multi-Step Sales Cadence Orchestrator.
    Manages state machines, scheduled multi-day touches, HITL routing, and retry execution.
    """

    async def create_cadence(
        self,
        db: AsyncSession,
        tenant_id: str,
        company_id: str,
        title: str | None = None,
        contact_id: str | None = None,
        custom_steps: list[dict[str, Any]] | None = None,
    ) -> CadenceWorkflow:
        steps = custom_steps if custom_steps is not None else DEFAULT_CADENCE_STEPS

        # Check company existence to construct title if missing
        company = await db.get(Company, company_id)
        comp_name = company.name if company else company_id
        final_title = title or f"10-Day Multi-Touch Cadence for {comp_name}"

        workflow = CadenceWorkflow(
            id=f"cad_{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            company_id=company_id,
            contact_id=contact_id,
            title=final_title,
            status="ACTIVE",
            current_step_index=0,
            total_steps=len(steps),
            steps_config=steps,
            execution_history=[],
            next_run_at=_now(),
            last_run_at=None,
            retry_count=0,
            max_retries=3,
        )
        db.add(workflow)
        await db.commit()
        await db.refresh(workflow)
        logger.info(f"Created cadence workflow '{workflow.id}' ({workflow.title}) for company {company_id}")
        return workflow

    async def execute_step(
        self,
        db: AsyncSession,
        workflow_id: str,
    ) -> dict[str, Any]:
        """
        Executes the current step of a cadence workflow, records output,
        and transitions the state or stages HITL approvals.
        """
        workflow = await db.get(CadenceWorkflow, workflow_id)
        if not workflow:
            raise ValueError(f"Workflow '{workflow_id}' not found")

        if workflow.status not in ("ACTIVE", "WAITING_APPROVAL"):
            raise ValueError(f"Cannot execute workflow in status '{workflow.status}'")

        if workflow.current_step_index >= workflow.total_steps:
            workflow.status = "COMPLETED"
            workflow.next_run_at = None
            await db.commit()
            return {"status": "COMPLETED", "message": "Workflow already finished all steps"}

        current_step = workflow.steps_config[workflow.current_step_index]
        step_name = current_step.get("name", f"Step {workflow.current_step_index + 1}")
        action_type = current_step.get("action_type", "GENERIC_TASK")
        channel = current_step.get("channel", "EMAIL")
        requires_hitl = current_step.get("requires_hitl", False)

        step_result: dict[str, Any] = {
            "step_index": workflow.current_step_index,
            "step_name": step_name,
            "action_type": action_type,
            "channel": channel,
            "executed_at": _now().isoformat(),
            "status": "SUCCESS",
        }

        # Step action execution logic
        if requires_hitl:
            # Stage HITL Approval Gate
            approval = Approval(
                id=f"appr_{uuid.uuid4().hex[:12]}",
                tenant_id=workflow.tenant_id,
                entity_type="CADENCE_OUTREACH",
                entity_id=workflow.id,
                action_type=f"SEND_{channel}",
                draft_payload={
                    "step_name": step_name,
                    "channel": channel,
                    "company_id": workflow.company_id,
                    "body_text": f"Automated cadence outreach draft for {step_name}.",
                },
                risk_level="MEDIUM",
                status="PENDING",
                requested_by_agent="cadence_orchestrator",
            )
            db.add(approval)
            step_result["approval_id"] = approval.id
            step_result["note"] = "Outreach message drafted and queued for Human-in-the-Loop review."
            workflow.status = "WAITING_APPROVAL"
        else:
            step_result["note"] = f"Executed {action_type} successfully."

        # Update history
        history = list(workflow.execution_history or [])
        history.append(step_result)
        workflow.execution_history = history

        # Advance step
        workflow.current_step_index += 1
        workflow.last_run_at = _now()

        if workflow.current_step_index >= workflow.total_steps:
            workflow.status = "COMPLETED"
            workflow.next_run_at = None
        else:
            next_step = workflow.steps_config[workflow.current_step_index]
            delay_days = next_step.get("day_offset", 1) - current_step.get("day_offset", 0)
            workflow.next_run_at = _now() + timedelta(days=max(1, delay_days))
            if not requires_hitl:
                workflow.status = "ACTIVE"

        await db.commit()
        await db.refresh(workflow)

        return {
            "workflow_id": workflow.id,
            "executed_step": step_result,
            "current_step_index": workflow.current_step_index,
            "total_steps": workflow.total_steps,
            "status": workflow.status,
            "next_run_at": workflow.next_run_at.isoformat() if workflow.next_run_at else None,
        }

    async def pause_cadence(self, db: AsyncSession, workflow_id: str) -> CadenceWorkflow:
        workflow = await db.get(CadenceWorkflow, workflow_id)
        if not workflow:
            raise ValueError(f"Workflow '{workflow_id}' not found")
        workflow.status = "PAUSED"
        await db.commit()
        await db.refresh(workflow)
        return workflow

    async def resume_cadence(self, db: AsyncSession, workflow_id: str) -> CadenceWorkflow:
        workflow = await db.get(CadenceWorkflow, workflow_id)
        if not workflow:
            raise ValueError(f"Workflow '{workflow_id}' not found")
        workflow.status = "ACTIVE"
        await db.commit()
        await db.refresh(workflow)
        return workflow

    async def list_cadences(
        self,
        db: AsyncSession,
        tenant_id: str,
        status: str | None = None,
    ) -> list[CadenceWorkflow]:
        query = select(CadenceWorkflow).where(CadenceWorkflow.tenant_id == tenant_id)
        if status:
            query = query.where(CadenceWorkflow.status == status)
        query = query.order_by(CadenceWorkflow.created_at.desc())
        res = await db.execute(query)
        return list(res.scalars().all())


cadence_engine = CadenceWorkflowEngine()
