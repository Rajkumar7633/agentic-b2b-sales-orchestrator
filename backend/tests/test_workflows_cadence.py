import pytest

from app.domain.models.models import Company, Tenant
from app.workflows.cadence import cadence_engine


@pytest.mark.asyncio
async def test_cadence_engine_lifecycle(db_session):
    """Test full programmatic lifecycle of CadenceWorkflowEngine: create, step, pause, resume."""
    tenant = Tenant(id="tenant_nexora_default", name="Default Org")
    company = Company(
        id="comp_cad_01",
        tenant_id="tenant_nexora_default",
        name="Titan Aerospace",
        industry="Aerospace",
        pipeline_stage="IDENTIFIED",
    )
    db_session.add_all([tenant, company])
    await db_session.commit()

    # 1. Create Cadence
    workflow = await cadence_engine.create_cadence(
        db=db_session,
        tenant_id="tenant_nexora_default",
        company_id="comp_cad_01",
    )
    assert workflow.id.startswith("cad_")
    assert workflow.status == "ACTIVE"
    assert workflow.current_step_index == 0
    assert workflow.total_steps == 4
    assert len(workflow.steps_config) == 4

    # 2. Execute Step 0 (Day 1 Research)
    res0 = await cadence_engine.execute_step(db=db_session, workflow_id=workflow.id)
    assert res0["current_step_index"] == 1
    assert res0["executed_step"]["action_type"] == "RESEARCH_ACCOUNT"
    assert res0["status"] == "ACTIVE"

    # 3. Execute Step 1 (Day 3 Outreach with HITL requirement)
    res1 = await cadence_engine.execute_step(db=db_session, workflow_id=workflow.id)
    assert res1["current_step_index"] == 2
    assert res1["status"] == "WAITING_APPROVAL"
    assert "approval_id" in res1["executed_step"]

    # 4. Pause Cadence
    paused = await cadence_engine.pause_cadence(db=db_session, workflow_id=workflow.id)
    assert paused.status == "PAUSED"

    # 5. Resume Cadence
    resumed = await cadence_engine.resume_cadence(db=db_session, workflow_id=workflow.id)
    assert resumed.status == "ACTIVE"


@pytest.mark.asyncio
async def test_cadence_api_endpoints(client, db_session, auth_headers):
    """Test REST API endpoints for cadence creation, listing, details, stepping, and pausing."""
    tenant = Tenant(id="tenant_nexora_default", name="Default Org")
    company = Company(
        id="comp_cad_api_01",
        tenant_id="tenant_nexora_default",
        name="Vertex Logistics",
        industry="Supply Chain",
        pipeline_stage="IDENTIFIED",
    )
    db_session.add_all([tenant, company])
    await db_session.commit()

    # 1. POST /workflows/cadence (Create)
    create_res = await client.post(
        "/api/v1/workflows/cadence",
        json={"company_id": "comp_cad_api_01", "title": "Vertex 14-Day Pursuit"},
        headers=auth_headers,
    )
    assert create_res.status_code == 201
    cadence_data = create_res.json()
    workflow_id = cadence_data["id"]
    assert cadence_data["title"] == "Vertex 14-Day Pursuit"
    assert cadence_data["status"] == "ACTIVE"

    # 2. GET /workflows/cadence (List)
    list_res = await client.get("/api/v1/workflows/cadence", headers=auth_headers)
    assert list_res.status_code == 200
    items = list_res.json()
    assert len(items) >= 1
    assert any(w["id"] == workflow_id for w in items)

    # 3. GET /workflows/cadence/{id} (Get Details)
    get_res = await client.get(f"/api/v1/workflows/cadence/{workflow_id}", headers=auth_headers)
    assert get_res.status_code == 200
    details = get_res.json()
    assert details["id"] == workflow_id
    assert len(details["steps_config"]) == 4

    # 4. POST /workflows/cadence/{id}/step (Execute Step 0)
    step_res = await client.post(f"/api/v1/workflows/cadence/{workflow_id}/step", headers=auth_headers)
    assert step_res.status_code == 200
    step_data = step_res.json()
    assert step_data["current_step_index"] == 1

    # 5. POST /workflows/cadence/{id}/pause (Pause)
    pause_res = await client.post(f"/api/v1/workflows/cadence/{workflow_id}/pause", headers=auth_headers)
    assert pause_res.status_code == 200
    assert pause_res.json()["status"] == "PAUSED"

    # 6. POST /workflows/cadence/{id}/resume (Resume)
    resume_res = await client.post(f"/api/v1/workflows/cadence/{workflow_id}/resume", headers=auth_headers)
    assert resume_res.status_code == 200
    assert resume_res.json()["status"] == "ACTIVE"


@pytest.mark.asyncio
async def test_cadence_full_completion_flow(db_session):
    """Running all 4 steps marks the cadence workflow as COMPLETED."""
    tenant = Tenant(id="tenant_nexora_default", name="Default Org")
    company = Company(
        id="comp_complete_01",
        tenant_id="tenant_nexora_default",
        name="Starlight Dynamics",
        industry="Defense",
    )
    db_session.add_all([tenant, company])
    await db_session.commit()

    workflow = await cadence_engine.create_cadence(
        db=db_session,
        tenant_id="tenant_nexora_default",
        company_id="comp_complete_01",
    )

    # Run step 0, 1, 2, 3
    for _ in range(4):
        # If waiting approval, resume to active to continue test simulation
        if workflow.status == "WAITING_APPROVAL":
            await cadence_engine.resume_cadence(db=db_session, workflow_id=workflow.id)
        res = await cadence_engine.execute_step(db=db_session, workflow_id=workflow.id)

    assert res["status"] == "COMPLETED"
    assert res["current_step_index"] == 4
