"""
Excel API & Exporter Tests
Covers /excel/inspect, /excel/import (success & error), /excel/export,
and ExcelExporter.export_pipeline.
"""
import io
import pandas as pd
import pytest

from app.domain.models.models import Company, Contact, Tenant
from app.excel.exporter import excel_exporter


def _make_sample_bytes() -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        pd.DataFrame([{"Company": "Export Co", "Industry": "Tech"}]).to_excel(w, sheet_name="Master Pipeline", index=False)
    return buf.getvalue()


@pytest.mark.asyncio
async def test_excel_exporter_with_data(db_session):
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    co = Company(tenant_id="tenant_nexora_default", name="Export Co", industry="Tech", pipeline_stage="TARGET")
    db_session.add_all([tenant, co])
    await db_session.commit()
    await db_session.refresh(co)

    cnt = Contact(tenant_id="tenant_nexora_default", company_id=co.id, first_name="Export", last_name="User", title="CTO")
    db_session.add(cnt)
    await db_session.commit()

    excel_bytes = await excel_exporter.export_pipeline(db_session, "tenant_nexora_default")
    assert isinstance(excel_bytes, bytes)
    assert len(excel_bytes) > 100


@pytest.mark.asyncio
async def test_excel_exporter_empty_data(db_session):
    tenant = Tenant(id="tenant_empty_exp", name="Empty")
    db_session.add(tenant)
    await db_session.commit()

    excel_bytes = await excel_exporter.export_pipeline(db_session, "tenant_empty_exp")
    assert isinstance(excel_bytes, bytes)
    assert len(excel_bytes) > 100


@pytest.mark.asyncio
async def test_excel_inspect_api(client, auth_headers):
    wb_bytes = _make_sample_bytes()
    files = {"file": ("test.xlsx", wb_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    res = await client.post("/api/v1/excel/inspect", files=files, headers=auth_headers)
    assert res.status_code == 200
    assert "sheets_found" in res.json()


@pytest.mark.asyncio
async def test_excel_inspect_api_invalid_file(client, auth_headers):
    files = {"file": ("corrupt.xlsx", b"not an excel file", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    res = await client.post("/api/v1/excel/inspect", files=files, headers=auth_headers)
    assert res.status_code == 400
    assert "Invalid Excel workbook" in res.json()["detail"]


@pytest.mark.asyncio
async def test_excel_import_api(client, db_session, auth_headers):
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    wb_bytes = _make_sample_bytes()
    files = {"file": ("import.xlsx", wb_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    res = await client.post("/api/v1/excel/import", files=files, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["status"] == "SUCCESS"


@pytest.mark.asyncio
async def test_excel_import_api_invalid_file(client, db_session, auth_headers):
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    files = {"file": ("invalid.xlsx", b"bad bytes", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    res = await client.post("/api/v1/excel/import", files=files, headers=auth_headers)
    assert res.status_code == 400
    assert "Import failed" in res.json()["detail"]


@pytest.mark.asyncio
async def test_excel_export_api(client, db_session, auth_headers):
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    res = await client.get("/api/v1/excel/export", headers=auth_headers)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
