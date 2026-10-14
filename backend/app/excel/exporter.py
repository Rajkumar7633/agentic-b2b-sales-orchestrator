import io

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.models import Company, Contact


class ExcelExporter:
    """
    Excel export engine generating multi-tab Excel workbooks matching NEXORA business formats.
    """
    async def export_pipeline(self, db: AsyncSession, tenant_id: str) -> bytes:
        # Fetch companies
        comp_res = await db.execute(select(Company).where(Company.tenant_id == tenant_id))
        companies = comp_res.scalars().all()

        comp_data = []
        for c in companies:
            comp_data.append({
                "Company ID": c.id,
                "Company Name": c.name,
                "Domain": c.domain,
                "Industry": c.industry,
                "Size": c.size,
                "Location": c.location,
                "Revenue": c.revenue,
                "Why Now Signal": c.why_now_signal,
                "Recommended Service": c.recommended_service,
                "Pipeline Stage": c.pipeline_stage,
                "Research Confidence": c.research_confidence
            })

        # Fetch contacts
        cnt_res = await db.execute(select(Contact).where(Contact.tenant_id == tenant_id))
        contacts = cnt_res.scalars().all()

        cnt_data = []
        for cnt in contacts:
            cnt_data.append({
                "Contact ID": cnt.id,
                "First Name": cnt.first_name,
                "Last Name": cnt.last_name,
                "Title": cnt.title,
                "Email": cnt.email,
                "LinkedIn URL": cnt.linkedin_url,
                "Seniority": cnt.seniority,
                "Influence Score": cnt.influence_score,
                "Relationship Status": cnt.relationship_status
            })

        output_bytes = io.BytesIO()
        with pd.ExcelWriter(output_bytes, engine="openpyxl") as writer:
            pd.DataFrame(comp_data if comp_data else [{"Info": "No accounts"}]).to_excel(
                writer, sheet_name="Master Pipeline", index=False
            )
            pd.DataFrame(cnt_data if cnt_data else [{"Info": "No contacts"}]).to_excel(
                writer, sheet_name="Named Contacts", index=False
            )

        output_bytes.seek(0)
        return output_bytes.getvalue()


excel_exporter = ExcelExporter()
