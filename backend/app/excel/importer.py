import io
import logging
from typing import Any

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.models import (
    Company,
    CompanyProject,
    Contact,
    Lead,
    Meeting,
    OutreachMessage,
    WorkbookImport,
)

logger = logging.getLogger(__name__)


def find_header_row(excel_file: pd.ExcelFile, sheet_name: str) -> int:
    """
    Auto-detects the real header row index in sheets that have title/subtitle rows above data.
    Scans up to 10 rows looking for the first row that has 3+ non-null string cells
    and whose first cell is NOT a single merged title.
    Returns 0 if not found (standard header).
    """
    df_raw = pd.read_excel(excel_file, sheet_name=sheet_name, header=None, nrows=15)
    for i, row in df_raw.iterrows():
        non_null = [v for v in row.tolist() if pd.notnull(v) and str(v).strip()]
        if len(non_null) >= 3:
            # Check it looks like headers (mostly short strings, not paragraph text)
            short_vals = [v for v in non_null if len(str(v)) < 80]
            if len(short_vals) >= 3:
                return i
    return 0


def read_sheet_with_header(excel_file: pd.ExcelFile, sheet_name: str) -> pd.DataFrame:
    """Read sheet with auto-detected header row."""
    header_row = find_header_row(excel_file, sheet_name)
    df = pd.read_excel(excel_file, sheet_name=sheet_name, header=header_row)
    df = df.where(pd.notnull(df), None)
    # Drop rows where all values are None
    df = df.dropna(how='all')
    return df


def find_column_val(row: pd.Series, keywords: list[str]) -> str | None:
    """Helper to fuzzy match row column values based on semantic keywords."""
    for col in row.index:
        col_str = str(col).strip().lower()
        for kw in keywords:
            if kw.lower() in col_str:
                val = row.get(col)
                if pd.notnull(val) and str(val).strip():
                    return str(val).strip()
    return None


class ExcelImporter:
    """
    Dynamic XLSX Ingestion Engine supporting flexible business workbooks,
    automatic header detection, configurable column mapping, and multi-tenant persistence.
    """

    def parse_workbook(self, file_bytes: bytes) -> dict[str, Any]:
        excel_file = pd.ExcelFile(io.BytesIO(file_bytes))
        sheet_names = excel_file.sheet_names

        parsed_sheets = {}
        for sheet in sheet_names:
            df = read_sheet_with_header(excel_file, sheet)
            real_cols = [str(c) for c in df.columns if not str(c).startswith('Unnamed')]
            
            # Clean sample rows to replace any remaining NaN/Inf values with None for JSON compliance
            sample_records = df.head(3).to_dict(orient="records")
            clean_samples = []
            for rec in sample_records:
                clean_rec = {}
                for k, v in rec.items():
                    if pd.isna(v):
                        clean_rec[str(k)] = None
                    else:
                        clean_rec[str(k)] = str(v) if isinstance(v, (float, int)) and not pd.isna(v) else v
                clean_samples.append(clean_rec)

            parsed_sheets[sheet] = {
                "columns": real_cols,
                "row_count": len(df),
                "sample_rows": clean_samples,
            }

        return {
            "sheets_found": sheet_names,
            "parsed_summary": parsed_sheets,
        }

    async def import_data(
        self, db: AsyncSession, file_bytes: bytes, tenant_id: str, filename: str = "uploaded_workbook.xlsx"
    ) -> dict[str, Any]:
        excel_file = pd.ExcelFile(io.BytesIO(file_bytes))
        imported_companies = 0
        imported_contacts = 0
        imported_projects = 0
        warnings = []
        errors = []

        import_rec = WorkbookImport(
            tenant_id=tenant_id,
            filename=filename,
            sheet_names=excel_file.sheet_names,
            rows_processed=0,
            status="PROCESSING",
        )
        db.add(import_rec)
        await db.flush()

        for sheet in excel_file.sheet_names:
            sheet_lower = sheet.lower().strip()
            df = read_sheet_with_header(excel_file, sheet)

            if df.empty:
                continue

            import_rec.rows_processed += len(df)

            # Master Pipeline / Pursuit Profiles / Company Sheet
            if any(k in sheet_lower for k in ["master", "pipeline", "profile", "company", "pursuit", "sprint"]):
                for idx, row in df.iterrows():
                    company_name = find_column_val(row, ["company", "account", "firm"])
                    if not company_name:
                        continue

                    # Query existing company or create
                    res = await db.execute(
                        select(Company).where(Company.name == company_name, Company.tenant_id == tenant_id)
                    )
                    comp = res.scalars().first()

                    sector = find_column_val(row, ["sector", "industry"]) or "Enterprise"
                    priority = find_column_val(row, ["priority", "rank"]) or "High"
                    hq_focus = find_column_val(row, ["hq", "focus", "location"])
                    active_work = find_column_val(row, ["active", "upcoming", "work", "project"])
                    why_now = find_column_val(row, ["why now", "why-now", "signal", "trigger"]) or "Expansion signal detected"
                    lead_service = find_column_val(row, ["lead service", "service", "offering"])
                    named_contacts_str = find_column_val(row, ["named", "contact", "target contact"])
                    relationship = find_column_val(row, ["relationship", "stage"]) or "TARGET"
                    timing = find_column_val(row, ["timing", "timeframe"])
                    next_action = find_column_val(row, ["next action", "recommended next action", "action"])
                    company_src = find_column_val(row, ["source", "portfolio source"]) or f"Sheet: {sheet}"
                    notes = find_column_val(row, ["notes", "context"])

                    if not comp:
                        comp = Company(
                            tenant_id=tenant_id,
                            name=company_name,
                            domain=f"{company_name.lower().replace(' ', '').replace(',', '')}.com",
                            industry=sector,
                            sector=sector,
                            priority=priority,
                            hq_focus=hq_focus,
                            location=hq_focus or "USA",
                            active_upcoming_work=active_work,
                            why_now_signal=why_now,
                            recommended_service=lead_service or "AI Pursuit Engine",
                            lead_service=lead_service,
                            named_contacts_str=named_contacts_str,
                            relationship_stage=relationship,
                            timing=timing,
                            recommended_next_action=next_action or "Initiate Executive Research",
                            company_source=company_src,
                            notes=notes,
                            pipeline_stage="IDENTIFIED",
                        )
                        db.add(comp)
                        await db.flush()
                        imported_companies += 1

                    # Ensure associated Lead exists for dynamic pipeline card rendering
                    res_lead = await db.execute(
                        select(Lead).where(Lead.company_id == comp.id, Lead.tenant_id == tenant_id)
                    )
                    lead = res_lead.scalars().first()
                    if not lead:
                        lead = Lead(
                            tenant_id=tenant_id,
                            company_id=comp.id,
                            pipeline_stage="IDENTIFIED",
                            fit_score=85 if priority.lower() == "high" else 70,
                            fit_classification="HIGH" if priority.lower() == "high" else "MEDIUM",
                            score_reasoning=f"Imported from {sheet}. Why Now: {why_now}",
                            positive_signals=[sector, priority, why_now],
                            score_confidence=0.9,
                            linkedin_status="NOT_STARTED",
                            meeting_status="NOT_SCHEDULED",
                        )
                        db.add(lead)

            # Contacts / Role Coverage Sheet
            if any(k in sheet_lower for k in ["contact", "role", "coverage", "people"]):
                for idx, row in df.iterrows():
                    full_name = find_column_val(row, ["contact", "name", "target role", "person"])
                    comp_name = find_column_val(row, ["company", "account"])
                    title = find_column_val(row, ["title", "role"]) or "Executive"

                    if not full_name and not title:
                        continue

                    if not comp_name:
                        comp_name = "Imported Enterprise"

                    # Find or create company reference
                    res_c = await db.execute(
                        select(Company).where(Company.name == comp_name, Company.tenant_id == tenant_id)
                    )
                    comp = res_c.scalars().first()
                    if not comp:
                        comp = Company(
                            tenant_id=tenant_id,
                            name=comp_name,
                            domain=f"{comp_name.lower().replace(' ', '')}.com",
                            industry="Enterprise",
                            pipeline_stage="IDENTIFIED",
                        )
                        db.add(comp)
                        await db.flush()
                        imported_companies += 1

                    name_parts = (full_name or "Executive Decision-Maker").split()
                    first_name = name_parts[0]
                    last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else "Executive"

                    why_person = find_column_val(row, ["why this person", "why", "relevance"])
                    pub_profile = find_column_val(row, ["public profile", "source", "linkedin"])
                    pub_email = find_column_val(row, ["email", "public email"])
                    priority = find_column_val(row, ["priority", "influence"])
                    suggested_channel = find_column_val(row, ["channel", "suggested channel"]) or "LINKEDIN"
                    opening_ctx = find_column_val(row, ["opening context", "context"])
                    intro_draft = find_column_val(row, ["linkedin intro", "intro"])
                    next_action = find_column_val(row, ["next best action", "next action", "action"])
                    notes = find_column_val(row, ["notes", "research status"])

                    cnt = Contact(
                        tenant_id=tenant_id,
                        company_id=comp.id,
                        first_name=first_name,
                        last_name=last_name,
                        title=title,
                        email=pub_email or f"{first_name.lower()}.{last_name.lower()}@{comp.name.lower().replace(' ', '')}.com",
                        linkedin_url=pub_profile,
                        why_this_person=why_person,
                        public_profile=pub_profile,
                        public_email=pub_email,
                        priority=priority,
                        suggested_channel=suggested_channel,
                        opening_context=opening_ctx,
                        linkedin_intro=intro_draft,
                        next_best_action=next_action,
                        notes=notes,
                        linkedin_status="NOT_STARTED",
                        source=f"Sheet: {sheet}",
                    )
                    db.add(cnt)
                    imported_contacts += 1

            # Active Projects Sheet
            if any(k in sheet_lower for k in ["project", "program", "active"]):
                for idx, row in df.iterrows():
                    proj_name = find_column_val(row, ["project", "program", "active project"])
                    comp_name = find_column_val(row, ["company", "account"])
                    if not proj_name or not comp_name:
                        continue

                    res_c = await db.execute(
                        select(Company).where(Company.name == comp_name, Company.tenant_id == tenant_id)
                    )
                    comp = res_c.scalars().first()
                    if comp:
                        proj = CompanyProject(
                            tenant_id=tenant_id,
                            company_id=comp.id,
                            project_name=proj_name,
                            location=find_column_val(row, ["location", "hq"]),
                            stage=find_column_val(row, ["stage", "status"]) or "Active",
                            sector=find_column_val(row, ["sector", "industry"]),
                            scale_context=find_column_val(row, ["scale", "context"]),
                            expected_completion=find_column_val(row, ["completion", "expected completion", "timeframe"]),
                            lead_quality=find_column_val(row, ["lead quality", "quality"]),
                            source=find_column_val(row, ["source"]),
                        )
                        db.add(proj)
                        imported_projects += 1

        import_rec.companies_imported = imported_companies
        import_rec.contacts_imported = imported_contacts
        import_rec.projects_imported = imported_projects
        import_rec.status = "COMPLETED"
        import_rec.warnings = warnings
        import_rec.errors = errors

        await db.commit()

        return {
            "status": "SUCCESS",
            "import_id": import_rec.id,
            "filename": filename,
            "imported_companies": imported_companies,
            "imported_contacts": imported_contacts,
            "imported_projects": imported_projects,
            "warnings": warnings,
            "errors": errors,
        }


excel_importer = ExcelImporter()
