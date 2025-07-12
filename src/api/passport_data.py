from fastapi import APIRouter, Depends, UploadFile, File, Form
from datetime import date
from src.service.passport_data import PassportDataCrud
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.passport_data import (
    PassportDataBase,
    PassportDataResponse,
    PassportDataUpdate,
)
from src.core.db import get_db
from sharq_models.models import User
from src.utils.auth import require_roles
from typing import Annotated


passport_data_router = APIRouter(prefix="/passport_data", tags=["Passport Data"])


def get_service_crud(db: AsyncSession = Depends(get_db)):
    return PassportDataCrud(db)


@passport_data_router.post("/create")
async def create_passport_data(
    passport_series_number: Annotated[str, Form()],
    jshshir: Annotated[str, Form()],
    file: Annotated[UploadFile, File(...)],
    service: Annotated[PassportDataCrud, Depends(get_service_crud)],
    current_user: Annotated[User, Depends(require_roles(["user"]))],
) -> PassportDataResponse:
    passport_data_item = PassportDataBase(
        jshshir=jshshir,
        passport_series_number=passport_series_number
    )
    return await service.create_passport_data(
        passport_data_item=passport_data_item, file=file, user_id=current_user.id
    )


@passport_data_router.get("/get_by_id/{passport_data_id}")
async def get_by_passport_data_id(
    passport_data_id: int,
    service: Annotated[PassportDataCrud, Depends(get_service_crud)],
    current_user: Annotated[User, Depends(require_roles(["user"]))],
) -> PassportDataResponse:
    return await service.get_passport_data_by_id(
        passport_data_id=passport_data_id, user_id=current_user.id
    )


@passport_data_router.get("/get_all")
async def get_all_passport_data(
    service: Annotated[PassportDataCrud, Depends(get_service_crud)],
    current_user: Annotated[User, Depends(require_roles(["user"]))],
    limit: int | None = 20,
    offset: int | None = 0,
) -> list[PassportDataResponse]:
    return await service.get_all_passport_data(
        limit=limit, offset=offset, current_user=current_user
    )


@passport_data_router.put("/update/{passport_data_id}")
async def update_passport_data(
    passport_data_id: int,
    passport_data_items: PassportDataUpdate,
    service: Annotated[PassportDataCrud, Depends(get_service_crud)],
    current_user: Annotated[User, Depends(require_roles(["user"]))],
):
    return await service.update_passport_data(
        passport_data_id=passport_data_id,
        user_id=current_user.id,
        update_items=passport_data_items,
    )


@passport_data_router.delete("/delete/{passport_data_id}")
async def delete_passport_data(
    passport_data_id: int,
    service: Annotated[PassportDataCrud, Depends(get_service_crud)],
    current_user: Annotated[User, Depends(require_roles(["user"]))],
):
    return await service.delete_passport_data(
        passport_data_id=passport_data_id, user_id=current_user.id
    )
