# Development

This guide covers contributing to CloudViz, setting up a development environment, testing, and extending the platform.

## 🚀 Getting Started

### Prerequisites

- **Python**: 3.8 or higher (3.11 recommended)
- **Git**: For version control
- **Docker**: For running dependencies
- **Node.js**: For Mermaid CLI and frontend tools
- **Redis**: For caching and background jobs
- **PostgreSQL**: For data persistence

### Development Environment Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/navidrast/cloudviz.git
   cd cloudviz
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   # Install development dependencies
   pip install -r requirements/dev.txt
   
   # Install pre-commit hooks
   pre-commit install
   ```

4. **Start Development Services**
   ```bash
   # Start PostgreSQL and Redis
   docker-compose -f docker-compose.dev.yml up -d postgres redis
   
   # Or install locally
   sudo apt install postgresql redis-server  # Ubuntu/Debian
   brew install postgresql redis             # macOS
   ```

5. **Configure Environment**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit with your settings
   nano .env
   ```

6. **Initialize Database**
   ```bash
   # Run migrations
   python scripts/migrate.py migrate
   
   # Create test data (optional)
   python scripts/seed_data.py
   ```

7. **Start Development Server**
   ```bash
   # Start with auto-reload
   uvicorn cloudviz.api.main:app --reload --host 0.0.0.0 --port 8000
   
   # Or using the development script
   python scripts/dev_server.py
   ```

8. **Verify Installation**
   ```bash
   # Test API
   curl http://localhost:8000/health
   
   # View interactive docs
   open http://localhost:8000/docs
   ```

## 🏗️ Project Structure

```
cloudviz/
├── cloudviz/                 # Main application package
│   ├── __init__.py
│   ├── api/                  # FastAPI application
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI app creation
│   │   ├── dependencies.py  # Dependency injection
│   │   ├── middleware.py    # Custom middleware
│   │   ├── models.py        # Pydantic models
│   │   └── routes/          # API route handlers
│   │       ├── __init__.py
│   │       ├── auth.py      # Authentication routes
│   │       ├── azure.py     # Azure-specific routes
│   │       ├── diagrams.py  # Diagram generation routes
│   │       └── system.py    # System/health routes
│   ├── core/                # Core functionality
│   │   ├── __init__.py
│   │   ├── base.py          # Base classes
│   │   ├── config.py        # Configuration management
│   │   ├── models.py        # SQLAlchemy models
│   │   └── utils/           # Utility functions
│   ├── providers/           # Cloud provider integrations
│   │   ├── __init__.py
│   │   ├── base.py          # Base provider interface
│   │   ├── azure/           # Azure implementation
│   │   ├── aws/             # AWS implementation (planned)
│   │   └── gcp/             # GCP implementation (planned)
│   └── visualization/       # Diagram generation
│       ├── __init__.py
│       ├── mermaid/         # Mermaid diagram generator
│       ├── themes/          # Visualization themes
│       └── exporters/       # Export functionality
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── conftest.py         # Pytest configuration
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── e2e/                # End-to-end tests
├── scripts/                # Utility scripts
│   ├── dev_server.py       # Development server
│   ├── migrate.py          # Database migrations
│   ├── seed_data.py        # Test data generation
│   └── deploy.py           # Deployment scripts
├── config/                 # Configuration files
│   ├── default.yml
│   ├── development.yml
│   ├── staging.yml
│   └── production.yml
├── docs/                   # Documentation
├── examples/               # Example configurations
├── requirements/           # Dependency specifications
│   ├── base.txt           # Base dependencies
│   ├── dev.txt            # Development dependencies
│   └── prod.txt           # Production dependencies
├── docker-compose.yml      # Production compose file
├── docker-compose.dev.yml  # Development compose file
├── Dockerfile             # Container definition
├── pyproject.toml         # Project metadata
└── README.md
```

## 🧪 Testing

### Test Structure

```
tests/
├── unit/                   # Unit tests (fast, isolated)
│   ├── test_config.py
│   ├── test_models.py
│   ├── api/
│   │   ├── test_routes.py
│   │   └── test_auth.py
│   ├── providers/
│   │   ├── test_azure.py
│   │   └── test_base.py
│   └── visualization/
│       ├── test_mermaid.py
│       └── test_themes.py
├── integration/            # Integration tests (with external services)
│   ├── test_database.py
│   ├── test_cache.py
│   └── test_cloud_apis.py
└── e2e/                   # End-to-end tests (full workflows)
    ├── test_discovery.py
    ├── test_visualization.py
    └── test_api_workflows.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=cloudviz --cov-report=html

# Run specific test categories
pytest tests/unit/           # Unit tests only
pytest tests/integration/    # Integration tests only
pytest tests/e2e/           # End-to-end tests only

# Run specific test files
pytest tests/unit/api/test_routes.py

# Run with verbose output
pytest -v

# Run tests in parallel
pytest -n auto

# Run tests matching pattern
pytest -k "test_azure"
```

### Writing Tests

#### Unit Test Example

```python
# tests/unit/providers/test_azure.py
import pytest
from unittest.mock import Mock, patch
from cloudviz.providers.azure.client import AzureProvider

class TestAzureProvider:
    
    @pytest.fixture
    def azure_provider(self):
        return AzureProvider(
            client_id="test-client-id",
            client_secret="test-secret",
            tenant_id="test-tenant-id"
        )
    
    @patch('azure.mgmt.resource.ResourceManagementClient')
    def test_discover_resources_success(self, mock_client, azure_provider):
        # Arrange
        mock_client.resources.list.return_value = [
            Mock(
                id="/subscriptions/test/resourceGroups/test/providers/Microsoft.Compute/virtualMachines/vm1",
                name="vm1",
                type="Microsoft.Compute/virtualMachines",
                location="eastus"
            )
        ]
        
        # Act
        resources = azure_provider.discover_resources()
        
        # Assert
        assert len(resources) == 1
        assert resources[0].name == "vm1"
        assert resources[0].type == "Microsoft.Compute/virtualMachines"
    
    def test_discover_resources_with_filters(self, azure_provider):
        # Test resource filtering
        filters = {
            "resource_group": "production",
            "resource_types": ["Microsoft.Compute/virtualMachines"]
        }
        
        with patch.object(azure_provider, '_filter_resources') as mock_filter:
            azure_provider.discover_resources(filters=filters)
            mock_filter.assert_called_once_with(filters)
```

#### Integration Test Example

```python
# tests/integration/test_api.py
import pytest
from fastapi.testclient import TestClient
from cloudviz.api.main import app

class TestAPIIntegration:
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_discovery_endpoint_with_auth(self, client, auth_token):
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.get("/api/v1/azure/resources", headers=headers)
        assert response.status_code == 200
        assert "resources" in response.json()
    
    def test_diagram_generation(self, client, sample_resources):
        response = client.post(
            "/api/v1/diagrams/mermaid",
            json={
                "resources": sample_resources,
                "theme": "enterprise"
            }
        )
        assert response.status_code == 200
        assert "diagram" in response.json()
        assert "flowchart" in response.json()["diagram"]
```

#### End-to-End Test Example

```python
# tests/e2e/test_discovery_workflow.py
import pytest
from cloudviz.providers.azure.client import AzureProvider
from cloudviz.visualization.mermaid.generator import MermaidGenerator

class TestDiscoveryWorkflow:
    
    @pytest.mark.e2e
    @pytest.mark.azure
    def test_full_discovery_and_visualization(self, azure_credentials):
        # End-to-end test of discovery -> visualization workflow
        
        # Step 1: Discover resources
        provider = AzureProvider(**azure_credentials)
        resources = provider.discover_resources(
            filters={"resource_group": "test-resources"}
        )
        
        assert len(resources) > 0
        
        # Step 2: Generate visualization
        generator = MermaidGenerator(theme="enterprise")
        diagram = generator.generate_diagram(resources)
        
        assert "flowchart" in diagram
        assert len(diagram.split('\n')) > 5  # Should have multiple lines
        
        # Step 3: Verify diagram contains expected elements
        for resource in resources:
            assert resource.name in diagram
```

### Test Configuration

```python
# tests/conftest.py
import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from cloudviz.core.models import Base
from cloudviz.core.config import get_settings

@pytest.fixture(scope="session")
def test_db():
    """Create test database"""
    engine = create_engine("sqlite:///test.db")
    Base.metadata.create_all(engine)
    yield engine
    os.unlink("test.db")

@pytest.fixture
def db_session(test_db):
    """Create database session for tests"""
    Session = sessionmaker(bind=test_db)
    session = Session()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def auth_token():
    """Generate test JWT token"""
    from cloudviz.core.auth import create_access_token
    return create_access_token(data={"sub": "test-user"})

@pytest.fixture
def sample_resources():
    """Sample resource data for testing"""
    return [
        {
            "id": "/subscriptions/test/resourceGroups/test/providers/Microsoft.Compute/virtualMachines/vm1",
            "name": "vm1",
            "type": "Microsoft.Compute/virtualMachines",
            "provider": "azure",
            "region": "eastus",
            "resource_group": "test",
            "properties": {"vm_size": "Standard_D2s_v3"}
        }
    ]

@pytest.fixture
def azure_credentials():
    """Azure test credentials (for integration tests)"""
    return {
        "client_id": os.getenv("AZURE_TEST_CLIENT_ID"),
        "client_secret": os.getenv("AZURE_TEST_CLIENT_SECRET"),
        "tenant_id": os.getenv("AZURE_TEST_TENANT_ID")
    }
```

### Test Markers

```python
# pytest.ini
[tool:pytest]
markers =
    unit: Unit tests (fast, no external dependencies)
    integration: Integration tests (require external services)
    e2e: End-to-end tests (full workflow tests)
    azure: Tests requiring Azure credentials
    aws: Tests requiring AWS credentials
    slow: Slow-running tests
```

```bash
# Run only unit tests
pytest -m unit

# Run integration tests (requires services)
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Run Azure-specific tests
pytest -m azure
```

## 🎨 Code Style & Standards

### Code Formatting

```bash
# Install formatting tools
pip install black isort flake8 mypy

# Format code
black cloudviz/
isort cloudviz/

# Check style
flake8 cloudviz/
mypy cloudviz/
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.1
    hooks:
      - id: mypy
        additional_dependencies: [types-requests, types-PyYAML]
```

### Code Guidelines

1. **Python Style**: Follow PEP 8 with Black formatting
2. **Type Hints**: Use type hints for all functions and methods
3. **Docstrings**: Use Google-style docstrings
4. **Error Handling**: Use specific exceptions with meaningful messages
5. **Logging**: Use structured logging with appropriate levels

#### Example Code Style

```python
"""Azure resource discovery module.

This module provides functionality for discovering and mapping Azure resources
to the CloudViz unified resource model.
"""

from typing import List, Optional, Dict, Any
import logging
from azure.mgmt.resource import ResourceManagementClient
from cloudviz.core.models import CloudResource
from cloudviz.providers.base import CloudProvider

logger = logging.getLogger(__name__)

class AzureProvider(CloudProvider):
    """Azure cloud provider implementation.
    
    Provides methods for authenticating with Azure and discovering resources
    across subscriptions and resource groups.
    
    Args:
        client_id: Azure service principal client ID
        client_secret: Azure service principal secret
        tenant_id: Azure tenant ID
        
    Example:
        >>> provider = AzureProvider(
        ...     client_id="12345678-1234-1234-1234-123456789012",
        ...     client_secret="secret",
        ...     tenant_id="87654321-4321-4321-4321-210987654321"
        ... )
        >>> resources = await provider.discover_resources()
    """
    
    def __init__(
        self, 
        client_id: str, 
        client_secret: str, 
        tenant_id: str,
        subscription_id: Optional[str] = None
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.subscription_id = subscription_id
        self._client: Optional[ResourceManagementClient] = None
    
    async def discover_resources(
        self, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[CloudResource]:
        """Discover Azure resources.
        
        Args:
            filters: Optional filters to apply during discovery.
                Supported filters:
                - resource_group: Filter by resource group name
                - resource_types: List of resource types to include
                - regions: List of regions to include
                
        Returns:
            List of discovered CloudResource objects.
            
        Raises:
            AuthenticationError: If Azure authentication fails
            DiscoveryError: If resource discovery fails
            
        Example:
            >>> filters = {
            ...     "resource_group": "production",
            ...     "resource_types": ["Microsoft.Compute/virtualMachines"]
            ... }
            >>> resources = await provider.discover_resources(filters)
        """
        try:
            logger.info(
                "Starting Azure resource discovery",
                extra={
                    "subscription_id": self.subscription_id,
                    "filters": filters
                }
            )
            
            client = await self._get_client()
            raw_resources = await self._fetch_resources(client, filters)
            resources = [self._map_resource(r) for r in raw_resources]
            
            logger.info(
                "Azure resource discovery completed",
                extra={
                    "resource_count": len(resources),
                    "subscription_id": self.subscription_id
                }
            )
            
            return resources
            
        except Exception as e:
            logger.error(
                "Azure resource discovery failed",
                extra={
                    "error": str(e),
                    "subscription_id": self.subscription_id
                },
                exc_info=True
            )
            raise DiscoveryError(f"Failed to discover Azure resources: {e}") from e
```

## 🔌 Extending CloudViz

### Adding a New Cloud Provider

1. **Create Provider Directory**
   ```bash
   mkdir cloudviz/providers/newcloud
   touch cloudviz/providers/newcloud/__init__.py
   ```

2. **Implement Provider Interface**
   ```python
   # cloudviz/providers/newcloud/client.py
   from typing import List, Optional, Dict, Any
   from cloudviz.providers.base import CloudProvider
   from cloudviz.core.models import CloudResource
   
   class NewCloudProvider(CloudProvider):
       
       async def authenticate(self) -> bool:
           """Authenticate with the cloud provider."""
           # Implementation here
           pass
       
       async def discover_resources(
           self, 
           filters: Optional[Dict[str, Any]] = None
       ) -> List[CloudResource]:
           """Discover cloud resources."""
           # Implementation here
           pass
       
       async def get_resource_dependencies(
           self, 
           resource_id: str
       ) -> List[str]:
           """Get resource dependencies."""
           # Implementation here
           pass
   ```

3. **Add Resource Mappings**
   ```python
   # cloudviz/providers/newcloud/mappings.py
   RESOURCE_MAPPINGS = {
       "NewCloud::Compute::Instance": {
           "category": "compute",
           "icon": "🖥️",
           "properties": ["instance_type", "state", "public_ip"]
       },
       "NewCloud::Network::VPC": {
           "category": "network",
           "icon": "🌐",
           "properties": ["cidr_block", "state"]
       }
   }
   ```

4. **Register Provider**
   ```python
   # cloudviz/providers/__init__.py
   from .newcloud.client import NewCloudProvider
   
   PROVIDERS = {
       "azure": "cloudviz.providers.azure.client.AzureProvider",
       "aws": "cloudviz.providers.aws.client.AWSProvider",
       "gcp": "cloudviz.providers.gcp.client.GCPProvider",
       "newcloud": "cloudviz.providers.newcloud.client.NewCloudProvider",
   }
   ```

5. **Add API Routes**
   ```python
   # cloudviz/api/routes/newcloud.py
   from fastapi import APIRouter, Depends
   from cloudviz.providers.newcloud.client import NewCloudProvider
   
   router = APIRouter(prefix="/newcloud", tags=["newcloud"])
   
   @router.get("/resources")
   async def discover_newcloud_resources(
       provider: NewCloudProvider = Depends(get_newcloud_provider)
   ):
       """Discover NewCloud resources."""
       resources = await provider.discover_resources()
       return {"resources": resources}
   ```

### Adding Visualization Themes

1. **Create Theme Definition**
   ```python
   # cloudviz/visualization/themes/custom.py
   CUSTOM_THEME = {
       "name": "Custom Corporate",
       "description": "Custom corporate brand theme",
       "colors": {
           "primary": "#FF6B35",      # Corporate orange
           "secondary": "#004E89",    # Corporate blue
           "accent": "#009639",       # Corporate green
           "neutral": "#6A6A6A",      # Corporate gray
           
           # Resource type mappings
           "compute": "#004E89",
           "network": "#009639",
           "storage": "#FF6B35",
           "security": "#8B0000",
           "management": "#6A6A6A"
       },
       "styles": {
           "node_shape": "round",
           "edge_style": "curved",
           "font_family": "Roboto, sans-serif",
           "font_size": "11px",
           "border_width": "2px"
       }
   }
   ```

2. **Register Theme**
   ```python
   # cloudviz/visualization/themes/__init__.py
   from .custom import CUSTOM_THEME
   
   THEMES = {
       "enterprise": ENTERPRISE_THEME,
       "security": SECURITY_THEME,
       "cost": COST_THEME,
       "custom": CUSTOM_THEME,
   }
   ```

### Adding Export Formats

1. **Create Exporter**
   ```python
   # cloudviz/visualization/exporters/pdf.py
   from typing import Dict, Any
   from cloudviz.visualization.exporters.base import BaseExporter
   
   class PDFExporter(BaseExporter):
       
       def export(self, diagram: str, options: Dict[str, Any]) -> bytes:
           """Export diagram to PDF format."""
           # Implementation using reportlab or similar
           pass
   ```

2. **Register Exporter**
   ```python
   # cloudviz/visualization/exporters/__init__.py
   EXPORTERS = {
       "png": "cloudviz.visualization.exporters.png.PNGExporter",
       "svg": "cloudviz.visualization.exporters.svg.SVGExporter",
       "pdf": "cloudviz.visualization.exporters.pdf.PDFExporter",
   }
   ```

## 🚀 Contributing Guidelines

### Pull Request Process

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/your-username/cloudviz.git
   cd cloudviz
   git remote add upstream https://github.com/navidrast/cloudviz.git
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/add-new-provider
   ```

3. **Make Changes**
   - Follow coding standards
   - Add tests for new functionality
   - Update documentation
   - Ensure all tests pass

4. **Commit Changes**
   ```bash
   # Use conventional commit format
   git commit -m "feat: add support for NewCloud provider"
   git commit -m "fix: resolve Azure timeout issues"
   git commit -m "docs: update API documentation"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/add-new-provider
   # Create pull request on GitHub
   ```

### Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(azure): add support for Azure SQL databases
fix(api): resolve timeout issues in resource discovery
docs(wiki): add troubleshooting guide for common issues
test(providers): add integration tests for AWS provider
```

### Code Review Guidelines

#### For Contributors:
- Ensure all tests pass
- Include comprehensive test coverage
- Update documentation
- Follow coding standards
- Provide clear PR description

#### For Reviewers:
- Check code quality and standards
- Verify test coverage
- Test functionality manually
- Review security implications
- Ensure backward compatibility

### Release Process

1. **Version Bump**
   ```bash
   # Update version in pyproject.toml
   poetry version patch|minor|major
   ```

2. **Update Changelog**
   ```markdown
   # CHANGELOG.md
   ## [1.1.0] - 2024-02-01
   
   ### Added
   - Support for AWS resource discovery
   - New cost analysis visualization theme
   
   ### Fixed
   - Azure timeout issues during large resource discovery
   - Memory leaks in diagram generation
   
   ### Changed
   - Improved error handling in cloud provider authentication
   ```

3. **Create Release**
   ```bash
   git tag v1.1.0
   git push origin v1.1.0
   ```

## 📚 Development Resources

### Useful Commands

```bash
# Development server with auto-reload
uvicorn cloudviz.api.main:app --reload

# Run linting
flake8 cloudviz/
black --check cloudviz/
isort --check-only cloudviz/
mypy cloudviz/

# Run tests with coverage
pytest --cov=cloudviz --cov-report=html

# Generate API documentation
python scripts/generate_docs.py

# Build Docker image
docker build -t cloudviz:dev .

# Run security checks
bandit -r cloudviz/
safety check
```

### IDE Configuration

#### VS Code Settings
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "files.associations": {
        "*.yml": "yaml"
    }
}
```

#### PyCharm Settings
- Enable Black as the code formatter
- Configure pytest as the test runner
- Set up pre-commit hooks
- Enable type checking with mypy

### Debugging

#### Debug Configuration
```python
# debug_server.py
import uvicorn
from cloudviz.api.main import app

if __name__ == "__main__":
    uvicorn.run(
        "cloudviz.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug"
    )
```

#### Using Python Debugger
```python
import pdb; pdb.set_trace()  # Set breakpoint

# Or use ipdb for better interface
import ipdb; ipdb.set_trace()
```

#### Remote Debugging (VS Code)
```json
{
    "name": "Python: Remote Attach",
    "type": "python",
    "request": "attach",
    "port": 5678,
    "host": "localhost",
    "pathMappings": [
        {
            "localRoot": "${workspaceFolder}",
            "remoteRoot": "/app"
        }
    ]
}
```

---

Ready to contribute? Check out our [GitHub Issues](https://github.com/navidrast/cloudviz/issues) for beginner-friendly tasks labeled `good first issue` or `help wanted`.