"""
GCP resource models for CloudViz platform.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
from cloudviz.core.models import BaseResource, ResourceProvider


class GCPRegion(BaseModel):
    """GCP region information."""
    name: str
    description: str
    zones: List[str] = Field(default_factory=list)
    status: str = "UP"
    

class GCPProject(BaseModel):
    """GCP project information."""
    project_id: str
    project_name: str
    project_number: str
    organization_id: Optional[str] = None
    folder_id: Optional[str] = None
    billing_account_id: Optional[str] = None
    regions: List[GCPRegion] = Field(default_factory=list)
    labels: Dict[str, str] = Field(default_factory=dict)
    

class GCPResource(BaseResource):
    """GCP-specific resource model."""
    provider: ResourceProvider = ResourceProvider.GCP
    
    # GCP-specific fields
    project_id: str
    region: Optional[str] = None
    zone: Optional[str] = None
    self_link: str
    network: Optional[str] = None
    subnetwork: Optional[str] = None
    
    # Cost information
    estimated_monthly_cost: Optional[float] = None
    billing_account_id: Optional[str] = None
    cost_labels: Dict[str, str] = Field(default_factory=dict)
    
    # GCP-specific metadata
    machine_type: Optional[str] = None
    status: Optional[str] = None
    creation_timestamp: Optional[datetime] = None
    

class GCPComputeInstance(GCPResource):
    """GCP Compute Engine Instance resource."""
    resource_type: str = "compute_instance"
    
    # Compute Engine-specific fields
    instance_id: str
    machine_type: str
    zone: str
    image: str
    disk_size_gb: int
    external_ip: Optional[str] = None
    internal_ip: Optional[str] = None
    preemptible: bool = False
    can_ip_forward: bool = False
    startup_script: Optional[str] = None
    service_accounts: List[Dict[str, Any]] = Field(default_factory=list)
    

class GCPCloudStorage(GCPResource):
    """GCP Cloud Storage Bucket resource."""
    resource_type: str = "cloud_storage"
    
    # Cloud Storage-specific fields
    bucket_name: str
    location: str
    location_type: str  # region, multi-region, dual-region
    storage_class: str  # STANDARD, NEARLINE, COLDLINE, ARCHIVE
    versioning_enabled: bool = False
    uniform_bucket_level_access: bool = False
    public_access_prevention: str = "inherited"
    size_bytes: Optional[int] = None
    object_count: Optional[int] = None
    

class GCPCloudSQL(GCPResource):
    """GCP Cloud SQL Instance resource."""
    resource_type: str = "cloud_sql"
    
    # Cloud SQL-specific fields
    instance_name: str
    database_version: str
    tier: str
    region: str
    availability_type: str  # ZONAL, REGIONAL
    storage_size_gb: int
    storage_type: str  # SSD, HDD
    storage_auto_resize: bool = True
    backup_enabled: bool = False
    binary_log_enabled: bool = False
    point_in_time_recovery_enabled: bool = False
    

class GCPKubernetesCluster(GCPResource):
    """GCP Kubernetes Engine Cluster resource."""
    resource_type: str = "gke_cluster"
    
    # GKE-specific fields
    cluster_name: str
    zone: Optional[str] = None
    region: Optional[str] = None
    node_pools: List[Dict[str, Any]] = Field(default_factory=list)
    initial_node_count: int
    current_node_count: int
    network: str
    subnetwork: str
    cluster_ipv4_cidr: Optional[str] = None
    services_ipv4_cidr: Optional[str] = None
    master_version: str
    node_version: str
    

class GCPVPCNetwork(GCPResource):
    """GCP VPC Network resource."""
    resource_type: str = "vpc_network"
    
    # VPC-specific fields
    network_name: str
    auto_create_subnetworks: bool = False
    routing_mode: str  # REGIONAL, GLOBAL
    subnets: List[str] = Field(default_factory=list)
    firewall_rules: List[str] = Field(default_factory=list)
    routes: List[str] = Field(default_factory=list)
    

class GCPCloudFunction(GCPResource):
    """GCP Cloud Functions resource."""
    resource_type: str = "cloud_function"
    
    # Cloud Functions-specific fields
    function_name: str
    runtime: str
    entry_point: str
    source_archive_url: Optional[str] = None
    source_repository: Optional[Dict[str, str]] = None
    timeout: str = "60s"
    available_memory_mb: int = 256
    max_instances: Optional[int] = None
    environment_variables: Dict[str, str] = Field(default_factory=dict)
    trigger: Dict[str, Any] = Field(default_factory=dict)
    

class GCPLoadBalancer(GCPResource):
    """GCP Load Balancer resource."""
    resource_type: str = "load_balancer"
    
    # Load Balancer-specific fields
    load_balancer_name: str
    load_balancer_type: str  # EXTERNAL, INTERNAL, INTERNAL_MANAGED
    ip_address: Optional[str] = None
    port_range: Optional[str] = None
    backend_services: List[str] = Field(default_factory=list)
    target_pools: List[str] = Field(default_factory=list)
    url_maps: List[str] = Field(default_factory=list)
    

class GCPPubSubTopic(GCPResource):
    """GCP Pub/Sub Topic resource."""
    resource_type: str = "pubsub_topic"
    
    # Pub/Sub-specific fields
    topic_name: str
    subscriptions: List[str] = Field(default_factory=list)
    message_retention_duration: str = "604800s"  # 7 days
    message_encoding: str = "ENCODING_UNSPECIFIED"
    

# GCP Resource Type Registry
GCP_RESOURCE_TYPES = {
    "compute_instance": GCPComputeInstance,
    "cloud_storage": GCPCloudStorage,
    "cloud_sql": GCPCloudSQL,
    "gke_cluster": GCPKubernetesCluster,
    "vpc_network": GCPVPCNetwork,
    "cloud_function": GCPCloudFunction,
    "load_balancer": GCPLoadBalancer,
    "pubsub_topic": GCPPubSubTopic,
}
