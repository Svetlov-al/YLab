from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

SQLALCHEMY_DATABASE_URL = (f'postgresql+asyncpg://{settings.database_username}:{settings.database_password}@'
                           f'{settings.database_hostname}:{settings.database_port}/{settings.database_name}')

async_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
    future=True,
)

SQLALCHEMY_SYNC_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace('postgresql+asyncpg', 'postgresql')
sync_engine = create_engine(SQLALCHEMY_SYNC_DATABASE_URL)

# Используйте sessionmaker с асинхронным движком
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autoflush=False,
    future=True,
)

metadata = MetaData()
Base = declarative_base(metadata=metadata)


# async def get_db() -> AsyncIterator[AsyncSession]:
#     db = AsyncSessionLocal()
#     try:
#         yield db
#     finally:
#         await db.close()

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
