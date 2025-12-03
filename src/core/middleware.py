# src/core/middleware.py
from time import time, perf_counter
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    """
    处理时间中间件
    计算请求从接收开始到处理完成的时间
    并将其添加到响应头 X-Process-Time 中（单位：毫秒）
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = perf_counter()
        response = await call_next(request)
        process_time = (perf_counter() - start_time) * 1000
        response.headers["X-Process-Time"] = f"{process_time:.2f}"
        return response
