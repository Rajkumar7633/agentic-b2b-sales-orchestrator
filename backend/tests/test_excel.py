import io

import pandas as pd

from app.excel.importer import excel_importer


def test_excel_workbook_parsing():
    # Generate synthetic Excel file in memory matching NEXORA workbook structure
    df_pipeline = pd.DataFrame([
        {"Company": "Acme Construction", "Domain": "acme.com", "Industry": "Construction", "Size": "1000+", "Stage": "TARGET"},
        {"Company": "Apex Energy", "Domain": "apex.com", "Industry": "Energy", "Size": "5000+", "Stage": "QUALIFIED"}
    ])

    df_contacts = pd.DataFrame([
        {"First Name": "Marcus", "Last Name": "Vance", "Title": "VP Procurement", "Company": "Acme Construction", "Email": "marcus@acme.com"}
    ])

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_pipeline.to_excel(writer, sheet_name="Master Pipeline", index=False)
        df_contacts.to_excel(writer, sheet_name="Named Contacts", index=False)

    bytes_val = output.getvalue()

    summary = excel_importer.parse_workbook(bytes_val)
    assert "Master Pipeline" in summary["sheets_found"]
    assert "Named Contacts" in summary["sheets_found"]
    assert summary["parsed_summary"]["Master Pipeline"]["row_count"] == 2
