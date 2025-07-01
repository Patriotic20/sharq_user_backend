from fastapi import APIRouter , Depends , Security
from src.service.study_info import StudyInfoCrud
from sqlalchemy.ext.asyncio import  AsyncSession
from src.schemas.study_info import (
    StudyInfoBase,
    StudyInfoResponse,
    StudyInfoUpdate,
    StudyInfoFilter
)
from src.db.session import get_db
from src.models import  User
from src.utils import get_current_user
from typing import  Annotated


study_info_router = APIRouter(
    prefix="/study_info",
    tags=["Study Info"]
)

def get_service_crud(db: AsyncSession = Depends(get_db)):
    return StudyInfoCrud(db)

@study_info_router.post("/create")
async def create_study_info(
        study_info_item: StudyInfoBase,
        service: Annotated[StudyInfoCrud , Depends(get_service_crud)],
        current_user: Annotated[User , Security(get_current_user , scopes=["user"])]
) -> StudyInfoResponse:
    return await service.create_study_info(obj_info=study_info_item , user_id=current_user.id)


@study_info_router.get("/get_by_id/{study_info_id}")
async def get_by_study_info_id(
        study_info_id: int,
        service: Annotated[StudyInfoCrud, Depends(get_service_crud)],
        current_user: Annotated[User, Security(get_current_user, scopes=["user"])]
)-> StudyInfoResponse:
    return await service.get_by_id_study_info(study_info_id=study_info_id , user_id=current_user.id)

@study_info_router.get("/get_all")
async def get_all_study_info(
        service: Annotated[StudyInfoCrud, Depends(get_service_crud)],
        current_user: Annotated[User, Security(get_current_user, scopes=["user"])],
        filter_items: StudyInfoFilter = Depends(),
        limit: int | None = 20,
        offset: int | None = 0,
) -> list[StudyInfoResponse]:
    return await service.get_all_study_info(limit=limit, offset=offset, filters_data=filter_items)

@study_info_router.put("/update/{study_info_id}")
async def update_study_info(
        study_info_id: int,
        study_info_items: StudyInfoUpdate,
        service: Annotated[StudyInfoCrud, Depends(get_service_crud)],
        current_user: Annotated[User, Security(get_current_user, scopes=["user"])],
):
    return await service.update_study_info(
        study_info_id=study_info_id,  
        user_id=current_user.id, 
        obj=study_info_items
        )

@study_info_router.delete("/delete/{study_info_id}")
async def delete_study_info(
        study_info_id: int,
        service: Annotated[StudyInfoCrud, Depends(get_service_crud)],
        current_user: Annotated[User, Security(get_current_user, scopes=["user"])],
):
    return await service.delete_study_info(study_info_id=study_info_id , user_id=current_user.id)
