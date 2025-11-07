# src/auth/redis_db.py
from typing import cast

from fastapi import Request
from redis.asyncio import Redis
from src.core.config import settings


# 验证缓存
def create_auth_redis() -> Redis:
    return Redis.from_url(
        settings.auth_redis_url,
        max_connections=20,
        decode_responses=True,
    )

async def get_auth_redis(request: Request) -> Redis:
    return cast(Redis, request.state.auth_redis) # cast 强制类型转换，避免类型检查错误