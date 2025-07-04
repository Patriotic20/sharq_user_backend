from fastapi import HTTPException, status
from src.service import BasicCrud
from sharq_models.models import StudyDirection
from src.schemas.study_direction import (
    StudyDirectionBase,
    StudyDirectionUpdate,  
    StudyDirectionFilter,
    StudyDirectionResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List


class StudyDirectionCrud(BasicCrud[StudyDirection, StudyDirectionBase]):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def create_study_direction(self, obj: StudyDirectionBase) -> StudyDirectionResponse:
        existing = await super().get_by_field(
            model=StudyDirection,
            field_name="study_code",
            field_value=obj.study_code,
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Bunday fan mavjud",
            )

        return await super().create(model=StudyDirection, obj_items=obj)

    async def get_by_study_direction_id(self, direction_id: int) -> StudyDirectionResponse:
        study_direction = await super().get_by_id(model=StudyDirection, item_id=direction_id)

        if not study_direction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Yo'nalish topilmadi"
            )

        return study_direction

    async def get_study_direction_all(
        self,
        filter_obj: StudyDirectionFilter,
        limit: int = 100,
        offset: int = 0
    ) -> List[StudyDirectionResponse]:
        filters = []

        if filter_obj.name:
            filters.append(StudyDirection.name.ilike(f"%{filter_obj.name}%"))
        if filter_obj.study_form:
            filters.append(StudyDirection.study_form == filter_obj.study_form)
        if filter_obj.contract_sum:
            filters.append(StudyDirection.contract_sum == filter_obj.contract_sum)
        if filter_obj.education_years:
            filters.append(StudyDirection.education_years == filter_obj.education_years)
        if filter_obj.study_code:
            filters.append(StudyDirection.study_code == filter_obj.study_code)

        return await super().get_all(
            model=StudyDirection,
            limit=limit,
            offset=offset,
            filters=filters or None
        )



    async def update_study_direction(self, direction_id: int, obj: StudyDirectionUpdate) -> StudyDirectionResponse:
        await self.get_by_study_direction_id(direction_id)
        return await super().update(model=StudyDirection, item_id=direction_id, obj_items=obj)

    async def delete_study_direction(self, direction_id: int) -> dict:
        await self.get_by_study_direction_id(direction_id)
        return await super().delete(model=StudyDirection, item_id=direction_id)
