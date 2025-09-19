"""
API middleware for CloudViz REST API.
Custom middleware for correlation IDs, rate limiting, and error handling.
"""

import uuid
import time
import json
from typing import Dict, Any
from datetime import datetime

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from cloudviz.core.utils import get_logger
from cloudviz.api.models import APIError


logger = get_logger(__name__)


# Rate limiting storage (in production, use Redis)
rate_limit_storage: Dict[str, Dict[str, Any]] = {}


async def correlation_id_middleware(request: Request, call_next):
    """Add correlation ID to requests for tracing."""
    # Check if correlation ID exists in headers, otherwise generate one
    correlation_id = request.headers.get("x-correlation-id", str(uuid.uuid4()))
    
    # Store in request state
    request.state.correlation_id = correlation_id
    
    # Process request
    response = await call_next(request)
    
    # Add correlation ID to response headers
    response.headers["x-correlation-id"] = correlation_id
    
    return response


async def rate_limiting_middleware(request: Request, call_next):
    """Rate limiting middleware."""
    # Get client identifier
    client_ip = request.client.host if request.client else "unknown"
    
    # Rate limiting configuration (in production, load from config)
    requests_per_minute = 100
    window_seconds = 60
    
    current_time = time.time()
    window_start = current_time - window_seconds
    
    # Initialize client data if not exists
    if client_ip not in rate_limit_storage:
        rate_limit_storage[client_ip] = {
            "requests": [],
            "blocked_until": 0
        }
    
    client_data = rate_limit_storage[client_ip]
    
    # Check if client is currently blocked
    if current_time < client_data["blocked_until"]:
        remaining_time = int(client_data["blocked_until"] - current_time)
        
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Rate limit exceeded",
                "detail": f"Too many requests. Try again in {remaining_time} seconds.",
                "retry_after": remaining_time
            },
            headers={"Retry-After": str(remaining_time)}
        )
    
    # Clean old requests outside the window
    client_data["requests"] = [
        req_time for req_time in client_data["requests"] 
        if req_time > window_start
    ]
    
    # Check if rate limit is exceeded
    if len(client_data["requests"]) >= requests_per_minute:
        # Block client for the remainder of the window
        client_data["blocked_until"] = window_start + window_seconds
        
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Rate limit exceeded",
                "detail": f"Maximum {requests_per_minute} requests per minute exceeded.",
                "retry_after": window_seconds
            },
            headers={"Retry-After": str(window_seconds)}
        )
    
    # Record this request
    client_data["requests"].append(current_time)
    
    # Add rate limit headers
    response = await call_next(request)
    
    remaining_requests = requests_per_minute - len(client_data["requests"])
    reset_time = int(window_start + window_seconds)
    
    response.headers["X-RateLimit-Limit"] = str(requests_per_minute)
    response.headers["X-RateLimit-Remaining"] = str(remaining_requests)
    response.headers["X-RateLimit-Reset"] = str(reset_time)
    
    return response


async def error_handling_middleware(request: Request, call_next):
    """Global error handling middleware."""
    try:
        response = await call_next(request)
        return response
        
    except HTTPException as e:
        # FastAPI HTTPExceptions are handled normally
        correlation_id = getattr(request.state, 'correlation_id', 'unknown')
        
        logger.warning("HTTP exception occurred",
                      status_code=e.status_code,
                      detail=e.detail,
                      correlation_id=correlation_id,
                      path=request.url.path,
                      method=request.method)
        
        error_response = APIError(
            error=f"HTTP {e.status_code}",
            detail=e.detail,
            correlation_id=correlation_id,
            timestamp=datetime.now()
        )
        
        return JSONResponse(
            status_code=e.status_code,
            content=error_response.dict(),
            headers=e.headers
        )
        
    except Exception as e:
        # Unexpected server errors
        correlation_id = getattr(request.state, 'correlation_id', 'unknown')
        
        logger.error("Unhandled exception occurred",
                    exc_info=True,
                    error=str(e),
                    correlation_id=correlation_id,
                    path=request.url.path,
                    method=request.method)
        
        error_response = APIError(
            error="Internal Server Error",
            detail="An unexpected error occurred. Please try again later.",
            correlation_id=correlation_id,
            timestamp=datetime.now()
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.dict()
        )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log API requests and responses."""
    
    async def dispatch(self, request: Request, call_next):
        # Log request
        start_time = time.time()
        correlation_id = getattr(request.state, 'correlation_id', 'unknown')
        
        logger.info("API request started",
                   method=request.method,
                   path=request.url.path,
                   query_params=str(request.query_params),
                   client_ip=request.client.host if request.client else "unknown",
                   correlation_id=correlation_id)
        
        # Process request
        response = await call_next(request)
        
        # Log response
        duration = time.time() - start_time
        
        logger.info("API request completed",
                   method=request.method,
                   path=request.url.path,
                   status_code=response.status_code,
                   duration_ms=round(duration * 1000, 2),
                   correlation_id=correlation_id)
        
        # Add timing header
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        
        return response
