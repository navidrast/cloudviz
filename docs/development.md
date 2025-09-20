# Development Setup Guide

This guide helps you set up a complete development environment for CloudViz.

## 🛠️ Prerequisites

### Required Software
- **Python 3.8+** - Main programming language
- **Git** - Version control
- **Docker & Docker Compose** - Container development
- **Node.js 16+** - For development tools (optional)
- **VS Code or PyCharm** - Recommended IDEs

### Recommended Tools
- **pyenv** - Python version management
- **poetry** - Python dependency management
- **pre-commit** - Git hooks for code quality
- **httpie** - API testing tool
- **jq** - JSON processing

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/navidrast/cloudviz.git
cd cloudviz

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements/dev.txt

# Install pre-commit hooks
pre-commit install

# Copy environment template
cp .env.example .env
# Edit .env with your configuration
```

### 2. Development Environment

```bash
# Start development services
docker-compose -f docker-compose.dev.yml up -d

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn cloudviz.api.main:app --reload --host 0.0.0.0 --port 8000

# Verify setup
curl http://localhost:8000/health
```

## 🔧 Development Configuration

### Environment Variables

Create a `.env` file for development:

```bash
# Development Environment
CLOUDVIZ_ENV=development
CLOUDVIZ_DEBUG=true
CLOUDVIZ_LOG_LEVEL=DEBUG

# Database
DATABASE_URL=postgresql://cloudviz:dev_password@localhost:5432/cloudviz_dev

# Cache
REDIS_URL=redis://localhost:6379/0

# Cloud Provider Credentials (for testing)
AZURE_CLIENT_ID=your-dev-azure-client-id
AZURE_CLIENT_SECRET=your-dev-azure-client-secret
AZURE_TENANT_ID=your-dev-azure-tenant-id
AZURE_SUBSCRIPTION_ID=your-dev-subscription-id

AWS_ACCESS_KEY_ID=your-dev-aws-access-key
AWS_SECRET_ACCESS_KEY=your-dev-aws-secret-key
AWS_DEFAULT_REGION=ap-southeast-2

GOOGLE_APPLICATION_CREDENTIALS=./config/gcp-dev-key.json
GCP_PROJECT_ID=your-dev-gcp-project

# Development Features
ENABLE_DEBUG_TOOLBAR=true
ENABLE_HOT_RELOAD=true
ENABLE_MOCK_PROVIDERS=true
```

### Development Docker Compose

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  postgres-dev:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: cloudviz_dev
      POSTGRES_USER: cloudviz
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data
    command: postgres -c log_statement=all  # Log all SQL for debugging

  redis-dev:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --loglevel verbose

  mailhog:
    image: mailhog/mailhog
    ports:
      - "1025:1025"  # SMTP
      - "8025:8025"  # Web UI
    logging:
      driver: none

volumes:
  postgres_dev_data:
```

## 🏗️ Project Structure

```
cloudviz/
├── .github/                 # GitHub workflows and templates
├── cloudviz/               # Main application package
│   ├── __init__.py
│   ├── api/               # FastAPI application
│   │   ├── __init__.py
│   │   ├── main.py        # FastAPI app and routes
│   │   ├── routes/        # API route handlers
│   │   ├── middleware/    # Custom middleware
│   │   ├── dependencies.py # Dependency injection
│   │   └── models.py      # Pydantic models
│   ├── core/              # Core business logic
│   │   ├── __init__.py
│   │   ├── config.py      # Configuration management
│   │   ├── database.py    # Database setup
│   │   ├── cache.py       # Caching logic
│   │   └── utils.py       # Utility functions
│   ├── providers/         # Cloud provider integrations
│   │   ├── __init__.py
│   │   ├── base.py        # Abstract base classes
│   │   ├── azure/         # Azure implementation
│   │   ├── aws/           # AWS implementation
│   │   └── gcp/           # GCP implementation
│   └── visualization/     # Diagram generation
│       ├── __init__.py
│       ├── mermaid.py     # Mermaid diagrams
│       ├── themes.py      # Visual themes
│       └── layouts.py     # Layout algorithms
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── conftest.py        # Pytest configuration
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── fixtures/          # Test data
├── docs/                  # Documentation
├── scripts/               # Utility scripts
├── config/                # Configuration files
├── examples/              # Example configurations
├── requirements/          # Dependency files
│   ├── base.txt          # Base dependencies
│   ├── dev.txt           # Development dependencies
│   └── test.txt          # Testing dependencies
├── alembic/              # Database migrations
├── .env.example          # Environment template
├── .gitignore            # Git ignore rules
├── .pre-commit-config.yaml # Pre-commit configuration
├── pyproject.toml        # Project configuration
├── Dockerfile            # Container definition
├── docker-compose.yml    # Production compose
├── docker-compose.dev.yml # Development compose
└── README.md             # Project README
```

## 🧪 Testing Setup

### Test Configuration

```python
# tests/conftest.py
import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from cloudviz.api.main import app
from cloudviz.core.database import get_db, Base
from cloudviz.core.config import settings

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    """Test client for API testing."""
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
async def async_client():
    """Async test client for async testing."""
    Base.metadata.create_all(bind=engine)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def mock_azure_client():
    """Mock Azure client for testing."""
    with patch('cloudviz.providers.azure.client.AzureClient') as mock:
        mock.return_value.get_resources.return_value = [
            {
                "id": "test-vm-1",
                "name": "test-vm-1",
                "type": "VirtualMachine",
                "location": "australiaeast"
            }
        ]
        yield mock
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=cloudviz --cov-report=html

# Run specific test file
pytest tests/unit/test_azure_provider.py

# Run with verbose output
pytest -v

# Run only failed tests
pytest --lf

# Run tests in parallel
pytest -n auto

# Watch for changes and re-run tests
ptw
```

### Writing Tests

```python
# tests/unit/test_azure_provider.py
import pytest
from unittest.mock import AsyncMock, patch

from cloudviz.providers.azure import AzureProvider

class TestAzureProvider:
    """Test Azure provider functionality."""
    
    @pytest.fixture
    def azure_provider(self):
        """Create Azure provider instance."""
        return AzureProvider(
            client_id="test-client-id",
            client_secret="test-client-secret",
            tenant_id="test-tenant-id",
            subscription_id="test-subscription-id"
        )
    
    @pytest.mark.asyncio
    async def test_authenticate_success(self, azure_provider):
        """Test successful Azure authentication."""
        with patch('azure.identity.ClientSecretCredential') as mock_cred:
            mock_cred.return_value = AsyncMock()
            
            result = await azure_provider.authenticate()
            
            assert result is True
            mock_cred.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_discover_resources(self, azure_provider, mock_azure_client):
        """Test resource discovery."""
        resources = await azure_provider.discover_resources({})
        
        assert len(resources) == 1
        assert resources[0]["name"] == "test-vm-1"
        assert resources[0]["type"] == "VirtualMachine"
    
    @pytest.mark.asyncio
    async def test_discover_resources_with_filters(self, azure_provider):
        """Test resource discovery with filters."""
        filters = {
            "resource_groups": ["production"],
            "resource_types": ["VirtualMachine"]
        }
        
        with patch.object(azure_provider, '_get_filtered_resources') as mock_get:
            mock_get.return_value = []
            
            resources = await azure_provider.discover_resources(filters)
            
            mock_get.assert_called_once_with(filters)
```

### Integration Tests

```python
# tests/integration/test_api.py
import pytest
from httpx import AsyncClient

class TestHealthAPI:
    """Test health API endpoints."""
    
    @pytest.mark.asyncio
    async def test_health_check(self, async_client: AsyncClient):
        """Test health check endpoint."""
        response = await async_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data

class TestResourceAPI:
    """Test resource API endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_resources_unauthorized(self, async_client: AsyncClient):
        """Test unauthorized access to resources."""
        response = await async_client.get("/api/v1/resources")
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_resources_authorized(self, async_client: AsyncClient):
        """Test authorized access to resources."""
        # Create test user and get token
        token = await self.get_test_token(async_client)
        
        headers = {"Authorization": f"Bearer {token}"}
        response = await async_client.get("/api/v1/resources", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "resources" in data
        assert "total" in data
    
    async def get_test_token(self, client: AsyncClient) -> str:
        """Get test authentication token."""
        login_data = {
            "username": "test_user",
            "password": "test_password"
        }
        response = await client.post("/auth/token", json=login_data)
        return response.json()["access_token"]
```

## 🔍 Code Quality Tools

### Pre-commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3

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
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ["-r", "cloudviz/"]
        exclude: tests/
```

### Code Formatting

```bash
# Format code with black
black cloudviz/ tests/

# Sort imports with isort
isort cloudviz/ tests/

# Check code style with flake8
flake8 cloudviz/ tests/

# Type checking with mypy
mypy cloudviz/

# Security analysis with bandit
bandit -r cloudviz/
```

### VS Code Configuration

```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".pytest_cache": true,
        ".mypy_cache": true,
        "*.egg-info": true
    }
}
```

### Launch Configuration

```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "CloudViz API",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/venv/bin/uvicorn",
            "args": [
                "cloudviz.api.main:app",
                "--reload",
                "--host", "0.0.0.0",
                "--port", "8000"
            ],
            "console": "integratedTerminal",
            "envFile": "${workspaceFolder}/.env"
        },
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal"
        },
        {
            "name": "Python: Pytest",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["${workspaceFolder}/tests"],
            "console": "integratedTerminal"
        }
    ]
}
```

## 🔧 Development Tools

### Custom Development Scripts

```bash
#!/bin/bash
# scripts/dev-setup.sh

set -e

echo "🚀 Setting up CloudViz development environment..."

# Check prerequisites
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements/dev.txt

# Install pre-commit hooks
echo "🪝 Installing pre-commit hooks..."
pre-commit install

# Setup environment file
if [ ! -f .env ]; then
    echo "⚙️ Creating environment file..."
    cp .env.example .env
    echo "📝 Please edit .env with your configuration"
fi

# Start development services
echo "🐳 Starting development services..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for database
echo "⏳ Waiting for database..."
sleep 10

# Run migrations
echo "🗄️ Running database migrations..."
alembic upgrade head

echo "✅ Development environment ready!"
echo "🌐 Start the API server with: uvicorn cloudviz.api.main:app --reload"
echo "📖 API documentation: http://localhost:8000/docs"
```

### Development Utilities

```python
# scripts/dev_utils.py
"""Development utilities for CloudViz."""

import asyncio
import json
from typing import Dict, Any

import httpx
from cloudviz.core.config import settings

class DevClient:
    """Development client for testing CloudViz API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url)
        self.token = None
    
    async def authenticate(self, username: str = "admin", password: str = "admin"):
        """Authenticate with the API."""
        response = await self.client.post("/auth/token", json={
            "username": username,
            "password": password
        })
        response.raise_for_status()
        data = response.json()
        self.token = data["access_token"]
        self.client.headers["Authorization"] = f"Bearer {self.token}"
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check."""
        response = await self.client.get("/health")
        response.raise_for_status()
        return response.json()
    
    async def discover_azure_resources(self, subscription_id: str) -> Dict[str, Any]:
        """Discover Azure resources."""
        response = await self.client.post("/api/v1/azure/extract", json={
            "subscription_id": subscription_id,
            "include_costs": True
        })
        response.raise_for_status()
        return response.json()
    
    async def generate_diagram(self, providers: list = None) -> Dict[str, Any]:
        """Generate infrastructure diagram."""
        if providers is None:
            providers = ["azure"]
        
        response = await self.client.post("/api/v1/visualization/generate", json={
            "providers": providers,
            "format": "mermaid",
            "layout": "hierarchical"
        })
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close the client."""
        await self.client.aclose()

# Development CLI
async def main():
    """Development CLI for testing."""
    client = DevClient()
    
    try:
        # Health check
        health = await client.health_check()
        print(f"✅ Health check: {health['status']}")
        
        # Authenticate
        await client.authenticate()
        print("✅ Authenticated successfully")
        
        # Test Azure discovery (if configured)
        if settings.azure.subscription_id:
            print("🔍 Discovering Azure resources...")
            result = await client.discover_azure_resources(settings.azure.subscription_id)
            print(f"✅ Discovery job started: {result['job_id']}")
        
        # Generate diagram
        print("🎨 Generating diagram...")
        diagram = await client.generate_diagram()
        print(f"✅ Diagram generated: {diagram['diagram_id']}")
        
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Mock Providers for Testing

```python
# cloudviz/providers/mock.py
"""Mock cloud providers for development and testing."""

from typing import List, Dict, Any
from cloudviz.providers.base import CloudProvider
from cloudviz.core.models import CloudResource

class MockAzureProvider(CloudProvider):
    """Mock Azure provider for testing."""
    
    async def authenticate(self) -> bool:
        """Mock authentication."""
        return True
    
    async def discover_resources(self, filters: Dict[str, Any]) -> List[CloudResource]:
        """Mock resource discovery."""
        return [
            CloudResource(
                id="mock-vm-1",
                name="mock-web-server",
                type="VirtualMachine", 
                provider="azure",
                region="australiaeast",
                resource_group="mock-rg",
                state="running",
                cost_per_month=156.78,
                tags={"environment": "dev", "team": "platform"},
                properties={
                    "size": "Standard_D2s_v3",
                    "os": "Ubuntu 20.04",
                    "public_ip": "203.0.113.1"
                }
            ),
            CloudResource(
                id="mock-db-1",
                name="mock-database",
                type="SqlDatabase",
                provider="azure",
                region="australiaeast",
                resource_group="mock-rg",
                state="online",
                cost_per_month=245.60,
                tags={"environment": "dev"},
                properties={
                    "tier": "Standard",
                    "size": "S2",
                    "backup_retention": 7
                }
            )
        ]

class MockAWSProvider(CloudProvider):
    """Mock AWS provider for testing."""
    
    async def authenticate(self) -> bool:
        """Mock authentication."""
        return True
    
    async def discover_resources(self, filters: Dict[str, Any]) -> List[CloudResource]:
        """Mock resource discovery."""
        return [
            CloudResource(
                id="i-1234567890abcdef0",
                name="mock-ec2-instance",
                type="EC2Instance",
                provider="aws",
                region="ap-southeast-2",
                state="running",
                cost_per_month=89.50,
                tags={"Name": "mock-ec2", "Environment": "dev"},
                properties={
                    "instance_type": "t3.medium",
                    "ami_id": "ami-12345678",
                    "vpc_id": "vpc-12345678"
                }
            )
        ]
```

## 🐳 Docker Development

### Development Dockerfile

```dockerfile
# Dockerfile.dev
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt requirements/dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r dev.txt

# Copy source code
COPY . .

# Install in development mode
RUN pip install -e .

# Expose port
EXPOSE 8000

# Development server with hot reload
CMD ["uvicorn", "cloudviz.api.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
```

### Hot Reload Configuration

```yaml
# docker-compose.override.yml (for development)
version: '3.8'

services:
  cloudviz:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - .:/app
      - /app/.venv  # Exclude virtual env from mount
    environment:
      - CLOUDVIZ_ENV=development
      - CLOUDVIZ_DEBUG=true
    ports:
      - "8000:8000"
      - "5678:5678"  # Debugger port
```

## 📊 Performance Profiling

### Performance Testing

```python
# scripts/performance_test.py
"""Performance testing utilities."""

import asyncio
import time
from typing import List
import httpx

async def load_test_endpoint(url: str, concurrent_requests: int = 10, total_requests: int = 100):
    """Load test an API endpoint."""
    
    async def make_request(client: httpx.AsyncClient, request_id: int):
        start_time = time.time()
        try:
            response = await client.get(url)
            end_time = time.time()
            return {
                "request_id": request_id,
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "success": response.status_code < 400
            }
        except Exception as e:
            end_time = time.time()
            return {
                "request_id": request_id,
                "status_code": 0,
                "response_time": end_time - start_time,
                "success": False,
                "error": str(e)
            }
    
    async with httpx.AsyncClient() as client:
        results = []
        semaphore = asyncio.Semaphore(concurrent_requests)
        
        async def controlled_request(request_id: int):
            async with semaphore:
                return await make_request(client, request_id)
        
        tasks = [controlled_request(i) for i in range(total_requests)]
        results = await asyncio.gather(*tasks)
    
    # Calculate statistics
    successful_requests = [r for r in results if r["success"]]
    failed_requests = [r for r in results if not r["success"]]
    
    if successful_requests:
        response_times = [r["response_time"] for r in successful_requests]
        avg_response_time = sum(response_times) / len(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
    else:
        avg_response_time = min_response_time = max_response_time = 0
    
    print(f"Load Test Results for {url}")
    print(f"Total requests: {total_requests}")
    print(f"Successful requests: {len(successful_requests)}")
    print(f"Failed requests: {len(failed_requests)}")
    print(f"Success rate: {len(successful_requests)/total_requests*100:.2f}%")
    print(f"Average response time: {avg_response_time:.3f}s")
    print(f"Min response time: {min_response_time:.3f}s")
    print(f"Max response time: {max_response_time:.3f}s")

if __name__ == "__main__":
    asyncio.run(load_test_endpoint("http://localhost:8000/health"))
```

### Memory Profiling

```python
# scripts/memory_profile.py
"""Memory profiling for CloudViz."""

import tracemalloc
import asyncio
from cloudviz.providers.azure import AzureProvider

async def profile_azure_discovery():
    """Profile memory usage during Azure resource discovery."""
    
    tracemalloc.start()
    
    # Initial snapshot
    snapshot1 = tracemalloc.take_snapshot()
    
    # Perform resource discovery
    provider = AzureProvider(
        client_id="test",
        client_secret="test", 
        tenant_id="test",
        subscription_id="test"
    )
    
    # This would normally make real API calls
    resources = await provider.discover_resources({})
    
    # Final snapshot
    snapshot2 = tracemalloc.take_snapshot()
    
    # Compare snapshots
    top_stats = snapshot2.compare_to(snapshot1, 'lineno')
    
    print("Memory usage during Azure discovery:")
    for stat in top_stats[:10]:
        print(stat)

if __name__ == "__main__":
    asyncio.run(profile_azure_discovery())
```

## 🚀 Deployment Pipeline

### Development to Production Flow

```mermaid
graph LR
    DEV[Development] --> PR[Pull Request]
    PR --> REVIEW[Code Review]
    REVIEW --> TEST[Automated Tests]
    TEST --> STAGING[Staging Environment]
    STAGING --> MANUAL_TEST[Manual Testing]
    MANUAL_TEST --> PROD[Production]
    
    TEST --> |Fails| PR
    MANUAL_TEST --> |Issues| PR
```

### GitHub Actions Workflow

```yaml
# .github/workflows/development.yml
name: Development Workflow

on:
  push:
    branches: [develop]
  pull_request:
    branches: [develop, main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: cloudviz_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements/dev.txt
    
    - name: Lint with flake8
      run: flake8 cloudviz/ tests/
    
    - name: Type check with mypy
      run: mypy cloudviz/
    
    - name: Test with pytest
      env:
        DATABASE_URL: postgresql://postgres:test_password@localhost:5432/cloudviz_test
        REDIS_URL: redis://localhost:6379
      run: |
        pytest --cov=cloudviz --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## 📚 Learning Resources

### Recommended Reading
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Pydantic Documentation**: https://pydantic-docs.helpmanual.io/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
- **pytest Documentation**: https://docs.pytest.org/
- **Docker Documentation**: https://docs.docker.com/

### CloudViz Specific
- [Architecture Overview](../architecture.md)
- [API Reference](../api/README.md)
- [Contributing Guidelines](../contributing.md)
- [Security Guide](../security/README.md)

## 🆘 Troubleshooting

### Common Development Issues

1. **Database Connection Issues**
   ```bash
   # Check if PostgreSQL is running
   docker-compose -f docker-compose.dev.yml ps
   
   # Reset database
   docker-compose -f docker-compose.dev.yml down -v
   docker-compose -f docker-compose.dev.yml up -d postgres-dev
   ```

2. **Import Errors**
   ```bash
   # Make sure virtual environment is activated
   source venv/bin/activate
   
   # Install in development mode
   pip install -e .
   ```

3. **Port Already in Use**
   ```bash
   # Find process using port 8000
   lsof -i :8000
   
   # Kill the process
   kill -9 <PID>
   ```

4. **Pre-commit Hook Failures**
   ```bash
   # Skip hooks temporarily
   git commit --no-verify
   
   # Fix formatting issues
   black cloudviz/ tests/
   isort cloudviz/ tests/
   ```

### Getting Help

- **GitHub Issues**: Report bugs or ask questions
- **Discord Community**: Join our developer community  
- **Documentation**: Check the comprehensive docs
- **Code Review**: Request help in pull requests

---

This development setup guide provides everything needed to start contributing to CloudViz. Happy coding! 🚀