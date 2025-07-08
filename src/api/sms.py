from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from src.core.db import get_db
from src.service.sms import SMSVerificationService
from src.service.auth import UserAuthService
from src.schemas.sms import (
    SendVerificationCodeRequest,
    SendVerificationCodeResponse,
    RegisterWithVerificationRequest,
    RegisterWithVerificationResponse,
)

sms_router = APIRouter(prefix="/sms", tags=["SMS Verification"])


def get_sms_service(db: AsyncSession = Depends(get_db)):
    return SMSVerificationService(db)


def get_auth_service(db: AsyncSession = Depends(get_db)):
    return UserAuthService(db)


@sms_router.post("/send-verification", response_model=SendVerificationCodeResponse)
async def send_verification_code(
    request: SendVerificationCodeRequest,
    service: Annotated[SMSVerificationService, Depends(get_sms_service)],
):
    result = await service.create_verification_session(request.phone_number)
    return SendVerificationCodeResponse(**result)

@sms_router.post("/register", response_model=RegisterWithVerificationResponse)
async def register_with_verification(
    request: RegisterWithVerificationRequest,
    auth_service: Annotated[UserAuthService, Depends(get_auth_service)],
):
    result = await auth_service.register_with_verification(request)
    return RegisterWithVerificationResponse(**result)
