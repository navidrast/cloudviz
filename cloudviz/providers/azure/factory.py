"""
Azure provider factory implementation.
Creates and configures Azure resource extractors and other Azure-specific components.
"""

from typing import Dict, Any, List
from cloudviz.core.base import CloudProviderFactory, ResourceExtractor
from cloudviz.core.models import CloudProvider
from cloudviz.providers.azure.extractor import AzureResourceExtractor


class AzureProviderFactory(CloudProviderFactory):
    """
    Factory for creating Azure provider components.
    """
    
    def create_extractor(self, config: Dict[str, Any]) -> ResourceExtractor:
        """
        Create Azure resource extractor with configuration.
        
        Args:
            config: Azure provider configuration
            
        Returns:
            ResourceExtractor: Configured Azure extractor
        """
        return AzureResourceExtractor(config)
    
    def get_provider_type(self) -> CloudProvider:
        """
        Get the cloud provider type.
        
        Returns:
            CloudProvider: Azure provider enum
        """
        return CloudProvider.AZURE
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate Azure provider configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            bool: True if configuration is valid
        """
        auth_method = config.get('authentication_method', 'interactive')
        
        # Validate authentication method
        valid_auth_methods = [
            'service_principal',
            'managed_identity', 
            'interactive',
            'device_code'
        ]
        
        if auth_method not in valid_auth_methods:
            return False
        
        # Validate service principal credentials if required
        if auth_method == 'service_principal':
            required_fields = ['tenant_id', 'client_id', 'client_secret']
            for field in required_fields:
                if not config.get(field):
                    return False
        
        # Validate optional fields
        if 'timeout' in config:
            try:
                timeout = int(config['timeout'])
                if timeout < 1 or timeout > 3600:  # 1 second to 1 hour
                    return False
            except (ValueError, TypeError):
                return False
        
        if 'max_retries' in config:
            try:
                retries = int(config['max_retries'])
                if retries < 0 or retries > 10:
                    return False
            except (ValueError, TypeError):
                return False
        
        return True
    
    def get_required_config_keys(self) -> List[str]:
        """
        Get list of required configuration keys.
        
        Returns:
            List[str]: Required configuration keys
        """
        return ['authentication_method']
    
    def get_optional_config_keys(self) -> List[str]:
        """
        Get list of optional configuration keys.
        
        Returns:
            List[str]: Optional configuration keys
        """
        return [
            'tenant_id',
            'client_id', 
            'client_secret',
            'subscription_id',
            'timeout',
            'max_retries',
            'include_resource_types',
            'exclude_resource_types',
            'include_properties',
            'include_tags',
            'include_relationships'
        ]
    
    def get_authentication_methods(self) -> List[str]:
        """
        Get supported authentication methods.
        
        Returns:
            List[str]: Supported authentication methods
        """
        return [
            'service_principal',
            'managed_identity',
            'interactive', 
            'device_code'
        ]
    
    def get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration for Azure provider.
        
        Returns:
            Dict[str, Any]: Default configuration
        """
        return {
            'authentication_method': 'interactive',
            'timeout': 300,
            'max_retries': 3,
            'include_properties': True,
            'include_tags': True,
            'include_relationships': True,
            'include_resource_types': [],
            'exclude_resource_types': []
        }
    
    def get_config_schema(self) -> Dict[str, Any]:
        """
        Get configuration schema for validation.
        
        Returns:
            Dict[str, Any]: JSON schema for configuration
        """
        return {
            "type": "object",
            "properties": {
                "authentication_method": {
                    "type": "string",
                    "enum": self.get_authentication_methods(),
                    "description": "Azure authentication method to use"
                },
                "tenant_id": {
                    "type": "string",
                    "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
                    "description": "Azure tenant ID (required for service principal auth)"
                },
                "client_id": {
                    "type": "string", 
                    "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
                    "description": "Azure client ID (required for service principal auth)"
                },
                "client_secret": {
                    "type": "string",
                    "description": "Azure client secret (required for service principal auth)"
                },
                "subscription_id": {
                    "type": "string",
                    "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
                    "description": "Default Azure subscription ID"
                },
                "timeout": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 3600,
                    "description": "PowerShell execution timeout in seconds"
                },
                "max_retries": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 10,
                    "description": "Maximum number of retry attempts"
                },
                "include_resource_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Resource types to include (empty = all)"
                },
                "exclude_resource_types": {
                    "type": "array", 
                    "items": {"type": "string"},
                    "description": "Resource types to exclude"
                },
                "include_properties": {
                    "type": "boolean",
                    "description": "Include detailed resource properties"
                },
                "include_tags": {
                    "type": "boolean",
                    "description": "Include resource tags"
                },
                "include_relationships": {
                    "type": "boolean",
                    "description": "Extract resource relationships"
                }
            },
            "required": ["authentication_method"],
            "additionalProperties": False,
            "if": {
                "properties": {"authentication_method": {"const": "service_principal"}}
            },
            "then": {
                "required": ["authentication_method", "tenant_id", "client_id", "client_secret"]
            }
        }
    
    def create_config_from_environment(self) -> Dict[str, Any]:
        """
        Create configuration from environment variables.
        
        Returns:
            Dict[str, Any]: Configuration from environment
        """
        import os
        
        config = self.get_default_config()
        
        # Authentication method
        if os.getenv('AZURE_AUTH_METHOD'):
            config['authentication_method'] = os.getenv('AZURE_AUTH_METHOD')
        
        # Service principal credentials
        if os.getenv('AZURE_TENANT_ID'):
            config['tenant_id'] = os.getenv('AZURE_TENANT_ID')
            config['authentication_method'] = 'service_principal'
        
        if os.getenv('AZURE_CLIENT_ID'):
            config['client_id'] = os.getenv('AZURE_CLIENT_ID')
        
        if os.getenv('AZURE_CLIENT_SECRET'):
            config['client_secret'] = os.getenv('AZURE_CLIENT_SECRET')
        
        # Subscription ID
        if os.getenv('AZURE_SUBSCRIPTION_ID'):
            config['subscription_id'] = os.getenv('AZURE_SUBSCRIPTION_ID')
        
        # Timeout
        if os.getenv('AZURE_TIMEOUT'):
            try:
                config['timeout'] = int(os.getenv('AZURE_TIMEOUT'))
            except ValueError:
                pass
        
        # Max retries
        if os.getenv('AZURE_MAX_RETRIES'):
            try:
                config['max_retries'] = int(os.getenv('AZURE_MAX_RETRIES'))
            except ValueError:
                pass
        
        # Boolean flags
        for flag in ['include_properties', 'include_tags', 'include_relationships']:
            env_var = f'AZURE_{flag.upper()}'
            if os.getenv(env_var):
                config[flag] = os.getenv(env_var).lower() in ('true', '1', 'yes')
        
        return config
    
    def get_provider_capabilities(self) -> Dict[str, Any]:
        """
        Get Azure provider capabilities.
        
        Returns:
            Dict[str, Any]: Provider capabilities
        """
        return {
            'supports_incremental_extraction': True,
            'supports_relationship_discovery': True,
            'supports_resource_properties': True,
            'supports_resource_tags': True,
            'supports_cost_information': True,
            'supports_compliance_information': True,
            'requires_powershell': True,
            'required_powershell_modules': ['Az.Resources', 'Az.Profile'],
            'supported_scopes': [
                'subscription',
                'resource_group',
                'tag'
            ],
            'supported_filters': [
                'resource_type',
                'tag',
                'location',
                'resource_group'
            ],
            'extraction_features': [
                'parallel_processing',
                'retry_logic',
                'detailed_logging',
                'progress_tracking',
                'error_handling'
            ]
        }
