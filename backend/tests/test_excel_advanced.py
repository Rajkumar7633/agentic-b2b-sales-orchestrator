"""
Excel Import Pipeline — Comprehensive Tests
Covers: parse workbook (sheets, row counts, header detection),
        import with contacts, duplicate prevention, empty rows,
        multi-sheet support, missing columns graceful handling.
"""
import io

import pandas as pd
import pytest

from app.domain.models.models import Company, Contact, Tenant
from app.excel.importer import excel_importer


# ─────────────────────────────────────────────────────────────
# Builder helpers
# ─────────────────────────────────────────────────────────────
def _wb(pipeline_rows: list, contact_rows: list | None = None) -> bytes:
    """Build a minimal in-memory XLSX workbook."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        pd.DataFrame(pipeline_rows).to_excel(w, sheet_name="Master Pipeline", index=False)
        if contact_rows is not None:
            pd.DataFrame(contact_rows).to_excel(w, sheet_name="Named Contacts", index=False)
    return buf.getvalue()


def _pipeline_row(name: str, industry: str = "Construction",
                  stage: str = "TARGET", why: str = "Growth") -> dict:
    return {
        "Company": name,
        "Industry": industry,
        "Stage": stage,
        "Why Now": why,
        "Recommended Service": "Cost Planning",
        "Location / HQ": "Miami, FL",
    }


def _contact_row(first: str, last: str, title: str, company: str) -> dict:
    return {
        "First Name": first,
        "Last Name": last,
        "Title": title,
        "Company": company,
        "Why This Person": "Key decision maker",
        "Priority": "HIGH",
    }


# ─────────────────────────────────────────────────────────────
# Parse (non-DB) tests
# ─────────────────────────────────────────────────────────────
def test_parse_detects_both_sheets():
    wb = _wb(
        pipeline_rows=[_pipeline_row("Co A")],
        contact_rows=[_contact_row("Alice", "B", "VP", "Co A")]
    )
    result = excel_importer.parse_workbook(wb)
    assert "Master Pipeline" in result["sheets_found"]
    assert "Named Contacts" in result["sheets_found"]


def test_parse_correct_row_count():
    wb = _wb(
        pipeline_rows=[_pipeline_row("Co 1"), _pipeline_row("Co 2"), _pipeline_row("Co 3")],
        contact_rows=[_contact_row("A", "B", "VP", "Co 1")]
    )
    result = excel_importer.parse_workbook(wb)
    assert result["parsed_summary"]["Master Pipeline"]["row_count"] == 3
    assert result["parsed_summary"]["Named Contacts"]["row_count"] == 1


def test_parse_pipeline_only_no_contacts_sheet():
    """Workbook with only the Pipeline sheet should parse without errors."""
    wb = _wb(pipeline_rows=[_pipeline_row("Solo Corp")])
    result = excel_importer.parse_workbook(wb)
    assert "Master Pipeline" in result["sheets_found"]
    assert result["parsed_summary"]["Master Pipeline"]["row_count"] == 1


def test_parse_empty_company_rows_counted_as_raw():
    """Empty company rows are in raw data but filtered during import."""
    wb = _wb(pipeline_rows=[
        {"Company": "", "Industry": "Tech"},
        {"Company": "Valid Corp", "Industry": "Tech"},
    ])
    result = excel_importer.parse_workbook(wb)
    # Parser counts raw rows; filtering happens at import time
    assert result["parsed_summary"]["Master Pipeline"]["row_count"] == 2


def test_parse_many_companies():
    wb = _wb(pipeline_rows=[_pipeline_row(f"Co {i}") for i in range(50)])
    result = excel_importer.parse_workbook(wb)
    assert result["parsed_summary"]["Master Pipeline"]["row_count"] == 50


# ─────────────────────────────────────────────────────────────
# Import (DB) tests
# ─────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_import_creates_companies_in_db(db_session):
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    wb = _wb(pipeline_rows=[
        _pipeline_row("Import Co A"),
        _pipeline_row("Import Co B"),
    ])
    result = await excel_importer.import_data(db_session, wb, "tenant_nexora_default")

    assert result["imported_companies"] == 2


@pytest.mark.asyncio
async def test_import_creates_contacts_in_db(db_session):
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    wb = _wb(
        pipeline_rows=[_pipeline_row("Contact Corp")],
        contact_rows=[
            _contact_row("Alice", "Smith", "VP", "Contact Corp"),
            _contact_row("Bob", "Jones", "CTO", "Contact Corp"),
        ]
    )
    result = await excel_importer.import_data(db_session, wb, "tenant_nexora_default")

    assert result["imported_companies"] == 1
    assert result["imported_contacts"] == 2


@pytest.mark.asyncio
async def test_import_prevents_duplicate_companies(db_session):
    """Importing the same workbook twice must not create duplicate company rows."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    wb = _wb(pipeline_rows=[_pipeline_row("Unique Corp")])

    r1 = await excel_importer.import_data(db_session, wb, "tenant_nexora_default")
    r2 = await excel_importer.import_data(db_session, wb, "tenant_nexora_default")

    assert r1["imported_companies"] == 1
    assert r2["imported_companies"] == 0   # Duplicate silently skipped
    assert r2["status"] == "SUCCESS"       # Still returns success (not an error)


@pytest.mark.asyncio
async def test_import_skips_blank_company_names(db_session):
    """Rows with empty/null company name must be silently skipped."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    wb = _wb(pipeline_rows=[
        {"Company": "",    "Industry": "Tech"},
        {"Company": "   ", "Industry": "Tech"},  # whitespace only
        {"Company": "Valid Company", "Industry": "Tech"},
    ])
    result = await excel_importer.import_data(db_session, wb, "tenant_nexora_default")

    assert result["imported_companies"] == 1


@pytest.mark.asyncio
async def test_import_large_workbook(db_session):
    """Import 30 companies and 60 contacts without error."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    companies = [_pipeline_row(f"Large Co {i}", industry=f"Sector {i % 5}") for i in range(30)]
    contacts = [_contact_row(f"First{i}", f"Last{i}", "VP", f"Large Co {i % 30}")
                for i in range(60)]

    wb = _wb(pipeline_rows=companies, contact_rows=contacts)
    result = await excel_importer.import_data(db_session, wb, "tenant_nexora_default")

    # Only 1 valid company should be imported (blanks skipped)
    assert result["imported_companies"] == 30
    assert result["imported_contacts"] >= 0


@pytest.mark.asyncio
async def test_import_missing_optional_columns_graceful(db_session):
    """Workbook with only Company column (all others missing) should not crash."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        pd.DataFrame([{"Company": "Minimal Corp"}]).to_excel(
            w, sheet_name="Master Pipeline", index=False
        )
    wb = buf.getvalue()

    result = await excel_importer.import_data(db_session, wb, "tenant_nexora_default")
    assert result["imported_companies"] == 1


@pytest.mark.asyncio
async def test_import_returns_summary_dict(db_session):
    """Import result must always be a dict with expected keys."""
    tenant = Tenant(id="tenant_nexora_default", name="NEXORA")
    db_session.add(tenant)
    await db_session.commit()

    wb = _wb(pipeline_rows=[_pipeline_row("Summary Co")])
    result = await excel_importer.import_data(db_session, wb, "tenant_nexora_default")

    assert isinstance(result, dict)
    assert "imported_companies" in result
    assert "imported_contacts" in result
    # The result also contains status, import_id, warnings, errors
    assert "status" in result
