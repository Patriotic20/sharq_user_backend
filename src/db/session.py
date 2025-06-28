from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from .config import settings

engine = create_async_engine(settings.connection_string, echo=True)


AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, autoflush=False, expire_on_commit=False
)


async def get_db():
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()
