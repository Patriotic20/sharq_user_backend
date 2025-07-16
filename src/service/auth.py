from typing import Annotated

from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import (
    OAuth2PasswordRequestForm,
)
from sqlalchemy.ext.asyncio import AsyncSession


from src.service.amo import create_initial_lead
from src.schemas.sms import RegisterWithVerificationRequest
from src.service.sms import SMSVerificationService
from src.service import BasicCrud
from src.utils import hash_password, authenticate_user, create_access_token
from src.schemas.user import Token, RegisterData
from sharq_models.models import User, AMOCrmLead # type: ignore
from src.schemas.amo import AMOCrmLead as AMOCrmLeadSchema
from src.service.role import RoleService
from src.core.config import settings


class UserAuthService(BasicCrud[User, RegisterData]):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def register_with_verification(
        self, user_data: RegisterWithVerificationRequest
    ):
        sms_service = SMSVerificationService(self.db)
        await sms_service.verify_code(
            user_data.phone_number, user_data.verification_code
        )

        if await self.get_by_field(
            model=User, field_name="phone_number", field_value=user_data.phone_number
        ):
            raise HTTPException(status_code=400, detail="User already exists")

        role_service = RoleService(self.db)
        if user_data.role_id:
            await role_service.get_role_by_id(user_data.role_id)
        else:
            default_role = await role_service.get_default_role()
            user_data.role_id = default_role.id

        user_info = RegisterData(
            phone_number=user_data.phone_number,
            password=hash_password(user_data.password),
            role_id=user_data.role_id,
        )
        result = await super().create(model=User, obj_items=user_info)

        access_token = create_access_token(
            data={"sub": result.phone_number, "role_id": result.role_id},
        )
        await self.handle_initial_lead(result.id, user_data.phone_number)

        return dict(
            message="User registered successfully",
            data={
                "user_id": result.id,
                "phone_number": result.phone_number,
                "role_id": result.role_id,
            },
            access_token=access_token,
        )

    async def handle_initial_lead(self, user_id: int, phone_number: str):
        lead = await self.get_by_field(
            model=AMOCrmLead, field_name="user_id", field_value=user_id
        )
        if not lead:
            initial_lead = create_initial_lead(phone_number, settings.amo_crm_config)
            await self.create(
                model=AMOCrmLead,
                obj_items=AMOCrmLeadSchema(
                    user_id=user_id,
                    contact_id=initial_lead.get("contact_id"),
                    lead_id=initial_lead.get("deal_id"),
                    phone_number=phone_number,
                    contact_data={},
                    lead_data={},
                ),
            )

    async def login(
        self, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
    ) -> Token:
        user = await authenticate_user(
            db=self.db, username=form_data.username, password=form_data.password
        )
        if not user:
            raise HTTPException(
                status_code=400, detail="Incorrect username or password"
            )

        access_token = create_access_token(
            data={"sub": user.phone_number, "role_id": user.role_id},
        )

        return Token(access_token=access_token, token_type="bearer")
