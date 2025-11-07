# src/core/redis_db.py
from typing import cast

from fastapi import Request
from redis.asyncio import Redis
from src.core.config import settings



# 应用缓存
def create_cache_redis() -> Redis:
    return Redis.from_url(
        settings.cache_redis_url,
        max_connections=20,
        decode_responses=True,
    )

async def get_cache_redis(request: Request) -> Redis:
    return cast(Redis,request.state.cache_redis)