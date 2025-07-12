from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload

from src.schemas.amo import AMOCrmLead
from src.service.amo import DealData, update_lead_with_full_data
from src.service import BasicCrud
from sharq_models.models import (
    Application,
    PassportData,
    StudyInfo,
    StudyDirection,
    StudyLanguage,
    StudyForm,
)
from src.schemas.application import (
    ApplicationBase,
    ApplicationResponse,
    ApplicationFilter,
)


class ApplicationCrud(BasicCrud[Application, ApplicationBase]):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def application_creation(self, user_id: int) -> ApplicationResponse:
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

        # Check for existing application
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

        # Create new application
        application_data = ApplicationBase(
            passport_data_id=passport_data.id, study_info_id=study_info.id
        )

        application = await super().create(
            model=Application, obj_items=application_data
        )

        # Re-fetch with relationships
        stmt = (
            select(Application)
            .options(
                joinedload(Application.study_info).joinedload(StudyInfo.study_language),
                joinedload(Application.study_info).joinedload(StudyInfo.study_form),
                joinedload(Application.study_info).joinedload(
                    StudyInfo.study_direction
                ),
                joinedload(Application.passport_data),
            )
            .where(Application.id == application.id)
        )
        result = await self.db.execute(stmt)
        application_with_joins = result.scalar_one()

        lead: AMOCrmLead = await self._get_lead(user_id)
        if not lead:
            print("Lead not found")
            pass

        update_lead_with_full_data(
            deal_id=lead.lead_id,
            deal_data=DealData(
                contact_id=lead.contact_id,
                name=f"{passport_data.first_name} {passport_data.last_name} {passport_data.third_name}",
                edu_lang_id=str(application_with_joins.study_info.study_language.name),
                edu_type=str(application_with_joins.study_info.study_form.name),
                edu_form=str(application_with_joins.study_info.study_form.name),
                edu_direction=str(
                    application_with_joins.study_info.study_direction.name
                ),
                edu_end_date=str(
                    application_with_joins.study_info.study_direction.education_years
                ),
                admission_id=0,
                certificate_link="",
                passport_file_link="",
            ),
        )

        return ApplicationResponse.model_validate(application_with_joins)

    async def get_application_with_nested_info(
        self, application_id: int, user_id: int | None = None
    ):
        stmt = (
            select(Application)
            .options(
                joinedload(Application.passport_data),
                joinedload(Application.study_info).joinedload(StudyInfo.study_form),
                joinedload(Application.study_info).joinedload(StudyInfo.study_language),
                joinedload(Application.study_info).joinedload(
                    StudyInfo.study_direction
                ),
            )
            .where(Application.id == application_id)
        )

        # Ownership filter
        if user_id is not None:
            stmt = stmt.where(
                Application.passport_data.has(PassportData.user_id == user_id),
                Application.study_info.has(StudyInfo.user_id == user_id),
            )

        result = await self.db.execute(stmt)
        application = result.scalars().first()

        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
            )

        return ApplicationResponse.model_validate(application)

    async def get_all_application_with_nested_info(
        self, filter_data: ApplicationFilter, limit: int = 10, offset: int = 0
    ):
        stmt = select(Application).options(
            joinedload(Application.passport_data),
            joinedload(Application.study_info).joinedload(StudyInfo.study_form),
            joinedload(Application.study_info).joinedload(StudyInfo.study_language),
            joinedload(Application.study_info).joinedload(StudyInfo.study_direction),
        )

        filters = []

        # PassportData filters
        if filter_data.passport_series_number:
            filters.append(
                Application.passport_data.has(
                    PassportData.passport_series_number
                    == filter_data.passport_series_number
                )
            )
        if filter_data.issue_date:
            filters.append(
                Application.passport_data.has(
                    PassportData.issue_date == filter_data.issue_date
                )
            )
        if filter_data.issuing_authority:
            filters.append(
                Application.passport_data.has(
                    PassportData.issuing_authority == filter_data.issuing_authority
                )
            )
        if filter_data.authority_code:
            filters.append(
                Application.passport_data.has(
                    PassportData.authority_code == filter_data.authority_code
                )
            )
        if filter_data.place_of_birth:
            filters.append(
                Application.passport_data.has(
                    PassportData.place_of_birth == filter_data.place_of_birth
                )
            )
        if filter_data.date_of_birth:
            filters.append(
                Application.passport_data.has(
                    PassportData.date_of_birth == filter_data.date_of_birth
                )
            )
        if filter_data.gender:
            filters.append(
                Application.passport_data.has(PassportData.gender == filter_data.gender)
            )
        if filter_data.nationality:
            filters.append(
                Application.passport_data.has(
                    PassportData.nationality == filter_data.nationality
                )
            )

        # StudyInfo filters
        if filter_data.study_direction_name:
            filters.append(
                Application.study_info.has(
                    StudyInfo.study_direction.has(
                        StudyDirection.name == filter_data.study_direction_name
                    )
                )
            )
        if filter_data.study_form_name:
            filters.append(
                Application.study_info.has(
                    StudyInfo.study_form.has(
                        StudyForm.name == filter_data.study_form_name
                    )
                )
            )
        if filter_data.study_language_name:
            filters.append(
                Application.study_info.has(
                    StudyInfo.study_language.has(
                        StudyLanguage.name == filter_data.study_language_name
                    )
                )
            )

        if filters:
            stmt = stmt.where(and_(*filters))

        stmt = stmt.limit(limit).offset(offset)

        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def delete_application(self, application_id: int, user_id: int | None = None):
        stmt = select(Application).where(Application.id == application_id)

        if user_id is not None:
            stmt = stmt.where(
                Application.passport_data.has(PassportData.user_id == user_id)
            )

        result = await self.db.execute(stmt)
        application = result.scalars().first()

        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ariza topilmadi yoki sizga tegishli emas",
            )

        await self.db.delete(application)
        await self.db.commit()
        return {"detail": "Ariza muvaffaqiyatli o'chirildi"}
