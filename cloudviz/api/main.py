"""
CloudViz REST API Main Application
FastAPI-based REST API for cloud infrastructure visualization
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
import uvicorn

from cloudviz.core.config import CloudVizConfig
from cloudviz.core.utils import get_logger, setup_logging
from cloudviz.api.routes import (
    auth_router,
    extraction_router, 
    visualization_router,
    health_router,
    admin_router,
    aws_router,
    gcp_router
)
from cloudviz.api.middleware import (
    correlation_id_middleware,
    rate_limiting_middleware,
    error_handling_middleware
)
from cloudviz.api.dependencies import get_current_config


logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    logger.info("Starting CloudViz API server")
    
    # Initialize configuration
    config = CloudVizConfig()
    app.state.config = config
    
    # Setup logging
    setup_logging()
    
    # Initialize services
    # TODO: Add database initialization, cache setup, etc.
    
    logger.info("CloudViz API server started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CloudViz API server")
    # TODO: Add cleanup logic


def create_app(config: CloudVizConfig = None) -> FastAPI:
    """Create and configure FastAPI application."""
    
    if config is None:
        config = CloudVizConfig()
    
    app = FastAPI(
        title="CloudViz API",
        description="Multi-cloud infrastructure visualization platform REST API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )
    
    # CORS middleware
    if config.api.cors_enabled:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=config.api.cors_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=["*"],
        )
    
    # Security middleware
    if config.api.enable_https:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # Configure based on your needs
        )
    
    # Custom middleware
    app.middleware("http")(correlation_id_middleware)
    app.middleware("http")(rate_limiting_middleware)
    app.middleware("http")(error_handling_middleware)
    
    # Include routers
    app.include_router(health_router, prefix="/health", tags=["Health"])
    app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
    app.include_router(extraction_router, prefix="/api/v1", tags=["Extraction"])
    app.include_router(visualization_router, prefix="/api/v1", tags=["Visualization"])
    app.include_router(admin_router, prefix="/api/v1/admin", tags=["Administration"])
    app.include_router(aws_router, prefix="/api/v1", tags=["AWS"])
    app.include_router(gcp_router, prefix="/api/v1", tags=["GCP"])
    
    return app


# Create app instance
app = create_app()


@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "CloudViz API",
        "version": "1.0.0",
        "description": "Multi-cloud infrastructure visualization platform",
        "docs_url": "/docs",
        "health_url": "/health",
        "status": "operational"
    }


if __name__ == "__main__":
    # Development server
    config = CloudVizConfig()
    
    uvicorn.run(
        "cloudviz.api.main:app",
        host=config.api.host,
        port=config.api.port,
        reload=config.api.reload,
        workers=1 if config.api.reload else config.api.workers,
        log_level=config.api.log_level.lower()
    )
