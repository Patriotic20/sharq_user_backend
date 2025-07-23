from fastapi import APIRouter, Depends 
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



@report_router.get("/download/ikki/{user_id}")
async def download_ikki_pdf(
    service: Annotated[ReportService, Depends(get_report_service)],
    current_user: Annotated[User, Depends(require_roles(["user"]))],
):
    filename, content = await service.download_pdf(user_id=current_user.id)

    return Response(
        content=content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
