import httpx
import random
import string
from typing import Optional
from fastapi import HTTPException , status
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_ 

from src.utils.auth import hash_password

from datetime import datetime, timedelta

from src.core.config import settings
from sharq_models.models.user import SMSVerificationSession , User #type: ignore


class SMSService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.base_url = settings.sms_base_url
        self.sender = settings.sms_sender

    def generate_verification_code(self, length: int = 4) -> str:
        return "".join(random.choices(string.digits, k=length))

    async def get_bearer_token(self) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/login",
                headers={"Content-Type": "application/json"},
                json={"email": settings.sms_sender, "password": settings.sms_api_key},
            )
            print(settings.sms_sender, settings.sms_api_key)
            print(response.json())
            if response.status_code == 200:
                return response.json().get("data").get("token")
            else:
                raise HTTPException(
                    status_code=500, detail="Bearer tokenini olib bo'lmadi"
                )

    async def send_sms(self, phone_number: str, message: str) -> bool:
        bearer_token = await self.get_bearer_token()
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/message/sms/send",
                    headers={
                        "Authorization": f"Bearer {bearer_token}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "mobile_phone": phone_number,
                        "message": message,
                        "from": self.sender,
                        "callback_url": settings.sms_callback_url,
                    },
                    timeout=30.0,
                )

                if response.status_code == 200:
                    return True
                else:
                    print(
                        f"SMS service error: {response.status_code} - {response.text}"
                    )
                    return False

        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False

    async def send_verification_code(self, phone_number: str) -> str:
        code = self.generate_verification_code()

        message = f"Sharq Universiteti. Qabuldan o'tish uchun tasdiqlash kod: {code}"
        # message = "This is test from Eskiz"

        success = await self.send_sms(phone_number, message)
        if not success:
            raise HTTPException(
                status_code=500, detail="SMS tasdiqlash kodini yuborib bo'lmadi"
            )

        return code


class SMSVerificationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.sms_service = SMSService(db)

    async def create_verification_session(self, phone_number: str) -> dict:
        existing_session = await self.get_active_session(phone_number)
        if existing_session:
            return {
                "message": "Verification code resent",
                "phone_number": phone_number,
                "expires_at": existing_session.expires_at,
            }

        code = await self.sms_service.send_verification_code(phone_number)

        session_data = {
            "phone_number": phone_number,
            "code": code,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(minutes=10),
            "verified": False,
        }

        await self.store_verification_session(session_data)

        return {
            "message": "Tasdiqlash kodi yuborildi",
            "phone_number": phone_number,
            "expires_at": session_data["expires_at"],
        }

    async def verify_code(self, phone_number: str, code: str) -> bool:
        session = await self.get_active_session(phone_number)

        if not session:
            raise HTTPException(
                status_code=400, detail="Faol tekshirish seansi topilmadi"
            )

        if session.expires_at < datetime.now():
            raise HTTPException(status_code=400, detail="Tasdiqlash kodi muddati tugadi")

        if session.code != code:
            await self.increment_attempts(phone_number)
            raise HTTPException(status_code=400, detail="Tasdiqlash kodi noto'g'ri")

        await self.mark_session_verified(phone_number)

        return True

    async def get_active_session(
        self, phone_number: str
    ) -> Optional[SMSVerificationSession]:
        stmt = (
            select(SMSVerificationSession)
            .where(
                and_(
                    SMSVerificationSession.phone_number == phone_number,
                    SMSVerificationSession.verified == sqlalchemy.false(),
                    SMSVerificationSession.expires_at > datetime.now(),
                )
            )
            .order_by(SMSVerificationSession.created_at.desc())
        )

        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def store_verification_session(self, session_data: dict):
        await self.invalidate_existing_sessions(session_data["phone_number"])

        session = SMSVerificationSession(
            phone_number=session_data["phone_number"],
            code=session_data["code"],
            created_at=session_data["created_at"],
            expires_at=session_data["expires_at"],
            verified=session_data["verified"],
        )

        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)

        return session

    async def mark_session_verified(self, phone_number: str):
        session = await self.get_active_session(phone_number)
        if session:
            session.verified = True
            await self.db.commit()

    async def invalidate_existing_sessions(self, phone_number: str):
        stmt = select(SMSVerificationSession).where(
            and_(
                SMSVerificationSession.phone_number == phone_number,
                SMSVerificationSession.verified == sqlalchemy.false(),
            )
        )

        result = await self.db.execute(stmt)
        sessions = result.scalars().all()

        for session in sessions:
            session.verified = True

        await self.db.commit()

    async def increment_attempts(self, phone_number: str):
        session = await self.get_active_session(phone_number)
        if session:
            session.attempts += 1
            await self.db.commit()



class SMSResetPassword:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.sms_service = SMSVerificationService(db)
        
    async def reset_password(self, verification_code: str, new_password: str):
        stmt = (
        select(SMSVerificationSession)
        .where(SMSVerificationSession.code == verification_code)
            )
        result = await self.db.execute(stmt)
        sms_data = result.scalars().first()
        
        check_status = await self.sms_service.verify_code(code=verification_code, phone_number=sms_data.phone_number)
        


        if not sms_data or not check_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Noto'g'ri yoki muddati o'tgan tasdiqlash kodi"
            )
        user_stmt = select(User).where(User.phone_number == sms_data.phone_number)
        user_result = await self.db.execute(user_stmt)
        user = user_result.scalars().first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Foydalanuvchi topilmadi"
            )
        user.password = hash_password(new_password)
        
        await self.db.commit()
        await self.db.refresh(user)

        return {"message": "Parol muvaffaqiyatli yangilandi"}
