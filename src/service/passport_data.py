from fastapi import HTTPException, status, UploadFile
from src.service.amo import update_lead_with_passport_data
from src.service import BasicCrud
from sharq_models.models import PassportData, User, AMOCrmLead 
from src.schemas.passport_data import (
    PassportDataBase,
    PassportDataUpdate,
    PassportDataCreate,
    PersonalInfo
)
from sqlalchemy.ext.asyncio import AsyncSession
from src.utils.work_with_file import save_uploaded_file , save_base64_image
from src.core.config import settings
import httpx

class PassportDataCrud(BasicCrud[PassportData, PassportDataBase]):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def create_passport_data(
        self, passport_data_item: PassportDataBase, file: UploadFile, user_id: int
    ):
        file_path = await save_uploaded_file(file=file)

    
        login_payload = {
            "phoneNumber": settings.passport_login_username,
            "password": settings.passport_login_passport
        }
        headers = {"Content-Type": "application/json"}
        
        async with httpx.AsyncClient() as client:
            login_response = await client.post(
                settings.passport_data_login_url, json=login_payload, headers=headers
            )
            login_response.raise_for_status()

            token = login_response.json().get("data", {}).get("token")
            if not token:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid login response")

            # 4. Fetch personal info
            info_payload = {
                "serialAndNumber": passport_data_item.passport_series_number,
                "pinfl": passport_data_item.jshshir
            }

            auth_headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }

            info_response = await client.post(
                settings.passport_data_info_url, json=info_payload, headers=auth_headers
            )
            info_response.raise_for_status()

            data = info_response.json().get("data")
            if not data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User data not found"
                )
                

                
            personal_info = PersonalInfo(**data)
            
            user_photo = save_base64_image(base64_string=personal_info.photo)            
            
        
        passport_data_with_user = PassportDataCreate(
                user_id=user_id,
                passport_filepath=file_path,
                photo=user_photo,
                **personal_info.model_dump()
            )
        
        lead: AMOCrmLead = await self._get_lead(user_id)
        if not lead:
            print("Lead not found")
            pass
                
        update_lead_with_passport_data(
            contact_id=lead.contact_id,
            passport_data=passport_data_item,
            config_data=settings.amo_crm_config,
        )

        return await super().create(model=PassportData, obj_items=passport_data_with_user)
        
    async def _get_lead(self, user_id: int):
        lead = await super().get_by_field(
            model=AMOCrmLead, field_name="user_id", field_value=user_id
        )
        return lead

    async def get_passport_data_by_id(self, passport_data_id: int, user_id: int):
        passport_data_info: PassportData = await super().get_by_id(
            model=PassportData, item_id=passport_data_id
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

    async def get_all_passport_data(
        self, limit: int = 20, offset: int = 0, current_user: User | None = None
    ):
        try:
            if current_user:
                return await super().get_all(
                    model=PassportData,
                    limit=limit,
                    offset=offset,
                    filters=[PassportData.user_id == current_user.id],
                )

            return await super().get_all(
                model=PassportData,
                limit=limit,
                offset=offset,
                filters=None,  # Optional, can be omitted
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve passport data records",
            ) from e

    async def update_passport_data(
        self,
        passport_data_id: int,
        update_items: PassportDataUpdate,
        user_id: int,
    ):
        await self.get_passport_data_by_id(
            passport_data_id=passport_data_id, user_id=user_id
        )
        return await super().update(
            model=PassportData, item_id=passport_data_id, obj_items=update_items
        )

    async def delete_passport_data(self, passport_data_id: int, user_id: int):
        await self.get_passport_data_by_id(
            passport_data_id=passport_data_id, user_id=user_id
        )
        return await super().delete(model=PassportData, item_id=passport_data_id)
