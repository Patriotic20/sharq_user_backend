from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SendVerificationCodeRequest(BaseModel):
    phone_number: str


class SendVerificationCodeResponse(BaseModel):
    message: str
    phone_number: str
    expires_at: datetime


class VerifyCodeRequest(BaseModel):
    phone_number: str
    code: str


class VerifyCodeResponse(BaseModel):
    message: str
    verified: bool


class RegisterWithVerificationRequest(BaseModel):
    phone_number: str
    password: str
    verification_code: str
    role_id: Optional[int] = None


class RegisterWithVerificationResponse(BaseModel):
    message: str
    data: dict
    token: str
