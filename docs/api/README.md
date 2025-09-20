# CloudViz API Reference

Complete REST API documentation for CloudViz - Multi-Cloud Infrastructure Visualization Platform.

## 🔗 Base URL

```
http://localhost:8000
```

## 🔐 Authentication

CloudViz supports multiple authentication methods:

### API Key Authentication
```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/v1/resources
```

### JWT Token Authentication
```bash
# Get token
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Use token
curl -H "Authorization: Bearer your-jwt-token" http://localhost:8000/api/v1/resources
```

## 📊 Endpoints Overview

| Category | Endpoints | Description |
|----------|-----------|-------------|
| **Health** | `/health` | System health and status |
| **Authentication** | `/auth/*` | Authentication and authorization |
| **Resources** | `/api/v1/resources/*` | Cloud resource discovery |
| **Visualization** | `/api/v1/visualization/*` | Diagram generation |
| **Azure** | `/api/v1/azure/*` | Azure-specific operations |
| **AWS** | `/api/v1/aws/*` | AWS-specific operations |
| **GCP** | `/api/v1/gcp/*` | GCP-specific operations |
| **Administration** | `/api/v1/admin/*` | System administration |

## 🏥 Health & System

### GET /health
System health check and version information.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-01-20T10:30:00Z",
  "uptime": 3600,
  "components": {
    "database": "healthy",
    "cache": "healthy",
    "azure_client": "healthy",
    "aws_client": "healthy",
    "gcp_client": "healthy"
  }
}
```

### GET /metrics
Prometheus metrics for monitoring.

```
# HELP cloudviz_requests_total Total number of requests
# TYPE cloudviz_requests_total counter
cloudviz_requests_total{method="GET",endpoint="/health"} 100
```

## 🔐 Authentication

### POST /auth/token
Generate JWT authentication token.

**Request:**
```json
{
  "username": "admin",
  "password": "password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### POST /auth/refresh
Refresh an existing JWT token.

**Request:**
```json
{
  "refresh_token": "your-refresh-token"
}
```

## ☁️ Multi-Cloud Resource Discovery

### GET /api/v1/resources
List all discovered cloud resources across all providers.

**Query Parameters:**
- `provider` (string): Filter by cloud provider (azure, aws, gcp)
- `region` (string): Filter by region
- `resource_type` (string): Filter by resource type
- `limit` (int): Number of results (default: 100)
- `offset` (int): Pagination offset (default: 0)

**Response:**
```json
{
  "total": 150,
  "limit": 100,
  "offset": 0,
  "resources": [
    {
      "id": "resource-123",
      "name": "web-server-01",
      "type": "VirtualMachine",
      "provider": "azure",
      "region": "australiaeast",
      "resource_group": "production",
      "status": "running",
      "cost_per_month": 156.78,
      "tags": {
        "environment": "production",
        "team": "platform"
      },
      "created_at": "2025-01-15T09:00:00Z",
      "last_updated": "2025-01-20T10:30:00Z"
    }
  ]
}
```

### GET /api/v1/resources/{provider}
List resources for a specific cloud provider.

**Path Parameters:**
- `provider` (string): Cloud provider (azure, aws, gcp)

## 🔷 Azure Operations

### POST /api/v1/azure/extract
Extract resources from Azure subscription.

**Request:**
```json
{
  "subscription_id": "12345678-1234-1234-1234-123456789012",
  "resource_groups": ["production", "staging"],
  "regions": ["australiaeast", "australiasoutheast"],
  "resource_types": ["VirtualMachine", "StorageAccount", "SqlDatabase"],
  "include_costs": true,
  "webhook_url": "http://your-webhook.com/azure-complete"
}
```

**Response:**
```json
{
  "job_id": "azure-job-456",
  "status": "started",
  "subscription_id": "12345678-1234-1234-1234-123456789012",
  "estimated_duration": 300,
  "webhook_url": "http://your-webhook.com/azure-complete"
}
```

### GET /api/v1/azure/subscription-info
Get Azure subscription information.

**Response:**
```json
{
  "subscription_id": "12345678-1234-1234-1234-123456789012",
  "display_name": "Production Subscription",
  "state": "Enabled",
  "tenant_id": "87654321-4321-4321-4321-210987654321",
  "resource_groups": ["production", "staging", "development"],
  "regions": ["australiaeast", "australiasoutheast"]
}
```

### POST /api/v1/azure/test-connection
Test Azure connection and credentials.

**Request:**
```json
{
  "subscription_id": "12345678-1234-1234-1234-123456789012"
}
```

**Response:**
```json
{
  "status": "success",
  "subscription_name": "Production Subscription",
  "permissions": ["Reader", "Contributor"],
  "accessible_resource_groups": 15
}
```

## ☁️ AWS Operations

### POST /api/v1/aws/extract
Extract resources from AWS account.

**Request:**
```json
{
  "account_id": "123456789012",
  "regions": ["ap-southeast-2", "us-east-1"],
  "services": ["EC2", "RDS", "S3", "Lambda"],
  "include_costs": true,
  "webhook_url": "http://your-webhook.com/aws-complete"
}
```

**Response:**
```json
{
  "job_id": "aws-job-789",
  "status": "started",
  "account_id": "123456789012",
  "estimated_duration": 240,
  "webhook_url": "http://your-webhook.com/aws-complete"
}
```

### GET /api/v1/aws/account-info
Get AWS account information.

**Response:**
```json
{
  "account_id": "123456789012",
  "alias": "production-account",
  "regions": ["ap-southeast-2", "us-east-1", "eu-west-1"],
  "services_enabled": ["EC2", "RDS", "S3", "Lambda", "ECS"]
}
```

## 🔵 GCP Operations

### POST /api/v1/gcp/extract
Extract resources from GCP project.

**Request:**
```json
{
  "project_id": "my-gcp-project",
  "regions": ["australia-southeast1", "us-central1"],
  "services": ["compute", "storage", "sql", "functions"],
  "include_costs": true,
  "webhook_url": "http://your-webhook.com/gcp-complete"
}
```

**Response:**
```json
{
  "job_id": "gcp-job-321",
  "status": "started",
  "project_id": "my-gcp-project",
  "estimated_duration": 180,
  "webhook_url": "http://your-webhook.com/gcp-complete"
}
```

### GET /api/v1/gcp/project-info
Get GCP project information.

**Response:**
```json
{
  "project_id": "my-gcp-project",
  "project_name": "Production Project",
  "project_number": "123456789012",
  "regions": ["australia-southeast1", "us-central1"],
  "enabled_apis": ["compute.googleapis.com", "storage.googleapis.com"]
}
```

## 🎨 Visualization

### POST /api/v1/visualization/generate
Generate infrastructure visualization diagram.

**Request:**
```json
{
  "providers": ["azure", "aws", "gcp"],
  "format": "mermaid",
  "layout": "hierarchical",
  "include_costs": true,
  "include_dependencies": true,
  "theme": "professional",
  "filters": {
    "regions": ["australiaeast", "ap-southeast-2"],
    "resource_types": ["VirtualMachine", "EC2Instance"],
    "tags": {"environment": "production"}
  }
}
```

**Response:**
```json
{
  "diagram_id": "diagram-abc123",
  "format": "mermaid",
  "layout": "hierarchical",
  "generated_at": "2025-01-20T10:30:00Z",
  "resource_count": 45,
  "diagram_code": "flowchart TD\n  subgraph azure[\"Azure\"]\n    vm1[\"web-server-01\"]\n  end",
  "export_urls": {
    "mermaid": "/api/v1/visualization/export/diagram-abc123?format=mermaid",
    "png": "/api/v1/visualization/export/diagram-abc123?format=png",
    "svg": "/api/v1/visualization/export/diagram-abc123?format=svg"
  }
}
```

### GET /api/v1/visualization/export/{diagram_id}
Export diagram in various formats.

**Query Parameters:**
- `format` (string): Export format (mermaid, png, svg, pdf)
- `theme` (string): Diagram theme (professional, dark, light)
- `width` (int): Image width for PNG/SVG export
- `height` (int): Image height for PNG/SVG export

**Response:**
Returns the diagram in the requested format.

### GET /api/v1/visualization/diagrams
List all generated diagrams.

**Response:**
```json
{
  "total": 10,
  "diagrams": [
    {
      "diagram_id": "diagram-abc123",
      "name": "Production Infrastructure",
      "format": "mermaid",
      "layout": "hierarchical",
      "resource_count": 45,
      "generated_at": "2025-01-20T10:30:00Z",
      "export_formats": ["mermaid", "png", "svg"]
    }
  ]
}
```

## 🔧 Administration

### POST /api/v1/admin/cache/clear
Clear system cache.

**Response:**
```json
{
  "status": "success",
  "message": "Cache cleared successfully",
  "cleared_entries": 150
}
```

### GET /api/v1/admin/jobs
List background jobs.

**Response:**
```json
{
  "total": 5,
  "jobs": [
    {
      "job_id": "azure-job-456",
      "type": "azure_extract",
      "status": "completed",
      "progress": 100,
      "started_at": "2025-01-20T10:00:00Z",
      "completed_at": "2025-01-20T10:05:00Z",
      "result": {
        "resources_discovered": 25,
        "diagram_generated": true
      }
    }
  ]
}
```

### GET /api/v1/admin/stats
System statistics and metrics.

**Response:**
```json
{
  "resources": {
    "total": 250,
    "by_provider": {
      "azure": 100,
      "aws": 90,
      "gcp": 60
    }
  },
  "diagrams": {
    "total": 15,
    "generated_today": 3
  },
  "cache": {
    "hit_rate": 0.85,
    "size": 1024
  }
}
```

## 📋 Job Management

### GET /api/v1/jobs/{job_id}
Get job status and details.

**Response:**
```json
{
  "job_id": "azure-job-456",
  "type": "azure_extract",
  "status": "running",
  "progress": 65,
  "started_at": "2025-01-20T10:00:00Z",
  "estimated_completion": "2025-01-20T10:05:00Z",
  "details": {
    "subscription_id": "12345678-1234-1234-1234-123456789012",
    "resources_discovered": 16,
    "current_operation": "Scanning SQL databases"
  }
}
```

### DELETE /api/v1/jobs/{job_id}
Cancel a running job.

**Response:**
```json
{
  "status": "cancelled",
  "job_id": "azure-job-456",
  "message": "Job cancelled successfully"
}
```

## 🚫 Error Responses

All API endpoints return consistent error responses:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested resource was not found",
    "details": {
      "resource_id": "invalid-id",
      "timestamp": "2025-01-20T10:30:00Z"
    }
  }
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| `AUTHENTICATION_REQUIRED` | Authentication credentials missing |
| `INVALID_CREDENTIALS` | Invalid authentication credentials |
| `AUTHORIZATION_FAILED` | Insufficient permissions |
| `RESOURCE_NOT_FOUND` | Requested resource not found |
| `VALIDATION_ERROR` | Request validation failed |
| `RATE_LIMIT_EXCEEDED` | API rate limit exceeded |
| `INTERNAL_ERROR` | Internal server error |
| `CLOUD_PROVIDER_ERROR` | Cloud provider API error |

## 📊 Rate Limiting

CloudViz implements rate limiting to ensure fair usage:

- **Default limit**: 100 requests per minute per API key
- **Burst limit**: 200 requests per minute
- **Headers returned**:
  - `X-RateLimit-Limit`: Request limit per window
  - `X-RateLimit-Remaining`: Requests remaining in current window
  - `X-RateLimit-Reset`: Time when the rate limit resets

## 🔄 Webhooks

CloudViz can send webhook notifications when jobs complete:

### Webhook Payload
```json
{
  "job_id": "azure-job-456",
  "type": "azure_extract",
  "status": "completed",
  "completed_at": "2025-01-20T10:05:00Z",
  "result": {
    "resources_discovered": 25,
    "diagram_id": "diagram-abc123",
    "diagram_url": "http://localhost:8000/api/v1/visualization/export/diagram-abc123"
  }
}
```

## 🔗 SDKs and Client Libraries

Official CloudViz SDKs are available for:

- **Python**: `pip install cloudviz-sdk`
- **JavaScript/Node.js**: `npm install cloudviz-sdk`
- **Go**: `go get github.com/navidrast/cloudviz-go`

### Python SDK Example
```python
from cloudviz import CloudVizClient

client = CloudVizClient(api_key="your-api-key")

# Extract Azure resources
job = client.azure.extract(
    subscription_id="12345678-1234-1234-1234-123456789012",
    resource_groups=["production"]
)

# Generate diagram
diagram = client.visualization.generate(
    providers=["azure"],
    format="mermaid"
)
```

## 📚 Additional Resources

- [Authentication Guide](authentication.md) - Detailed authentication setup
- [Rate Limiting](rate-limiting.md) - Rate limiting configuration
- [Error Handling](error-handling.md) - Error handling best practices

---

For interactive API documentation, visit: `http://localhost:8000/docs`