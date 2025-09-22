# CloudViz Quick Start Guide

Get up and running with CloudViz in minutes! This guide provides complete workflow examples for all supported cloud providers and deployment scenarios.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Installation](#quick-installation)
3. [Basic Setup](#basic-setup)
4. [Azure Quick Start](#azure-quick-start)
5. [AWS Quick Start](#aws-quick-start)
6. [GCP Quick Start](#gcp-quick-start)
7. [Multi-Cloud Setup](#multi-cloud-setup)
8. [First Visualization](#first-visualization)
9. [API Usage Examples](#api-usage-examples)
10. [Common Workflows](#common-workflows)
11. [Troubleshooting](#troubleshooting)
12. [Next Steps](#next-steps)

## Prerequisites

### System Requirements
- **Operating System**: Linux, macOS, or Windows
- **Python**: 3.8+ (3.9+ recommended)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 2GB free space
- **Network**: Internet connectivity for cloud provider APIs

### Required Software
- **Docker** (recommended) or Python 3.8+
- **PostgreSQL** (for persistent storage)
- **Redis** (for caching - optional but recommended)

### Cloud Provider Access
At least one of the following:
- **Azure**: Active subscription with Service Principal
- **AWS**: Account with programmatic access
- **GCP**: Project with Service Account

## Quick Installation

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/cloudviz.git
cd cloudviz

# Start with Docker Compose
docker-compose up -d

# Check status
docker-compose ps
```

### Option 2: Python Installation

```bash
# Clone and install
git clone https://github.com/your-org/cloudviz.git
cd cloudviz
pip install -e .

# Start services
cloudviz server start
```

### Option 3: One-Line Install

```bash
# Quick Docker setup
curl -sSL https://raw.githubusercontent.com/your-org/cloudviz/main/scripts/quick-install.sh | bash
```

## Basic Setup

### 1. Environment Configuration

Create a `.env` file in the project root:

```bash
# Basic Configuration
CLOUDVIZ_ENV=development
CLOUDVIZ_SECRET_KEY=your-super-secret-key-here
CLOUDVIZ_JWT_SECRET=your-jwt-secret-here

# Database (PostgreSQL)
DATABASE_URL=postgresql://cloudviz:cloudviz@localhost:5432/cloudviz

# Cache (Redis - optional)
REDIS_URL=redis://localhost:6379/0

# API Configuration
CLOUDVIZ_API_HOST=0.0.0.0
CLOUDVIZ_API_PORT=8000
CLOUDVIZ_LOG_LEVEL=INFO
```

### 2. Database Initialization

```bash
# Initialize database
cloudviz db init

# Run migrations
cloudviz db migrate

# Verify setup
cloudviz db status
```

### 3. Verify Installation

```bash
# Check health
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0",
  "components": {
    "database": "healthy",
    "cache": "healthy",
    "providers": "ready"
  }
}
```

## Azure Quick Start

### 1. Azure Prerequisites

#### Create Service Principal
```bash
# Login to Azure
az login

# Create service principal
az ad sp create-for-rbac --name "CloudViz" --role="Reader" --scopes="/subscriptions/YOUR_SUBSCRIPTION_ID"

# Output:
{
  "appId": "12345678-1234-1234-1234-123456789012",
  "displayName": "CloudViz",
  "password": "your-client-secret",
  "tenant": "87654321-4321-4321-4321-210987654321"
}
```

#### Grant Additional Permissions
```bash
# Grant Network Contributor for network discovery
az role assignment create --assignee "12345678-1234-1234-1234-123456789012" \
  --role "Network Contributor" \
  --scope "/subscriptions/YOUR_SUBSCRIPTION_ID"

# Grant Storage Account Contributor for storage analysis
az role assignment create --assignee "12345678-1234-1234-1234-123456789012" \
  --role "Storage Account Contributor" \
  --scope "/subscriptions/YOUR_SUBSCRIPTION_ID"
```

### 2. Azure Configuration

Add to your `.env` file:
```bash
# Azure Configuration
AZURE_TENANT_ID=87654321-4321-4321-4321-210987654321
AZURE_CLIENT_ID=12345678-1234-1234-1234-123456789012
AZURE_CLIENT_SECRET=your-client-secret
AZURE_SUBSCRIPTION_ID=your-subscription-id
```

Or use configuration file `config/azure.yml`:
```yaml
providers:
  azure:
    enabled: true
    authentication_method: "service_principal"
    tenant_id: "${AZURE_TENANT_ID}"
    client_id: "${AZURE_CLIENT_ID}"
    client_secret: "${AZURE_CLIENT_SECRET}"
    subscription_id: "${AZURE_SUBSCRIPTION_ID}"
    
    # Optional: Customize discovery
    default_filters:
      include_resource_types:
        - "Microsoft.Compute/virtualMachines"
        - "Microsoft.Storage/storageAccounts"
        - "Microsoft.Sql/servers"
        - "Microsoft.Network/virtualNetworks"
        - "Microsoft.Web/sites"
      exclude_resource_groups:
        - "NetworkWatcherRG"
```

### 3. Test Azure Connection

```bash
# Test authentication
cloudviz provider test azure

# Expected output:
{
  "provider": "azure",
  "status": "success",
  "subscription": {
    "id": "your-subscription-id",
    "name": "Your Subscription Name"
  },
  "permissions": ["Reader", "Network Contributor"],
  "resource_count": 42
}
```

### 4. First Azure Discovery

```bash
# Discover Azure resources
cloudviz extract azure --output azure-inventory.json

# Generate visualization
cloudviz render azure-inventory.json --format mermaid --output azure-diagram.md

# View results
cat azure-diagram.md
```

## AWS Quick Start

### 1. AWS Prerequisites

#### Create IAM User
```bash
# Using AWS CLI
aws iam create-user --user-name cloudviz

# Create access key
aws iam create-access-key --user-name cloudviz

# Output:
{
    "AccessKey": {
        "UserName": "cloudviz",
        "AccessKeyId": "AKIAIOSFODNN7EXAMPLE",
        "Status": "Active",
        "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    }
}
```

#### Attach Permissions
```bash
# Attach read-only policy
aws iam attach-user-policy --user-name cloudviz \
  --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess

# Or create custom policy for minimal permissions
aws iam put-user-policy --user-name cloudviz \
  --policy-name CloudVizPolicy \
  --policy-document file://cloudviz-policy.json
```

Custom policy (`cloudviz-policy.json`):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "s3:ListAllMyBuckets",
        "s3:GetBucketLocation",
        "rds:Describe*",
        "lambda:List*",
        "lambda:Get*",
        "vpc:Describe*",
        "iam:ListRoles",
        "iam:ListUsers"
      ],
      "Resource": "*"
    }
  ]
}
```

### 2. AWS Configuration

Add to your `.env` file:
```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_DEFAULT_REGION=us-east-1
```

Or use configuration file `config/aws.yml`:
```yaml
providers:
  aws:
    enabled: true
    authentication_method: "access_key"
    access_key_id: "${AWS_ACCESS_KEY_ID}"
    secret_access_key: "${AWS_SECRET_ACCESS_KEY}"
    region: "us-east-1"
    
    # Multi-region discovery
    regions:
      - "us-east-1"
      - "us-west-2"
      - "eu-west-1"
    
    # Service filtering
    default_filters:
      include_resource_types:
        - "ec2_instance"
        - "s3_bucket"
        - "rds_instance"
        - "lambda_function"
        - "vpc"
```

### 3. Test AWS Connection

```bash
# Test authentication
cloudviz provider test aws

# Expected output:
{
  "provider": "aws",
  "status": "success",
  "account": {
    "id": "123456789012",
    "alias": "my-aws-account"
  },
  "regions": ["us-east-1", "us-west-2", "eu-west-1"],
  "resource_count": 156
}
```

### 4. First AWS Discovery

```bash
# Discover AWS resources
cloudviz extract aws --regions us-east-1,us-west-2 --output aws-inventory.json

# Generate visualization
cloudviz render aws-inventory.json --format mermaid --theme professional --output aws-diagram.md

# View results
cat aws-diagram.md
```

## GCP Quick Start

### 1. GCP Prerequisites

#### Create Service Account
```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Create service account
gcloud iam service-accounts create cloudviz \
  --display-name="CloudViz Service Account"

# Grant permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:cloudviz@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/viewer"

# Create and download key
gcloud iam service-accounts keys create cloudviz-key.json \
  --iam-account=cloudviz@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

### 2. GCP Configuration

Add to your `.env` file:
```bash
# GCP Configuration
GCP_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/cloudviz-key.json
```

Or use configuration file `config/gcp.yml`:
```yaml
providers:
  gcp:
    enabled: true
    authentication_method: "service_account"
    project_id: "${GCP_PROJECT_ID}"
    credentials_path: "${GOOGLE_APPLICATION_CREDENTIALS}"
    
    # Multi-project support
    projects:
      - "your-project-id"
      - "another-project-id"
    
    # Service filtering
    default_filters:
      include_resource_types:
        - "compute_instance"
        - "cloud_storage"
        - "cloud_sql"
        - "vpc_network"
        - "cloud_function"
```

### 3. Test GCP Connection

```bash
# Test authentication
cloudviz provider test gcp

# Expected output:
{
  "provider": "gcp",
  "status": "success",
  "project": {
    "id": "your-project-id",
    "name": "Your Project Name"
  },
  "zones": ["us-central1-a", "us-central1-b"],
  "resource_count": 89
}
```

### 4. First GCP Discovery

```bash
# Discover GCP resources
cloudviz extract gcp --project your-project-id --output gcp-inventory.json

# Generate visualization
cloudviz render gcp-inventory.json --format svg --layout hierarchical --output gcp-diagram.svg

# View results (if on desktop)
open gcp-diagram.svg
```

## Multi-Cloud Setup

### 1. Configure All Providers

Create `config/multi-cloud.yml`:
```yaml
providers:
  azure:
    enabled: true
    authentication_method: "service_principal"
    tenant_id: "${AZURE_TENANT_ID}"
    client_id: "${AZURE_CLIENT_ID}"
    client_secret: "${AZURE_CLIENT_SECRET}"
    subscription_id: "${AZURE_SUBSCRIPTION_ID}"
    
  aws:
    enabled: true
    authentication_method: "access_key"
    access_key_id: "${AWS_ACCESS_KEY_ID}"
    secret_access_key: "${AWS_SECRET_ACCESS_KEY}"
    region: "us-east-1"
    regions:
      - "us-east-1"
      - "eu-west-1"
    
  gcp:
    enabled: true
    authentication_method: "service_account"
    project_id: "${GCP_PROJECT_ID}"
    credentials_path: "${GOOGLE_APPLICATION_CREDENTIALS}"

# Global settings
visualization:
  default_theme: "professional"
  default_format: "mermaid"
  default_layout: "hierarchical"
```

### 2. Multi-Cloud Discovery

```bash
# Discover all clouds simultaneously
cloudviz extract all --config config/multi-cloud.yml --output multi-cloud-inventory.json

# Or discover individually and merge
cloudviz extract azure --output azure.json
cloudviz extract aws --output aws.json
cloudviz extract gcp --output gcp.json
cloudviz merge azure.json aws.json gcp.json --output multi-cloud-inventory.json
```

### 3. Multi-Cloud Visualization

```bash
# Generate comprehensive diagram
cloudviz render multi-cloud-inventory.json \
  --format mermaid \
  --theme professional \
  --layout hierarchical \
  --group-by provider \
  --output multi-cloud-architecture.md

# Generate provider-specific views
cloudviz render multi-cloud-inventory.json \
  --filter "provider=azure" \
  --output azure-view.md

cloudviz render multi-cloud-inventory.json \
  --filter "provider=aws" \
  --output aws-view.md

cloudviz render multi-cloud-inventory.json \
  --filter "provider=gcp" \
  --output gcp-view.md
```

## First Visualization

### 1. Basic Visualization

```bash
# Simple discovery and visualization
cloudviz discover --provider azure --visualize --format mermaid

# Output will be generated in ./output/
ls output/
# azure-discovery-2024-01-01.json
# azure-visualization-2024-01-01.md
```

### 2. Custom Visualization

```bash
# Discover with custom filters
cloudviz extract azure \
  --resource-types "virtualMachines,storageAccounts,sqlServers" \
  --resource-groups "prod-rg,staging-rg" \
  --output filtered-inventory.json

# Render with custom theme
cloudviz render filtered-inventory.json \
  --format svg \
  --theme dark \
  --layout force \
  --width 1920 \
  --height 1080 \
  --output custom-diagram.svg
```

### 3. Interactive Visualization

```bash
# Start web interface
cloudviz web start --port 8080

# Open in browser
open http://localhost:8080
```

## API Usage Examples

### 1. Python SDK

```python
from cloudviz import CloudVizClient

# Initialize client
client = CloudVizClient(
    base_url="http://localhost:8000",
    api_key="your-api-key"
)

# Authenticate
client.auth.login(username="admin", password="password")

# Extract Azure resources
azure_job = client.extract.start_azure_extraction(
    subscription_id="your-subscription-id",
    resource_groups=["prod-rg", "dev-rg"]
)

# Wait for completion
result = client.jobs.wait_for_completion(azure_job.id)

# Generate visualization
diagram = client.render.create_diagram(
    inventory_id=result.inventory_id,
    format="mermaid",
    theme="professional",
    layout="hierarchical"
)

print(diagram.content)
```

### 2. REST API

```bash
# Authenticate
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Response: {"access_token": "eyJ...", "token_type": "bearer"}

# Start extraction
curl -X POST http://localhost:8000/api/v1/extract/azure \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "subscription_id": "your-subscription-id",
    "resource_groups": ["prod-rg"],
    "resource_types": ["virtualMachines", "storageAccounts"]
  }'

# Response: {"job_id": "123e4567-e89b-12d3-a456-426614174000"}

# Check job status
curl -X GET http://localhost:8000/api/v1/jobs/123e4567-e89b-12d3-a456-426614174000 \
  -H "Authorization: Bearer eyJ..."

# Generate visualization
curl -X POST http://localhost:8000/api/v1/render \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "inventory_id": "inventory-123",
    "format": "mermaid",
    "theme": "professional",
    "layout": "hierarchical"
  }'
```

### 3. JavaScript SDK

```javascript
import { CloudVizClient } from 'cloudviz-js';

// Initialize client
const client = new CloudVizClient({
  baseURL: 'http://localhost:8000',
  apiKey: 'your-api-key'
});

// Authenticate
await client.auth.login('admin', 'password');

// Extract AWS resources
const job = await client.extract.aws({
  region: 'us-east-1',
  resourceTypes: ['ec2_instance', 's3_bucket', 'rds_instance']
});

// Wait for completion
const result = await client.jobs.waitForCompletion(job.id);

// Generate visualization
const diagram = await client.render.createDiagram({
  inventoryId: result.inventoryId,
  format: 'svg',
  theme: 'dark',
  layout: 'force'
});

// Download result
const blob = await diagram.download();
const url = URL.createObjectURL(blob);
window.open(url);
```

## Common Workflows

### 1. Daily Infrastructure Monitoring

Create `scripts/daily-scan.sh`:
```bash
#!/bin/bash

# Daily infrastructure discovery and comparison
DATE=$(date +%Y-%m-%d)
OUTPUT_DIR="./reports/$DATE"
mkdir -p "$OUTPUT_DIR"

# Discover current state
cloudviz extract all --output "$OUTPUT_DIR/current-inventory.json"

# Compare with yesterday
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d)
if [ -f "./reports/$YESTERDAY/current-inventory.json" ]; then
  cloudviz compare \
    "./reports/$YESTERDAY/current-inventory.json" \
    "$OUTPUT_DIR/current-inventory.json" \
    --output "$OUTPUT_DIR/changes.json"
  
  # Generate change report
  cloudviz render "$OUTPUT_DIR/changes.json" \
    --format mermaid \
    --theme minimal \
    --highlight-changes \
    --output "$OUTPUT_DIR/change-report.md"
fi

# Generate current state diagram
cloudviz render "$OUTPUT_DIR/current-inventory.json" \
  --format svg \
  --theme professional \
  --layout hierarchical \
  --output "$OUTPUT_DIR/architecture-diagram.svg"

echo "Daily scan complete. Reports available in $OUTPUT_DIR"
```

### 2. Security Audit Workflow

```bash
# Discover with security focus
cloudviz extract azure \
  --include-security-info \
  --include-compliance-status \
  --output security-inventory.json

# Generate security-focused visualization
cloudviz render security-inventory.json \
  --format mermaid \
  --theme security \
  --layout network \
  --highlight security_groups,nsg_rules,firewalls \
  --output security-diagram.md

# Export security report
cloudviz export security-inventory.json \
  --format csv \
  --include security_groups,public_ips,open_ports \
  --output security-report.csv
```

### 3. Cost Analysis Workflow

```bash
# Extract with cost information
cloudviz extract aws \
  --include-cost-data \
  --cost-period "last-30-days" \
  --output cost-inventory.json

# Generate cost visualization
cloudviz render cost-inventory.json \
  --format treemap \
  --color-by cost \
  --size-by cost \
  --output cost-analysis.html

# Export cost report
cloudviz export cost-inventory.json \
  --format excel \
  --group-by service,region \
  --aggregate cost \
  --output cost-report.xlsx
```

### 4. Compliance Reporting

```bash
# Extract with compliance tags
cloudviz extract gcp \
  --include-tags \
  --include-compliance-info \
  --output compliance-inventory.json

# Generate compliance dashboard
cloudviz render compliance-inventory.json \
  --format dashboard \
  --theme compliance \
  --group-by compliance_status \
  --output compliance-dashboard.html

# Export compliance report
cloudviz export compliance-inventory.json \
  --format pdf \
  --template compliance-report \
  --output compliance-report.pdf
```

## Troubleshooting

### Common Issues

#### 1. Authentication Failures

**Azure: "Invalid client secret"**
```bash
# Verify credentials
az login --service-principal \
  -u $AZURE_CLIENT_ID \
  -p $AZURE_CLIENT_SECRET \
  --tenant $AZURE_TENANT_ID

# Check service principal permissions
az role assignment list --assignee $AZURE_CLIENT_ID
```

**AWS: "Invalid access key"**
```bash
# Test credentials
aws sts get-caller-identity

# Check permissions
aws iam get-user
aws iam list-attached-user-policies --user-name cloudviz
```

**GCP: "Service account not found"**
```bash
# Verify service account
gcloud iam service-accounts describe cloudviz@$GCP_PROJECT_ID.iam.gserviceaccount.com

# Check permissions
gcloud projects get-iam-policy $GCP_PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:cloudviz@$GCP_PROJECT_ID.iam.gserviceaccount.com"
```

#### 2. API Errors

**Rate Limiting: "Too many requests"**
```bash
# Check rate limit status
curl -I http://localhost:8000/api/v1/health

# Headers show rate limit info:
# X-RateLimit-Limit: 100
# X-RateLimit-Remaining: 0
# X-RateLimit-Reset: 1609459200

# Wait or configure higher limits in config
```

**Memory Issues: "Out of memory"**
```bash
# Check memory usage
docker stats cloudviz

# Increase memory limits in docker-compose.yml
services:
  cloudviz:
    mem_limit: 4g
    memswap_limit: 4g
```

#### 3. Visualization Issues

**Large Diagrams: "Diagram too large"**
```bash
# Filter resources to reduce size
cloudviz extract azure \
  --resource-groups "prod-rg" \
  --resource-types "virtualMachines,storageAccounts" \
  --output filtered.json

# Use pagination for large datasets
cloudviz render large-inventory.json \
  --paginate \
  --max-nodes-per-page 100 \
  --output-dir diagrams/
```

**Rendering Failures: "Graphviz not found"**
```bash
# Install Graphviz
# Ubuntu/Debian
sudo apt-get install graphviz

# macOS
brew install graphviz

# Or use Docker image with Graphviz pre-installed
docker run -it cloudviz/cloudviz:graphviz
```

### Debug Mode

Enable debug logging for troubleshooting:

```bash
# Environment variable
export CLOUDVIZ_LOG_LEVEL=DEBUG

# Command line
cloudviz --debug extract azure

# Configuration file
logging:
  level: DEBUG
  console: true
```

### Getting Help

```bash
# Show help for any command
cloudviz --help
cloudviz extract --help
cloudviz render --help

# Show configuration
cloudviz config show

# Validate configuration
cloudviz config validate

# Test components
cloudviz test --component database
cloudviz test --component providers
```

## Next Steps

### 1. Advanced Configuration
- Set up [multi-environment configuration](Configuration.md#deployment-specific-configurations)
- Configure [monitoring and alerting](Configuration.md#monitoring-configuration)
- Set up [SSL/TLS encryption](Configuration.md#security-configuration)

### 2. Integration Setup
- Configure [n8n workflows](n8n-Integration.md) for automation
- Set up [CI/CD pipelines](Installation-Guide.md#cicd-integration)
- Integrate with [monitoring systems](System-Architecture.md#monitoring-and-observability)

### 3. Scaling
- Deploy to [Kubernetes](Installation-Guide.md#kubernetes-deployment)
- Configure [load balancing](Installation-Guide.md#load-balancer-setup)
- Set up [multi-region deployment](Installation-Guide.md#multi-region-deployment)

### 4. Customization
- Create [custom themes](Configuration.md#theme-configuration)
- Develop [custom extractors](API-Reference.md#custom-extractors)
- Build [custom visualizations](API-Reference.md#custom-visualizations)

### 5. Community
- Join our [Discord community](https://discord.gg/cloudviz)
- Contribute to the [GitHub repository](https://github.com/your-org/cloudviz)
- Report issues and request features

For detailed documentation on any topic, see the complete [CloudViz Wiki](Home.md).
