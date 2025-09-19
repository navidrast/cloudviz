"""
Azure-specific models and enums for CloudViz platform.
Extends base models with Azure-specific properties and resource types.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from cloudviz.core.models import CloudResource, ResourceType, CloudProvider


class AzureResourceType(Enum):
    """Extended Azure resource types."""
    # Compute
    VIRTUAL_MACHINE = "Microsoft.Compute/virtualMachines"
    VIRTUAL_MACHINE_SCALE_SET = "Microsoft.Compute/virtualMachineScaleSets"
    AVAILABILITY_SET = "Microsoft.Compute/availabilitySets"
    DISK = "Microsoft.Compute/disks"
    SNAPSHOT = "Microsoft.Compute/snapshots"
    IMAGE = "Microsoft.Compute/images"
    
    # Container Services
    CONTAINER_INSTANCE = "Microsoft.ContainerInstance/containerGroups"
    KUBERNETES_SERVICE = "Microsoft.ContainerService/managedClusters"
    CONTAINER_REGISTRY = "Microsoft.ContainerRegistry/registries"
    
    # App Services
    APP_SERVICE = "Microsoft.Web/sites"
    APP_SERVICE_PLAN = "Microsoft.Web/serverfarms"
    FUNCTION_APP = "Microsoft.Web/sites"
    STATIC_WEB_APP = "Microsoft.Web/staticSites"
    
    # Storage
    STORAGE_ACCOUNT = "Microsoft.Storage/storageAccounts"
    
    # Database
    SQL_SERVER = "Microsoft.Sql/servers"
    SQL_DATABASE = "Microsoft.Sql/servers/databases"
    COSMOS_DB = "Microsoft.DocumentDB/databaseAccounts"
    MYSQL_SERVER = "Microsoft.DBforMySQL/servers"
    POSTGRESQL_SERVER = "Microsoft.DBforPostgreSQL/servers"
    REDIS_CACHE = "Microsoft.Cache/Redis"
    
    # Networking
    VIRTUAL_NETWORK = "Microsoft.Network/virtualNetworks"
    SUBNET = "Microsoft.Network/virtualNetworks/subnets"
    NETWORK_SECURITY_GROUP = "Microsoft.Network/networkSecurityGroups"
    PUBLIC_IP = "Microsoft.Network/publicIPAddresses"
    LOAD_BALANCER = "Microsoft.Network/loadBalancers"
    APPLICATION_GATEWAY = "Microsoft.Network/applicationGateways"
    VPN_GATEWAY = "Microsoft.Network/virtualNetworkGateways"
    NETWORK_INTERFACE = "Microsoft.Network/networkInterfaces"
    ROUTE_TABLE = "Microsoft.Network/routeTables"
    TRAFFIC_MANAGER = "Microsoft.Network/trafficManagerProfiles"
    
    # Security
    KEY_VAULT = "Microsoft.KeyVault/vaults"
    
    # Management
    RESOURCE_GROUP = "Microsoft.Resources/resourceGroups"
    SUBSCRIPTION = "Microsoft.Resources/subscriptions"
    MANAGEMENT_GROUP = "Microsoft.Management/managementGroups"
    
    # Monitoring
    LOG_ANALYTICS_WORKSPACE = "Microsoft.OperationalInsights/workspaces"
    APPLICATION_INSIGHTS = "Microsoft.Insights/components"
    
    # AI/ML
    COGNITIVE_SERVICES = "Microsoft.CognitiveServices/accounts"
    MACHINE_LEARNING_WORKSPACE = "Microsoft.MachineLearningServices/workspaces"
    
    # Integration
    SERVICE_BUS = "Microsoft.ServiceBus/namespaces"
    EVENT_HUB = "Microsoft.EventHub/namespaces"
    LOGIC_APP = "Microsoft.Logic/workflows"
    API_MANAGEMENT = "Microsoft.ApiManagement/service"
    
    # IoT
    IOT_HUB = "Microsoft.Devices/IotHubs"
    
    # Other
    OTHER = "Other"


@dataclass
class AzureResource(CloudResource):
    """
    Azure-specific resource model extending CloudResource.
    """
    resource_group_name: Optional[str] = None
    subscription_name: Optional[str] = None
    tenant_id: Optional[str] = None
    provisioning_state: Optional[str] = None
    created_by: Optional[str] = None
    managed_by: Optional[str] = None
    kind: Optional[str] = None
    sku: Optional[Dict[str, Any]] = None
    identity: Optional[Dict[str, Any]] = None
    zones: Optional[List[str]] = None
    
    def __post_init__(self):
        """Post-initialization processing for Azure resources."""
        super().__post_init__()
        
        # Set provider to Azure
        self.provider = CloudProvider.AZURE
        
        # Extract resource group from ID if not set
        if not self.resource_group_name and self.id:
            self.resource_group_name = self._extract_resource_group_from_id()
        
        # Set resource group property for compatibility
        if self.resource_group_name:
            self.resource_group = self.resource_group_name
    
    def _extract_resource_group_from_id(self) -> Optional[str]:
        """Extract resource group name from Azure resource ID."""
        if not self.id:
            return None
        
        # Azure resource ID format: /subscriptions/{sub}/resourceGroups/{rg}/providers/{provider}/{type}/{name}
        parts = self.id.split('/')
        try:
            rg_index = parts.index('resourceGroups')
            if rg_index + 1 < len(parts):
                return parts[rg_index + 1]
        except (ValueError, IndexError):
            pass
        
        return None
    
    def get_azure_resource_type(self) -> Optional[AzureResourceType]:
        """Get Azure-specific resource type."""
        if hasattr(self, '_azure_type'):
            return self._azure_type
        
        # Try to map from properties
        type_str = self.properties.get('type') or self.metadata.get('type')
        if type_str:
            try:
                return AzureResourceType(type_str)
            except ValueError:
                return AzureResourceType.OTHER
        
        return None
    
    def set_azure_resource_type(self, azure_type: AzureResourceType):
        """Set Azure-specific resource type and map to generic type."""
        self._azure_type = azure_type
        
        # Map to generic resource type
        type_mapping = {
            AzureResourceType.VIRTUAL_MACHINE: ResourceType.VIRTUAL_MACHINE,
            AzureResourceType.VIRTUAL_MACHINE_SCALE_SET: ResourceType.VIRTUAL_MACHINE,
            AzureResourceType.CONTAINER_INSTANCE: ResourceType.CONTAINER_INSTANCE,
            AzureResourceType.KUBERNETES_SERVICE: ResourceType.KUBERNETES_CLUSTER,
            AzureResourceType.APP_SERVICE: ResourceType.SERVERLESS_FUNCTION,
            AzureResourceType.FUNCTION_APP: ResourceType.SERVERLESS_FUNCTION,
            AzureResourceType.STORAGE_ACCOUNT: ResourceType.STORAGE_ACCOUNT,
            AzureResourceType.SQL_DATABASE: ResourceType.DATABASE,
            AzureResourceType.COSMOS_DB: ResourceType.DATABASE,
            AzureResourceType.MYSQL_SERVER: ResourceType.DATABASE,
            AzureResourceType.POSTGRESQL_SERVER: ResourceType.DATABASE,
            AzureResourceType.REDIS_CACHE: ResourceType.CACHE,
            AzureResourceType.VIRTUAL_NETWORK: ResourceType.VIRTUAL_NETWORK,
            AzureResourceType.SUBNET: ResourceType.SUBNET,
            AzureResourceType.LOAD_BALANCER: ResourceType.LOAD_BALANCER,
            AzureResourceType.APPLICATION_GATEWAY: ResourceType.APPLICATION_GATEWAY,
            AzureResourceType.VPN_GATEWAY: ResourceType.VPN_GATEWAY,
            AzureResourceType.NETWORK_SECURITY_GROUP: ResourceType.SECURITY_GROUP,
            AzureResourceType.KEY_VAULT: ResourceType.KEY_VAULT,
            AzureResourceType.RESOURCE_GROUP: ResourceType.RESOURCE_GROUP,
            AzureResourceType.SUBSCRIPTION: ResourceType.SUBSCRIPTION
        }
        
        self.resource_type = type_mapping.get(azure_type, ResourceType.OTHER)
    
    def get_management_hierarchy(self) -> Dict[str, Optional[str]]:
        """Get Azure management hierarchy information."""
        return {
            'tenant_id': self.tenant_id,
            'subscription_id': self.subscription_id,
            'subscription_name': self.subscription_name,
            'resource_group': self.resource_group_name
        }
    
    def get_cost_information(self) -> Dict[str, Any]:
        """Get cost-related information if available."""
        cost_info = {}
        
        # Extract cost center from tags
        if self.tags:
            cost_info['cost_center'] = self.tags.get('CostCenter') or self.tags.get('costCenter')
            cost_info['project'] = self.tags.get('Project') or self.tags.get('project')
            cost_info['department'] = self.tags.get('Department') or self.tags.get('department')
        
        # Extract SKU information
        if self.sku:
            cost_info['sku_name'] = self.sku.get('name')
            cost_info['sku_tier'] = self.sku.get('tier')
            cost_info['sku_size'] = self.sku.get('size')
        
        return cost_info
    
    def get_compliance_information(self) -> Dict[str, Any]:
        """Get compliance-related information."""
        compliance_info = {}
        
        if self.tags:
            compliance_info['environment'] = self.tags.get('Environment') or self.tags.get('environment')
            compliance_info['data_classification'] = self.tags.get('DataClassification')
            compliance_info['compliance_scope'] = self.tags.get('ComplianceScope')
            compliance_info['retention_policy'] = self.tags.get('RetentionPolicy')
        
        return compliance_info
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Azure resource to dictionary with Azure-specific fields."""
        data = super().to_dict()
        
        # Add Azure-specific fields
        data.update({
            'resource_group_name': self.resource_group_name,
            'subscription_name': self.subscription_name,
            'tenant_id': self.tenant_id,
            'provisioning_state': self.provisioning_state,
            'created_by': self.created_by,
            'managed_by': self.managed_by,
            'kind': self.kind,
            'sku': self.sku,
            'identity': self.identity,
            'zones': self.zones
        })
        
        # Add Azure resource type if available
        azure_type = self.get_azure_resource_type()
        if azure_type:
            data['azure_resource_type'] = azure_type.value
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AzureResource':
        """Create AzureResource from dictionary."""
        # Extract Azure-specific fields
        azure_fields = {
            'resource_group_name': data.pop('resource_group_name', None),
            'subscription_name': data.pop('subscription_name', None),
            'tenant_id': data.pop('tenant_id', None),
            'provisioning_state': data.pop('provisioning_state', None),
            'created_by': data.pop('created_by', None),
            'managed_by': data.pop('managed_by', None),
            'kind': data.pop('kind', None),
            'sku': data.pop('sku', None),
            'identity': data.pop('identity', None),
            'zones': data.pop('zones', None)
        }
        
        # Create base resource
        resource = cls(**{**data, **azure_fields})
        
        # Set Azure resource type if available
        azure_type_str = data.get('azure_resource_type')
        if azure_type_str:
            try:
                azure_type = AzureResourceType(azure_type_str)
                resource.set_azure_resource_type(azure_type)
            except ValueError:
                pass
        
        return resource


def get_azure_resource_type_from_string(type_string: str) -> AzureResourceType:
    """
    Get Azure resource type enum from string.
    
    Args:
        type_string: Azure resource type string
        
    Returns:
        AzureResourceType: Matching enum value or OTHER
    """
    try:
        return AzureResourceType(type_string)
    except ValueError:
        return AzureResourceType.OTHER


def map_azure_to_generic_resource_type(azure_type: AzureResourceType) -> ResourceType:
    """
    Map Azure resource type to generic resource type.
    
    Args:
        azure_type: Azure resource type
        
    Returns:
        ResourceType: Generic resource type
    """
    mapping = {
        AzureResourceType.VIRTUAL_MACHINE: ResourceType.VIRTUAL_MACHINE,
        AzureResourceType.VIRTUAL_MACHINE_SCALE_SET: ResourceType.VIRTUAL_MACHINE,
        AzureResourceType.CONTAINER_INSTANCE: ResourceType.CONTAINER_INSTANCE,
        AzureResourceType.KUBERNETES_SERVICE: ResourceType.KUBERNETES_CLUSTER,
        AzureResourceType.APP_SERVICE: ResourceType.SERVERLESS_FUNCTION,
        AzureResourceType.FUNCTION_APP: ResourceType.SERVERLESS_FUNCTION,
        AzureResourceType.STORAGE_ACCOUNT: ResourceType.STORAGE_ACCOUNT,
        AzureResourceType.SQL_DATABASE: ResourceType.DATABASE,
        AzureResourceType.COSMOS_DB: ResourceType.DATABASE,
        AzureResourceType.MYSQL_SERVER: ResourceType.DATABASE,
        AzureResourceType.POSTGRESQL_SERVER: ResourceType.DATABASE,
        AzureResourceType.REDIS_CACHE: ResourceType.CACHE,
        AzureResourceType.VIRTUAL_NETWORK: ResourceType.VIRTUAL_NETWORK,
        AzureResourceType.SUBNET: ResourceType.SUBNET,
        AzureResourceType.LOAD_BALANCER: ResourceType.LOAD_BALANCER,
        AzureResourceType.APPLICATION_GATEWAY: ResourceType.APPLICATION_GATEWAY,
        AzureResourceType.VPN_GATEWAY: ResourceType.VPN_GATEWAY,
        AzureResourceType.NETWORK_SECURITY_GROUP: ResourceType.SECURITY_GROUP,
        AzureResourceType.KEY_VAULT: ResourceType.KEY_VAULT,
        AzureResourceType.RESOURCE_GROUP: ResourceType.RESOURCE_GROUP,
        AzureResourceType.SUBSCRIPTION: ResourceType.SUBSCRIPTION
    }
    
    return mapping.get(azure_type, ResourceType.OTHER)
