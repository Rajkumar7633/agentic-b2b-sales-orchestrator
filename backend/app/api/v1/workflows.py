from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import UserContext, get_current_user
from app.domain.models.models import CadenceWorkflow
from app.workflows.cadence import cadence_engine

router = APIRouter(prefix="/workflows", tags=["Durable Workflows & Cadences"])


class CreateCadenceRequest(BaseModel):
    company_id: str
    title: str | None = None
    contact_id: str | None = None
    custom_steps: list[dict[str, Any]] | None = None


@router.post("/cadence", status_code=201)
async def create_cadence(
    payload: CreateCadenceRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    """
    Creates a new multi-step, durable B2B sales pursuit cadence for a target company.
    """
    workflow = await cadence_engine.create_cadence(
        db=db,
        tenant_id=current_user.tenant_id,
        company_id=payload.company_id,
        title=payload.title,
        contact_id=payload.contact_id,
        custom_steps=payload.custom_steps,
    )
    return {
        "id": workflow.id,
        "title": workflow.title,
        "company_id": workflow.company_id,
        "status": workflow.status,
        "total_steps": workflow.total_steps,
        "current_step_index": workflow.current_step_index,
        "next_run_at": workflow.next_run_at.isoformat() if workflow.next_run_at else None,
        "steps_config": workflow.steps_config,
    }


@router.get("/cadence")
async def list_cadences(
    status: str | None = Query(None, description="Filter by status (ACTIVE, PAUSED, COMPLETED, WAITING_APPROVAL)"),
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    """
    List all sales pursuit cadences belonging to the active tenant.
    """
    items = await cadence_engine.list_cadences(db=db, tenant_id=current_user.tenant_id, status=status)
    return [
        {
            "id": w.id,
            "title": w.title,
            "company_id": w.company_id,
            "status": w.status,
            "current_step_index": w.current_step_index,
            "total_steps": w.total_steps,
            "next_run_at": w.next_run_at.isoformat() if w.next_run_at else None,
            "last_run_at": w.last_run_at.isoformat() if w.last_run_at else None,
            "created_at": w.created_at.isoformat(),
        }
        for w in items
    ]


@router.get("/cadence/{workflow_id}")
async def get_cadence(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    """
    Retrieve full details, step configuration, and execution history for a cadence workflow.
    """
    workflow = await db.get(CadenceWorkflow, workflow_id)
    if not workflow or workflow.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Cadence workflow not found")

    return {
        "id": workflow.id,
        "tenant_id": workflow.tenant_id,
        "company_id": workflow.company_id,
        "contact_id": workflow.contact_id,
        "title": workflow.title,
        "status": workflow.status,
        "current_step_index": workflow.current_step_index,
        "total_steps": workflow.total_steps,
        "steps_config": workflow.steps_config,
        "execution_history": workflow.execution_history,
        "next_run_at": workflow.next_run_at.isoformat() if workflow.next_run_at else None,
        "last_run_at": workflow.last_run_at.isoformat() if workflow.last_run_at else None,
        "created_at": workflow.created_at.isoformat(),
    }


@router.post("/cadence/{workflow_id}/step")
async def execute_cadence_step(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    """
    Manually advance or execute the next step of a cadence workflow.
    """
    workflow = await db.get(CadenceWorkflow, workflow_id)
    if not workflow or workflow.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Cadence workflow not found")

    try:
        result = await cadence_engine.execute_step(db=db, workflow_id=workflow_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/cadence/{workflow_id}/pause")
async def pause_cadence(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    """
    Pauses an active cadence workflow.
    """
    workflow = await db.get(CadenceWorkflow, workflow_id)
    if not workflow or workflow.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Cadence workflow not found")

    updated = await cadence_engine.pause_cadence(db=db, workflow_id=workflow_id)
    return {"id": updated.id, "status": updated.status}


@router.post("/cadence/{workflow_id}/resume")
async def resume_cadence(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserContext = Depends(get_current_user),
):
    """
    Resumes a paused cadence workflow.
    """
    workflow = await db.get(CadenceWorkflow, workflow_id)
    if not workflow or workflow.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Cadence workflow not found")

    updated = await cadence_engine.resume_cadence(db=db, workflow_id=workflow_id)
    return {"id": updated.id, "status": updated.status}
