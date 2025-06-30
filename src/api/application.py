from src.service.application import create_application
from fastapi import APIRouter , Security , Depends
from src.models.user import User
from src.utils.auth import get_current_user
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_db

application_router = APIRouter(
    prefix="/application"
)


@application_router.post()
async def create_app(
    db: Annotated[AsyncSession , Depends(get_db)],
    current_user: Annotated[User , Security(get_current_user , scopes=["user"])]
):
    return await create_application(db=db , user_id=current_user.id)

