from typing import AsyncIterator

from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.config import settings

SQLALCHEMY_DATABASE_URL = (f'postgresql+asyncpg://{settings.database_username}:{settings.database_password}@'
                           f'{settings.database_hostname}:{settings.database_port}/{settings.database_name}')

async_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=0,
    future=True,
)

SQLALCHEMY_SYNC_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace('postgresql+asyncpg', 'postgresql')
sync_engine = create_engine(SQLALCHEMY_SYNC_DATABASE_URL)

async_session = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    future=True,
)

metadata = MetaData()
Base = declarative_base(metadata=metadata)


async def get_db() -> AsyncIterator[AsyncSession]:
    db = async_session()
    try:
        yield db
    finally:
        await db.close()
