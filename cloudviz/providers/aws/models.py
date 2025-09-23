"""
AWS resource models for CloudViz platform.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from cloudviz.core.models import BaseResource, ResourceProvider


class AWSRegion(BaseModel):
    """AWS region information."""

    name: str
    display_name: str
    endpoint: str
    availability_zones: List[str] = Field(default_factory=list)


class AWSSubscription(BaseModel):
    """AWS account information."""

    account_id: str
    account_name: Optional[str] = None
    organization_id: Optional[str] = None
    regions: List[AWSRegion] = Field(default_factory=list)
    tags: Dict[str, str] = Field(default_factory=dict)


class AWSResource(BaseResource):
    """AWS-specific resource model."""

    provider: ResourceProvider = ResourceProvider.AWS

    # AWS-specific fields
    account_id: str
    region: str
    arn: str
    availability_zone: Optional[str] = None
    vpc_id: Optional[str] = None
    subnet_id: Optional[str] = None
    security_groups: List[str] = Field(default_factory=list)

    # Cost information
    estimated_monthly_cost: Optional[float] = None
    cost_center: Optional[str] = None
    billing_tags: Dict[str, str] = Field(default_factory=dict)

    # AWS-specific metadata
    instance_type: Optional[str] = None
    instance_state: Optional[str] = None
    launch_time: Optional[datetime] = None
    platform: Optional[str] = None  # Linux, Windows, etc.


class AWSEC2Instance(AWSResource):
    """AWS EC2 Instance resource."""

    resource_type: str = "ec2_instance"

    # EC2-specific fields
    instance_id: str
    instance_type: str
    image_id: str
    key_name: Optional[str] = None
    public_ip: Optional[str] = None
    private_ip: Optional[str] = None
    public_dns: Optional[str] = None
    private_dns: Optional[str] = None
    monitoring_enabled: bool = False
    ebs_optimized: bool = False


class AWSS3Bucket(AWSResource):
    """AWS S3 Bucket resource."""

    resource_type: str = "s3_bucket"

    # S3-specific fields
    bucket_name: str
    creation_date: datetime
    versioning_enabled: bool = False
    encryption_enabled: bool = False
    public_read_enabled: bool = False
    public_write_enabled: bool = False
    size_bytes: Optional[int] = None
    object_count: Optional[int] = None
    storage_class: Optional[str] = None


class AWSRDSInstance(AWSResource):
    """AWS RDS Database Instance resource."""

    resource_type: str = "rds_instance"

    # RDS-specific fields
    db_instance_identifier: str
    db_instance_class: str
    engine: str
    engine_version: str
    allocated_storage: int
    storage_type: str
    multi_az: bool = False
    publicly_accessible: bool = False
    backup_retention_period: int = 0
    preferred_backup_window: Optional[str] = None
    preferred_maintenance_window: Optional[str] = None


class AWSVPCNetwork(AWSResource):
    """AWS VPC Network resource."""

    resource_type: str = "vpc"

    # VPC-specific fields
    vpc_id: str
    cidr_block: str
    dhcp_options_id: Optional[str] = None
    instance_tenancy: str = "default"
    is_default: bool = False
    subnets: List[str] = Field(default_factory=list)
    route_tables: List[str] = Field(default_factory=list)
    internet_gateways: List[str] = Field(default_factory=list)
    nat_gateways: List[str] = Field(default_factory=list)


class AWSLoadBalancer(AWSResource):
    """AWS Elastic Load Balancer resource."""

    resource_type: str = "load_balancer"

    # ELB-specific fields
    load_balancer_name: str
    load_balancer_type: str  # application, network, gateway, classic
    scheme: str  # internet-facing, internal
    dns_name: str
    canonical_hosted_zone_id: Optional[str] = None
    listeners: List[Dict[str, Any]] = Field(default_factory=list)
    target_groups: List[str] = Field(default_factory=list)


class AWSLambdaFunction(AWSResource):
    """AWS Lambda Function resource."""

    resource_type: str = "lambda_function"

    # Lambda-specific fields
    function_name: str
    function_arn: str
    runtime: str
    handler: str
    code_size: int
    timeout: int
    memory_size: int
    last_modified: datetime
    code_sha256: str
    version: str
    environment_variables: Dict[str, str] = Field(default_factory=dict)


class AWSECSCluster(AWSResource):
    """AWS ECS Cluster resource."""

    resource_type: str = "ecs_cluster"

    # ECS-specific fields
    cluster_name: str
    cluster_arn: str
    status: str
    running_tasks_count: int = 0
    pending_tasks_count: int = 0
    active_services_count: int = 0
    registered_container_instances_count: int = 0
    capacity_providers: List[str] = Field(default_factory=list)


# AWS Resource Type Registry
AWS_RESOURCE_TYPES = {
    "ec2_instance": AWSEC2Instance,
    "s3_bucket": AWSS3Bucket,
    "rds_instance": AWSRDSInstance,
    "vpc": AWSVPCNetwork,
    "load_balancer": AWSLoadBalancer,
    "lambda_function": AWSLambdaFunction,
    "ecs_cluster": AWSECSCluster,
}
