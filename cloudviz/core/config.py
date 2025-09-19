"""
Configuration management for CloudViz platform.
Handles loading, validation, and management of configuration from various sources.
"""

import os
import yaml
import json
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from pathlib import Path
from cloudviz.core.models import CloudProvider, ExtractionScope


@dataclass
class ProviderConfig:
    """Configuration for a specific cloud provider."""
    provider: CloudProvider
    authentication_method: str
    enabled: bool = True
    region: Optional[str] = None
    profile: Optional[str] = None
    credentials: Dict[str, Any] = field(default_factory=dict)
    extraction_settings: Dict[str, Any] = field(default_factory=dict)
    rate_limits: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization processing."""
        if isinstance(self.provider, str):
            self.provider = CloudProvider(self.provider)


@dataclass
class VisualizationConfig:
    """Configuration for visualization settings."""
    default_theme: str = "professional"
    default_format: str = "mermaid"
    default_layout: str = "hierarchical"
    output_directory: str = "./output"
    supported_formats: List[str] = field(default_factory=lambda: ["mermaid", "png", "svg", "dot"])
    themes: List[str] = field(default_factory=lambda: ["professional", "dark", "light", "minimal"])
    layouts: List[str] = field(default_factory=lambda: ["hierarchical", "force", "circular", "tree"])
    render_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APIConfig:
    """Configuration for API server."""
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    reload: bool = False
    log_level: str = "info"
    cors_enabled: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    max_request_size: int = 10485760  # 10MB
    request_timeout: int = 300  # 5 minutes
    
    # Authentication
    jwt_secret: Optional[str] = None
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600  # 1 hour
    
    # Security
    enable_https: bool = False
    ssl_cert_file: Optional[str] = None
    ssl_key_file: Optional[str] = None


@dataclass
class DatabaseConfig:
    """Configuration for database connections."""
    url: Optional[str] = None
    driver: str = "sqlite"
    host: Optional[str] = None
    port: Optional[int] = None
    database: str = "cloudviz.db"
    username: Optional[str] = None
    password: Optional[str] = None
    pool_size: int = 5
    max_overflow: int = 10
    echo: bool = False


@dataclass
class CacheConfig:
    """Configuration for caching."""
    enabled: bool = True
    backend: str = "memory"  # memory, redis, memcached
    url: Optional[str] = None
    default_ttl: int = 3600
    max_size: int = 1000
    
    # Redis specific
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None


@dataclass
class LoggingConfig:
    """Configuration for logging."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10485760  # 10MB
    backup_count: int = 5
    json_format: bool = False
    correlation_id: bool = True


@dataclass
class JobConfig:
    """Configuration for job management."""
    max_concurrent_jobs: int = 5
    job_timeout: int = 3600  # 1 hour
    cleanup_completed_jobs_after: int = 86400  # 24 hours
    cleanup_failed_jobs_after: int = 604800  # 7 days
    result_storage_path: str = "./job_results"


class CloudVizConfig:
    """
    Main configuration class for CloudViz platform.
    Loads configuration from files, environment variables, and provides validation.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to configuration file (YAML or JSON)
        """
        self.config_file = config_file
        self.providers: Dict[str, ProviderConfig] = {}
        self.visualization = VisualizationConfig()
        self.api = APIConfig()
        self.database = DatabaseConfig()
        self.cache = CacheConfig()
        self.logging = LoggingConfig()
        self.jobs = JobConfig()
        self.custom_settings: Dict[str, Any] = {}
        
        self._load_configuration()
    
    def _load_configuration(self):
        """Load configuration from file and environment variables."""
        # Load from file if specified
        if self.config_file and os.path.exists(self.config_file):
            self._load_from_file(self.config_file)
        else:
            # Try default locations
            default_locations = [
                "config/config.yaml",
                "config/config.yml", 
                "config.yaml",
                "config.yml",
                os.path.expanduser("~/.cloudviz/config.yaml"),
                "/etc/cloudviz/config.yaml"
            ]
            
            for location in default_locations:
                if os.path.exists(location):
                    self._load_from_file(location)
                    break
        
        # Override with environment variables
        self._load_from_environment()
        
        # Validate configuration
        self._validate_configuration()
    
    def _load_from_file(self, file_path: str):
        """Load configuration from YAML or JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith(('.yaml', '.yml')):
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
            
            self._apply_config_data(config_data)
            
        except Exception as e:
            print(f"Warning: Failed to load configuration from {file_path}: {e}")
    
    def _load_from_environment(self):
        """Load configuration from environment variables."""
        # API configuration
        if os.getenv('CLOUDVIZ_API_HOST'):
            self.api.host = os.getenv('CLOUDVIZ_API_HOST')
        if os.getenv('CLOUDVIZ_API_PORT'):
            self.api.port = int(os.getenv('CLOUDVIZ_API_PORT'))
        if os.getenv('CLOUDVIZ_JWT_SECRET'):
            self.api.jwt_secret = os.getenv('CLOUDVIZ_JWT_SECRET')
        
        # Database configuration
        if os.getenv('CLOUDVIZ_DATABASE_URL'):
            self.database.url = os.getenv('CLOUDVIZ_DATABASE_URL')
        
        # Cache configuration
        if os.getenv('CLOUDVIZ_CACHE_URL'):
            self.cache.url = os.getenv('CLOUDVIZ_CACHE_URL')
        if os.getenv('REDIS_URL'):
            self.cache.url = os.getenv('REDIS_URL')
            self.cache.backend = 'redis'
        
        # Logging configuration
        if os.getenv('CLOUDVIZ_LOG_LEVEL'):
            self.logging.level = os.getenv('CLOUDVIZ_LOG_LEVEL')
        if os.getenv('CLOUDVIZ_LOG_FILE'):
            self.logging.file_path = os.getenv('CLOUDVIZ_LOG_FILE')
        
        # Provider-specific environment variables
        self._load_provider_env_vars()
    
    def _load_provider_env_vars(self):
        """Load provider configurations from environment variables."""
        # Azure
        if any(os.getenv(var) for var in ['AZURE_TENANT_ID', 'AZURE_CLIENT_ID', 'AZURE_CLIENT_SECRET']):
            azure_config = ProviderConfig(
                provider=CloudProvider.AZURE,
                authentication_method="service_principal",
                credentials={
                    'tenant_id': os.getenv('AZURE_TENANT_ID'),
                    'client_id': os.getenv('AZURE_CLIENT_ID'),
                    'client_secret': os.getenv('AZURE_CLIENT_SECRET')
                }
            )
            self.providers['azure'] = azure_config
        
        # AWS
        if any(os.getenv(var) for var in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']):
            aws_config = ProviderConfig(
                provider=CloudProvider.AWS,
                authentication_method="access_key",
                credentials={
                    'access_key_id': os.getenv('AWS_ACCESS_KEY_ID'),
                    'secret_access_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
                    'session_token': os.getenv('AWS_SESSION_TOKEN')
                },
                region=os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
            )
            self.providers['aws'] = aws_config
        
        # GCP
        if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            gcp_config = ProviderConfig(
                provider=CloudProvider.GCP,
                authentication_method="service_account",
                credentials={
                    'service_account_file': os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
                }
            )
            self.providers['gcp'] = gcp_config
    
    def _apply_config_data(self, config_data: Dict[str, Any]):
        """Apply configuration data from file."""
        if not config_data:
            return
        
        # Provider configurations
        if 'providers' in config_data:
            for provider_name, provider_data in config_data['providers'].items():
                try:
                    provider_config = ProviderConfig(
                        provider=CloudProvider(provider_name.lower()),
                        **provider_data
                    )
                    self.providers[provider_name.lower()] = provider_config
                except (ValueError, TypeError) as e:
                    print(f"Warning: Invalid provider configuration for {provider_name}: {e}")
        
        # Visualization configuration
        if 'visualization' in config_data:
            viz_data = config_data['visualization']
            for key, value in viz_data.items():
                if hasattr(self.visualization, key):
                    setattr(self.visualization, key, value)
        
        # API configuration
        if 'api' in config_data:
            api_data = config_data['api']
            for key, value in api_data.items():
                if hasattr(self.api, key):
                    setattr(self.api, key, value)
        
        # Database configuration
        if 'database' in config_data:
            db_data = config_data['database']
            for key, value in db_data.items():
                if hasattr(self.database, key):
                    setattr(self.database, key, value)
        
        # Cache configuration
        if 'cache' in config_data:
            cache_data = config_data['cache']
            for key, value in cache_data.items():
                if hasattr(self.cache, key):
                    setattr(self.cache, key, value)
        
        # Logging configuration
        if 'logging' in config_data:
            log_data = config_data['logging']
            for key, value in log_data.items():
                if hasattr(self.logging, key):
                    setattr(self.logging, key, value)
        
        # Job configuration
        if 'jobs' in config_data:
            job_data = config_data['jobs']
            for key, value in job_data.items():
                if hasattr(self.jobs, key):
                    setattr(self.jobs, key, value)
        
        # Custom settings
        for key, value in config_data.items():
            if key not in ['providers', 'visualization', 'api', 'database', 'cache', 'logging', 'jobs']:
                self.custom_settings[key] = value
    
    def _validate_configuration(self):
        """Validate the loaded configuration."""
        errors = []
        
        # Validate API configuration
        if self.api.port < 1 or self.api.port > 65535:
            errors.append("API port must be between 1 and 65535")
        
        if self.api.workers < 1:
            errors.append("API workers must be at least 1")
        
        # Validate provider configurations
        for provider_name, provider_config in self.providers.items():
            if not provider_config.authentication_method:
                errors.append(f"Provider {provider_name} missing authentication method")
        
        # Validate visualization configuration
        if not os.path.exists(os.path.dirname(self.visualization.output_directory)):
            try:
                os.makedirs(os.path.dirname(self.visualization.output_directory), exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create output directory: {e}")
        
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
    
    def get_provider_config(self, provider: Union[str, CloudProvider]) -> Optional[ProviderConfig]:
        """
        Get configuration for a specific provider.
        
        Args:
            provider: Provider name or enum
            
        Returns:
            Optional[ProviderConfig]: Provider configuration if found
        """
        if isinstance(provider, CloudProvider):
            provider = provider.value
        
        return self.providers.get(provider.lower())
    
    def is_provider_enabled(self, provider: Union[str, CloudProvider]) -> bool:
        """
        Check if a provider is enabled.
        
        Args:
            provider: Provider name or enum
            
        Returns:
            bool: True if provider is enabled
        """
        config = self.get_provider_config(provider)
        return config is not None and config.enabled
    
    def get_enabled_providers(self) -> List[CloudProvider]:
        """
        Get list of enabled providers.
        
        Returns:
            List[CloudProvider]: List of enabled providers
        """
        return [config.provider for config in self.providers.values() if config.enabled]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dict[str, Any]: Configuration as dictionary
        """
        return {
            'providers': {
                name: {
                    'provider': config.provider.value,
                    'authentication_method': config.authentication_method,
                    'enabled': config.enabled,
                    'region': config.region,
                    'profile': config.profile,
                    'extraction_settings': config.extraction_settings,
                    'rate_limits': config.rate_limits
                    # Note: credentials excluded for security
                }
                for name, config in self.providers.items()
            },
            'visualization': {
                'default_theme': self.visualization.default_theme,
                'default_format': self.visualization.default_format,
                'default_layout': self.visualization.default_layout,
                'output_directory': self.visualization.output_directory,
                'supported_formats': self.visualization.supported_formats,
                'themes': self.visualization.themes,
                'layouts': self.visualization.layouts,
                'render_settings': self.visualization.render_settings
            },
            'api': {
                'host': self.api.host,
                'port': self.api.port,
                'workers': self.api.workers,
                'cors_enabled': self.api.cors_enabled,
                'cors_origins': self.api.cors_origins,
                'rate_limit_requests': self.api.rate_limit_requests,
                'rate_limit_window': self.api.rate_limit_window,
                'max_request_size': self.api.max_request_size,
                'request_timeout': self.api.request_timeout,
                'jwt_algorithm': self.api.jwt_algorithm,
                'jwt_expiration': self.api.jwt_expiration,
                'enable_https': self.api.enable_https
            },
            'database': {
                'driver': self.database.driver,
                'database': self.database.database,
                'pool_size': self.database.pool_size,
                'max_overflow': self.database.max_overflow,
                'echo': self.database.echo
            },
            'cache': {
                'enabled': self.cache.enabled,
                'backend': self.cache.backend,
                'default_ttl': self.cache.default_ttl,
                'max_size': self.cache.max_size,
                'redis_host': self.cache.redis_host,
                'redis_port': self.cache.redis_port,
                'redis_db': self.cache.redis_db
            },
            'logging': {
                'level': self.logging.level,
                'format': self.logging.format,
                'file_path': self.logging.file_path,
                'max_file_size': self.logging.max_file_size,
                'backup_count': self.logging.backup_count,
                'json_format': self.logging.json_format,
                'correlation_id': self.logging.correlation_id
            },
            'jobs': {
                'max_concurrent_jobs': self.jobs.max_concurrent_jobs,
                'job_timeout': self.jobs.job_timeout,
                'cleanup_completed_jobs_after': self.jobs.cleanup_completed_jobs_after,
                'cleanup_failed_jobs_after': self.jobs.cleanup_failed_jobs_after,
                'result_storage_path': self.jobs.result_storage_path
            },
            'custom_settings': self.custom_settings
        }
    
    def save_to_file(self, file_path: str):
        """
        Save configuration to file.
        
        Args:
            file_path: Path to save configuration
        """
        config_dict = self.to_dict()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            if file_path.endswith(('.yaml', '.yml')):
                yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
            else:
                json.dump(config_dict, f, indent=2, sort_keys=False)


# Global configuration instance
_config_instance: Optional[CloudVizConfig] = None


def get_config() -> CloudVizConfig:
    """
    Get the global configuration instance.
    
    Returns:
        CloudVizConfig: Global configuration instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = CloudVizConfig()
    return _config_instance


def set_config(config: CloudVizConfig):
    """
    Set the global configuration instance.
    
    Args:
        config: Configuration instance to set as global
    """
    global _config_instance
    _config_instance = config


def reload_config(config_file: Optional[str] = None):
    """
    Reload the global configuration.
    
    Args:
        config_file: Optional path to configuration file
    """
    global _config_instance
    _config_instance = CloudVizConfig(config_file)
