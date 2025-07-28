from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.service import BasicCrud
from sharq_models.models import ( # type: ignore
    Application,
    PassportData,
    StudyInfo
)
from src.schemas.application import (
    ApplicationBase,
    ApplicationResponse
)


class ApplicationCrud(BasicCrud[Application, ApplicationBase]):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def application_creation(self, user_id: int) -> dict:
        passport_data = await super().get_by_field(
            model=PassportData, field_name="user_id", field_value=user_id
        )
        study_info = await super().get_by_field(
            model=StudyInfo, field_name="user_id", field_value=user_id
        )

        if not passport_data or not study_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Passport yoki Ta'lim ma'lumotlari topilmadi",
            )

        stmt = select(Application).where(
            Application.passport_data_id == passport_data.id,
            Application.study_info_id == study_info.id,
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Bu foydalanuvchi uchun ariza allaqachon mavjud",
            )

        application = await super().create(
            model=Application, 
            obj_items=ApplicationBase(
                passport_data_id=passport_data.id, 
                study_info_id=study_info.id,
            )
        )
        
        return {
            "message": "Ariza muvaffaqiyatli yaratildi",
            "application": application
        }

    async def get_application_by_user_id(self, user_id: int):
        stmt = (
            select(Application)
            .options(
                selectinload(Application.passport_data),
                selectinload(Application.study_info).selectinload(StudyInfo.study_form),
                selectinload(Application.study_info).selectinload(StudyInfo.study_language),
                selectinload(Application.study_info).selectinload(StudyInfo.study_type),
                selectinload(Application.study_info).selectinload(StudyInfo.education_type),
                selectinload(Application.study_info).selectinload(StudyInfo.study_direction)
            )
            .join(Application.passport_data)
            .where(PassportData.user_id == user_id)
        )


        result = await self.db.execute(stmt)
        application = result.scalars().first()

        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ariza topilmadi"
            )

        return ApplicationResponse.model_validate(application)
    
    

