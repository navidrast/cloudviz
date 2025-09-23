"""
AWS extraction API routes for CloudViz platform.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, Field

from cloudviz.api.dependencies import get_current_config, get_current_user
from cloudviz.api.models import (
    ErrorResponse,
    ExtractionRequest,
    ExtractionResponse,
    JobResponse,
    JobStatus,
)
from cloudviz.core.utils.logging import get_logger
from cloudviz.providers.aws import AWSResourceExtractor

logger = get_logger(__name__)
router = APIRouter(prefix="/aws", tags=["AWS Extraction"])


class AWSExtractionRequest(BaseModel):
    """AWS resource extraction request."""

    account_id: Optional[str] = Field(None, description="AWS account ID")
    regions: List[str] = Field(default_factory=list, description="AWS regions to scan")
    resource_types: Optional[List[str]] = Field(
        None, description="Resource types to extract"
    )
    access_key_id: Optional[str] = Field(None, description="AWS access key ID")
    secret_access_key: Optional[str] = Field(None, description="AWS secret access key")
    session_token: Optional[str] = Field(None, description="AWS session token")
    profile_name: Optional[str] = Field(None, description="AWS profile name")
    include_global_resources: bool = Field(
        True, description="Include global resources (S3, IAM, etc.)"
    )
    tags_filter: Optional[Dict[str, str]] = Field(None, description="Filter by tags")


class AWSAccountInfo(BaseModel):
    """AWS account information response."""

    account_id: str
    organization_id: Optional[str] = None
    regions: List[Dict[str, Any]]
    total_regions: int


@router.post("/extract", response_model=ExtractionResponse)
async def extract_aws_resources(
    request: AWSExtractionRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user),
    config=Depends(get_current_config),
) -> ExtractionResponse:
    """
    Extract resources from AWS account.

    This endpoint initiates an AWS resource extraction job that runs in the background.
    Use the returned job ID to check progress and retrieve results.
    """
    try:
        # Create AWS extractor
        extractor = AWSResourceExtractor(
            access_key_id=request.access_key_id,
            secret_access_key=request.secret_access_key,
            session_token=request.session_token,
            profile_name=request.profile_name,
        )

        # Test authentication
        if not await extractor.authenticate():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="AWS authentication failed. Please check your credentials.",
            )

        # Create extraction job
        job_id = f"aws-extraction-{hash(str(request.dict()))}"

        # Start background extraction
        background_tasks.add_task(
            _perform_aws_extraction,
            job_id=job_id,
            extractor=extractor,
            request=request,
            user_id=current_user.get("id", "unknown"),
        )

        logger.info(
            "Started AWS extraction job",
            job_id=job_id,
            account_id=request.account_id,
            user_id=current_user.get("id"),
        )

        return ExtractionResponse(
            job_id=job_id,
            status=JobStatus.RUNNING,
            message="AWS resource extraction started",
            provider="aws",
            estimated_duration="5-15 minutes",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to start AWS extraction: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start AWS extraction",
        )


@router.get("/account-info", response_model=AWSAccountInfo)
async def get_aws_account_info(
    access_key_id: Optional[str] = None,
    secret_access_key: Optional[str] = None,
    session_token: Optional[str] = None,
    profile_name: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> AWSAccountInfo:
    """
    Get AWS account information and available regions.

    This endpoint provides information about the AWS account that will be scanned,
    including available regions and organization details.
    """
    try:
        # Create AWS extractor
        extractor = AWSResourceExtractor(
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
            session_token=session_token,
            profile_name=profile_name,
        )

        # Get account info
        account_info = await extractor.get_account_info()

        return AWSAccountInfo(
            account_id=account_info.account_id,
            organization_id=account_info.organization_id,
            regions=[region.dict() for region in account_info.regions],
            total_regions=len(account_info.regions),
        )

    except Exception as e:
        logger.error("Failed to get AWS account info: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve AWS account information",
        )


@router.get("/regions", response_model=List[Dict[str, Any]])
async def get_aws_regions(
    access_key_id: Optional[str] = None,
    secret_access_key: Optional[str] = None,
    profile_name: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """
    Get available AWS regions.

    Returns a list of all AWS regions that can be scanned for resources.
    """
    try:
        # Create AWS extractor
        extractor = AWSResourceExtractor(
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
            profile_name=profile_name,
        )

        # Get account info to retrieve regions
        account_info = await extractor.get_account_info()

        return [region.dict() for region in account_info.regions]

    except Exception as e:
        logger.error("Failed to get AWS regions: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve AWS regions",
        )


@router.get("/resource-types", response_model=List[str])
async def get_aws_resource_types() -> List[str]:
    """
    Get supported AWS resource types.

    Returns a list of all AWS resource types that can be extracted by CloudViz.
    """
    from cloudviz.providers.aws.models import AWS_RESOURCE_TYPES

    return list(AWS_RESOURCE_TYPES.keys())


async def _perform_aws_extraction(
    job_id: str,
    extractor: AWSResourceExtractor,
    request: AWSExtractionRequest,
    user_id: str,
):
    """
    Perform AWS resource extraction in background.

    Args:
        job_id: Unique job identifier
        extractor: AWS resource extractor instance
        request: Extraction request parameters
        user_id: User who initiated the extraction
    """
    try:
        logger.info("Starting AWS resource extraction", job_id=job_id, user_id=user_id)

        # TODO: Store job status in database/cache
        # For now, just perform extraction

        all_resources = []

        # Extract regional resources
        regions_to_scan = request.regions
        if not regions_to_scan:
            # Get all available regions
            account_info = await extractor.get_account_info()
            regions_to_scan = [region.name for region in account_info.regions]

        for region in regions_to_scan:
            logger.info(
                "Extracting resources from AWS region", region=region, job_id=job_id
            )

            try:
                resources = await extractor.extract_resources_by_region(
                    region=region, resource_types=request.resource_types
                )
                all_resources.extend(resources)

            except Exception as e:
                logger.error("Failed to extract from AWS region %s: %s", region, str(e))
                continue

        # Extract global resources
        if request.include_global_resources:
            logger.info("Extracting global AWS resources", job_id=job_id)
            try:
                global_resources = await extractor.extract_global_resources(
                    resource_types=request.resource_types
                )
                all_resources.extend(global_resources)

            except Exception as e:
                logger.error("Failed to extract global AWS resources: %s", str(e))

        # TODO: Store results in database
        # TODO: Update job status to completed

        logger.info(
            "Completed AWS resource extraction",
            job_id=job_id,
            total_resources=len(all_resources),
        )

    except Exception as e:
        logger.error(
            "AWS extraction job failed: %s", str(e), exc_info=True, job_id=job_id
        )
        # TODO: Update job status to failed
