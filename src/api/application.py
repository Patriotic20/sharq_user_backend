from fastapi import APIRouter, Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from src.service.application import ApplicationCrud
from src.schemas.application import ApplicationResponse
from sharq_models.models import User
from src.core.db import get_db
from src.utils.auth import require_roles

application_router = APIRouter(prefix="/application", tags=["Application"])


def get_service_crud(db: AsyncSession = Depends(get_db)):
    return ApplicationCrud(db)


@application_router.post("/create", response_model=ApplicationResponse)
async def application_create(
    service: Annotated[ApplicationCrud, Depends(get_service_crud)],
    current_user: Annotated[User, Depends(require_roles(["user"]))],
):
    return await service.application_creation(user_id=current_user.id)


@application_router.get(
    "/get_by_id/{applicationd_id}", response_model=ApplicationResponse
)
async def get_application_by_id(
    applicationd_id: int,
    service: Annotated[ApplicationCrud, Depends(get_service_crud)],
    current_user: Annotated[User, Depends(require_roles(["user"]))],
):
    return await service.get_application_with_nested_info(
        application_id=applicationd_id, user_id=current_user.id
    )
