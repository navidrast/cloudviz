"""
API dependencies for CloudViz REST API.
Provides common dependency injection functions.
"""

from typing import Dict, Any, Optional
from fastapi import Depends, HTTPException, Request, status

from cloudviz.core.config import CloudVizConfig
from cloudviz.core.utils import get_logger


logger = get_logger(__name__)


def get_current_config() -> CloudVizConfig:
    """Get current CloudViz configuration."""
    try:
        # In a real implementation, you might want to cache this
        # or get it from the application state
        return CloudVizConfig()
    except Exception as e:
        logger.error("Failed to load configuration", exc_info=True, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Configuration error"
        )


def get_current_user():
    """Get current authenticated user - placeholder for auth dependency."""
    # This is imported here to avoid circular imports
    # In the actual implementation, this would be imported from auth module
    pass


def get_correlation_id(request: Request) -> str:
    """Extract correlation ID from request headers."""
    return getattr(request.state, 'correlation_id', 'unknown')


def get_client_info(request: Request) -> Dict[str, Any]:
    """Extract client information from request."""
    return {
        "ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown"),
        "correlation_id": get_correlation_id(request)
    }
