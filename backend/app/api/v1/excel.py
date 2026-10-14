from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import UserContext, get_current_user
from app.excel.exporter import excel_exporter
from app.excel.importer import excel_importer

router = APIRouter(prefix="/excel", tags=["Excel Import / Export"])


@router.post("/inspect")
async def inspect_excel_workbook(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        summary = excel_importer.parse_workbook(contents)
        return summary
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid Excel workbook: {exc!s}")


@router.post("/import")
async def import_excel_workbook(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(get_current_user)
):
    contents = await file.read()
    try:
        res = await excel_importer.import_data(db, contents, user.tenant_id)
        return res
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Import failed: {exc!s}")


@router.get("/export")
async def export_pipeline_excel(
    db: AsyncSession = Depends(get_db),
    user: UserContext = Depends(get_current_user)
):
    excel_bytes = await excel_exporter.export_pipeline(db, user.tenant_id)
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=NEXORA_Pursuit_Pipeline.xlsx"}
    )
