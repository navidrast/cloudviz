"""
Abstract base classes for CloudViz platform components.
Defines the interfaces that all cloud providers, extractors, and visualization engines must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Iterator, Union
from cloudviz.core.models import (
    CloudResource, ResourceRelationship, ResourceInventory, 
    ExtractionScope, CloudProvider, ExtractionJob
)


class ResourceExtractor(ABC):
    """
    Abstract base class for cloud resource extractors.
    
    Each cloud provider must implement this interface to provide
    consistent resource extraction capabilities.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the extractor with provider-specific configuration."""
        self.config = config or {}
        self._authenticated = False
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """
        Authenticate with the cloud provider.
        
        Returns:
            bool: True if authentication successful, False otherwise.
        """
        pass
    
    @abstractmethod
    async def extract_resources(
        self, 
        scope: ExtractionScope,
        scope_identifier: str,
        resource_types: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> ResourceInventory:
        """
        Extract resources from the cloud provider.
        
        Args:
            scope: The scope of extraction (subscription, resource group, etc.)
            scope_identifier: The identifier for the scope (subscription ID, RG name, etc.)
            resource_types: Optional list of resource types to extract
            tags: Optional tag filters
            **kwargs: Additional provider-specific parameters
            
        Returns:
            ResourceInventory: Complete inventory of extracted resources and relationships
        """
        pass
    
    @abstractmethod
    async def extract_resource_relationships(
        self, 
        resources: List[CloudResource]
    ) -> List[ResourceRelationship]:
        """
        Extract relationships between resources.
        
        Args:
            resources: List of resources to analyze for relationships
            
        Returns:
            List[ResourceRelationship]: List of discovered relationships
        """
        pass
    
    @abstractmethod
    async def get_available_scopes(self) -> Dict[str, List[str]]:
        """
        Get available extraction scopes for the authenticated user.
        
        Returns:
            Dict[str, List[str]]: Dictionary mapping scope types to available identifiers
        """
        pass
    
    @abstractmethod
    async def validate_scope(self, scope: ExtractionScope, scope_identifier: str) -> bool:
        """
        Validate that a scope identifier is accessible.
        
        Args:
            scope: The scope type
            scope_identifier: The scope identifier
            
        Returns:
            bool: True if scope is valid and accessible
        """
        pass
    
    async def extract_incremental(
        self,
        scope: ExtractionScope,
        scope_identifier: str,
        last_extraction_time: Optional[str] = None,
        **kwargs
    ) -> ResourceInventory:
        """
        Extract only resources that have changed since last extraction.
        
        Args:
            scope: The scope of extraction
            scope_identifier: The identifier for the scope
            last_extraction_time: ISO format timestamp of last extraction
            **kwargs: Additional parameters
            
        Returns:
            ResourceInventory: Inventory of changed resources
        """
        # Default implementation falls back to full extraction
        return await self.extract_resources(scope, scope_identifier, **kwargs)
    
    def get_supported_resource_types(self) -> List[str]:
        """
        Get list of resource types supported by this extractor.
        
        Returns:
            List[str]: List of supported resource type names
        """
        return []
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about this provider.
        
        Returns:
            Dict[str, Any]: Provider metadata
        """
        return {
            'name': self.__class__.__name__,
            'provider': 'unknown',
            'version': '1.0.0',
            'supported_scopes': [],
            'supported_resource_types': self.get_supported_resource_types()
        }


class VisualizationEngine(ABC):
    """
    Abstract base class for visualization engines.
    
    Visualization engines render resource inventories into various output formats.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the visualization engine with configuration."""
        self.config = config or {}
    
    @abstractmethod
    async def render(
        self,
        inventory: ResourceInventory,
        output_format: str,
        theme: Optional[str] = None,
        layout: Optional[str] = None,
        **kwargs
    ) -> bytes:
        """
        Render the resource inventory to the specified format.
        
        Args:
            inventory: Resource inventory to visualize
            output_format: Target output format (png, svg, mermaid, dot, etc.)
            theme: Optional theme name
            layout: Optional layout algorithm
            **kwargs: Additional rendering parameters
            
        Returns:
            bytes: Rendered diagram data
        """
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported output formats.
        
        Returns:
            List[str]: List of supported format names
        """
        pass
    
    @abstractmethod
    def get_available_themes(self) -> List[str]:
        """
        Get list of available themes.
        
        Returns:
            List[str]: List of theme names
        """
        pass
    
    @abstractmethod
    def get_available_layouts(self) -> List[str]:
        """
        Get list of available layout algorithms.
        
        Returns:
            List[str]: List of layout algorithm names
        """
        pass
    
    async def validate_options(
        self,
        output_format: str,
        theme: Optional[str] = None,
        layout: Optional[str] = None
    ) -> bool:
        """
        Validate rendering options.
        
        Args:
            output_format: Target output format
            theme: Theme name
            layout: Layout algorithm name
            
        Returns:
            bool: True if options are valid
        """
        if output_format not in self.get_supported_formats():
            return False
        
        if theme and theme not in self.get_available_themes():
            return False
            
        if layout and layout not in self.get_available_layouts():
            return False
            
        return True
    
    def get_engine_info(self) -> Dict[str, Any]:
        """
        Get information about this visualization engine.
        
        Returns:
            Dict[str, Any]: Engine metadata
        """
        return {
            'name': self.__class__.__name__,
            'version': '1.0.0',
            'supported_formats': self.get_supported_formats(),
            'available_themes': self.get_available_themes(),
            'available_layouts': self.get_available_layouts()
        }


class CloudProviderFactory(ABC):
    """
    Abstract factory for creating cloud provider instances.
    """
    
    @abstractmethod
    def create_extractor(self, config: Dict[str, Any]) -> ResourceExtractor:
        """
        Create a resource extractor instance.
        
        Args:
            config: Provider-specific configuration
            
        Returns:
            ResourceExtractor: Configured extractor instance
        """
        pass
    
    @abstractmethod
    def get_provider_type(self) -> CloudProvider:
        """
        Get the cloud provider type.
        
        Returns:
            CloudProvider: The provider enum value
        """
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate provider configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            bool: True if configuration is valid
        """
        pass
    
    def get_required_config_keys(self) -> List[str]:
        """
        Get list of required configuration keys.
        
        Returns:
            List[str]: Required configuration keys
        """
        return []
    
    def get_optional_config_keys(self) -> List[str]:
        """
        Get list of optional configuration keys.
        
        Returns:
            List[str]: Optional configuration keys
        """
        return []


class JobManager(ABC):
    """
    Abstract base class for managing asynchronous extraction jobs.
    """
    
    @abstractmethod
    async def create_job(
        self,
        provider: CloudProvider,
        scope: ExtractionScope,
        scope_identifier: str,
        user_id: Optional[str] = None,
        **kwargs
    ) -> ExtractionJob:
        """
        Create a new extraction job.
        
        Args:
            provider: Cloud provider
            scope: Extraction scope
            scope_identifier: Scope identifier
            user_id: Optional user identifier
            **kwargs: Additional job parameters
            
        Returns:
            ExtractionJob: Created job instance
        """
        pass
    
    @abstractmethod
    async def get_job(self, job_id: str) -> Optional[ExtractionJob]:
        """
        Get a job by ID.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Optional[ExtractionJob]: Job instance if found
        """
        pass
    
    @abstractmethod
    async def update_job_status(
        self,
        job_id: str,
        status: str,
        progress: Optional[float] = None,
        message: Optional[str] = None
    ) -> bool:
        """
        Update job status and progress.
        
        Args:
            job_id: Job identifier
            status: New status
            progress: Optional progress percentage
            message: Optional status message
            
        Returns:
            bool: True if update successful
        """
        pass
    
    @abstractmethod
    async def list_jobs(
        self,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[ExtractionJob]:
        """
        List jobs with optional filters.
        
        Args:
            user_id: Optional user filter
            status: Optional status filter
            limit: Maximum number of jobs to return
            
        Returns:
            List[ExtractionJob]: List of matching jobs
        """
        pass
    
    @abstractmethod
    async def delete_job(self, job_id: str) -> bool:
        """
        Delete a job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            bool: True if deletion successful
        """
        pass


class EventHook(ABC):
    """
    Abstract base class for event hooks.
    
    Event hooks allow custom processing at various stages of the extraction
    and visualization pipeline.
    """
    
    @abstractmethod
    async def on_extraction_started(self, job: ExtractionJob):
        """Called when extraction job starts."""
        pass
    
    @abstractmethod
    async def on_extraction_completed(self, job: ExtractionJob, inventory: ResourceInventory):
        """Called when extraction job completes successfully."""
        pass
    
    @abstractmethod
    async def on_extraction_failed(self, job: ExtractionJob, error: Exception):
        """Called when extraction job fails."""
        pass
    
    @abstractmethod
    async def on_visualization_generated(self, inventory: ResourceInventory, output_format: str, result: bytes):
        """Called when visualization is generated."""
        pass


class CacheManager(ABC):
    """
    Abstract base class for caching extracted resources and generated visualizations.
    """
    
    @abstractmethod
    async def get_cached_inventory(
        self,
        cache_key: str
    ) -> Optional[ResourceInventory]:
        """
        Get cached resource inventory.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Optional[ResourceInventory]: Cached inventory if found
        """
        pass
    
    @abstractmethod
    async def cache_inventory(
        self,
        cache_key: str,
        inventory: ResourceInventory,
        ttl_seconds: int = 3600
    ) -> bool:
        """
        Cache resource inventory.
        
        Args:
            cache_key: Cache key
            inventory: Inventory to cache
            ttl_seconds: Time to live in seconds
            
        Returns:
            bool: True if caching successful
        """
        pass
    
    @abstractmethod
    async def get_cached_visualization(
        self,
        cache_key: str
    ) -> Optional[bytes]:
        """
        Get cached visualization.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Optional[bytes]: Cached visualization if found
        """
        pass
    
    @abstractmethod
    async def cache_visualization(
        self,
        cache_key: str,
        visualization: bytes,
        ttl_seconds: int = 1800
    ) -> bool:
        """
        Cache visualization.
        
        Args:
            cache_key: Cache key
            visualization: Visualization data to cache
            ttl_seconds: Time to live in seconds
            
        Returns:
            bool: True if caching successful
        """
        pass
    
    @abstractmethod
    async def invalidate_cache(self, pattern: str) -> int:
        """
        Invalidate cached items matching pattern.
        
        Args:
            pattern: Cache key pattern
            
        Returns:
            int: Number of items invalidated
        """
        pass
