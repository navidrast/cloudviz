"""
API models for CloudViz REST API.
Shared data models and enums used across API endpoints.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

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


class ExtractionRequest(BaseModel):
    """Base extraction request model."""

    regions: Optional[List[str]] = None
    resource_types: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None
    webhook_url: Optional[str] = None


class ExtractionResponse(BaseModel):
    """Base extraction response model."""

    job_id: str
    status: JobStatus
    message: str
    estimated_completion: Optional[datetime] = None
    resource_count: Optional[int] = None


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    detail: str
    status_code: int
    timestamp: datetime
