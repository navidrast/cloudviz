"""
GCP resource extractor for CloudViz platform.
"""

import asyncio
from typing import Dict, List, Optional, Any
from google.cloud import compute_v1, storage
# from google.cloud import sql_v1  # TODO: Fix import issue
from google.cloud.exceptions import GoogleCloudError
from google.oauth2 import service_account
from datetime import datetime

from cloudviz.core.base import BaseResourceExtractor
from cloudviz.core.utils.logging import get_logger
from .models import (
    GCPResource, GCPProject, GCPComputeInstance, GCPCloudStorage,
    GCPCloudSQL, GCPKubernetesCluster, GCPVPCNetwork, GCPCloudFunction,
    GCPLoadBalancer, GCPPubSubTopic, GCP_RESOURCE_TYPES
)

logger = get_logger(__name__)


class GCPResourceExtractor(BaseResourceExtractor):
    """
    GCP resource extractor using Google Cloud SDK.
    """
    
    def __init__(self, project_id: str,
                 credentials_path: Optional[str] = None,
                 credentials_info: Optional[Dict[str, Any]] = None):
        """
        Initialize GCP extractor.
        
        Args:
            project_id: GCP project ID
            credentials_path: Path to service account JSON file
            credentials_info: Service account credentials as dict
        """
        super().__init__()
        
        self.project_id = project_id
        self.credentials_path = credentials_path
        self.credentials_info = credentials_info
        
        self._credentials = None
        self._project_info = None
        
    @property
    def credentials(self):
        """Get or create GCP credentials."""
        if self._credentials is None:
            if self.credentials_info:
                self._credentials = service_account.Credentials.from_service_account_info(
                    self.credentials_info
                )
            elif self.credentials_path:
                self._credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
            else:
                # Use default credentials
                from google.auth import default
                self._credentials, _ = default()
                
        return self._credentials
        
    async def authenticate(self) -> bool:
        """
        Authenticate with GCP.
        
        Returns:
            bool: True if authentication successful
        """
        try:
            # Test authentication by creating a client
            compute_client = compute_v1.InstancesClient(credentials=self.credentials)
            
            # Try to list instances (will fail if no auth)
            try:
                request = compute_v1.AggregatedListInstancesRequest(
                    project=self.project_id,
                    max_results=1
                )
                # Just make the request to test auth - don't process results
                list(compute_client.aggregated_list(request=request))
            except Exception:
                pass  # Expected if no compute instances, auth still worked
                
            logger.info("GCP authentication successful", project_id=self.project_id)
            return True
            
        except GoogleCloudError as e:
            logger.error("GCP authentication failed: %s", str(e))
            return False
            
    async def get_project_info(self) -> GCPProject:
        """
        Get GCP project information.
        
        Returns:
            GCPProject: Project information
        """
        if not await self.authenticate():
            raise RuntimeError("GCP authentication failed")
            
        try:
            # Get project details
            from google.cloud import resource_manager
            client = resource_manager.Client(credentials=self.credentials)
            
            project = client.fetch_project(self.project_id)
            
            # Get available regions and zones
            compute_client = compute_v1.RegionsClient(credentials=self.credentials)
            regions_request = compute_v1.ListRegionsRequest(project=self.project_id)
            regions_response = compute_client.list(request=regions_request)
            
            regions = []
            for region_data in regions_response:
                # Get zones for this region
                zones_client = compute_v1.ZonesClient(credentials=self.credentials)
                zones_request = compute_v1.ListZonesRequest(project=self.project_id)
                zones_response = zones_client.list(request=zones_request)
                
                region_zones = [
                    zone.name for zone in zones_response 
                    if zone.region.endswith(f"regions/{region_data.name}")
                ]
                
                regions.append({
                    'name': region_data.name,
                    'description': region_data.description,
                    'zones': region_zones,
                    'status': region_data.status
                })
                
            return GCPProject(
                project_id=self.project_id,
                project_name=project.name,
                project_number=str(project.number),
                regions=regions,
                labels=dict(project.labels) if project.labels else {}
            )
            
        except GoogleCloudError as e:
            logger.error("Failed to get GCP project info: %s", str(e))
            raise
            
    async def extract_compute_instances(self, zone: Optional[str] = None) -> List[GCPComputeInstance]:
        """Extract Compute Engine instances."""
        try:
            compute_client = compute_v1.InstancesClient(credentials=self.credentials)
            
            instances = []
            
            if zone:
                # Extract from specific zone
                request = compute_v1.ListInstancesRequest(
                    project=self.project_id,
                    zone=zone
                )
                response = compute_client.list(request=request)
                
                for instance in response:
                    instance_resource = await self._convert_compute_instance(instance, zone)
                    instances.append(instance_resource)
            else:
                # Extract from all zones
                request = compute_v1.AggregatedListInstancesRequest(
                    project=self.project_id
                )
                response = compute_client.aggregated_list(request=request)
                
                for zone_name, zone_instances in response:
                    if zone_instances.instances:
                        for instance in zone_instances.instances:
                            zone_short = zone_name.split('/')[-1]
                            instance_resource = await self._convert_compute_instance(instance, zone_short)
                            instances.append(instance_resource)
                            
            logger.info("Extracted %d Compute Engine instances", len(instances))
            return instances
            
        except GoogleCloudError as e:
            logger.error("Failed to extract Compute Engine instances: %s", str(e))
            return []
            
    async def extract_cloud_storage_buckets(self) -> List[GCPCloudStorage]:
        """Extract Cloud Storage buckets."""
        try:
            storage_client = storage.Client(
                project=self.project_id,
                credentials=self.credentials
            )
            
            buckets = []
            for bucket in storage_client.list_buckets():
                bucket_resource = GCPCloudStorage(
                    id=bucket.name,
                    name=bucket.name,
                    project_id=self.project_id,
                    self_link=f"https://www.googleapis.com/storage/v1/b/{bucket.name}",
                    resource_type="cloud_storage",
                    
                    # Cloud Storage-specific fields
                    bucket_name=bucket.name,
                    location=bucket.location,
                    location_type=bucket.location_type,
                    storage_class=bucket.storage_class,
                    versioning_enabled=bucket.versioning_enabled,
                    uniform_bucket_level_access=bucket.iam_configuration.uniform_bucket_level_access_enabled,
                    
                    # Metadata
                    creation_timestamp=bucket.time_created,
                    labels=dict(bucket.labels) if bucket.labels else {},
                    tags=dict(bucket.labels) if bucket.labels else {}
                )
                buckets.append(bucket_resource)
                
            logger.info("Extracted %d Cloud Storage buckets", len(buckets))
            return buckets
            
        except GoogleCloudError as e:
            logger.error("Failed to extract Cloud Storage buckets: %s", str(e))
            return []
            
    async def extract_resources_by_region(self, region: str,
                                        resource_types: Optional[List[str]] = None) -> List[GCPResource]:
        """
        Extract GCP resources from a specific region.
        
        Args:
            region: GCP region name
            resource_types: List of resource types to extract (None for all)
            
        Returns:
            List[GCPResource]: Extracted resources
        """
        logger.info("Starting resource extraction for GCP region: %s", region)
        
        if not await self.authenticate():
            raise RuntimeError("GCP authentication failed")
            
        resources = []
        
        # Extract Compute Engine instances from all zones in region
        if not resource_types or 'compute_instance' in resource_types:
            # Get zones for this region
            zones_client = compute_v1.ZonesClient(credentials=self.credentials)
            zones_request = compute_v1.ListZonesRequest(project=self.project_id)
            zones_response = zones_client.list(request=zones_request)
            
            region_zones = [
                zone.name for zone in zones_response
                if zone.region.endswith(f"regions/{region}")
            ]
            
            for zone in region_zones:
                compute_instances = await self.extract_compute_instances(zone)
                resources.extend(compute_instances)
                
        # TODO: Add more resource types
        # - Cloud SQL instances
        # - GKE clusters  
        # - VPC networks
        # - Load balancers
        # - Cloud Functions
        
        logger.info("Extracted %d resources from GCP region %s", len(resources), region)
        return resources
        
    async def extract_global_resources(self,
                                     resource_types: Optional[List[str]] = None) -> List[GCPResource]:
        """
        Extract GCP global resources (not tied to a specific region).
        
        Args:
            resource_types: List of resource types to extract (None for all)
            
        Returns:
            List[GCPResource]: Extracted global resources
        """
        logger.info("Starting global resource extraction for GCP")
        
        if not await self.authenticate():
            raise RuntimeError("GCP authentication failed")
            
        resources = []
        
        # Extract Cloud Storage buckets (global)
        if not resource_types or 'cloud_storage' in resource_types:
            storage_buckets = await self.extract_cloud_storage_buckets()
            resources.extend(storage_buckets)
            
        # TODO: Add more global resource types
        # - IAM policies and service accounts
        # - DNS zones
        # - Global load balancers
        # - Pub/Sub topics
        
        logger.info("Extracted %d global resources from GCP", len(resources))
        return resources
        
    async def _convert_compute_instance(self, instance, zone: str) -> GCPComputeInstance:
        """Convert GCP compute instance to CloudViz model."""
        # Extract machine type from URL
        machine_type = instance.machine_type.split('/')[-1] if instance.machine_type else "unknown"
        
        # Extract network interfaces
        external_ip = None
        internal_ip = None
        network = None
        subnetwork = None
        
        if instance.network_interfaces:
            interface = instance.network_interfaces[0]
            internal_ip = interface.network_i_p
            network = interface.network.split('/')[-1] if interface.network else None
            subnetwork = interface.subnetwork.split('/')[-1] if interface.subnetwork else None
            
            if interface.access_configs:
                external_ip = interface.access_configs[0].nat_i_p
                
        # Extract disk size
        disk_size_gb = 0
        if instance.disks:
            disk_size_gb = sum(disk.disk_size_gb for disk in instance.disks if disk.disk_size_gb)
            
        return GCPComputeInstance(
            id=str(instance.id),
            name=instance.name,
            project_id=self.project_id,
            zone=zone,
            region='-'.join(zone.split('-')[:-1]),  # Extract region from zone
            self_link=instance.self_link,
            resource_type="compute_instance",
            
            # Compute-specific fields
            instance_id=str(instance.id),
            machine_type=machine_type,
            image=instance.source_machine_image.split('/')[-1] if instance.source_machine_image else "unknown",
            disk_size_gb=disk_size_gb,
            external_ip=external_ip,
            internal_ip=internal_ip,
            network=network,
            subnetwork=subnetwork,
            
            # General fields
            status=instance.status,
            creation_timestamp=datetime.fromisoformat(instance.creation_timestamp.rstrip('Z')),
            labels=dict(instance.labels) if instance.labels else {},
            tags=dict(instance.labels) if instance.labels else {},
            preemptible=instance.scheduling.preemptible if instance.scheduling else False,
            can_ip_forward=instance.can_ip_forward
        )
