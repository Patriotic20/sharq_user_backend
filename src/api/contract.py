from fastapi import APIRouter, Depends , HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db import get_db
from src.service.contract import ReportService
from typing import Annotated


from fastapi.responses import Response
from sharq_models.models import User # type: ignore
from src.utils.auth import require_roles 

report_router = APIRouter(prefix="/contract", tags=["Contract Reports"])


def get_report_service(db: AsyncSession = Depends(get_db)):
    return ReportService(db)




@report_router.get("/download/two_side")
async def download_two_side_pdf(
    service: Annotated[ReportService, Depends(get_report_service)],
    current_user: Annotated[User, Depends(require_roles(["user"]))],
):
    result = await service.get_two_side_report(user_id=current_user.id)
    if result is None:
        raise HTTPException(status_code=404, detail="Two-side contract not found")
    
    filename, content = result
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@report_router.get("/download/three_side")
async def download_three_side_pdf(
    service: Annotated[ReportService, Depends(get_report_service)],
    current_user: Annotated[User, Depends(require_roles(["user"]))],
):
    result = await service.get_three_side_report(user_id=current_user.id)
    if result is None:
        raise HTTPException(status_code=404, detail="Three-side contract not found")
    
    filename, content = result
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
    
@report_router.get("/get_status")
async def get_user_comtract_status(
    service: Annotated[ReportService, Depends(get_report_service)],
    current_user: Annotated[User, Depends(require_roles(["user"]))],
):
    return await service.check_by_status(user_id=current_user.id)
