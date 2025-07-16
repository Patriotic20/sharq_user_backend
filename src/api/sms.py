from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from src.core.db import get_db
from src.service.sms import SMSVerificationService , SMSResetPassword
from src.service.auth import UserAuthService
from src.schemas.sms import (
    ResetPasswordRequest,
    SendVerificationCodeRequest,
    SendVerificationCodeResponse,
    RegisterWithVerificationRequest,
    RegisterWithVerificationResponse,
)
from src.utils.auth import check_phone_not_exists , check_phone_for_exists

sms_router = APIRouter(prefix="/sms", tags=["SMS Verification"])


def get_sms_service(db: AsyncSession = Depends(get_db)):
    return SMSVerificationService(db)


def get_auth_service(db: AsyncSession = Depends(get_db)):
    return UserAuthService(db)


def get_reset_password(db: AsyncSession = Depends(get_db)):
    return SMSResetPassword(db)

@sms_router.post("/send-verification", response_model=SendVerificationCodeResponse)
async def send_verification_code(
    request: Annotated[SendVerificationCodeRequest, Depends(check_phone_not_exists)],
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


@sms_router.post("/callback", include_in_schema=False)
async def sms_callback(request: Request):
    print(request.body)
    return {"message": "SMS callback received"}


@sms_router.post("/send_forgot_password_code", response_model=SendVerificationCodeResponse)
async def send_forgot_password_code(
    request: Annotated[SendVerificationCodeRequest, Depends(check_phone_for_exists)],
    service: Annotated[SMSVerificationService, Depends(get_sms_service)],
):
    result = await service.create_verification_session(request.phone_number)
    return SendVerificationCodeResponse(**result)


@sms_router.post("/reset_password")
async def reset_password(
    request: ResetPasswordRequest,
    service: Annotated[SMSResetPassword, Depends(get_reset_password)],
):
    return await service.reset_password(verification_code=request.verification_code , new_password=request.new_password)
    
