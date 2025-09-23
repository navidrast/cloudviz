"""
Administrative endpoints for CloudViz API.
Handles system administration, monitoring, and management operations.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from cloudviz.api.dependencies import get_current_config, get_current_user
from cloudviz.core.config import CloudVizConfig
from cloudviz.core.utils import get_logger

logger = get_logger(__name__)
router = APIRouter()


class SystemMetrics(BaseModel):
    """System metrics response model."""

    uptime_seconds: float
    active_jobs: int
    completed_jobs: int
    failed_jobs: int
    total_users: int
    api_requests_24h: int
    memory_usage_mb: float
    disk_usage_percent: float


class UserManagementRequest(BaseModel):
    """User management request model."""

    username: str
    email: Optional[str] = None
    roles: List[str] = []
    permissions: List[str] = []
    enabled: bool = True


class ConfigurationUpdate(BaseModel):
    """Configuration update request model."""

    section: str
    key: str
    value: Any


def require_admin_permission():
    """Dependency to check admin permissions."""

    def check_admin(current_user: Dict[str, Any] = Depends(get_current_user)):
        if "admin" not in current_user.get("roles", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Administrator role required",
            )
        return current_user

    return check_admin


# Track startup time for metrics
startup_time = datetime.now()


@router.get("/metrics", response_model=SystemMetrics)
async def get_system_metrics(
    current_user: Dict[str, Any] = Depends(require_admin_permission()),
    config: CloudVizConfig = Depends(get_current_config),
):
    """
    Get system metrics and performance data.
    """
    try:
        # Import job stores from other modules
        from cloudviz.api.routes.extraction import extraction_jobs
        from cloudviz.api.routes.visualization import render_jobs

        # Calculate uptime
        uptime = (datetime.now() - startup_time).total_seconds()

        # Count jobs by status
        all_jobs = list(extraction_jobs.values()) + list(render_jobs.values())
        active_jobs = len(
            [job for job in all_jobs if job["status"] in ["pending", "running"]]
        )
        completed_jobs = len([job for job in all_jobs if job["status"] == "completed"])
        failed_jobs = len([job for job in all_jobs if job["status"] == "failed"])

        # Mock metrics (in production, integrate with actual monitoring)
        metrics = SystemMetrics(
            uptime_seconds=uptime,
            active_jobs=active_jobs,
            completed_jobs=completed_jobs,
            failed_jobs=failed_jobs,
            total_users=3,  # Mock data
            api_requests_24h=150,  # Mock data
            memory_usage_mb=256.5,  # Mock data
            disk_usage_percent=45.2,  # Mock data
        )

        logger.info(
            "System metrics retrieved",
            uptime=uptime,
            active_jobs=active_jobs,
            user=current_user["username"],
        )

        return metrics

    except Exception as e:
        logger.error("Failed to get system metrics: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system metrics",
        )


@router.get("/jobs/cleanup")
async def cleanup_old_jobs(
    days: int = 7, current_user: Dict[str, Any] = Depends(require_admin_permission())
):
    """
    Clean up old completed/failed jobs.
    """
    try:
        # Import job stores
        from cloudviz.api.routes.extraction import extraction_jobs
        from cloudviz.api.routes.visualization import render_jobs

        cutoff_date = datetime.now() - timedelta(days=days)

        # Clean extraction jobs
        extraction_cleaned = 0
        for job_id in list(extraction_jobs.keys()):
            job = extraction_jobs[job_id]
            if (
                job.get("completed_at")
                and job["completed_at"] < cutoff_date
                and job["status"] in ["completed", "failed"]
            ):
                del extraction_jobs[job_id]
                extraction_cleaned += 1

        # Clean render jobs
        render_cleaned = 0
        for job_id in list(render_jobs.keys()):
            job = render_jobs[job_id]
            if (
                job.get("completed_at")
                and job["completed_at"] < cutoff_date
                and job["status"] in ["completed", "failed"]
            ):
                del render_jobs[job_id]
                render_cleaned += 1

        total_cleaned = extraction_cleaned + render_cleaned

        logger.info(
            "Job cleanup completed",
            extraction_cleaned=extraction_cleaned,
            render_cleaned=render_cleaned,
            total_cleaned=total_cleaned,
            days=days,
            user=current_user["username"],
        )

        return {
            "message": f"Cleaned up {total_cleaned} old jobs",
            "extraction_jobs_cleaned": extraction_cleaned,
            "render_jobs_cleaned": render_cleaned,
            "cutoff_date": cutoff_date.isoformat(),
        }

    except Exception as e:
        logger.error("Job cleanup failed: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Job cleanup failed",
        )


@router.get("/users")
async def list_users(
    current_user: Dict[str, Any] = Depends(require_admin_permission()),
):
    """
    List all users (mock implementation).
    """
    # In production, this would query the actual user database
    from cloudviz.api.routes.auth import MOCK_USERS

    users = []
    for username, user_data in MOCK_USERS.items():
        users.append(
            {
                "username": user_data["username"],
                "email": user_data["email"],
                "roles": user_data["roles"],
                "permissions": user_data["permissions"],
                "last_login": user_data.get("last_login"),
                "enabled": True,
            }
        )

    return users


@router.post("/users")
async def create_user(
    request: UserManagementRequest,
    current_user: Dict[str, Any] = Depends(require_admin_permission()),
):
    """
    Create new user (mock implementation).
    """
    # In production, this would create a user in the actual database
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User creation not implemented in mock version",
    )


@router.put("/users/{username}")
async def update_user(
    username: str,
    request: UserManagementRequest,
    current_user: Dict[str, Any] = Depends(require_admin_permission()),
):
    """
    Update existing user (mock implementation).
    """
    # In production, this would update the user in the actual database
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User updates not implemented in mock version",
    )


@router.delete("/users/{username}")
async def delete_user(
    username: str, current_user: Dict[str, Any] = Depends(require_admin_permission())
):
    """
    Delete user (mock implementation).
    """
    # In production, this would delete the user from the actual database
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User deletion not implemented in mock version",
    )


@router.get("/config")
async def get_configuration(
    current_user: Dict[str, Any] = Depends(require_admin_permission()),
    config: CloudVizConfig = Depends(get_current_config),
):
    """
    Get current system configuration.
    """
    # Return sanitized configuration (without sensitive data)
    config_data = {
        "api": {
            "host": config.api.host,
            "port": config.api.port,
            "workers": config.api.workers,
            "cors_enabled": config.api.cors_enabled,
            "cors_origins": config.api.cors_origins,
            "rate_limit_requests": config.api.rate_limit_requests,
            "rate_limit_window": config.api.rate_limit_window,
        },
        "logging": {
            "level": config.logging.level,
            "format": config.logging.format,
            "file": config.logging.file,
        },
        "cache": {
            "enabled": config.cache.enabled,
            "backend": config.cache.backend,
            "ttl": config.cache.ttl,
        },
        "visualization": {
            "cache_enabled": config.visualization.cache_enabled,
            "cache_ttl": config.visualization.cache_ttl,
            "output_dir": config.visualization.output_dir,
        },
    }

    return config_data


@router.put("/config")
async def update_configuration(
    request: ConfigurationUpdate,
    current_user: Dict[str, Any] = Depends(require_admin_permission()),
):
    """
    Update system configuration (limited implementation).
    """
    # In production, this would update the actual configuration
    # and might require service restart for some changes

    logger.info(
        "Configuration update requested",
        section=request.section,
        key=request.key,
        user=current_user["username"],
    )

    return {
        "message": "Configuration update queued",
        "section": request.section,
        "key": request.key,
        "note": "Some changes may require service restart",
    }


@router.post("/maintenance/restart")
async def restart_service(
    current_user: Dict[str, Any] = Depends(require_admin_permission()),
):
    """
    Restart the CloudViz service (mock implementation).
    """
    logger.warning("Service restart requested", user=current_user["username"])

    return {
        "message": "Service restart initiated",
        "note": "This is a mock implementation. In production, this would trigger a graceful restart.",
    }


@router.get("/logs")
async def get_recent_logs(
    lines: int = 100,
    level: str = "INFO",
    current_user: Dict[str, Any] = Depends(require_admin_permission()),
):
    """
    Get recent application logs (mock implementation).
    """
    # In production, this would read from actual log files

    mock_logs = [
        {
            "timestamp": datetime.now().isoformat(),
            "level": "INFO",
            "logger": "cloudviz.api.main",
            "message": "API server started",
            "correlation_id": "N/A",
        },
        {
            "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(),
            "level": "INFO",
            "logger": "cloudviz.api.routes.extraction",
            "message": "Extraction job completed",
            "correlation_id": "abc123",
        },
    ]

    return {
        "logs": mock_logs[:lines],
        "total_lines": len(mock_logs),
        "level_filter": level,
    }
