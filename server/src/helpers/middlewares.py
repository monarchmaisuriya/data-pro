import time
from typing import Callable
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .logger import setup_logger

logger = setup_logger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Get client IP, handling potential proxy headers
        client_ip = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()

        # Log request
        logger.info(
            f"Incoming request | {request.method} {request.url.path} | Client IP: {client_ip}"
        )

        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            # Log response
            logger.info(
                f"Request completed | {request.method} {request.url.path} | "
                f"Status: {response.status_code} | Time: {process_time:.3f}s | "
                f"Client IP: {client_ip}"
            )
            return response

        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed | {request.method} {request.url.path} | "
                f"Error: {str(e)} | Time: {process_time:.3f}s | "
                f"Client IP: {client_ip}"
            )
            raise

