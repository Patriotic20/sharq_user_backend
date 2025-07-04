from typing import Annotated

from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import (
    OAuth2PasswordRequestForm,
)
from sqlalchemy.ext.asyncio import AsyncSession


from src.service import BasicCrud
from src.utils import ( 
    hash_password,
    authenticate_user,
    create_access_token
    )
from src.schemas.user import  Token , RegisterData
from sharq_models.models import User


class UserAuthService(BasicCrud[User, RegisterData]):
    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def register(self, user_data: RegisterData):
        hashed_password = hash_password(user_data.password)
        user_info = RegisterData(
            phone_number=user_data.phone_number,
            password=hashed_password
        )
        return await super().create(model=User, obj_items=user_info)

    async def login(
        self,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
    ) -> Token:
        user = await authenticate_user(
            db=self.db,
            username=form_data.username,
            password=form_data.password
        )
        if not user:
            raise HTTPException(status_code=400, detail="Incorrect username or password")

        access_token = create_access_token(
            data={"sub": user.phone_number, "scopes": form_data.scopes},
        )

        return Token(access_token=access_token, token_type="bearer")




