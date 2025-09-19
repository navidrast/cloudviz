"""
Core data models for CloudViz platform.
Defines the foundational data structures for cloud resources, relationships, and extraction scopes.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
import json


class ResourceType(Enum):
    """Enumeration of supported cloud resource types."""
    # Compute
    VIRTUAL_MACHINE = "virtual_machine"
    CONTAINER_INSTANCE = "container_instance"
    KUBERNETES_CLUSTER = "kubernetes_cluster"
    SERVERLESS_FUNCTION = "serverless_function"
    
    # Storage
    STORAGE_ACCOUNT = "storage_account"
    DATABASE = "database"
    CACHE = "cache"
    BLOB_STORAGE = "blob_storage"
    OBJECT_STORAGE = "object_storage"
    
    # Networking
    VIRTUAL_NETWORK = "virtual_network"
    SUBNET = "subnet"
    LOAD_BALANCER = "load_balancer"
    APPLICATION_GATEWAY = "application_gateway"
    VPN_GATEWAY = "vpn_gateway"
    
    # Security
    KEY_VAULT = "key_vault"
    SECURITY_GROUP = "security_group"
    FIREWALL = "firewall"
    
    # Management
    RESOURCE_GROUP = "resource_group"
    SUBSCRIPTION = "subscription"
    MANAGEMENT_GROUP = "management_group"
    
    # Other
    OTHER = "other"


class CloudProvider(Enum):
    """Supported cloud providers."""
    AZURE = "azure"
    AWS = "aws"
    GCP = "gcp"


class RelationshipType(Enum):
    """Types of relationships between cloud resources."""
    CONTAINS = "contains"
    CONNECTS_TO = "connects_to"
    DEPENDS_ON = "depends_on"
    MANAGED_BY = "managed_by"
    SECURED_BY = "secured_by"
    ROUTES_TO = "routes_to"
    REPLICATES_TO = "replicates_to"
    BACKS_UP_TO = "backs_up_to"


class ExtractionScope(Enum):
    """Defines the scope of resource extraction."""
    SUBSCRIPTION = "subscription"
    RESOURCE_GROUP = "resource_group"
    TAG = "tag"
    REGION = "region"
    ORGANIZATION = "organization"
    PROJECT = "project"
    ACCOUNT = "account"


@dataclass
class CloudResource:
    """
    Represents a cloud resource with comprehensive metadata.
    
    This is the core data model for all cloud resources across providers.
    """
    id: str
    name: str
    resource_type: ResourceType
    provider: CloudProvider
    region: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)
    properties: Dict[str, Any] = field(default_factory=dict)
    created_time: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    resource_group: Optional[str] = None
    subscription_id: Optional[str] = None
    parent_resource: Optional[str] = None
    state: Optional[str] = None
    location: Optional[str] = None
    size: Optional[str] = None
    cost_center: Optional[str] = None
    owner: Optional[str] = None
    environment: Optional[str] = None
    
    def __post_init__(self):
        """Post-initialization processing."""
        if self.location is None:
            self.location = self.region
        
        # Ensure datetime objects
        if isinstance(self.created_time, str):
            self.created_time = datetime.fromisoformat(self.created_time.replace('Z', '+00:00'))
        if isinstance(self.last_modified, str):
            self.last_modified = datetime.fromisoformat(self.last_modified.replace('Z', '+00:00'))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert resource to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'resource_type': self.resource_type.value,
            'provider': self.provider.value,
            'region': self.region,
            'metadata': self.metadata,
            'tags': self.tags,
            'properties': self.properties,
            'created_time': self.created_time.isoformat() if self.created_time else None,
            'last_modified': self.last_modified.isoformat() if self.last_modified else None,
            'resource_group': self.resource_group,
            'subscription_id': self.subscription_id,
            'parent_resource': self.parent_resource,
            'state': self.state,
            'location': self.location,
            'size': self.size,
            'cost_center': self.cost_center,
            'owner': self.owner,
            'environment': self.environment
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CloudResource':
        """Create CloudResource from dictionary representation."""
        # Convert enum strings back to enums
        data['resource_type'] = ResourceType(data['resource_type'])
        data['provider'] = CloudProvider(data['provider'])
        
        return cls(**data)
    
    def to_json(self) -> str:
        """Convert resource to JSON string."""
        return json.dumps(self.to_dict(), indent=2, default=str)
    
    def get_display_name(self) -> str:
        """Get human-readable display name for the resource."""
        if self.tags.get('DisplayName'):
            return self.tags['DisplayName']
        if self.tags.get('Name'):
            return self.tags['Name']
        return self.name
    
    def get_category(self) -> str:
        """Get resource category for visualization grouping."""
        type_categories = {
            ResourceType.VIRTUAL_MACHINE: "Compute",
            ResourceType.CONTAINER_INSTANCE: "Compute", 
            ResourceType.KUBERNETES_CLUSTER: "Compute",
            ResourceType.SERVERLESS_FUNCTION: "Compute",
            ResourceType.STORAGE_ACCOUNT: "Storage",
            ResourceType.DATABASE: "Storage",
            ResourceType.CACHE: "Storage",
            ResourceType.BLOB_STORAGE: "Storage",
            ResourceType.OBJECT_STORAGE: "Storage",
            ResourceType.VIRTUAL_NETWORK: "Networking",
            ResourceType.SUBNET: "Networking",
            ResourceType.LOAD_BALANCER: "Networking",
            ResourceType.APPLICATION_GATEWAY: "Networking",
            ResourceType.VPN_GATEWAY: "Networking",
            ResourceType.KEY_VAULT: "Security",
            ResourceType.SECURITY_GROUP: "Security",
            ResourceType.FIREWALL: "Security",
            ResourceType.RESOURCE_GROUP: "Management",
            ResourceType.SUBSCRIPTION: "Management",
            ResourceType.MANAGEMENT_GROUP: "Management"
        }
        return type_categories.get(self.resource_type, "Other")


@dataclass
class ResourceRelationship:
    """
    Represents a relationship between two cloud resources.
    """
    source_id: str
    target_id: str
    relationship_type: RelationshipType
    properties: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    strength: float = 1.0  # Relationship strength for visualization
    bidirectional: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert relationship to dictionary representation."""
        return {
            'source_id': self.source_id,
            'target_id': self.target_id,
            'relationship_type': self.relationship_type.value,
            'properties': self.properties,
            'metadata': self.metadata,
            'strength': self.strength,
            'bidirectional': self.bidirectional
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResourceRelationship':
        """Create ResourceRelationship from dictionary representation."""
        data['relationship_type'] = RelationshipType(data['relationship_type'])
        return cls(**data)
    
    def get_edge_label(self) -> str:
        """Get label for visualization edges."""
        labels = {
            RelationshipType.CONTAINS: "contains",
            RelationshipType.CONNECTS_TO: "connects to",
            RelationshipType.DEPENDS_ON: "depends on",
            RelationshipType.MANAGED_BY: "managed by",
            RelationshipType.SECURED_BY: "secured by",
            RelationshipType.ROUTES_TO: "routes to",
            RelationshipType.REPLICATES_TO: "replicates to",
            RelationshipType.BACKS_UP_TO: "backs up to"
        }
        return labels.get(self.relationship_type, self.relationship_type.value)


@dataclass
class ResourceInventory:
    """
    Container for a complete set of resources and their relationships.
    """
    resources: List[CloudResource] = field(default_factory=list)
    relationships: List[ResourceRelationship] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    extraction_time: datetime = field(default_factory=datetime.now)
    extraction_scope: Optional[ExtractionScope] = None
    scope_identifier: Optional[str] = None
    provider: Optional[CloudProvider] = None
    
    def add_resource(self, resource: CloudResource):
        """Add a resource to the inventory."""
        self.resources.append(resource)
    
    def add_relationship(self, relationship: ResourceRelationship):
        """Add a relationship to the inventory."""
        self.relationships.append(relationship)
    
    def get_resource_by_id(self, resource_id: str) -> Optional[CloudResource]:
        """Get a resource by its ID."""
        for resource in self.resources:
            if resource.id == resource_id:
                return resource
        return None
    
    def get_resources_by_type(self, resource_type: ResourceType) -> List[CloudResource]:
        """Get all resources of a specific type."""
        return [r for r in self.resources if r.resource_type == resource_type]
    
    def get_resources_by_tag(self, tag_key: str, tag_value: Optional[str] = None) -> List[CloudResource]:
        """Get resources by tag key and optionally value."""
        if tag_value is None:
            return [r for r in self.resources if tag_key in r.tags]
        return [r for r in self.resources if r.tags.get(tag_key) == tag_value]
    
    def get_resource_relationships(self, resource_id: str) -> List[ResourceRelationship]:
        """Get all relationships for a specific resource."""
        return [r for r in self.relationships 
                if r.source_id == resource_id or r.target_id == resource_id]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert inventory to dictionary representation."""
        return {
            'resources': [r.to_dict() for r in self.resources],
            'relationships': [r.to_dict() for r in self.relationships],
            'metadata': self.metadata,
            'extraction_time': self.extraction_time.isoformat(),
            'extraction_scope': self.extraction_scope.value if self.extraction_scope else None,
            'scope_identifier': self.scope_identifier,
            'provider': self.provider.value if self.provider else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResourceInventory':
        """Create ResourceInventory from dictionary representation."""
        inventory = cls()
        inventory.resources = [CloudResource.from_dict(r) for r in data.get('resources', [])]
        inventory.relationships = [ResourceRelationship.from_dict(r) for r in data.get('relationships', [])]
        inventory.metadata = data.get('metadata', {})
        inventory.extraction_time = datetime.fromisoformat(data['extraction_time'])
        inventory.extraction_scope = ExtractionScope(data['extraction_scope']) if data.get('extraction_scope') else None
        inventory.scope_identifier = data.get('scope_identifier')
        inventory.provider = CloudProvider(data['provider']) if data.get('provider') else None
        return inventory
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get inventory statistics."""
        stats = {
            'total_resources': len(self.resources),
            'total_relationships': len(self.relationships),
            'resource_types': {},
            'providers': {},
            'regions': {},
            'resource_groups': {}
        }
        
        for resource in self.resources:
            # Count by type
            type_name = resource.resource_type.value
            stats['resource_types'][type_name] = stats['resource_types'].get(type_name, 0) + 1
            
            # Count by provider
            provider_name = resource.provider.value
            stats['providers'][provider_name] = stats['providers'].get(provider_name, 0) + 1
            
            # Count by region
            stats['regions'][resource.region] = stats['regions'].get(resource.region, 0) + 1
            
            # Count by resource group
            if resource.resource_group:
                stats['resource_groups'][resource.resource_group] = stats['resource_groups'].get(resource.resource_group, 0) + 1
        
        return stats


@dataclass
class ExtractionJob:
    """
    Represents an asynchronous extraction job.
    """
    job_id: str
    provider: CloudProvider
    scope: ExtractionScope
    scope_identifier: str
    status: str = "pending"  # pending, running, completed, failed
    created_time: datetime = field(default_factory=datetime.now)
    started_time: Optional[datetime] = None
    completed_time: Optional[datetime] = None
    progress: float = 0.0
    message: str = ""
    result_path: Optional[str] = None
    error_message: Optional[str] = None
    user_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary representation."""
        return {
            'job_id': self.job_id,
            'provider': self.provider.value,
            'scope': self.scope.value,
            'scope_identifier': self.scope_identifier,
            'status': self.status,
            'created_time': self.created_time.isoformat(),
            'started_time': self.started_time.isoformat() if self.started_time else None,
            'completed_time': self.completed_time.isoformat() if self.completed_time else None,
            'progress': self.progress,
            'message': self.message,
            'result_path': self.result_path,
            'error_message': self.error_message,
            'user_id': self.user_id
        }
