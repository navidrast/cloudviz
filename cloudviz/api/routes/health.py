"""
Health check endpoints for CloudViz API.
Provides system health monitoring and readiness checks.
"""

from typing import Dict, Any
from datetime import datetime
import asyncio

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from cloudviz.core.config import CloudVizConfig
from cloudviz.core.utils import get_logger
from cloudviz.api.dependencies import get_current_config


logger = get_logger(__name__)
router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime
    version: str
    uptime_seconds: float
    checks: Dict[str, Any]


class ReadinessResponse(BaseModel):
    """Readiness check response model."""
    ready: bool
    services: Dict[str, str]
    timestamp: datetime


# Track startup time for uptime calculation
startup_time = datetime.now()


@router.get("/", response_model=HealthResponse)
async def health_check(config: CloudVizConfig = Depends(get_current_config)):
    """
    Basic health check endpoint.
    Returns overall system health status.
    """
    try:
        uptime = (datetime.now() - startup_time).total_seconds()
        
        # Perform basic health checks
        checks = {
            "api": "healthy",
            "config": "healthy" if config else "unhealthy",
            "memory": "healthy",  # Could add actual memory checks
            "disk": "healthy"     # Could add actual disk checks
        }
        
        # Determine overall status
        status = "healthy" if all(check == "healthy" for check in checks.values()) else "degraded"
        
        response = HealthResponse(
            status=status,
            timestamp=datetime.now(),
            version="1.0.0",
            uptime_seconds=uptime,
            checks=checks
        )
        
        logger.debug("Health check completed", status=status, uptime=uptime)
        return response
        
    except Exception as e:
        logger.error("Health check failed: %s", str(e), exc_info=True)
        raise HTTPException(status_code=503, detail="Health check failed")


@router.get("/ready", response_model=ReadinessResponse)
async def readiness_check(config: CloudVizConfig = Depends(get_current_config)):
    """
    Readiness check endpoint.
    Verifies that all required services are available.
    """
    try:
        services = {}
        
        # Check core services
        services["config"] = "ready" if config else "not_ready"
        services["logging"] = "ready"
        
        # Check optional services
        try:
            # Could add database connectivity check
            services["database"] = "ready"
        except Exception:
            services["database"] = "not_ready"
        
        try:
            # Could add cache connectivity check  
            services["cache"] = "ready" if not config.cache.enabled else "not_ready"
        except Exception:
            services["cache"] = "not_ready"
        
        # Determine overall readiness
        critical_services = ["config", "logging"]
        ready = all(services.get(svc) == "ready" for svc in critical_services)
        
        response = ReadinessResponse(
            ready=ready,
            services=services,
            timestamp=datetime.now()
        )
        
        logger.debug("Readiness check completed", ready=ready, services=services)
        
        if not ready:
            raise HTTPException(status_code=503, detail="Service not ready")
            
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Readiness check failed: %s", str(e), exc_info=True)
        raise HTTPException(status_code=503, detail="Readiness check failed")


@router.get("/live")
async def liveness_check():
    """
    Liveness check endpoint.
    Simple endpoint to verify the service is running.
    """
    return {"status": "alive", "timestamp": datetime.now()}


@router.get("/startup")
async def startup_check():
    """
    Startup check endpoint.
    Indicates if the service has completed startup procedures.
    """
    # Simple startup check - could be enhanced with actual startup tasks
    uptime = (datetime.now() - startup_time).total_seconds()
    
    # Consider startup complete after 10 seconds
    startup_complete = uptime > 10
    
    return {
        "status": "started" if startup_complete else "starting",
        "uptime_seconds": uptime,
        "timestamp": datetime.now()
    }
