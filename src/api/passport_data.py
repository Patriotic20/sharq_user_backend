from fastapi import APIRouter , Depends , Security
from src.service.passport_data import PassportDataCrud
from sqlalchemy.ext.asyncio import  AsyncSession
from src.schemas.passport_data import (
    PassportDataBase ,
    PassportDataResponse ,
    PassportDataUpdate
)
from src.db.session import get_db
from src.models import  User
from src.utils import get_current_user
from typing import  Annotated


passport_data_router = APIRouter(
    prefix="/passport_data",
    tags=["Passport Data"]
)

def get_service_crud(db: AsyncSession = Depends(get_db)):
    return PassportDataCrud(db)

@passport_data_router.post("/create")
async def create_passport_data(
        passport_data_item: PassportDataBase,
        service: Annotated[PassportDataCrud , Depends(get_service_crud)],
        current_user: Annotated[User , Security(get_current_user , scopes=["user"])]
) -> PassportDataResponse:
    return await service.create_passport_data(passport_data_item=passport_data_item , user_id=current_user.id)


@passport_data_router.get("/get_by_id/{passport_data_id}")
async def get_by_passport_data_id(
        passport_data_id: int,
        service: Annotated[PassportDataCrud, Depends(get_service_crud)],
        current_user: Annotated[User, Security(get_current_user, scopes=["user"])]
)-> PassportDataResponse:
    return await service.get_passport_data_by_id(passport_data_id=passport_data_id , user_id=current_user.id)

@passport_data_router.get("/get_all")
async def get_all_passport_data(
        service: Annotated[PassportDataCrud, Depends(get_service_crud)],
        current_user: Annotated[User, Security(get_current_user, scopes=["user"])],
        limit: int | None = 20,
        offset: int | None = 0,
) -> list[PassportDataResponse]:
    return await service.get_all_passport_data(limit=limit , offset=offset , current_user=current_user)

@passport_data_router.put("/update/{passport_data_id}")
async def update_passport_data(
        passport_data_id: int,
        passport_data_items: PassportDataUpdate,
        service: Annotated[PassportDataCrud, Depends(get_service_crud)],
        current_user: Annotated[User, Security(get_current_user, scopes=["user"])],
):
    return await service.update_passport_data(passport_data_id=passport_data_id ,  user_id=current_user.id , update_items=passport_data_items)

@passport_data_router.delete("/delete/{passport_data_id}")
async def delete_passport_data(
        passport_data_id: int,
        service: Annotated[PassportDataCrud, Depends(get_service_crud)],
        current_user: Annotated[User, Security(get_current_user, scopes=["user"])],
):
    return await service.delete_passport_data(passport_data_id=passport_data_id , user_id=current_user.id)
