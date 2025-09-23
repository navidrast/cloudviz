"""
Diagram visualization endpoints for CloudViz API.
Handles diagram generation and rendering operations.
"""

import asyncio
import base64
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field

from cloudviz.api.dependencies import get_current_config, get_current_user
from cloudviz.api.models import JobResponse, JobStatus
from cloudviz.core.config import CloudVizConfig
from cloudviz.core.models import ResourceInventory
from cloudviz.core.utils import get_logger
from cloudviz.visualization.engines import GraphvizEngine, ImageEngine, MermaidEngine

logger = get_logger(__name__)
router = APIRouter()


class OutputFormat(str, Enum):
    """Supported output formats."""

    MERMAID = "mermaid"
    GRAPHVIZ = "graphviz"
    DOT = "dot"
    PNG = "png"
    SVG = "svg"
    PDF = "pdf"
    JPG = "jpg"
    JPEG = "jpeg"


class ThemeName(str, Enum):
    """Available themes."""

    PROFESSIONAL = "professional"
    DARK = "dark"
    LIGHT = "light"
    MINIMAL = "minimal"
    COLORFUL = "colorful"


class LayoutAlgorithm(str, Enum):
    """Available layout algorithms."""

    HIERARCHICAL = "hierarchical"
    FLOWCHART = "flowchart"
    CIRCULAR = "circular"
    FORCE = "force"
    GRID = "grid"
    RADIAL = "radial"
    GRAPH = "graph"
    MINDMAP = "mindmap"
    TIMELINE = "timeline"


class RenderRequest(BaseModel):
    """Diagram rendering request model."""

    inventory: Dict[str, Any] = Field(..., description="Resource inventory data")
    format: OutputFormat = Field(
        default=OutputFormat.MERMAID, description="Output format"
    )
    theme: ThemeName = Field(default=ThemeName.PROFESSIONAL, description="Visual theme")
    layout: LayoutAlgorithm = Field(
        default=LayoutAlgorithm.HIERARCHICAL, description="Layout algorithm"
    )
    options: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional rendering options"
    )

    # Image-specific options
    width: Optional[int] = Field(default=None, description="Image width in pixels")
    height: Optional[int] = Field(default=None, description="Image height in pixels")
    dpi: Optional[int] = Field(default=300, description="Image DPI for raster formats")
    background_color: Optional[str] = Field(
        default="white", description="Background color"
    )


class RenderResponse(BaseModel):
    """Diagram rendering response model."""

    job_id: str
    status: JobStatus
    message: str
    format: OutputFormat
    estimated_duration_seconds: Optional[int] = None
    result_url: Optional[str] = None


class DiagramResponse(BaseModel):
    """Diagram content response model."""

    content: str = Field(
        ..., description="Diagram content (base64 encoded for binary formats)"
    )
    format: OutputFormat
    encoding: str = Field(..., description="Content encoding (utf-8 or base64)")
    metadata: Dict[str, Any]


class CompareRequest(BaseModel):
    """Infrastructure comparison request model."""

    before_inventory: Dict[str, Any] = Field(..., description="Before state inventory")
    after_inventory: Dict[str, Any] = Field(..., description="After state inventory")
    format: OutputFormat = Field(
        default=OutputFormat.MERMAID, description="Output format"
    )
    theme: ThemeName = Field(default=ThemeName.PROFESSIONAL, description="Visual theme")
    highlight_changes: bool = Field(default=True, description="Highlight differences")


# In-memory job storage for rendering jobs
render_jobs: Dict[str, Dict[str, Any]] = {}


def require_permission(permission: str):
    """Dependency to check user permissions."""

    def check_permission(current_user: Dict[str, Any] = Depends(get_current_user)):
        if permission not in current_user.get("permissions", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required",
            )
        return current_user

    return check_permission


async def perform_rendering(job_id: str, request: RenderRequest) -> None:
    """Background task to perform diagram rendering."""
    try:
        # Update job status
        render_jobs[job_id]["status"] = JobStatus.RUNNING
        render_jobs[job_id]["started_at"] = datetime.now()

        logger.info(
            "Starting diagram rendering",
            job_id=job_id,
            format=request.format.value,
            theme=request.theme.value,
            layout=request.layout.value,
        )

        # Parse inventory
        inventory = ResourceInventory.from_dict(request.inventory)

        # Choose appropriate engine based on format
        if request.format in [OutputFormat.MERMAID]:
            engine = MermaidEngine(request.options)
            result = await engine.render(
                inventory,
                output_format=request.format.value,
                theme=request.theme.value,
                layout=request.layout.value,
                **request.options,
            )
            encoding = "utf-8"

        elif request.format in [OutputFormat.GRAPHVIZ, OutputFormat.DOT]:
            engine = GraphvizEngine(request.options)
            result = await engine.render(
                inventory,
                output_format=request.format.value,
                theme=request.theme.value,
                layout=request.layout.value,
                **request.options,
            )
            encoding = "utf-8"

        elif request.format in [
            OutputFormat.PNG,
            OutputFormat.SVG,
            OutputFormat.PDF,
            OutputFormat.JPG,
            OutputFormat.JPEG,
        ]:
            engine = ImageEngine(
                {
                    **request.options,
                    "width": request.width,
                    "height": request.height,
                    "dpi": request.dpi,
                    "background_color": request.background_color,
                }
            )
            result = await engine.render(
                inventory,
                output_format=request.format.value,
                theme=request.theme.value,
                layout=request.layout.value,
                **request.options,
            )
            encoding = "base64"

        else:
            raise ValueError(f"Unsupported format: {request.format}")

        # Encode result appropriately
        if encoding == "base64":
            content = base64.b64encode(result).decode("utf-8")
        else:
            content = result.decode("utf-8") if isinstance(result, bytes) else result

        # Store results
        render_jobs[job_id]["status"] = JobStatus.COMPLETED
        render_jobs[job_id]["completed_at"] = datetime.now()
        render_jobs[job_id]["result"] = {
            "content": content,
            "format": request.format.value,
            "encoding": encoding,
            "metadata": {
                "theme": request.theme.value,
                "layout": request.layout.value,
                "resource_count": len(inventory.resources),
                "relationship_count": len(inventory.relationships),
                "size_bytes": (
                    len(result)
                    if isinstance(result, bytes)
                    else len(result.encode("utf-8"))
                ),
            },
        }

        logger.info(
            "Diagram rendering completed",
            job_id=job_id,
            format=request.format.value,
            size_bytes=render_jobs[job_id]["result"]["metadata"]["size_bytes"],
        )

    except Exception as e:
        logger.error(
            "Diagram rendering failed", job_id=job_id, exc_info=True, error=str(e)
        )

        render_jobs[job_id]["status"] = JobStatus.FAILED
        render_jobs[job_id]["error"] = str(e)
        render_jobs[job_id]["completed_at"] = datetime.now()


@router.post("/render", response_model=RenderResponse)
async def render_diagram(
    request: RenderRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(require_permission("render")),
    config: CloudVizConfig = Depends(get_current_config),
):
    """
    Render infrastructure diagram from inventory data.

    This endpoint creates a diagram rendering job and returns immediately.
    Use the job_id to check rendering status and retrieve results.
    """
    try:
        # Generate job ID
        job_id = str(uuid.uuid4())

        # Initialize job record
        render_jobs[job_id] = {
            "id": job_id,
            "status": JobStatus.PENDING,
            "request": request.dict(),
            "user": current_user["username"],
            "created_at": datetime.now(),
            "started_at": None,
            "completed_at": None,
            "result": None,
            "error": None,
        }

        # Start background rendering
        background_tasks.add_task(perform_rendering, job_id, request)

        # Estimate duration based on format and inventory size
        resource_count = len(request.inventory.get("resources", []))
        base_duration = 5  # Base 5 seconds

        if request.format in [OutputFormat.PNG, OutputFormat.SVG, OutputFormat.PDF]:
            base_duration += 10  # Image rendering takes longer

        if resource_count > 100:
            base_duration += resource_count // 50  # Add time for large inventories

        response = RenderResponse(
            job_id=job_id,
            status=JobStatus.PENDING,
            message="Rendering job started",
            format=request.format,
            estimated_duration_seconds=base_duration,
            result_url=f"/api/v1/render/jobs/{job_id}",
        )

        logger.info(
            "Rendering job created",
            job_id=job_id,
            user=current_user["username"],
            format=request.format.value,
        )

        return response

    except Exception as e:
        logger.error("Failed to start rendering: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start rendering",
        )


@router.get("/render/jobs/{job_id}", response_model=JobResponse)
async def get_render_job(
    job_id: str, current_user: Dict[str, Any] = Depends(require_permission("view"))
):
    """
    Get diagram rendering job status and results.
    """
    if job_id not in render_jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rendering job not found"
        )

    job = render_jobs[job_id]

    return JobResponse(
        id=job["id"],
        status=job["status"],
        created_at=job["created_at"],
        started_at=job.get("started_at"),
        completed_at=job.get("completed_at"),
        result=job.get("result"),
        error=job.get("error"),
        metadata={"user": job["user"], "request": job["request"]},
    )


@router.get("/render/jobs/{job_id}/download")
async def download_diagram(
    job_id: str, current_user: Dict[str, Any] = Depends(require_permission("view"))
):
    """
    Download rendered diagram file.
    """
    if job_id not in render_jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Rendering job not found"
        )

    job = render_jobs[job_id]

    if job["status"] != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Job not completed"
        )

    result = job["result"]
    content = result["content"]
    format_ext = result["format"]
    encoding = result["encoding"]

    # Decode content if base64 encoded
    if encoding == "base64":
        content_bytes = base64.b64decode(content)
        media_type = {
            "png": "image/png",
            "svg": "image/svg+xml",
            "pdf": "application/pdf",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
        }.get(format_ext, "application/octet-stream")

        return Response(
            content=content_bytes,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename=diagram.{format_ext}"
            },
        )
    else:
        # Text-based formats
        media_type = {
            "mermaid": "text/plain",
            "graphviz": "text/plain",
            "dot": "text/plain",
        }.get(format_ext, "text/plain")

        return Response(
            content=content,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename=diagram.{format_ext}"
            },
        )


@router.post("/compare", response_model=RenderResponse)
async def compare_infrastructures(
    request: CompareRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(require_permission("render")),
):
    """
    Compare two infrastructure states and generate difference diagram.
    """
    # This is a simplified implementation
    # In production, you'd implement actual infrastructure comparison logic

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Infrastructure comparison not yet implemented",
    )


@router.get("/formats", response_model=List[Dict[str, Any]])
async def list_formats(
    current_user: Dict[str, Any] = Depends(require_permission("view")),
):
    """
    List available output formats.
    """
    formats = [
        {
            "name": "mermaid",
            "display_name": "Mermaid Markdown",
            "category": "text",
            "description": "Mermaid diagram syntax for web rendering",
        },
        {
            "name": "graphviz",
            "display_name": "Graphviz DOT",
            "category": "text",
            "description": "Graphviz DOT language syntax",
        },
        {
            "name": "png",
            "display_name": "PNG Image",
            "category": "image",
            "description": "Portable Network Graphics image",
        },
        {
            "name": "svg",
            "display_name": "SVG Vector",
            "category": "image",
            "description": "Scalable Vector Graphics",
        },
        {
            "name": "pdf",
            "display_name": "PDF Document",
            "category": "document",
            "description": "Portable Document Format",
        },
    ]

    return formats


@router.get("/themes", response_model=List[Dict[str, Any]])
async def list_themes(
    current_user: Dict[str, Any] = Depends(require_permission("view")),
):
    """
    List available visual themes.
    """
    themes = [
        {
            "name": "professional",
            "display_name": "Professional",
            "description": "Corporate blue theme suitable for business presentations",
        },
        {
            "name": "dark",
            "display_name": "Dark Mode",
            "description": "Dark theme for modern interfaces",
        },
        {
            "name": "light",
            "display_name": "Light Clean",
            "description": "Clean light theme with subtle colors",
        },
        {
            "name": "minimal",
            "display_name": "Minimal",
            "description": "Simple monochrome theme",
        },
        {
            "name": "colorful",
            "display_name": "Colorful",
            "description": "Vibrant multi-color theme",
        },
    ]

    return themes


@router.get("/layouts", response_model=List[Dict[str, Any]])
async def list_layouts(
    current_user: Dict[str, Any] = Depends(require_permission("view")),
):
    """
    List available layout algorithms.
    """
    layouts = [
        {
            "name": "hierarchical",
            "display_name": "Hierarchical",
            "description": "Top-down hierarchical layout",
            "best_for": ["organizational_charts", "dependency_trees"],
        },
        {
            "name": "flowchart",
            "display_name": "Flowchart",
            "description": "Left-to-right flowchart layout",
            "best_for": ["process_flows", "workflows"],
        },
        {
            "name": "circular",
            "display_name": "Circular",
            "description": "Circular/radial layout",
            "best_for": ["small_networks", "relationships"],
        },
        {
            "name": "force",
            "display_name": "Force-Directed",
            "description": "Physics-based force layout",
            "best_for": ["complex_networks", "clusters"],
        },
        {
            "name": "grid",
            "display_name": "Grid",
            "description": "Regular grid layout",
            "best_for": ["matrix_structures", "organized_data"],
        },
    ]

    return layouts
