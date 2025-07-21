from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from sharq_models.models import User  # type: ignore
from src.core.db import get_db
from src.utils.auth import require_roles
from src.service.contract import ReportService

report_router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

def get_report_service(db: AsyncSession = Depends(get_db)) -> ReportService:
    return ReportService(db)


@report_router.get(
    "/download",
    response_class=StreamingResponse,
    status_code=200,
    summary="Download user's contract report",
    description="Generates and returns a PDF report for the authenticated user."
)
async def download_report(
    current_user: Annotated[User, Depends(require_roles(["user"]))],
    service: ReportService = Depends(get_report_service),
):
    try:
        pdf_file = await service.download_pdf(current_user.id)
        return StreamingResponse(
            pdf_file,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=report_{current_user.id}.pdf"
            }
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
