"""
GCP extraction API routes for CloudViz platform.
"""

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, status
from pydantic import BaseModel, Field

from cloudviz.core.utils.logging import get_logger
from cloudviz.api.dependencies import get_current_config, get_current_user
from cloudviz.api.models import (
    ExtractionRequest, ExtractionResponse, JobResponse, 
    JobStatus, ErrorResponse
)
from cloudviz.providers.gcp import GCPResourceExtractor

logger = get_logger(__name__)
router = APIRouter(prefix="/gcp", tags=["GCP Extraction"])


class GCPExtractionRequest(BaseModel):
    """GCP resource extraction request."""
    project_id: str = Field(..., description="GCP project ID")
    regions: List[str] = Field(default_factory=list, description="GCP regions to scan")
    zones: List[str] = Field(default_factory=list, description="GCP zones to scan")
    resource_types: Optional[List[str]] = Field(None, description="Resource types to extract")
    credentials_path: Optional[str] = Field(None, description="Path to service account JSON file")
    credentials_json: Optional[Dict[str, Any]] = Field(None, description="Service account credentials as JSON")
    include_global_resources: bool = Field(True, description="Include global resources (Cloud Storage, IAM, etc.)")
    labels_filter: Optional[Dict[str, str]] = Field(None, description="Filter by labels")


class GCPProjectInfo(BaseModel):
    """GCP project information response."""
    project_id: str
    project_name: str
    project_number: str
    organization_id: Optional[str] = None
    folder_id: Optional[str] = None
    billing_account_id: Optional[str] = None
    regions: List[Dict[str, Any]]
    total_regions: int


@router.post("/extract", response_model=ExtractionResponse)
async def extract_gcp_resources(
    request: GCPExtractionRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
    config = Depends(get_current_config)
) -> ExtractionResponse:
    """
    Extract resources from GCP project.
    
    This endpoint initiates a GCP resource extraction job that runs in the background.
    Use the returned job ID to check progress and retrieve results.
    """
    try:
        # Create GCP extractor
        extractor = GCPResourceExtractor(
            project_id=request.project_id,
            credentials_path=request.credentials_path,
            credentials_info=request.credentials_json
        )
        
        # Test authentication
        if not await extractor.authenticate():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="GCP authentication failed. Please check your credentials and project ID."
            )
            
        # Create extraction job
        job_id = f"gcp-extraction-{hash(str(request.dict()))}"
        
        # Start background extraction
        background_tasks.add_task(
            _perform_gcp_extraction,
            job_id=job_id,
            extractor=extractor,
            request=request,
            user_id=current_user.get("id", "unknown")
        )
        
        logger.info("Started GCP extraction job", job_id=job_id, 
                   project_id=request.project_id, user_id=current_user.get("id"))
        
        return ExtractionResponse(
            job_id=job_id,
            status=JobStatus.RUNNING,
            message="GCP resource extraction started",
            provider="gcp",
            estimated_duration="5-15 minutes"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to start GCP extraction: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start GCP extraction"
        )


@router.get("/project-info", response_model=GCPProjectInfo)
async def get_gcp_project_info(
    project_id: str,
    credentials_path: Optional[str] = None,
    credentials_json: Optional[Dict[str, Any]] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> GCPProjectInfo:
    """
    Get GCP project information and available regions.
    
    This endpoint provides information about the GCP project that will be scanned,
    including available regions and zones.
    """
    try:
        # Create GCP extractor
        extractor = GCPResourceExtractor(
            project_id=project_id,
            credentials_path=credentials_path,
            credentials_info=credentials_json
        )
        
        # Get project info
        project_info = await extractor.get_project_info()
        
        return GCPProjectInfo(
            project_id=project_info.project_id,
            project_name=project_info.project_name,
            project_number=project_info.project_number,
            organization_id=project_info.organization_id,
            folder_id=project_info.folder_id,
            billing_account_id=project_info.billing_account_id,
            regions=[region.dict() for region in project_info.regions],
            total_regions=len(project_info.regions)
        )
        
    except Exception as e:
        logger.error("Failed to get GCP project info: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve GCP project information"
        )


@router.get("/regions", response_model=List[Dict[str, Any]])
async def get_gcp_regions(
    project_id: str,
    credentials_path: Optional[str] = None,
    credentials_json: Optional[Dict[str, Any]] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    Get available GCP regions.
    
    Returns a list of all GCP regions that can be scanned for resources.
    """
    try:
        # Create GCP extractor
        extractor = GCPResourceExtractor(
            project_id=project_id,
            credentials_path=credentials_path,
            credentials_info=credentials_json
        )
        
        # Get project info to retrieve regions
        project_info = await extractor.get_project_info()
        
        return [region.dict() for region in project_info.regions]
        
    except Exception as e:
        logger.error("Failed to get GCP regions: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve GCP regions"
        )


@router.get("/resource-types", response_model=List[str])
async def get_gcp_resource_types() -> List[str]:
    """
    Get supported GCP resource types.
    
    Returns a list of all GCP resource types that can be extracted by CloudViz.
    """
    from cloudviz.providers.gcp.models import GCP_RESOURCE_TYPES
    return list(GCP_RESOURCE_TYPES.keys())


async def _perform_gcp_extraction(
    job_id: str, 
    extractor: GCPResourceExtractor,
    request: GCPExtractionRequest,
    user_id: str
):
    """
    Perform GCP resource extraction in background.
    
    Args:
        job_id: Unique job identifier
        extractor: GCP resource extractor instance
        request: Extraction request parameters
        user_id: User who initiated the extraction
    """
    try:
        logger.info("Starting GCP resource extraction", job_id=job_id, user_id=user_id)
        
        # TODO: Store job status in database/cache
        # For now, just perform extraction
        
        all_resources = []
        
        # Extract regional resources
        regions_to_scan = request.regions
        if not regions_to_scan:
            # Get all available regions
            project_info = await extractor.get_project_info()
            regions_to_scan = [region.name for region in project_info.regions]
            
        for region in regions_to_scan:
            logger.info("Extracting resources from GCP region", region=region, job_id=job_id)
            
            try:
                resources = await extractor.extract_resources_by_region(
                    region=region,
                    resource_types=request.resource_types
                )
                all_resources.extend(resources)
                
            except Exception as e:
                logger.error("Failed to extract from GCP region %s: %s", region, str(e))
                continue
                
        # Extract global resources
        if request.include_global_resources:
            logger.info("Extracting global GCP resources", job_id=job_id)
            try:
                global_resources = await extractor.extract_global_resources(
                    resource_types=request.resource_types
                )
                all_resources.extend(global_resources)
                
            except Exception as e:
                logger.error("Failed to extract global GCP resources: %s", str(e))
                
        # TODO: Store results in database
        # TODO: Update job status to completed
        
        logger.info("Completed GCP resource extraction", 
                   job_id=job_id, total_resources=len(all_resources))
        
    except Exception as e:
        logger.error("GCP extraction job failed: %s", str(e), exc_info=True, job_id=job_id)
        # TODO: Update job status to failed
