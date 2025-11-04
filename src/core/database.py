from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from loguru import logger

from src.core.config import settings
from src.core.base_model import DateTimeMixin, Base


# 创建数据库引擎和会话工厂
engine = create_async_engine(settings.database_url, **settings.engine_options)

SessionFactory = async_sessionmaker(
    class_=AsyncSession, autoflush=False, expire_on_commit=False, bind=engine
)


# 数据库依赖注入
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        yield session


# 用于临时使用的创建数据库表的函数
# 注意：生产环境中不建议使用此函数，应通过迁移工具 Alembic 管理数据库
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("数据库表创建完成")
