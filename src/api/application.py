from fastapi import APIRouter, Depends, Query , Security
from typing import Annotated
from src.utils import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from src.service.application import ApplicationCrud
from src.schemas.application import ApplicationResponse
from sharq_models.models import User
from sharq_models.db import get_db

application_router = APIRouter(
    prefix="/application",
    tags=["Application"]
)


def get_service_crud(db: AsyncSession = Depends(get_db)):
    return ApplicationCrud(db)



@application_router.post("/create",response_model=ApplicationResponse)
async def application_create(
    service: Annotated[ApplicationCrud, Depends(get_service_crud)],
    current_user: Annotated[User , Security(get_current_user , scopes=["user"])]
):
    return await service.application_creation(user_id=current_user.id)



@application_router.get("/get_by_id/{applicationd_id}", response_model=ApplicationResponse)
async def get_application_by_id(
    applicationd_id: int,
    service: Annotated[ApplicationCrud, Depends(get_service_crud)],
    current_user: Annotated[User , Security(get_current_user , scopes=["user"])]
):
    return await service.get_application_with_nested_info(application_id=applicationd_id, user_id=current_user.id)
     



