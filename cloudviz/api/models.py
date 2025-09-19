"""
API models for CloudViz REST API.
Shared data models and enums used across API endpoints.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Job execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobResponse(BaseModel):
    """Generic job response model."""
    id: str
    status: JobStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class APIError(BaseModel):
    """API error response model."""
    error: str
    detail: str
    correlation_id: str
    timestamp: datetime


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


class WebhookConfig(BaseModel):
    """Webhook configuration model."""
    url: str
    events: List[str]
    secret: Optional[str] = None
    enabled: bool = True
    headers: Optional[Dict[str, str]] = None


class RateLimitInfo(BaseModel):
    """Rate limit information model."""
    requests_remaining: int
    reset_time: datetime
    window_seconds: int
