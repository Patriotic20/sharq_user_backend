from fastapi import APIRouter, Depends
from src.service.study_info import StudyInfoCrud
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.study_info import (
    StudyInfoCreate,
    StudyInfoResponse,
    StudyInfoCreateRequest,
    StudyInfoBase,
)
from src.core.db import get_db
from sharq_models.models import User # type: ignore
from src.utils.auth import require_roles
from typing import Annotated

application_router = APIRouter(prefix="/application")


def get_service_crud(db: AsyncSession = Depends(get_db)):
    return StudyInfoCrud(db)


@application_router.post("/create", tags=["Application"])
async def create_application(
    study_info: StudyInfoCreateRequest,
    service: Annotated[StudyInfoCrud, Depends(get_service_crud)],
    current_user: Annotated[User, Depends(require_roles(["user"]))],
):
    return await service.create_application(
        study_info=StudyInfoCreate(
            user_id=current_user.id, 
            **study_info.model_dump()
        )
    )


@application_router.get("", tags=["Application"])
async def get_user_study_info(
    service: Annotated[StudyInfoCrud, Depends(get_service_crud)],
    current_user: Annotated[User, Depends(require_roles(["user"]))],
) -> StudyInfoResponse:
    return await service.get_application_by_user_id(user_id=current_user.id)


@application_router.put("/update", tags=["Application"])
async def update_application(
    application: StudyInfoBase,
    service: Annotated[StudyInfoCrud, Depends(get_service_crud)],
    current_user: Annotated[User, Depends(require_roles(["user"]))],
):
    return await service.update_application(
        application=application,
        user_id=current_user.id
    )


@application_router.get("/study_direction", tags=["Study Direction"])
async def get_study_direction_list(
    service: Annotated[StudyInfoCrud, Depends(get_service_crud)],
):
    return await service.get_study_direction_list()


@application_router.get("/study_type", tags=["Study Type"])
async def get_study_type_list(
    service: Annotated[StudyInfoCrud, Depends(get_service_crud)],
):
    return await service.get_study_type_list()


@application_router.get("/study_form", tags=["Study Form"])
async def get_study_form_list(
    service: Annotated[StudyInfoCrud, Depends(get_service_crud)],
):
    return await service.get_study_form_list()


@application_router.get("/study_language", tags=["Study Language"])
async def get_study_language_list(
    service: Annotated[StudyInfoCrud, Depends(get_service_crud)],
):
    return await service.get_study_language_list()


@application_router.get("/education_type", tags=["Education Type"])
async def get_education_type_list(
    service: Annotated[StudyInfoCrud, Depends(get_service_crud)],
):
    return await service.get_education_type_list()
