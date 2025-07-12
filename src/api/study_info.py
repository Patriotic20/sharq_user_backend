from fastapi import APIRouter, Depends
from src.service.study_info import StudyInfoCrud
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.study_info import (
    StudyInfoCreate,
    StudyInfoResponse,
    StudyInfoCreateRequest,
)
from src.core.db import get_db
from sharq_models.models import User
from src.utils.auth import require_roles
from typing import Annotated

study_info_router = APIRouter(prefix="/study_info", tags=["Study Info"])


def get_service_crud(db: AsyncSession = Depends(get_db)):
    return StudyInfoCrud(db)


@study_info_router.post("/create")
async def create_user_study_info(
    study_info: StudyInfoCreateRequest,
    service: Annotated[StudyInfoCrud, Depends(get_service_crud)],
    current_user: Annotated[User, Depends(require_roles(["user"]))],
) -> StudyInfoResponse:
    return await service.create_study_info(
        study_info=StudyInfoCreate(
            user_id=current_user.id, 
            **study_info.model_dump()
        )
    )


@study_info_router.get("/")
async def get_user_study_info(
    service: Annotated[StudyInfoCrud, Depends(get_service_crud)],
    current_user: Annotated[User, Depends(require_roles(["user"]))],
) -> StudyInfoResponse:
    return await service.get_study_info_by_user_id(user_id=current_user.id)
