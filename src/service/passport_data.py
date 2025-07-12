from fastapi import HTTPException, status, UploadFile
from src.service.amo import update_lead_with_passport_data
from src.service import BasicCrud
from sharq_models.models import PassportData, User, AMOCrmLead
from src.schemas.passport_data import (
    PassportDataBase,
    PassportDataCreate,
    PersonalInfo,
    PassportDataResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.config import settings
from src.clients.passport_data import PassportDataClient
from src.utils.work_with_file import save_base64_image


class PassportDataCrud(BasicCrud[PassportData, PassportDataBase]):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def create_passport_data(
        self,
        passport_data_item: PassportDataBase,
        user_id: int,
    ):
        passport_data_client = PassportDataClient()

        passport_data_response = await passport_data_client.get_passport_data(
            passport_series_number=passport_data_item.passport_series_number,
            jshshir=passport_data_item.jshshir,
        )

        data = passport_data_response.json().get("data")
        base_64_image = data.get("photo")
        if base_64_image:
            image_path = save_base64_image(base_64_image)
            data["image_path"] = image_path
        
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Passport data not found"
            )

        passport_data_with_user = PassportDataCreate(
            user_id=user_id, **PersonalInfo(**data).model_dump(by_alias=True)
        )

        lead: AMOCrmLead = await self._get_lead(user_id)
        if not lead:
            print("Lead not found")
            pass
        else:
            update_lead_with_passport_data(
                contact_id=lead.contact_id,
                passport_data=passport_data_with_user,
                config_data=settings.amo_crm_config,
            )

        return await super().create(
            model=PassportData, obj_items=passport_data_with_user
        )
        

    async def _get_lead(self, user_id: int):
        lead = await super().get_by_field(
            model=AMOCrmLead, field_name="user_id", field_value=user_id
        )
        return lead

    async def get_passport_data_by_user_id(self, user_id: int):
        passport_data_info: PassportData = await super().get_by_field(
            model=PassportData, field_name="user_id", field_value=user_id
        )

        if not passport_data_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Passport data not found"
            )
        if passport_data_info.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authorized to access this resource",
            )

        return passport_data_info
