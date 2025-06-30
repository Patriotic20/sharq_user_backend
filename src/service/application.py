from sqlalchemy import select , update , delete
from src.models import Application
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.application import ApplicationStatus , Application


async def create_application(db: AsyncSession, user_id: int | None = None):
    new_app = Application(user_id=user_id)
    db.add(new_app)
    await db.commit()
    await db.refresh(new_app)
    return new_app


async def get_by_id_application(db: AsyncSession, application_id: int, user_id: int | None = None):
    stmt = select(Application).where(
        Application.id == application_id,
        Application.user_id == user_id if user_id is not None else True  # Optional user filtering
    )
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_all_application(db: AsyncSession, user_id: int | None = None):
    stmt = select(Application)
    if user_id is not None:
        stmt = stmt.where(Application.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalars().all()


async def update_application(
    db: AsyncSession,
    application_status: ApplicationStatus,
    application_id: int,
    user_id: int | None = None
):
    stmt = (
        update(Application)
        .where(Application.id == application_id)
        .values(status=application_status)
        .execution_options(synchronize_session="fetch")
    )

    if user_id is not None:
        stmt = stmt.where(Application.user_id == user_id)

    await db.execute(stmt)
    await db.commit()

async def delete_application(db: AsyncSession, application_id: int, user_id: int | None = None):
    stmt = delete(Application).where(Application.id == application_id)
    if user_id is not None:
        stmt = stmt.where(Application.user_id == user_id)

    await db.execute(stmt)
    await db.commit()
