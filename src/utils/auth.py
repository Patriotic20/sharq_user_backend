import string
import random
import jwt
from datetime import timedelta, timezone, datetime
from typing import Annotated

from fastapi import HTTPException, status
from fastapi.params import Depends
from fastapi.security import (
    OAuth2PasswordBearer,
    SecurityScopes,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from pydantic import ValidationError
from jwt.exceptions import InvalidTokenError

from src.schemas.user import  TokenData
from src.models import User
from src.db.config import settings
from src.db.session import get_db


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/user/auth/login",
    scopes={
        "me": "Read information about the current user.",
        "admin": "Full administrative access to all resources.",
        "manager": "Limited access to manage specific resources.",
        "user": "User accses",
    },
)


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(db: AsyncSession, username: str, password: str):
    user_data = await get_user(db=db , username=username)
    if not user_data:
        return None
    if not verify_password(plain_password=password, hashed_password=user_data.password):
        return None
    return user_data




async def get_user(db: AsyncSession, username: str):
    stmt = select(User).where(User.phone_number == username)
    result = await db.execute(stmt)
    return result.scalars().first()




async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db),
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    try:
        payload = jwt.decode(token, settings.ACCESS_SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (InvalidTokenError, ValidationError):
        raise credentials_exception

    user = await get_user(db=db, username=token_data.username)
    if user is None:
        raise credentials_exception

    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return user


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.ACCESS_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
