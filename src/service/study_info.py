from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import List

from sharq_models.models import StudyInfo
from src.schemas.study_info import (
    StudyInfoCreate,
    StudyInfoCreateRequest,
    StudyInfoResponse,
)

from src.schemas.study_language import StudyLanguageResponse
from src.schemas.study_form import StudyFormResponse
from src.schemas.study_direction import StudyDirectionResponse
from src.service import BasicCrud


class StudyInfoCrud(BasicCrud[StudyInfo, StudyInfoCreate]):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def create_study_info(self, study_info: StudyInfoCreate) -> StudyInfoResponse:
        await self._create_study_info_if_not_exists(study_info=study_info)
        return {"message": "Ma'lumot muvaffaqiyatli qo'shildi"}

    async def _create_study_info_if_not_exists(self, study_info: StudyInfoCreate):
        existing_study_info = await super().get_by_field(
            model=StudyInfo, field_name="user_id", field_value=study_info.user_id
        )
        if existing_study_info:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Foydalanuvchiga tegishli ma'lumot allaqachon mavjud",
            )
        await super().create(model=StudyInfo, obj_items=study_info)

    async def _get_with_join(
        self, user_id: int
    ) -> StudyInfoResponse:
        stmt = (
            select(StudyInfo)
            .options(
                joinedload(StudyInfo.study_language),
                joinedload(StudyInfo.study_form),
                joinedload(StudyInfo.study_direction),
            )
            .where(StudyInfo.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        study_info = result.scalar_one_or_none()

        if not study_info:
            raise HTTPException(status_code=404, detail="Ma'lumot topilmadi")

        if study_info.user_id != user_id:
            raise HTTPException(status_code=403, detail="Ruxsat yo'q")

        return self._to_response_with_names(study_info)

    def _to_response_with_names(self, study_info: StudyInfo) -> StudyInfoResponse:
        return StudyInfoResponse(
            id=study_info.id,
            user_id=study_info.user_id,
            study_language=StudyLanguageResponse.model_validate(
                study_info.study_language
            ),
            study_form=StudyFormResponse.model_validate(study_info.study_form),
            study_direction=StudyDirectionResponse.model_validate(
                study_info.study_direction
            ),
        )

    async def get_study_info_by_user_id(
        self, user_id: int
    ) -> StudyInfoResponse:
        return await self._get_with_join(user_id=user_id)