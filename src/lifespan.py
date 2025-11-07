# app/lifespan.py
from typing import TypedDict
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from redis.asyncio import Redis
from fastapi import FastAPI
from loguru import logger

from src.auth.redis_db import create_auth_redis
from src.core.redis_db import create_cache_redis
# from src.core.database import create_db_and_tables


# 固定字典结构，键可选
class State(TypedDict, total=False):
    auth_redis: Redis
    cache_redis: Redis


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator:
    # -------- 启动 --------
    logger.info("应用启动，开始加载所有资源...")
    # await create_db_and_tables()

    auth_redis = create_auth_redis()
    cache_redis = create_cache_redis()
    logger.info("Redis 已就绪")
    
    # -------- 运行 --------
    yield State(auth_redis=auth_redis, cache_redis=cache_redis)

    # -------- 关闭 --------
    await auth_redis.close()
    await cache_redis.close()

    logger.info("应用关闭，资源已释放")

