"""
AWS resource extractor for CloudViz platform.
"""

import asyncio
from typing import Dict, List, Optional, Any
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from datetime import datetime

from cloudviz.core.base import BaseResourceExtractor
from cloudviz.core.utils.logging import get_logger
from .models import (
    AWSResource, AWSSubscription, AWSEC2Instance, AWSS3Bucket, 
    AWSRDSInstance, AWSVPCNetwork, AWSLoadBalancer, AWSLambdaFunction,
    AWSECSCluster, AWS_RESOURCE_TYPES
)

logger = get_logger(__name__)


class AWSResourceExtractor(BaseResourceExtractor):
    """
    AWS resource extractor using boto3.
    """
    
    def __init__(self, access_key_id: Optional[str] = None,
                 secret_access_key: Optional[str] = None,
                 session_token: Optional[str] = None,
                 region_name: str = "us-east-1",
                 profile_name: Optional[str] = None):
        """
        Initialize AWS extractor.
        
        Args:
            access_key_id: AWS access key ID
            secret_access_key: AWS secret access key  
            session_token: AWS session token (for temporary credentials)
            region_name: Default AWS region
            profile_name: AWS profile name (alternative to key/secret)
        """
        super().__init__()
        
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.session_token = session_token
        self.region_name = region_name
        self.profile_name = profile_name
        
        self._session = None
        self._account_id = None
        
    @property
    def session(self) -> boto3.Session:
        """Get or create boto3 session."""
        if self._session is None:
            kwargs = {}
            
            if self.profile_name:
                kwargs['profile_name'] = self.profile_name
            else:
                if self.access_key_id:
                    kwargs['aws_access_key_id'] = self.access_key_id
                if self.secret_access_key:
                    kwargs['aws_secret_access_key'] = self.secret_access_key
                if self.session_token:
                    kwargs['aws_session_token'] = self.session_token
                    
            kwargs['region_name'] = self.region_name
            self._session = boto3.Session(**kwargs)
            
        return self._session
        
    async def authenticate(self) -> bool:
        """
        Authenticate with AWS.
        
        Returns:
            bool: True if authentication successful
        """
        try:
            # Test authentication by getting account ID
            sts_client = self.session.client('sts')
            response = sts_client.get_caller_identity()
            self._account_id = response['Account']
            
            logger.info("AWS authentication successful", account_id=self._account_id)
            return True
            
        except (ClientError, NoCredentialsError) as e:
            logger.error("AWS authentication failed: %s", str(e))
            return False
            
    async def get_account_info(self) -> AWSSubscription:
        """
        Get AWS account information.
        
        Returns:
            AWSSubscription: Account information
        """
        if not await self.authenticate():
            raise RuntimeError("AWS authentication failed")
            
        try:
            # Get account details
            organizations_client = self.session.client('organizations')
            
            try:
                # Try to get organization info
                org_response = organizations_client.describe_organization()
                org_id = org_response['Organization']['Id']
            except ClientError:
                # Account might not be in an organization
                org_id = None
                
            # Get available regions
            ec2_client = self.session.client('ec2')
            regions_response = ec2_client.describe_regions()
            
            regions = []
            for region_data in regions_response['Regions']:
                # Get availability zones for each region
                region_ec2 = self.session.client('ec2', region_name=region_data['RegionName'])
                try:
                    azs_response = region_ec2.describe_availability_zones()
                    azs = [az['ZoneName'] for az in azs_response['AvailabilityZones']]
                except ClientError:
                    azs = []
                    
                regions.append({
                    'name': region_data['RegionName'],
                    'display_name': region_data['RegionName'].replace('-', ' ').title(),
                    'endpoint': region_data['Endpoint'],
                    'availability_zones': azs
                })
                
            return AWSSubscription(
                account_id=self._account_id,
                organization_id=org_id,
                regions=regions
            )
            
        except ClientError as e:
            logger.error("Failed to get AWS account info: %s", str(e))
            raise
            
    async def extract_ec2_instances(self, region: str) -> List[AWSEC2Instance]:
        """Extract EC2 instances from a region."""
        try:
            ec2_client = self.session.client('ec2', region_name=region)
            response = ec2_client.describe_instances()
            
            instances = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    # Extract instance details
                    instance_resource = AWSEC2Instance(
                        id=instance['InstanceId'],
                        name=self._get_tag_value(instance.get('Tags', []), 'Name', instance['InstanceId']),
                        account_id=self._account_id,
                        region=region,
                        arn=f"arn:aws:ec2:{region}:{self._account_id}:instance/{instance['InstanceId']}",
                        resource_type="ec2_instance",
                        
                        # EC2-specific fields
                        instance_id=instance['InstanceId'],
                        instance_type=instance['InstanceType'],
                        image_id=instance['ImageId'],
                        key_name=instance.get('KeyName'),
                        public_ip=instance.get('PublicIpAddress'),
                        private_ip=instance.get('PrivateIpAddress'),
                        public_dns=instance.get('PublicDnsName'),
                        private_dns=instance.get('PrivateDnsName'),
                        
                        # General fields
                        status=instance['State']['Name'],
                        availability_zone=instance['Placement']['AvailabilityZone'],
                        vpc_id=instance.get('VpcId'),
                        subnet_id=instance.get('SubnetId'),
                        security_groups=[sg['GroupId'] for sg in instance.get('SecurityGroups', [])],
                        tags=self._extract_tags(instance.get('Tags', [])),
                        launch_time=instance.get('LaunchTime'),
                        platform=instance.get('Platform', 'Linux'),
                        monitoring_enabled=instance.get('Monitoring', {}).get('State') == 'enabled',
                        ebs_optimized=instance.get('EbsOptimized', False)
                    )
                    instances.append(instance_resource)
                    
            logger.info("Extracted %d EC2 instances from region %s", len(instances), region)
            return instances
            
        except ClientError as e:
            logger.error("Failed to extract EC2 instances from region %s: %s", region, str(e))
            return []
            
    async def extract_s3_buckets(self) -> List[AWSS3Bucket]:
        """Extract S3 buckets (global service)."""
        try:
            s3_client = self.session.client('s3')
            response = s3_client.list_buckets()
            
            buckets = []
            for bucket_data in response['Buckets']:
                bucket_name = bucket_data['Name']
                
                # Get bucket location
                try:
                    location_response = s3_client.get_bucket_location(Bucket=bucket_name)
                    region = location_response['LocationConstraint'] or 'us-east-1'
                except ClientError:
                    region = 'us-east-1'
                    
                # Get bucket details
                try:
                    # Check versioning
                    versioning_response = s3_client.get_bucket_versioning(Bucket=bucket_name)
                    versioning_enabled = versioning_response.get('Status') == 'Enabled'
                    
                    # Check encryption
                    try:
                        s3_client.get_bucket_encryption(Bucket=bucket_name)
                        encryption_enabled = True
                    except ClientError:
                        encryption_enabled = False
                        
                    # Check public access
                    try:
                        acl_response = s3_client.get_bucket_acl(Bucket=bucket_name)
                        public_read = any(
                            grant['Grantee'].get('URI') == 'http://acs.amazonaws.com/groups/global/AllUsers'
                            for grant in acl_response.get('Grants', [])
                            if 'READ' in grant.get('Permission', '')
                        )
                        public_write = any(
                            grant['Grantee'].get('URI') == 'http://acs.amazonaws.com/groups/global/AllUsers'
                            for grant in acl_response.get('Grants', [])
                            if 'WRITE' in grant.get('Permission', '')
                        )
                    except ClientError:
                        public_read = public_write = False
                        
                    # Get bucket tags
                    try:
                        tags_response = s3_client.get_bucket_tagging(Bucket=bucket_name)
                        tags = {tag['Key']: tag['Value'] for tag in tags_response.get('TagSet', [])}
                    except ClientError:
                        tags = {}
                        
                    bucket_resource = AWSS3Bucket(
                        id=bucket_name,
                        name=bucket_name,
                        account_id=self._account_id,
                        region=region,
                        arn=f"arn:aws:s3:::{bucket_name}",
                        resource_type="s3_bucket",
                        
                        # S3-specific fields
                        bucket_name=bucket_name,
                        creation_date=bucket_data['CreationDate'],
                        versioning_enabled=versioning_enabled,
                        encryption_enabled=encryption_enabled,
                        public_read_enabled=public_read,
                        public_write_enabled=public_write,
                        tags=tags
                    )
                    buckets.append(bucket_resource)
                    
                except ClientError as e:
                    logger.warning("Failed to get details for S3 bucket %s: %s", bucket_name, str(e))
                    continue
                    
            logger.info("Extracted %d S3 buckets", len(buckets))
            return buckets
            
        except ClientError as e:
            logger.error("Failed to extract S3 buckets: %s", str(e))
            return []
            
    async def extract_resources_by_region(self, region: str, 
                                        resource_types: Optional[List[str]] = None) -> List[AWSResource]:
        """
        Extract AWS resources from a specific region.
        
        Args:
            region: AWS region name
            resource_types: List of resource types to extract (None for all)
            
        Returns:
            List[AWSResource]: Extracted resources
        """
        logger.info("Starting resource extraction for AWS region: %s", region)
        
        if not await self.authenticate():
            raise RuntimeError("AWS authentication failed")
            
        resources = []
        
        # Extract EC2 instances
        if not resource_types or 'ec2_instance' in resource_types:
            ec2_instances = await self.extract_ec2_instances(region)
            resources.extend(ec2_instances)
            
        # TODO: Add more resource types
        # - RDS instances
        # - VPCs 
        # - Load balancers
        # - Lambda functions
        # - ECS clusters
        
        logger.info("Extracted %d resources from AWS region %s", len(resources), region)
        return resources
        
    async def extract_global_resources(self, 
                                     resource_types: Optional[List[str]] = None) -> List[AWSResource]:
        """
        Extract AWS global resources (not tied to a specific region).
        
        Args:
            resource_types: List of resource types to extract (None for all)
            
        Returns:
            List[AWSResource]: Extracted global resources
        """
        logger.info("Starting global resource extraction for AWS")
        
        if not await self.authenticate():
            raise RuntimeError("AWS authentication failed")
            
        resources = []
        
        # Extract S3 buckets (global)
        if not resource_types or 's3_bucket' in resource_types:
            s3_buckets = await self.extract_s3_buckets()
            resources.extend(s3_buckets)
            
        # TODO: Add more global resource types
        # - IAM roles, users, policies
        # - CloudFront distributions
        # - Route53 hosted zones
        # - WAF rules
        
        logger.info("Extracted %d global resources from AWS", len(resources))
        return resources
        
    def _get_tag_value(self, tags: List[Dict[str, str]], key: str, default: str = "") -> str:
        """Get tag value by key."""
        for tag in tags:
            if tag.get('Key') == key:
                return tag.get('Value', default)
        return default
        
    def _extract_tags(self, tags: List[Dict[str, str]]) -> Dict[str, str]:
        """Convert AWS tags to dictionary."""
        return {tag['Key']: tag['Value'] for tag in tags if 'Key' in tag and 'Value' in tag}
