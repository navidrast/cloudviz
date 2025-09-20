# Getting Started with CloudViz

This guide will help you get CloudViz up and running quickly, from installation to generating your first infrastructure diagram.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, or Windows
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 2GB free space

### Cloud Access Requirements
To discover and visualize cloud resources, you'll need:

#### Azure (Currently Supported)
- Azure subscription with resources
- Service principal with read access
- Azure CLI (optional, for easier authentication)

#### AWS (Planned)
- AWS account with resources
- IAM user with appropriate read permissions
- AWS CLI (optional)

#### GCP (Planned)
- Google Cloud project with resources
- Service account with read permissions
- Google Cloud SDK (optional)

## 🚀 Quick Start

### Step 1: Clone the Repository

```bash
git clone https://github.com/navidrast/cloudviz.git
cd cloudviz
```

### Step 2: Install Dependencies

#### Using pip (Recommended)
```bash
# Create virtual environment (recommended)
python -m venv cloudviz-env
source cloudviz-env/bin/activate  # On Windows: cloudviz-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Using Docker
```bash
# Build the Docker image
docker build -t cloudviz .

# Or use Docker Compose
docker-compose up -d
```

### Step 3: Configure Cloud Authentication

#### Azure Configuration
```bash
# Method 1: Environment variables
export AZURE_CLIENT_ID="your-azure-client-id"
export AZURE_CLIENT_SECRET="your-azure-client-secret"
export AZURE_TENANT_ID="your-azure-tenant-id"
export AZURE_SUBSCRIPTION_ID="your-subscription-id"

# Method 2: Azure CLI login (alternative)
az login
```

#### Configuration File (Optional)
Create `config/local.yml`:
```yaml
cloud_providers:
  azure:
    enabled: true
    subscription_ids: ["your-subscription-id"]
    regions: ["australiaeast", "australiasoutheast"]
    resource_groups: ["production", "staging"]

api:
  host: "0.0.0.0"
  port: 8000
  debug: true

visualization:
  default_format: "mermaid"
  theme: "enterprise"
  include_costs: true
```

### Step 4: Start the API Server

```bash
# Development mode (with auto-reload)
uvicorn cloudviz.api.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn cloudviz.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Step 5: Verify Installation

```bash
# Check API health
curl http://localhost:8000/health

# List available cloud providers
curl http://localhost:8000/api/v1/providers

# Discover Azure resources (requires authentication)
curl -H "Authorization: Bearer your-jwt-token" \
     http://localhost:8000/api/v1/azure/resources
```

## 🎨 Generate Your First Diagram

### Discover and Visualize Azure Resources

```bash
# 1. Discover Azure resources
curl -H "Authorization: Bearer your-jwt-token" \
     -X GET "http://localhost:8000/api/v1/azure/resources?resource_group=production" \
     -o resources.json

# 2. Generate Mermaid diagram
curl -X POST "http://localhost:8000/api/v1/diagrams/mermaid" \
     -H "Content-Type: application/json" \
     -d @resources.json \
     -o diagram.md

# 3. Generate PNG image (requires mermaid-cli)
curl -X POST "http://localhost:8000/api/v1/diagrams/mermaid/png" \
     -H "Content-Type: application/json" \
     -d @resources.json \
     --output diagram.png
```

### Using the Interactive API

1. Open http://localhost:8000/docs in your browser
2. Click "Authorize" and enter your credentials
3. Try the `/api/v1/azure/resources` endpoint
4. Copy the response to the `/api/v1/diagrams/mermaid` endpoint
5. View your generated diagram!

## 🐳 Docker Deployment

### Quick Docker Run

```bash
# Run with environment variables
docker run -d \
  --name cloudviz \
  -p 8000:8000 \
  -e AZURE_CLIENT_ID="your-client-id" \
  -e AZURE_CLIENT_SECRET="your-secret" \
  -e AZURE_TENANT_ID="your-tenant-id" \
  cloudviz
```

### Docker Compose (Recommended)

```yaml
# docker-compose.yml
version: '3.8'

services:
  cloudviz:
    build: .
    ports:
      - "8000:8000"
    environment:
      - AZURE_CLIENT_ID=${AZURE_CLIENT_ID}
      - AZURE_CLIENT_SECRET=${AZURE_CLIENT_SECRET}
      - AZURE_TENANT_ID=${AZURE_TENANT_ID}
      - AZURE_SUBSCRIPTION_ID=${AZURE_SUBSCRIPTION_ID}
    volumes:
      - ./config:/app/config
      - ./data:/app/data
    restart: unless-stopped

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
```

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f cloudviz

# Stop services
docker-compose down
```

## ⚙️ Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `AZURE_CLIENT_ID` | Azure service principal client ID | `12345678-1234-1234-1234-123456789012` |
| `AZURE_CLIENT_SECRET` | Azure service principal secret | `your-secret-value` |
| `AZURE_TENANT_ID` | Azure tenant ID | `87654321-4321-4321-4321-210987654321` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AZURE_SUBSCRIPTION_ID` | Specific Azure subscription | All accessible |
| `API_HOST` | API server host | `0.0.0.0` |
| `API_PORT` | API server port | `8000` |
| `DEBUG` | Enable debug mode | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379` |

### Environment File

Create `.env` file in the project root:
```bash
# Azure Configuration
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-secret
AZURE_TENANT_ID=your-tenant-id
AZURE_SUBSCRIPTION_ID=your-subscription-id

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
LOG_LEVEL=DEBUG

# Cache Configuration
REDIS_URL=redis://localhost:6379

# Security
JWT_SECRET_KEY=your-secure-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600
```

## 🔧 Verification & Testing

### Health Checks

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed system status
curl http://localhost:8000/api/v1/system/status

# Check cloud provider connectivity
curl -H "Authorization: Bearer your-token" \
     http://localhost:8000/api/v1/providers/azure/status
```

### Test Azure Integration

```bash
# List resource groups
curl -H "Authorization: Bearer your-token" \
     "http://localhost:8000/api/v1/azure/resource-groups"

# Get specific resource group details
curl -H "Authorization: Bearer your-token" \
     "http://localhost:8000/api/v1/azure/resource-groups/production"

# Discovery with filters
curl -H "Authorization: Bearer your-token" \
     "http://localhost:8000/api/v1/azure/resources?regions=australiaeast&resource_types=Microsoft.Compute/virtualMachines"
```

## 🚨 Common Issues & Solutions

### Authentication Issues

**Problem**: `401 Unauthorized` errors
**Solution**: Verify your Azure service principal has correct permissions:
```bash
# Check service principal permissions
az role assignment list --assignee your-client-id --all

# Grant Reader role if needed
az role assignment create \
  --assignee your-client-id \
  --role Reader \
  --scope /subscriptions/your-subscription-id
```

### Connection Issues

**Problem**: Can't connect to Azure APIs
**Solution**: Check network connectivity and credentials:
```bash
# Test Azure API directly
curl -H "Authorization: Bearer $(az account get-access-token --query accessToken -o tsv)" \
     "https://management.azure.com/subscriptions/your-subscription-id/resources?api-version=2021-04-01"
```

### Installation Issues

**Problem**: Dependency installation fails
**Solution**: Update pip and try again:
```bash
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

### Docker Issues

**Problem**: Docker container won't start
**Solution**: Check Docker logs and environment variables:
```bash
docker logs cloudviz
docker exec -it cloudviz env | grep AZURE
```

## 📚 Next Steps

Now that you have CloudViz running:

1. **[Explore the API](API-Documentation)** - Learn about all available endpoints
2. **[Configure Cloud Providers](Cloud-Providers)** - Set up Azure, AWS, or GCP
3. **[Customize Visualizations](Visualization)** - Themes, layouts, and styling
4. **[Set up n8n Integration](n8n-Integration)** - Automate your workflows
5. **[Deploy to Production](Deployment)** - Kubernetes, Docker, and scaling

## 🆘 Getting Help

- **Documentation**: Browse this wiki for detailed guides
- **Issues**: [Report bugs or request features](https://github.com/navidrast/cloudviz/issues)
- **Discussions**: [Community discussions](https://github.com/navidrast/cloudviz/discussions)
- **API Reference**: Interactive docs at `/docs` when running

---

**Having trouble?** Check our **[Troubleshooting Guide](Troubleshooting)** or **[file an issue](https://github.com/navidrast/cloudviz/issues/new)**.