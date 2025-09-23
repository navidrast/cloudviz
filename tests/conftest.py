"""Pytest configuration and fixtures for CloudViz tests."""
import os
import pytest
from unittest.mock import Mock, MagicMock


@pytest.fixture
def mock_azure_client():
    """Mock Azure client for testing."""
    client = Mock()
    client.resource_groups = Mock()
    client.virtual_machines = Mock()
    client.storage_accounts = Mock()
    return client


@pytest.fixture
def mock_aws_client():
    """Mock AWS client for testing."""
    client = Mock()
    client.describe_instances = Mock()
    client.describe_vpcs = Mock()
    client.list_buckets = Mock()
    return client


@pytest.fixture
def mock_gcp_client():
    """Mock GCP client for testing."""
    client = Mock()
    client.instances = Mock()
    client.projects = Mock()
    client.zones = Mock()
    return client


@pytest.fixture
def sample_cloud_resource():
    """Sample cloud resource for testing."""
    return {
        "id": "test-resource-123",
        "name": "test-resource",
        "type": "VirtualMachine",
        "provider": "azure",
        "region": "eastus",
        "metadata": {
            "size": "Standard_D2s_v3",
            "state": "running"
        }
    }


@pytest.fixture
def test_config():
    """Test configuration."""
    return {
        "test_mode": True,
        "debug": True,
        "database_url": "sqlite:///:memory:",
        "redis_url": "redis://localhost:6379/1"
    }


# Set up test environment variables
os.environ["CLOUDVIZ_ENV"] = "test"
os.environ["TESTING"] = "true"