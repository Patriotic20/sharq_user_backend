from fastapi import APIRouter, Depends
from src.service.passport_data import PassportDataCrud
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.passport_data import (
    PassportDataBase,
    PassportDataResponse,
    PassportDataCreateRequest,
)
from src.core.db import get_db
from sharq_models.models import User #type: ignore
from src.utils.auth import require_roles
from typing import Annotated


passport_data_router = APIRouter(prefix="/passport_data", tags=["Passport Data"])


def get_service_crud(db: AsyncSession = Depends(get_db)):
    return PassportDataCrud(db)


@passport_data_router.post("/create")
async def create_passport_data(
    passport_data_item: PassportDataCreateRequest,
    service: Annotated[PassportDataCrud, Depends(get_service_crud)],
    current_user: Annotated[User, Depends(require_roles(["user"]))],
) -> PassportDataResponse:
    passport_data_item = PassportDataBase(
        jshshir=passport_data_item.jshshir,
        passport_series_number=passport_data_item.passport_series_number,
    )
    return await service.create_passport_data(
        passport_data_item=passport_data_item,
        user_id=current_user.id,
    )


@passport_data_router.get("")
async def get_by_passport_data_id(
    service: Annotated[PassportDataCrud, Depends(get_service_crud)],
    current_user: Annotated[User, Depends(require_roles(["user"]))],
) -> PassportDataResponse:
    return await service.get_passport_data_by_user_id(user_id=current_user.id)
