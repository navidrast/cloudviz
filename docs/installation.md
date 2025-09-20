# Installation Guide

This guide will help you install and set up CloudViz in various environments.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Memory**: Minimum 2GB RAM (4GB recommended)
- **Storage**: 10GB free disk space
- **Network**: Internet access for cloud API calls

### Cloud Provider Access
- **Azure**: Service Principal with Contributor access
- **AWS**: IAM user with read permissions
- **GCP**: Service Account with Viewer role

## 🚀 Quick Installation

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/navidrast/cloudviz.git
cd cloudviz

# Start with Docker Compose
docker-compose up -d

# Verify installation
curl http://localhost:8000/health
```

### Option 2: Python Installation

```bash
# Clone the repository
git clone https://github.com/navidrast/cloudviz.git
cd cloudviz

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export AZURE_CLIENT_ID=your-azure-client-id
export AZURE_CLIENT_SECRET=your-azure-client-secret
export AZURE_TENANT_ID=your-azure-tenant-id

# Start the server
uvicorn cloudviz.api.main:app --host 0.0.0.0 --port 8000
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```bash
# API Configuration
CLOUDVIZ_HOST=0.0.0.0
CLOUDVIZ_PORT=8000
CLOUDVIZ_WORKERS=4

# Azure Configuration
AZURE_CLIENT_ID=your-azure-client-id
AZURE_CLIENT_SECRET=your-azure-client-secret
AZURE_TENANT_ID=your-azure-tenant-id
AZURE_SUBSCRIPTION_ID=your-subscription-id

# AWS Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_DEFAULT_REGION=ap-southeast-2

# GCP Configuration
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
GCP_PROJECT_ID=your-gcp-project-id

# Database Configuration (Optional)
DATABASE_URL=postgresql://user:password@localhost/cloudviz

# Cache Configuration (Optional)
REDIS_URL=redis://localhost:6379
```

### Configuration Files

CloudViz supports YAML configuration files for advanced settings:

```yaml
# config/production.yml
api:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  cors_enabled: true
  cors_origins: ["*"]

cloud_providers:
  azure:
    enabled: true
    regions: ["australiaeast", "australiasoutheast"]
    resource_groups: ["production", "staging"]
  
  aws:
    enabled: true
    regions: ["ap-southeast-2", "us-east-1"]
  
  gcp:
    enabled: true
    regions: ["australia-southeast1", "us-central1"]

visualization:
  default_format: "mermaid"
  default_layout: "hierarchical"
  include_costs: true
  include_dependencies: true

cache:
  enabled: true
  ttl: 3600
  backend: "memory"  # or "redis"

logging:
  level: "INFO"
  format: "json"
```

## 🔧 Cloud Provider Setup

### Azure Setup

1. **Create Service Principal**:
```bash
az ad sp create-for-rbac --name cloudviz-sp --role Contributor
```

2. **Grant Required Permissions**:
   - Reader access to subscriptions
   - Contributor access for resource discovery

3. **Test Connection**:
```bash
curl -X POST http://localhost:8000/api/v1/azure/test-connection \
  -H "Content-Type: application/json" \
  -d '{"subscription_id": "your-subscription-id"}'
```

### AWS Setup

1. **Create IAM User**:
```bash
aws iam create-user --user-name cloudviz-user
aws iam create-access-key --user-name cloudviz-user
```

2. **Attach Policies**:
```bash
aws iam attach-user-policy --user-name cloudviz-user \
  --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess
```

3. **Test Connection**:
```bash
curl -X POST http://localhost:8000/api/v1/aws/test-connection \
  -H "Content-Type: application/json"
```

### GCP Setup

1. **Create Service Account**:
```bash
gcloud iam service-accounts create cloudviz-sa \
  --description="CloudViz Service Account" \
  --display-name="CloudViz"
```

2. **Grant Permissions**:
```bash
gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:cloudviz-sa@your-project-id.iam.gserviceaccount.com" \
  --role="roles/viewer"
```

3. **Create Key**:
```bash
gcloud iam service-accounts keys create cloudviz-key.json \
  --iam-account=cloudviz-sa@your-project-id.iam.gserviceaccount.com
```

## 🐳 Docker Installation

### Single Container

```bash
# Build the image
docker build -t cloudviz:latest .

# Run the container
docker run -d \
  --name cloudviz \
  -p 8000:8000 \
  -e AZURE_CLIENT_ID=your-client-id \
  -e AZURE_CLIENT_SECRET=your-client-secret \
  -e AZURE_TENANT_ID=your-tenant-id \
  cloudviz:latest
```

### Docker Compose

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
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
    depends_on:
      - redis
      - postgres

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: cloudviz
      POSTGRES_USER: cloudviz
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

## ✅ Verification

After installation, verify CloudViz is working:

1. **Health Check**:
```bash
curl http://localhost:8000/health
```

2. **API Documentation**:
Visit `http://localhost:8000/docs`

3. **Test Resource Discovery**:
```bash
curl -X POST http://localhost:8000/api/v1/azure/extract \
  -H "Content-Type: application/json" \
  -d '{"subscription_id": "your-subscription-id", "resource_groups": ["test"]}'
```

## 🔍 Troubleshooting

### Common Issues

1. **Port Already in Use**:
```bash
# Check what's using port 8000
lsof -i :8000

# Use a different port
uvicorn cloudviz.api.main:app --port 8080
```

2. **Authentication Errors**:
```bash
# Verify environment variables
echo $AZURE_CLIENT_ID
echo $AWS_ACCESS_KEY_ID

# Test cloud provider credentials
az account show  # Azure
aws sts get-caller-identity  # AWS
gcloud auth list  # GCP
```

3. **Memory Issues**:
```bash
# Reduce worker count
export CLOUDVIZ_WORKERS=1

# Monitor memory usage
docker stats cloudviz
```

## 📚 Next Steps

- [Configuration Guide](configuration.md) - Customize CloudViz settings
- [Multi-Cloud Setup](guides/multi-cloud-setup.md) - Configure multiple cloud providers
- [API Reference](api/README.md) - Explore the REST API
- [n8n Integration](guides/n8n-integration.md) - Set up automation workflows

---

For production deployment, see the [Production Setup Guide](deployment/production.md).