from sqlalchemy.ext.asyncio import AsyncSession
from sharq_models.models import StudyInfo, AMOCrmLead

from src.core.config import settings
from src.service.amo import update_lead_with_full_data, DealData
from src.schemas.study_info import (
    StudyInfoBase,
    StudyInfoCreate,
    StudyInfoResponse,
)
from fastapi import HTTPException, status
from typing import Any, Type
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sharq_models.database import Base
from sharq_models.models import StudyLanguage, StudyForm, StudyDirection, StudyType, EducationType

from src.schemas.study_language import StudyLanguageResponse
from src.schemas.study_form import StudyFormResponse
from src.schemas.study_direction import StudyDirectionResponse
from src.schemas.study_type import StudyTypeResponse
from src.schemas.education_type import EducationTypeResponse

from src.service import BasicCrud

DEAL_DATA_MAPPING = {
    "name": "name",
    "contact_id": "contact_id",
    "StudyLanguage": "edu_lang_id",
    "EducationType": "edu_type",
    "StudyForm": "edu_form",
    "StudyDirection": "edu_direction",
    "edu_end_date": "edu_end_date",
    "admission_id": "admission_id",
    "certificate_link": "certificate_link",
    "passport_file_link": "passport_file_link",
}


class StudyInfoCrud(BasicCrud[StudyInfo, StudyInfoCreate]):
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.lead_data = {}
        
    async def _get_lead(self, user_id: int):
        lead = await super().get_by_field(
            model=AMOCrmLead, field_name="user_id", field_value=user_id
        )
        return lead

    async def create_application(self, study_info: StudyInfoCreate):
        application = await self._create_study_info_if_not_exists(study_info=study_info)
        lead = await self._get_lead(study_info.user_id)
        if not lead:
            print("Lead not found")
            pass
        else:
            update_lead_with_full_data(
                deal_id=lead.lead_id,
                deal_data=DealData(**{
                    "name": "Unnamed",
                    "contact_id": lead.contact_id,
                    **self.lead_data,
                }),
                config_data=settings.amo_crm_config,
            )
        
        return {
            "message": "Ariza muvaffaqiyatli yaratildi!",
            "application": application
        }
        
    async def update_application(self, application: StudyInfoBase, user_id: int):
        application = await super().update_by_field(
            model=StudyInfo, 
            obj_items=application,
            field_name="user_id",
            field_value=user_id,
        )
        return {
            "message": "Ariza muvaffaqiyatli yangilandi!",
            "application": application
        }

    async def _create_study_info_if_not_exists(self, study_info: StudyInfoCreate):
        existing_study_info = await super().get_by_field(
            model=StudyInfo, field_name="user_id", field_value=study_info.user_id
        )
        if existing_study_info:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Foydalanuvchiga tegishli ma'lumot allaqachon mavjud",
            )
            
        await self._validate_data(study_info=study_info)
        
        self.lead_data["admission_id"] = study_info.study_direction_id
        self.lead_data["edu_end_date"] = study_info.graduate_year
        self.lead_data["certificate_link"] = study_info.certificate_path
        self.lead_data["passport_file_link"] = study_info.dtm_sheet
        
        await super().create(model=StudyInfo, obj_items=study_info)
        
        application_data = await self._get_with_join(study_info.user_id)
        return application_data
        
    async def _validate_data(self, study_info: StudyInfoCreate):
        if not await self._check_exist(StudyLanguage, "id", study_info.study_language_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Study language not found")
        if not await self._check_exist(StudyForm, "id", study_info.study_form_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Study form not found")
        if not await self._check_exist(StudyDirection, "id", study_info.study_direction_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Study direction not found")
        if not await self._check_exist(StudyType, "id", study_info.study_type_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Study type not found")
        if not await self._check_exist(EducationType, "id", study_info.education_type_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Education type not found")
        
    async def _check_exist(self, model: Type[Base], field_name: str, field_value: Any):
        existing_data = await super().get_by_field(model=model, field_name=field_name, field_value=field_value)
        if model.__name__ in DEAL_DATA_MAPPING:
            self.lead_data[DEAL_DATA_MAPPING[model.__name__]] = existing_data.name if existing_data else None
        return existing_data is not None
        
    async def _get_with_join(self, user_id: int) -> StudyInfoResponse:
        stmt = (
            select(StudyInfo)
            .options(
                selectinload(StudyInfo.study_language),
                selectinload(StudyInfo.study_form),
                selectinload(StudyInfo.study_direction),
                selectinload(StudyInfo.study_type),
                selectinload(StudyInfo.education_type),
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
                study_info.study_language, from_attributes=True
            ),
            study_form=StudyFormResponse.model_validate(
                study_info.study_form, from_attributes=True
            ),
            study_direction=StudyDirectionResponse.model_validate(
                study_info.study_direction, from_attributes=True
            ),
            education_type=EducationTypeResponse.model_validate(
                study_info.education_type, from_attributes=True
            ),
            study_type=StudyTypeResponse.model_validate(
                study_info.study_type, from_attributes=True
            ),
            graduate_year=study_info.graduate_year,
            certificate_path=study_info.certificate_path,
            dtm_sheet=study_info.dtm_sheet,
        )

    async def _get_all(self, model: Type[Base], filters: dict[str, Any] = {}) -> list[Base]:
        stmt = select(model)
        if filters:
            stmt = stmt.where(and_(*[getattr(model, key) == value for key, value in filters.items()]))
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_application_by_user_id(self, user_id: int) -> StudyInfoResponse:
        return await self._get_with_join(user_id=user_id)
    
    
    async def get_study_direction_list(self) -> StudyDirectionResponse:
        return await self._get_all(StudyDirection)
    
    async def get_study_type_list(self) -> StudyTypeResponse:
        return await self._get_all(StudyType)
    
    async def get_study_form_list(self) -> StudyFormResponse:
        return await self._get_all(StudyForm)
    
    async def get_study_language_list(self) -> StudyLanguageResponse:
        return await self._get_all(StudyLanguage)
    
    async def get_education_type_list(self) -> EducationTypeResponse:
        return await self._get_all(EducationType)
    
    
    
