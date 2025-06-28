from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config.config import setting

DB_URL = setting.db.dsn


asyncio_engine = create_async_engine(
    DB_URL,
    # echo=settings.debug
)

AsyncSessionFactory = async_sessionmaker(
    asyncio_engine,
    autocommit=False,
    expire_on_commit=False,
    future=True,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


# async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
#     async with AsyncSessionFactory() as session:
#         try:
#             yield session
#             await session.commit()
#         except Exception as e:
#             await session.rollback()
#             raise e
#         finally:
#             await session.close()
#

