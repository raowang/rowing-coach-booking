import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

import valkey
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.config import get_settings

settings = get_settings()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

valkey_client: Optional[valkey.Valkey] = None


async def init_valkey():
    global valkey_client
    valkey_client = valkey.Valkey.from_url(settings.valkey_url, decode_responses=True)
    logger.info("Valkey connection established")


async def close_valkey():
    global valkey_client
    if valkey_client:
        valkey_client.close()
        logger.info("Valkey connection closed")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
