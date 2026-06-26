from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
<<<<<<< HEAD

from app.core.config import get_settings


settings = get_settings()

engine = create_async_engine(settings.database_url, future=True, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
=======
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings
from app.core.rls import apply_rls_context

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
>>>>>>> main


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
<<<<<<< HEAD
        yield session
=======
        await apply_rls_context(session)
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
>>>>>>> main
