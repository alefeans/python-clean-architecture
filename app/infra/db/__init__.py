from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import get_settings

DBSession = AsyncSession
engine = create_async_engine(get_settings().DB_URL)
async_session = async_sessionmaker(engine, class_=DBSession, expire_on_commit=False)
