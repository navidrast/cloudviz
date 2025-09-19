"""
Resource extraction endpoints for CloudViz API.
Handles cloud resource discovery and extraction operations.
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from pydantic import BaseModel, Field

from cloudviz.core.config import CloudVizConfig
from cloudviz.core.models import CloudProvider, ResourceInventory, CloudResource
from cloudviz.core.utils import get_logger
from cloudviz.api.dependencies import get_current_config, get_current_user
from cloudviz.api.models import JobStatus, JobResponse


logger = get_logger(__name__)
router = APIRouter()


class ExtractionScope(str, Enum):
    """Resource extraction scope."""
    SUBSCRIPTION = "subscription"
    RESOURCE_GROUP = "resource_group"
    REGION = "region"


class ExtractionRequest(BaseModel):
    """Resource extraction request model."""
    provider: CloudProvider
    scope: ExtractionScope = ExtractionScope.SUBSCRIPTION
    scope_identifier: str = Field(..., description="Subscription ID, Resource Group name, or Region name")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional filters")
    include_relationships: bool = Field(default=True, description="Include resource relationships")
    resource_types: Optional[List[str]] = Field(default=None, description="Filter by resource types")
    regions: Optional[List[str]] = Field(default=None, description="Filter by regions")
    tags: Optional[Dict[str, str]] = Field(default=None, description="Filter by tags")


class ExtractionResponse(BaseModel):
    """Resource extraction response model."""
    job_id: str
    status: JobStatus
    message: str
    estimated_duration_seconds: Optional[int] = None
    result_url: Optional[str] = None


class InventoryResponse(BaseModel):
    """Resource inventory response model."""
    inventory: Dict[str, Any]
    metadata: Dict[str, Any]
    extraction_time: datetime
    resource_count: int
    relationship_count: int


# In-memory job storage - In production, use Redis or database
extraction_jobs: Dict[str, Dict[str, Any]] = {}


def require_permission(permission: str):
    """Dependency to check user permissions."""
    def check_permission(current_user: Dict[str, Any] = Depends(get_current_user)):
        if permission not in current_user.get("permissions", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return current_user
    return check_permission


async def perform_extraction(job_id: str, request: ExtractionRequest) -> None:
    """Background task to perform resource extraction."""
    try:
        # Update job status
        extraction_jobs[job_id]["status"] = JobStatus.RUNNING
        extraction_jobs[job_id]["started_at"] = datetime.now()
        
        logger.info("Starting resource extraction", 
                   job_id=job_id, 
                   provider=request.provider.value,
                   scope=request.scope.value)
        
        # Simulate extraction process
        # In real implementation, this would call the actual provider extractors
        if request.provider == CloudProvider.AZURE:
            inventory = await extract_azure_resources(request)
        elif request.provider == CloudProvider.AWS:
            inventory = await extract_aws_resources(request)
        elif request.provider == CloudProvider.GCP:
            inventory = await extract_gcp_resources(request)
        else:
            raise ValueError(f"Unsupported provider: {request.provider}")
        
        # Store results
        extraction_jobs[job_id]["status"] = JobStatus.COMPLETED
        extraction_jobs[job_id]["completed_at"] = datetime.now()
        extraction_jobs[job_id]["result"] = inventory.to_dict()
        extraction_jobs[job_id]["resource_count"] = len(inventory.resources)
        extraction_jobs[job_id]["relationship_count"] = len(inventory.relationships)
        
        logger.info("Resource extraction completed", 
                   job_id=job_id,
                   resource_count=len(inventory.resources))
        
    except Exception as e:
        logger.error("Resource extraction failed", 
                    job_id=job_id, 
                    exc_info=True, 
                    error=str(e))
        
        extraction_jobs[job_id]["status"] = JobStatus.FAILED
        extraction_jobs[job_id]["error"] = str(e)
        extraction_jobs[job_id]["completed_at"] = datetime.now()


async def extract_azure_resources(request: ExtractionRequest) -> ResourceInventory:
    """Extract Azure resources (mock implementation)."""
    # This is a mock implementation
    # In production, this would use the actual Azure extractor
    import asyncio
    await asyncio.sleep(2)  # Simulate extraction time
    
    # Create mock resources
    resources = [
        CloudResource(
            id=f"azure-vm-{i}",
            name=f"vm-{i}",
            resource_type="virtual_machine",
            provider=CloudProvider.AZURE,
            region="eastus",
            resource_group="mock-rg",
            created_time=datetime.now()
        )
        for i in range(5)
    ]
    
    return ResourceInventory(
        resources=resources,
        relationships=[],
        provider=CloudProvider.AZURE,
        extraction_time=datetime.now(),
        extraction_scope=request.scope,
        scope_identifier=request.scope_identifier
    )


async def extract_aws_resources(request: ExtractionRequest) -> ResourceInventory:
    """Extract AWS resources (not implemented)."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="AWS extraction not yet implemented"
    )


async def extract_gcp_resources(request: ExtractionRequest) -> ResourceInventory:
    """Extract GCP resources (not implemented)."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="GCP extraction not yet implemented"
    )


@router.post("/extract", response_model=ExtractionResponse)
async def extract_resources(
    request: ExtractionRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(require_permission("extract")),
    config: CloudVizConfig = Depends(get_current_config)
):
    """
    Start resource extraction from cloud provider.
    
    This endpoint initiates an asynchronous extraction job and returns immediately.
    Use the job_id to check extraction status and retrieve results.
    """
    try:
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Initialize job record
        extraction_jobs[job_id] = {
            "id": job_id,
            "status": JobStatus.PENDING,
            "request": request.dict(),
            "user": current_user["username"],
            "created_at": datetime.now(),
            "started_at": None,
            "completed_at": None,
            "result": None,
            "error": None
        }
        
        # Start background extraction
        background_tasks.add_task(perform_extraction, job_id, request)
        
        # Estimate duration based on scope
        estimated_duration = {
            ExtractionScope.SUBSCRIPTION: 60,
            ExtractionScope.RESOURCE_GROUP: 30,
            ExtractionScope.REGION: 45
        }.get(request.scope, 60)
        
        response = ExtractionResponse(
            job_id=job_id,
            status=JobStatus.PENDING,
            message="Extraction job started",
            estimated_duration_seconds=estimated_duration,
            result_url=f"/api/v1/jobs/{job_id}"
        )
        
        logger.info("Extraction job created", 
                   job_id=job_id, 
                   user=current_user["username"],
                   provider=request.provider.value)
        
        return response
        
    except Exception as e:
        logger.error("Failed to start extraction", exc_info=True, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start extraction"
        )


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_extraction_job(
    job_id: str,
    current_user: Dict[str, Any] = Depends(require_permission("view"))
):
    """
    Get extraction job status and results.
    """
    if job_id not in extraction_jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    job = extraction_jobs[job_id]
    
    return JobResponse(
        id=job["id"],
        status=job["status"],
        created_at=job["created_at"],
        started_at=job.get("started_at"),
        completed_at=job.get("completed_at"),
        result=job.get("result"),
        error=job.get("error"),
        metadata={
            "user": job["user"],
            "request": job["request"],
            "resource_count": job.get("resource_count"),
            "relationship_count": job.get("relationship_count")
        }
    )


@router.get("/jobs", response_model=List[JobResponse])
async def list_extraction_jobs(
    status_filter: Optional[JobStatus] = None,
    limit: int = 50,
    current_user: Dict[str, Any] = Depends(require_permission("view"))
):
    """
    List extraction jobs.
    """
    jobs = list(extraction_jobs.values())
    
    # Filter by status if provided
    if status_filter:
        jobs = [job for job in jobs if job["status"] == status_filter]
    
    # Sort by creation time (newest first)
    jobs.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Apply limit
    jobs = jobs[:limit]
    
    return [
        JobResponse(
            id=job["id"],
            status=job["status"],
            created_at=job["created_at"],
            started_at=job.get("started_at"),
            completed_at=job.get("completed_at"),
            result=job.get("result"),
            error=job.get("error"),
            metadata={
                "user": job["user"],
                "request": job["request"],
                "resource_count": job.get("resource_count"),
                "relationship_count": job.get("relationship_count")
            }
        )
        for job in jobs
    ]


@router.delete("/jobs/{job_id}")
async def cancel_extraction_job(
    job_id: str,
    current_user: Dict[str, Any] = Depends(require_permission("extract"))
):
    """
    Cancel or delete an extraction job.
    """
    if job_id not in extraction_jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    job = extraction_jobs[job_id]
    
    # Only allow cancellation of pending/running jobs
    if job["status"] in [JobStatus.PENDING, JobStatus.RUNNING]:
        job["status"] = JobStatus.CANCELLED
        job["completed_at"] = datetime.now()
        logger.info("Extraction job cancelled", job_id=job_id)
    
    # Delete completed/failed jobs
    if job["status"] in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
        del extraction_jobs[job_id]
        logger.info("Extraction job deleted", job_id=job_id)
    
    return {"message": "Job cancelled/deleted successfully"}


@router.get("/providers", response_model=List[Dict[str, Any]])
async def list_providers(
    current_user: Dict[str, Any] = Depends(require_permission("view"))
):
    """
    List available cloud providers.
    """
    providers = [
        {
            "name": "azure",
            "display_name": "Microsoft Azure",
            "supported": True,
            "features": ["extraction", "visualization", "relationships"]
        },
        {
            "name": "aws", 
            "display_name": "Amazon Web Services",
            "supported": False,
            "features": ["extraction", "visualization"],
            "note": "Coming soon"
        },
        {
            "name": "gcp",
            "display_name": "Google Cloud Platform", 
            "supported": False,
            "features": ["extraction", "visualization"],
            "note": "Coming soon"
        }
    ]
    
    return providers
