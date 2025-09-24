import os
import pytest
import yaml
from unittest.mock import patch, mock_open

from cloudviz.core.config import (
    CloudVizConfig,
    get_config,
    set_config,
    reload_config,
    ProviderConfig,
    APIConfig,
    DatabaseConfig,
    CacheConfig,
    LoggingConfig,
    JobConfig,
    VisualizationConfig,
)
from cloudviz.core.models import CloudProvider


@pytest.fixture
def mock_yaml_config_file(tmp_path):
    """Fixture to create a mock YAML config file."""
    config_content = {
        "api": {"host": "127.0.0.1", "port": 8080},
        "database": {"driver": "postgresql", "database": "test_db"},
        "providers": {
            "aws": {
                "authentication_method": "access_key",
                "enabled": True,
            }
        },
    }
    config_file = tmp_path / "config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_content, f)
    return str(config_file)


def test_load_from_yaml_file(mock_yaml_config_file):
    """Test loading configuration from a YAML file."""
    config = CloudVizConfig(config_file=mock_yaml_config_file)

    assert config.api.host == "127.0.0.1"
    assert config.api.port == 8080
    assert config.database.driver == "postgresql"
    assert config.database.database == "test_db"
    assert "aws" in config.providers
    assert config.providers["aws"].provider == CloudProvider.AWS
    assert config.providers["aws"].authentication_method == "access_key"


@pytest.fixture
def mock_json_config_file(tmp_path):
    """Fixture to create a mock JSON config file."""
    config_content = {
        "api": {"host": "127.0.0.2", "port": 8081},
        "database": {"driver": "mysql", "database": "test_db2"},
    }
    config_file = tmp_path / "config.json"
    with open(config_file, "w") as f:
        import json
        json.dump(config_content, f)
    return str(config_file)


def test_load_from_json_file(mock_json_config_file):
    """Test loading configuration from a JSON file."""
    config = CloudVizConfig(config_file=mock_json_config_file)

    assert config.api.host == "127.0.0.2"
    assert config.api.port == 8081
    assert config.database.driver == "mysql"
    assert config.database.database == "test_db2"


@patch.dict(
    os.environ,
    {
        "CLOUDVIZ_API_HOST": "env_host",
        "CLOUDVIZ_API_PORT": "9000",
        "CLOUDVIZ_JWT_SECRET": "env_secret",
        "CLOUDVIZ_DATABASE_URL": "env_db_url",
        "REDIS_URL": "env_redis_url",
    },
)
def test_load_from_environment():
    """Test loading configuration from environment variables."""
    config = CloudVizConfig()

    assert config.api.host == "env_host"
    assert config.api.port == 9000
    assert config.api.jwt_secret == "env_secret"
    assert config.database.url == "env_db_url"
    assert config.cache.url == "env_redis_url"
    assert config.cache.backend == "redis"


@patch.dict(
    os.environ,
    {
        "CLOUDVIZ_API_HOST": "env_host_override",
        "CLOUDVIZ_API_PORT": "9001",
    },
)
def test_env_overrides_file_config(mock_yaml_config_file):
    """Test that environment variables override file configurations."""
    config = CloudVizConfig(config_file=mock_yaml_config_file)

    assert config.api.host == "env_host_override"
    assert config.api.port == 9001
    assert config.database.driver == "postgresql"


def test_validation_error_invalid_port():
    """Test configuration validation for an invalid port."""
    with pytest.raises(ValueError, match="API port must be between 1 and 65535"):
        config = CloudVizConfig()
        config.api.port = 0
        config._validate_configuration()


def test_get_provider_config(mock_yaml_config_file):
    """Test the get_provider_config method."""
    config = CloudVizConfig(config_file=mock_yaml_config_file)
    aws_config = config.get_provider_config("aws")
    assert aws_config is not None
    assert aws_config.provider == CloudProvider.AWS

    gcp_config = config.get_provider_config("gcp")
    assert gcp_config is None


def test_is_provider_enabled(mock_yaml_config_file):
    """Test the is_provider_enabled method."""
    config = CloudVizConfig(config_file=mock_yaml_config_file)
    assert config.is_provider_enabled("aws") is True
    assert config.is_provider_enabled("gcp") is False


def test_get_enabled_providers(mock_yaml_config_file):
    """Test the get_enabled_providers method."""
    config = CloudVizConfig(config_file=mock_yaml_config_file)
    enabled_providers = config.get_enabled_providers()
    assert enabled_providers == [CloudProvider.AWS]


def test_to_dict(mock_yaml_config_file):
    """Test the to_dict method."""
    config = CloudVizConfig(config_file=mock_yaml_config_file)
    config_dict = config.to_dict()

    assert config_dict["api"]["host"] == "127.0.0.1"
    assert "aws" in config_dict["providers"]
    # Ensure credentials are not exposed
    assert "credentials" not in config_dict["providers"]["aws"]


def test_save_to_file(mock_yaml_config_file, tmp_path):
    """Test the save_to_file method."""
    config = CloudVizConfig(config_file=mock_yaml_config_file)
    output_path = tmp_path / "output.yaml"
    config.save_to_file(str(output_path))

    with open(output_path, "r") as f:
        saved_config = yaml.safe_load(f)

    assert saved_config["api"]["host"] == "127.0.0.1"


def test_get_config_singleton():
    """Test that get_config returns a singleton instance."""
    # Reset the global config instance for a clean test
    reload_config()
    config1 = get_config()
    config2 = get_config()
    assert config1 is config2


def test_set_config():
    """Test the set_config function."""
    new_config = CloudVizConfig()
    set_config(new_config)
    retrieved_config = get_config()
    assert retrieved_config is new_config


def test_reload_config(mock_yaml_config_file):
    """Test the reload_config function."""
    # Initial config
    reload_config()
    config1 = get_config()
    config1.api.host = "initial_host"

    # Reload with a new config file
    reload_config(config_file=mock_yaml_config_file)
    config2 = get_config()

    assert config1 is not config2
    assert config2.api.host == "127.0.0.1"
