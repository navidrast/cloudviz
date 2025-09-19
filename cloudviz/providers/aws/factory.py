"""
AWS resource factory for CloudViz platform.
"""

from typing import Dict, Any, Type
from cloudviz.core.base import BaseResourceFactory
from cloudviz.core.utils.logging import get_logger
from .models import AWSResource, AWS_RESOURCE_TYPES

logger = get_logger(__name__)


class AWSResourceFactory(BaseResourceFactory):
    """
    Factory for creating AWS resource instances.
    """
    
    def __init__(self):
        super().__init__()
        self.resource_types = AWS_RESOURCE_TYPES
        
    def create_resource(self, resource_type: str, data: Dict[str, Any]) -> AWSResource:
        """
        Create an AWS resource instance from data.
        
        Args:
            resource_type: Type of AWS resource
            data: Resource data dictionary
            
        Returns:
            AWSResource: Created resource instance
            
        Raises:
            ValueError: If resource type is not supported
        """
        if resource_type not in self.resource_types:
            raise ValueError(f"Unsupported AWS resource type: {resource_type}")
            
        resource_class = self.resource_types[resource_type]
        
        try:
            return resource_class(**data)
        except Exception as e:
            logger.error("Failed to create AWS resource of type %s: %s", resource_type, str(e))
            raise
            
    def get_supported_types(self) -> list[str]:
        """
        Get list of supported AWS resource types.
        
        Returns:
            List[str]: Supported resource types
        """
        return list(self.resource_types.keys())
        
    def validate_resource_data(self, resource_type: str, data: Dict[str, Any]) -> bool:
        """
        Validate resource data for a specific type.
        
        Args:
            resource_type: Type of AWS resource
            data: Resource data to validate
            
        Returns:
            bool: True if data is valid
        """
        if resource_type not in self.resource_types:
            return False
            
        resource_class = self.resource_types[resource_type]
        
        try:
            # Try to create instance to validate
            resource_class(**data)
            return True
        except Exception as e:
            logger.warning("AWS resource data validation failed for type %s: %s", resource_type, str(e))
            return False
