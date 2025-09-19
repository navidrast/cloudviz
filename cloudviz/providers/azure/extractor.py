"""
Azure resource extractor implementation.
Uses PowerShell Az modules to extract Azure resources and relationships.
Renamed from AzViz to CloudViz Legacy PowerShell Module integration.
"""

import asyncio
import json
import subprocess
import tempfile
import os
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from cloudviz.core.base import ResourceExtractor
from cloudviz.core.models import (
    ResourceInventory, ExtractionScope, CloudProvider, 
    ResourceRelationship, RelationshipType
)
from cloudviz.core.utils import get_logger, retry_with_backoff, LoggerMixin
from cloudviz.providers.azure.models import AzureResource, AzureResourceType, get_azure_resource_type_from_string


class AzureResourceExtractor(ResourceExtractor, LoggerMixin):
    """
    Azure resource extractor using PowerShell Az modules.
    Implements comprehensive Azure resource discovery and relationship mapping.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Azure resource extractor.
        
        Args:
            config: Azure-specific configuration
        """
        super().__init__(config)
        self.tenant_id = self.config.get('tenant_id')
        self.client_id = self.config.get('client_id')
        self.client_secret = self.config.get('client_secret')
        self.subscription_id = self.config.get('subscription_id')
        self.authentication_method = self.config.get('authentication_method', 'interactive')
        
        # PowerShell execution settings
        self.powershell_timeout = self.config.get('timeout', 300)
        self.max_retries = self.config.get('max_retries', 3)
        
        # Resource extraction settings
        self.include_resource_types = self.config.get('include_resource_types', [])
        self.exclude_resource_types = self.config.get('exclude_resource_types', [])
        self.include_properties = self.config.get('include_properties', True)
        self.include_tags = self.config.get('include_tags', True)
        self.include_relationships = self.config.get('include_relationships', True)
    
    async def authenticate(self) -> bool:
        """
        Authenticate with Azure using configured method.
        
        Returns:
            bool: True if authentication successful
        """
        try:
            self.log_info("Starting Azure authentication", 
                         method=self.authentication_method)
            
            if self.authentication_method == 'service_principal':
                return await self._authenticate_service_principal()
            elif self.authentication_method == 'managed_identity':
                return await self._authenticate_managed_identity()
            elif self.authentication_method == 'interactive':
                return await self._authenticate_interactive()
            elif self.authentication_method == 'device_code':
                return await self._authenticate_device_code()
            else:
                self.log_error(f"Unsupported authentication method: {self.authentication_method}")
                return False
                
        except Exception as e:
            self.log_error("Azure authentication failed", exc_info=True, error=str(e))
            return False
    
    async def _authenticate_service_principal(self) -> bool:
        """Authenticate using service principal."""
        if not all([self.tenant_id, self.client_id, self.client_secret]):
            self.log_error("Service principal credentials not provided")
            return False
        
        script = f"""
        $SecurePassword = ConvertTo-SecureString '{self.client_secret}' -AsPlainText -Force
        $Credential = New-Object System.Management.Automation.PSCredential ('{self.client_id}', $SecurePassword)
        Connect-AzAccount -ServicePrincipal -Credential $Credential -Tenant '{self.tenant_id}' -ErrorAction Stop
        Write-Output "Authentication successful"
        """
        
        result = await self._execute_powershell(script)
        if result.returncode == 0:
            self._authenticated = True
            self.log_info("Service principal authentication successful")
            return True
        else:
            self.log_error("Service principal authentication failed", error=result.stderr)
            return False
    
    async def _authenticate_managed_identity(self) -> bool:
        """Authenticate using managed identity."""
        script = """
        Connect-AzAccount -Identity -ErrorAction Stop
        Write-Output "Managed identity authentication successful"
        """
        
        result = await self._execute_powershell(script)
        if result.returncode == 0:
            self._authenticated = True
            self.log_info("Managed identity authentication successful")
            return True
        else:
            self.log_error("Managed identity authentication failed", error=result.stderr)
            return False
    
    async def _authenticate_interactive(self) -> bool:
        """Authenticate using interactive login."""
        script = """
        Connect-AzAccount -ErrorAction Stop
        Write-Output "Interactive authentication successful"
        """
        
        result = await self._execute_powershell(script)
        if result.returncode == 0:
            self._authenticated = True
            self.log_info("Interactive authentication successful")
            return True
        else:
            self.log_error("Interactive authentication failed", error=result.stderr)
            return False
    
    async def _authenticate_device_code(self) -> bool:
        """Authenticate using device code flow."""
        script = """
        Connect-AzAccount -UseDeviceAuthentication -ErrorAction Stop
        Write-Output "Device code authentication successful"
        """
        
        result = await self._execute_powershell(script)
        if result.returncode == 0:
            self._authenticated = True
            self.log_info("Device code authentication successful")
            return True
        else:
            self.log_error("Device code authentication failed", error=result.stderr)
            return False
    
    @retry_with_backoff(max_retries=3)
    async def _execute_powershell(self, script: str) -> subprocess.CompletedProcess:
        """
        Execute PowerShell script asynchronously.
        
        Args:
            script: PowerShell script to execute
            
        Returns:
            subprocess.CompletedProcess: Execution result
        """
        # Create temporary script file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False) as f:
            f.write(script)
            script_path = f.name
        
        try:
            # Execute PowerShell script
            process = await asyncio.create_subprocess_exec(
                'powershell.exe', '-ExecutionPolicy', 'Bypass', '-File', script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=self.powershell_timeout
            )
            
            return subprocess.CompletedProcess(
                args=f'powershell.exe -File {script_path}',
                returncode=process.returncode,
                stdout=stdout.decode('utf-8') if stdout else '',
                stderr=stderr.decode('utf-8') if stderr else ''
            )
            
        finally:
            # Clean up temporary file
            try:
                os.unlink(script_path)
            except OSError:
                pass
    
    async def extract_resources(
        self,
        scope: ExtractionScope,
        scope_identifier: str,
        resource_types: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> ResourceInventory:
        """
        Extract Azure resources based on scope and filters.
        
        Args:
            scope: Extraction scope (subscription, resource group, etc.)
            scope_identifier: Scope identifier
            resource_types: Optional resource type filters
            tags: Optional tag filters
            **kwargs: Additional parameters
            
        Returns:
            ResourceInventory: Complete resource inventory
        """
        if not self._authenticated:
            await self.authenticate()
        
        self.log_info("Starting Azure resource extraction",
                     scope=scope.value, identifier=scope_identifier)
        
        inventory = ResourceInventory(
            extraction_scope=scope,
            scope_identifier=scope_identifier,
            provider=CloudProvider.AZURE,
            metadata={
                'extractor': 'AzureResourceExtractor',
                'config': {k: v for k, v in self.config.items() if k != 'client_secret'}
            }
        )
        
        try:
            # Extract resources based on scope
            if scope == ExtractionScope.SUBSCRIPTION:
                resources = await self._extract_subscription_resources(scope_identifier, resource_types, tags)
            elif scope == ExtractionScope.RESOURCE_GROUP:
                resources = await self._extract_resource_group_resources(scope_identifier, resource_types, tags)
            elif scope == ExtractionScope.TAG:
                resources = await self._extract_tagged_resources(scope_identifier, tags, resource_types)
            else:
                raise ValueError(f"Unsupported extraction scope: {scope}")
            
            # Add resources to inventory
            for resource in resources:
                inventory.add_resource(resource)
            
            # Extract relationships if enabled
            if self.include_relationships and resources:
                relationships = await self.extract_resource_relationships(resources)
                for relationship in relationships:
                    inventory.add_relationship(relationship)
            
            self.log_info("Azure resource extraction completed",
                         resource_count=len(resources),
                         relationship_count=len(inventory.relationships))
            
            return inventory
            
        except Exception as e:
            self.log_error("Azure resource extraction failed", exc_info=True, error=str(e))
            raise
    
    async def _extract_subscription_resources(
        self,
        subscription_id: str,
        resource_types: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> List[AzureResource]:
        """Extract all resources from a subscription."""
        script = self._build_extraction_script(
            scope='subscription',
            identifier=subscription_id,
            resource_types=resource_types,
            tags=tags
        )
        
        result = await self._execute_powershell(script)
        if result.returncode != 0:
            raise RuntimeError(f"PowerShell execution failed: {result.stderr}")
        
        return self._parse_resources_from_output(result.stdout)
    
    async def _extract_resource_group_resources(
        self,
        resource_group_name: str,
        resource_types: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> List[AzureResource]:
        """Extract all resources from a resource group."""
        script = self._build_extraction_script(
            scope='resourcegroup',
            identifier=resource_group_name,
            resource_types=resource_types,
            tags=tags
        )
        
        result = await self._execute_powershell(script)
        if result.returncode != 0:
            raise RuntimeError(f"PowerShell execution failed: {result.stderr}")
        
        return self._parse_resources_from_output(result.stdout)
    
    async def _extract_tagged_resources(
        self,
        tag_key: str,
        tags: Optional[Dict[str, str]] = None,
        resource_types: Optional[List[str]] = None
    ) -> List[AzureResource]:
        """Extract resources based on tag filters."""
        script = self._build_extraction_script(
            scope='tag',
            identifier=tag_key,
            resource_types=resource_types,
            tags=tags
        )
        
        result = await self._execute_powershell(script)
        if result.returncode != 0:
            raise RuntimeError(f"PowerShell execution failed: {result.stderr}")
        
        return self._parse_resources_from_output(result.stdout)
    
    def _build_extraction_script(
        self,
        scope: str,
        identifier: str,
        resource_types: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> str:
        """Build PowerShell script for resource extraction."""
        
        # Base script template - modernized from AzViz legacy
        script = """
# CloudViz Azure Resource Extraction Script
# Modernized from AzViz legacy PowerShell module

# Import required modules
Import-Module Az.Resources -Force
Import-Module Az.Profile -Force

# Set error action preference
$ErrorActionPreference = 'Stop'

# Initialize results array
$Resources = @()

try {
"""
        
        # Add scope-specific logic
        if scope == 'subscription':
            script += f"""
    # Set subscription context
    Set-AzContext -SubscriptionId '{identifier}' | Out-Null
    
    # Get all resources in subscription
    $AllResources = Get-AzResource"""
            
        elif scope == 'resourcegroup':
            script += f"""
    # Get resources in resource group
    $AllResources = Get-AzResource -ResourceGroupName '{identifier}'"""
            
        elif scope == 'tag':
            if tags:
                tag_conditions = []
                for key, value in tags.items():
                    tag_conditions.append(f"$_.Tags['{key}'] -eq '{value}'")
                tag_filter = " -and ".join(tag_conditions)
                script += f"""
    # Get resources with specific tags
    $AllResources = Get-AzResource | Where-Object {{ {tag_filter} }}"""
            else:
                script += f"""
    # Get resources with tag key
    $AllResources = Get-AzResource | Where-Object {{ $_.Tags.ContainsKey('{identifier}') }}"""
        
        # Add resource type filtering if specified
        if resource_types:
            types_filter = "'" + "', '".join(resource_types) + "'"
            script += f"""
    
    # Filter by resource types
    $AllResources = $AllResources | Where-Object {{ $_.ResourceType -in @({types_filter}) }}"""
        
        # Add main extraction logic
        script += """

    # Process each resource
    foreach ($Resource in $AllResources) {
        try {
            # Get detailed resource information
            $DetailedResource = Get-AzResource -ResourceId $Resource.ResourceId
            
            # Create resource object
            $ResourceObj = @{
                id = $Resource.ResourceId
                name = $Resource.Name
                type = $Resource.ResourceType
                location = $Resource.Location
                resourceGroup = $Resource.ResourceGroupName
                subscriptionId = $Resource.SubscriptionId
                tags = $Resource.Tags
                properties = $DetailedResource.Properties
                kind = $DetailedResource.Kind
                sku = $DetailedResource.Sku
                identity = $DetailedResource.Identity
                zones = $DetailedResource.Zones
                managedBy = $DetailedResource.ManagedBy
                createdTime = $DetailedResource.CreatedTime
                changedTime = $DetailedResource.ChangedTime
                provisioningState = $DetailedResource.Properties.provisioningState
            }
            
            $Resources += $ResourceObj
            
        } catch {
            Write-Warning "Failed to process resource $($Resource.Name): $($_.Exception.Message)"
        }
    }
    
    # Output results as JSON
    $Resources | ConvertTo-Json -Depth 10 -Compress

} catch {
    Write-Error "Resource extraction failed: $($_.Exception.Message)"
    exit 1
}
"""
        
        return script
    
    def _parse_resources_from_output(self, output: str) -> List[AzureResource]:
        """Parse Azure resources from PowerShell JSON output."""
        resources = []
        
        try:
            # Parse JSON output
            if not output.strip():
                return resources
            
            data = json.loads(output)
            if not isinstance(data, list):
                data = [data]
            
            for resource_data in data:
                resource = self._create_azure_resource_from_data(resource_data)
                if resource:
                    resources.append(resource)
                    
        except json.JSONDecodeError as e:
            self.log_error("Failed to parse resource JSON", error=str(e), output=output[:500])
        except Exception as e:
            self.log_error("Failed to process resource data", exc_info=True, error=str(e))
        
        return resources
    
    def _create_azure_resource_from_data(self, data: Dict[str, Any]) -> Optional[AzureResource]:
        """Create AzureResource object from parsed data."""
        try:
            # Get Azure resource type
            type_string = data.get('type', '')
            azure_type = get_azure_resource_type_from_string(type_string)
            
            # Create Azure resource
            resource = AzureResource(
                id=data.get('id', ''),
                name=data.get('name', ''),
                resource_type=None,  # Will be set by azure type
                provider=CloudProvider.AZURE,
                region=data.get('location', ''),
                metadata={
                    'type': type_string,
                    'extracted_at': datetime.now().isoformat(),
                    'source': 'powershell_az_modules'
                },
                tags=data.get('tags') or {},
                properties=data.get('properties') or {},
                resource_group_name=data.get('resourceGroup'),
                subscription_id=data.get('subscriptionId'),
                provisioning_state=data.get('provisioningState'),
                kind=data.get('kind'),
                sku=data.get('sku'),
                identity=data.get('identity'),
                zones=data.get('zones'),
                managed_by=data.get('managedBy'),
                created_time=self._parse_datetime(data.get('createdTime')),
                last_modified=self._parse_datetime(data.get('changedTime'))
            )
            
            # Set Azure resource type
            resource.set_azure_resource_type(azure_type)
            
            return resource
            
        except Exception as e:
            self.log_error("Failed to create Azure resource", exc_info=True, 
                          error=str(e), resource_data=data)
            return None
    
    def _parse_datetime(self, date_string: Optional[str]) -> Optional[datetime]:
        """Parse datetime string from Azure."""
        if not date_string:
            return None
        
        try:
            # Handle various Azure datetime formats
            formats = [
                '%Y-%m-%dT%H:%M:%S.%fZ',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d %H:%M:%S'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_string, fmt)
                except ValueError:
                    continue
            
            # If no format matches, try parsing as ISO format
            return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            
        except Exception:
            self.log_warning(f"Failed to parse datetime: {date_string}")
            return None
    
    async def extract_resource_relationships(
        self,
        resources: List[AzureResource]
    ) -> List[ResourceRelationship]:
        """
        Extract relationships between Azure resources.
        
        Args:
            resources: List of Azure resources
            
        Returns:
            List[ResourceRelationship]: Discovered relationships
        """
        relationships = []
        
        try:
            self.log_info("Extracting Azure resource relationships", 
                         resource_count=len(resources))
            
            # Build resource lookup
            resource_lookup = {resource.id: resource for resource in resources}
            
            # Extract different types of relationships
            relationships.extend(self._extract_containment_relationships(resources))
            relationships.extend(self._extract_network_relationships(resources, resource_lookup))
            relationships.extend(self._extract_dependency_relationships(resources, resource_lookup))
            relationships.extend(self._extract_management_relationships(resources, resource_lookup))
            
            self.log_info("Resource relationship extraction completed",
                         relationship_count=len(relationships))
            
        except Exception as e:
            self.log_error("Failed to extract resource relationships", exc_info=True, error=str(e))
        
        return relationships
    
    def _extract_containment_relationships(self, resources: List[AzureResource]) -> List[ResourceRelationship]:
        """Extract containment relationships (resource group -> resources)."""
        relationships = []
        
        # Group resources by resource group
        by_resource_group = {}
        resource_groups = {}
        
        for resource in resources:
            if resource.get_azure_resource_type() == AzureResourceType.RESOURCE_GROUP:
                resource_groups[resource.name] = resource
            elif resource.resource_group_name:
                if resource.resource_group_name not in by_resource_group:
                    by_resource_group[resource.resource_group_name] = []
                by_resource_group[resource.resource_group_name].append(resource)
        
        # Create containment relationships
        for rg_name, rg_resources in by_resource_group.items():
            if rg_name in resource_groups:
                rg_resource = resource_groups[rg_name]
                for resource in rg_resources:
                    relationships.append(ResourceRelationship(
                        source_id=rg_resource.id,
                        target_id=resource.id,
                        relationship_type=RelationshipType.CONTAINS,
                        properties={'type': 'resource_group_containment'}
                    ))
        
        return relationships
    
    def _extract_network_relationships(
        self,
        resources: List[AzureResource],
        resource_lookup: Dict[str, AzureResource]
    ) -> List[ResourceRelationship]:
        """Extract network-related relationships."""
        relationships = []
        
        # Find network-related resources
        vnets = [r for r in resources if r.get_azure_resource_type() == AzureResourceType.VIRTUAL_NETWORK]
        subnets = [r for r in resources if r.get_azure_resource_type() == AzureResourceType.SUBNET]
        nics = [r for r in resources if r.get_azure_resource_type() == AzureResourceType.NETWORK_INTERFACE]
        nsgs = [r for r in resources if r.get_azure_resource_type() == AzureResourceType.NETWORK_SECURITY_GROUP]
        
        # VNet -> Subnet relationships
        for subnet in subnets:
            subnet_id_parts = subnet.id.split('/')
            if '/virtualNetworks/' in subnet.id:
                vnet_id = '/'.join(subnet_id_parts[:subnet_id_parts.index('subnets')])
                if vnet_id in resource_lookup:
                    relationships.append(ResourceRelationship(
                        source_id=vnet_id,
                        target_id=subnet.id,
                        relationship_type=RelationshipType.CONTAINS,
                        properties={'type': 'vnet_subnet_containment'}
                    ))
        
        # NIC -> Subnet relationships (from properties)
        for nic in nics:
            if nic.properties:
                ip_configs = nic.properties.get('ipConfigurations', [])
                for ip_config in ip_configs:
                    if isinstance(ip_config, dict):
                        subnet_ref = ip_config.get('subnet', {})
                        if isinstance(subnet_ref, dict):
                            subnet_id = subnet_ref.get('id')
                            if subnet_id and subnet_id in resource_lookup:
                                relationships.append(ResourceRelationship(
                                    source_id=nic.id,
                                    target_id=subnet_id,
                                    relationship_type=RelationshipType.CONNECTS_TO,
                                    properties={'type': 'nic_subnet_connection'}
                                ))
        
        return relationships
    
    def _extract_dependency_relationships(
        self,
        resources: List[AzureResource],
        resource_lookup: Dict[str, AzureResource]
    ) -> List[ResourceRelationship]:
        """Extract dependency relationships between resources."""
        relationships = []
        
        # Look for dependencies in resource properties
        for resource in resources:
            if resource.properties:
                dependencies = self._find_resource_dependencies(resource.properties)
                for dep_id in dependencies:
                    if dep_id in resource_lookup:
                        relationships.append(ResourceRelationship(
                            source_id=resource.id,
                            target_id=dep_id,
                            relationship_type=RelationshipType.DEPENDS_ON,
                            properties={'type': 'resource_dependency'}
                        ))
        
        return relationships
    
    def _extract_management_relationships(
        self,
        resources: List[AzureResource],
        resource_lookup: Dict[str, AzureResource]
    ) -> List[ResourceRelationship]:
        """Extract management relationships (managed by, etc.)."""
        relationships = []
        
        for resource in resources:
            if resource.managed_by and resource.managed_by in resource_lookup:
                relationships.append(ResourceRelationship(
                    source_id=resource.id,
                    target_id=resource.managed_by,
                    relationship_type=RelationshipType.MANAGED_BY,
                    properties={'type': 'managed_by_relationship'}
                ))
        
        return relationships
    
    def _find_resource_dependencies(self, properties: Dict[str, Any]) -> List[str]:
        """Find resource IDs referenced in properties."""
        dependencies = []
        
        def extract_resource_ids(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key in ['id', 'resourceId'] and isinstance(value, str) and '/subscriptions/' in value:
                        dependencies.append(value)
                    else:
                        extract_resource_ids(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    extract_resource_ids(item, f"{path}[{i}]")
        
        extract_resource_ids(properties)
        return list(set(dependencies))  # Remove duplicates
    
    async def get_available_scopes(self) -> Dict[str, List[str]]:
        """Get available Azure scopes for the authenticated user."""
        if not self._authenticated:
            await self.authenticate()
        
        scopes = {}
        
        try:
            # Get subscriptions
            script = """
            Get-AzSubscription | Select-Object Id, Name | ConvertTo-Json -Depth 2
            """
            result = await self._execute_powershell(script)
            if result.returncode == 0:
                subscriptions = json.loads(result.stdout or '[]')
                if not isinstance(subscriptions, list):
                    subscriptions = [subscriptions]
                scopes['subscriptions'] = [sub['Id'] for sub in subscriptions]
            
            # Get resource groups from current subscription
            script = """
            Get-AzResourceGroup | Select-Object ResourceGroupName | ConvertTo-Json -Depth 2
            """
            result = await self._execute_powershell(script)
            if result.returncode == 0:
                resource_groups = json.loads(result.stdout or '[]')
                if not isinstance(resource_groups, list):
                    resource_groups = [resource_groups]
                scopes['resource_groups'] = [rg['ResourceGroupName'] for rg in resource_groups]
            
        except Exception as e:
            self.log_error("Failed to get available scopes", exc_info=True, error=str(e))
        
        return scopes
    
    async def validate_scope(self, scope: ExtractionScope, scope_identifier: str) -> bool:
        """Validate Azure scope accessibility."""
        if not self._authenticated:
            await self.authenticate()
        
        try:
            if scope == ExtractionScope.SUBSCRIPTION:
                script = f"Get-AzSubscription -SubscriptionId '{scope_identifier}' | Out-Null"
            elif scope == ExtractionScope.RESOURCE_GROUP:
                script = f"Get-AzResourceGroup -Name '{scope_identifier}' | Out-Null"
            else:
                return True  # Tag-based scopes are always valid
            
            result = await self._execute_powershell(script)
            return result.returncode == 0
            
        except Exception as e:
            self.log_error("Scope validation failed", exc_info=True, 
                          scope=scope.value, identifier=scope_identifier, error=str(e))
            return False
    
    def get_supported_resource_types(self) -> List[str]:
        """Get list of supported Azure resource types."""
        return [rt.value for rt in AzureResourceType]
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get Azure provider information."""
        return {
            'name': 'AzureResourceExtractor',
            'provider': 'azure',
            'version': '1.0.0',
            'supported_scopes': [
                ExtractionScope.SUBSCRIPTION.value,
                ExtractionScope.RESOURCE_GROUP.value,
                ExtractionScope.TAG.value
            ],
            'supported_resource_types': self.get_supported_resource_types(),
            'authentication_methods': [
                'service_principal',
                'managed_identity',
                'interactive',
                'device_code'
            ],
            'requires_powershell': True,
            'required_modules': ['Az.Resources', 'Az.Profile']
        }
