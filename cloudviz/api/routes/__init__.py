# API Routes package

from cloudviz.api.routes.health import router as health_router
from cloudviz.api.routes.auth import router as auth_router
from cloudviz.api.routes.extraction import router as extraction_router
from cloudviz.api.routes.visualization import router as visualization_router
from cloudviz.api.routes.admin import router as admin_router
from cloudviz.api.routes.aws import router as aws_router
from cloudviz.api.routes.gcp import router as gcp_router

__all__ = [
    "health_router",
    "auth_router", 
    "extraction_router",
    "visualization_router",
    "admin_router",
    "aws_router",
    "gcp_router"
]
