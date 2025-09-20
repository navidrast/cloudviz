# API Documentation

CloudViz provides a comprehensive REST API for cloud resource discovery, visualization generation, and system management. The API is built with FastAPI and provides interactive documentation, automatic validation, and OpenAPI specification.

## 📖 Interactive Documentation

When CloudViz is running, you can access interactive API documentation at:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## 🔐 Authentication

CloudViz uses JWT (JSON Web Tokens) for API authentication.

### Getting an Access Token

```bash
# Login and get JWT token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "your-username",
       "password": "your-password"
     }'

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Using the Token

Include the token in the `Authorization` header:

```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
     "http://localhost:8000/api/v1/azure/resources"
```

## 🏥 Health & System Endpoints

### Health Check
Check if the API is running and responsive.

**GET** `/health`

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

### System Status
Get detailed system information and component health.

**GET** `/api/v1/system/status`

```bash
curl -H "Authorization: Bearer your-token" \
     http://localhost:8000/api/v1/system/status
```

**Response:**
```json
{
  "api": {
    "status": "healthy",
    "version": "1.0.0",
    "uptime": 3600
  },
  "database": {
    "status": "connected",
    "pool_size": 10
  },
  "cache": {
    "status": "connected",
    "redis_version": "7.0.0"
  },
  "cloud_providers": {
    "azure": "configured",
    "aws": "not_configured",
    "gcp": "not_configured"
  }
}
```

### Metrics
Get API usage metrics and performance data.

**GET** `/api/v1/system/metrics`

```bash
curl -H "Authorization: Bearer your-token" \
     http://localhost:8000/api/v1/system/metrics
```

## 🔷 Azure Endpoints

### List Resource Groups

**GET** `/api/v1/azure/resource-groups`

```bash
curl -H "Authorization: Bearer your-token" \
     "http://localhost:8000/api/v1/azure/resource-groups"
```

**Query Parameters:**
- `subscription_id` (optional): Specific subscription ID
- `location` (optional): Filter by location/region

**Response:**
```json
[
  {
    "name": "production-rg",
    "location": "australiaeast",
    "subscription_id": "12345678-1234-1234-1234-123456789012",
    "tags": {
      "environment": "production",
      "owner": "platform-team"
    },
    "properties": {
      "provisioning_state": "Succeeded"
    }
  }
]
```

### Get Resource Group Details

**GET** `/api/v1/azure/resource-groups/{resource_group_name}`

```bash
curl -H "Authorization: Bearer your-token" \
     "http://localhost:8000/api/v1/azure/resource-groups/production-rg"
```

### Discover Resources

**GET** `/api/v1/azure/resources`

Discover all resources in your Azure subscription with optional filtering.

```bash
curl -H "Authorization: Bearer your-token" \
     "http://localhost:8000/api/v1/azure/resources?resource_group=production&regions=australiaeast"
```

**Query Parameters:**
- `subscription_id` (optional): Specific subscription
- `resource_group` (optional): Filter by resource group
- `regions` (optional): Comma-separated list of regions
- `resource_types` (optional): Filter by resource types
- `tags` (optional): Filter by tags (format: key=value)
- `include_dependencies` (optional): Include resource dependencies

**Response:**
```json
{
  "resources": [
    {
      "id": "/subscriptions/.../resourceGroups/prod/providers/Microsoft.Compute/virtualMachines/web-vm-01",
      "name": "web-vm-01",
      "type": "Microsoft.Compute/virtualMachines",
      "location": "australiaeast",
      "resource_group": "production-rg",
      "subscription_id": "12345678-1234-1234-1234-123456789012",
      "tags": {
        "environment": "production",
        "tier": "web"
      },
      "properties": {
        "vm_size": "Standard_D2s_v3",
        "os_type": "Linux",
        "power_state": "running"
      },
      "dependencies": [
        {
          "id": "/subscriptions/.../resourceGroups/prod/providers/Microsoft.Network/networkInterfaces/web-vm-01-nic",
          "type": "network_interface"
        }
      ],
      "cost": {
        "monthly_estimate": 156.80,
        "currency": "USD"
      }
    }
  ],
  "metadata": {
    "total_resources": 1,
    "discovery_time": "2024-01-15T10:30:00Z",
    "regions": ["australiaeast"],
    "resource_types": ["Microsoft.Compute/virtualMachines"]
  }
}
```

### Get Specific Resource

**GET** `/api/v1/azure/resources/{resource_id}`

```bash
curl -H "Authorization: Bearer your-token" \
     "http://localhost:8000/api/v1/azure/resources/web-vm-01?resource_group=production"
```

### Network Topology

**GET** `/api/v1/azure/network-topology`

Get network topology including VNets, subnets, and connectivity.

```bash
curl -H "Authorization: Bearer your-token" \
     "http://localhost:8000/api/v1/azure/network-topology?resource_group=production"
```

## 🎨 Visualization Endpoints

### Generate Mermaid Diagram

**POST** `/api/v1/diagrams/mermaid`

Generate a Mermaid diagram from resource data.

```bash
curl -X POST "http://localhost:8000/api/v1/diagrams/mermaid" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer your-token" \
     -d '{
       "resources": [...],
       "theme": "enterprise",
       "layout": "hierarchical",
       "include_costs": true,
       "include_dependencies": true
     }'
```

**Request Body:**
```json
{
  "resources": [...],  // Resource data from discovery endpoints
  "theme": "enterprise",  // Optional: enterprise, security, minimal
  "layout": "hierarchical",  // Optional: hierarchical, flat, network
  "include_costs": true,  // Optional: include cost information
  "include_dependencies": true,  // Optional: show dependencies
  "filters": {
    "resource_types": ["Microsoft.Compute/virtualMachines"],
    "regions": ["australiaeast"]
  }
}
```

**Response:**
```json
{
  "diagram": "flowchart TD\n    AZURE[Azure Cloud] --> RG[production-rg]\n    RG --> VM[web-vm-01]",
  "format": "mermaid",
  "theme": "enterprise",
  "metadata": {
    "node_count": 3,
    "edge_count": 2,
    "generation_time": "2024-01-15T10:30:00Z"
  }
}
```

### Generate PNG Diagram

**POST** `/api/v1/diagrams/mermaid/png`

Generate a PNG image from Mermaid diagram.

```bash
curl -X POST "http://localhost:8000/api/v1/diagrams/mermaid/png" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer your-token" \
     -d '{...}' \
     --output diagram.png
```

### Generate SVG Diagram

**POST** `/api/v1/diagrams/mermaid/svg`

Generate an SVG image from Mermaid diagram.

### List Available Themes

**GET** `/api/v1/diagrams/themes`

Get all available visualization themes.

```bash
curl http://localhost:8000/api/v1/diagrams/themes
```

**Response:**
```json
[
  {
    "name": "enterprise",
    "description": "Professional enterprise theme with corporate colors",
    "colors": {
      "compute": "#9b59b6",
      "network": "#3498db",
      "storage": "#e67e22",
      "security": "#e74c3c"
    }
  },
  {
    "name": "security",
    "description": "Security-focused theme highlighting security components",
    "colors": {
      "secure": "#27ae60",
      "warning": "#f39c12",
      "critical": "#e74c3c"
    }
  }
]
```

## 🔧 Configuration Endpoints

### Get Current Configuration

**GET** `/api/v1/config`

```bash
curl -H "Authorization: Bearer your-token" \
     http://localhost:8000/api/v1/config
```

### Update Configuration

**PUT** `/api/v1/config`

```bash
curl -X PUT "http://localhost:8000/api/v1/config" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer your-token" \
     -d '{
       "cloud_providers": {
         "azure": {
           "enabled": true,
           "regions": ["australiaeast", "australiasoutheast"]
         }
       },
       "visualization": {
         "default_theme": "enterprise",
         "include_costs": true
       }
     }'
```

## 📊 Analytics Endpoints

### Resource Statistics

**GET** `/api/v1/analytics/resource-stats`

Get statistics about discovered resources.

```bash
curl -H "Authorization: Bearer your-token" \
     "http://localhost:8000/api/v1/analytics/resource-stats?timeframe=30d"
```

**Response:**
```json
{
  "total_resources": 245,
  "by_type": {
    "Microsoft.Compute/virtualMachines": 45,
    "Microsoft.Storage/storageAccounts": 12,
    "Microsoft.Network/virtualNetworks": 8
  },
  "by_region": {
    "australiaeast": 180,
    "australiasoutheast": 65
  },
  "by_resource_group": {
    "production": 150,
    "staging": 60,
    "development": 35
  },
  "cost_summary": {
    "total_monthly": 15640.50,
    "currency": "USD"
  }
}
```

### Cost Analysis

**GET** `/api/v1/analytics/costs`

Get detailed cost analysis and trends.

### Security Analysis

**GET** `/api/v1/analytics/security`

Analyze security posture and compliance.

## 🚀 Background Jobs

### Job Status

**GET** `/api/v1/jobs/{job_id}`

Check the status of a background job.

### List Jobs

**GET** `/api/v1/jobs`

List all background jobs with their status.

### Start Discovery Job

**POST** `/api/v1/jobs/discovery`

Start a background resource discovery job.

```bash
curl -X POST "http://localhost:8000/api/v1/jobs/discovery" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer your-token" \
     -d '{
       "provider": "azure",
       "subscription_id": "12345678-1234-1234-1234-123456789012",
       "regions": ["australiaeast"],
       "notify_webhook": "https://your-webhook.com/cloudviz-complete"
     }'
```

## 🔌 Webhook Integration

### Register Webhook

**POST** `/api/v1/webhooks`

Register a webhook for notifications.

### List Webhooks

**GET** `/api/v1/webhooks`

List all registered webhooks.

### Webhook Events

CloudViz sends webhook notifications for:
- **discovery.completed**: Resource discovery finished
- **diagram.generated**: Diagram generation completed
- **error.occurred**: Error during processing
- **cost.threshold**: Cost threshold exceeded

**Webhook Payload Example:**
```json
{
  "event": "discovery.completed",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "job_id": "job-12345",
    "provider": "azure",
    "resource_count": 245,
    "duration": 45.2,
    "subscription_id": "12345678-1234-1234-1234-123456789012"
  }
}
```

## 📝 Error Handling

### HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully  
- **400 Bad Request**: Invalid request parameters
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation error
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error
- **503 Service Unavailable**: Service temporarily unavailable

### Error Response Format

```json
{
  "error": {
    "code": "INVALID_RESOURCE_GROUP",
    "message": "Resource group 'invalid-rg' not found",
    "details": {
      "subscription_id": "12345678-1234-1234-1234-123456789012",
      "available_resource_groups": ["production", "staging"]
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req-12345"
  }
}
```

## 🚦 Rate Limiting

CloudViz implements rate limiting to ensure fair usage:

- **Discovery Endpoints**: 10 requests per minute
- **Diagram Generation**: 20 requests per minute  
- **General API**: 100 requests per minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642252200
```

## 📚 SDK and Client Libraries

### Python SDK

```python
from cloudviz_sdk import CloudVizClient

client = CloudVizClient(
    base_url="http://localhost:8000",
    token="your-jwt-token"
)

# Discover Azure resources
resources = client.azure.discover_resources(
    resource_group="production",
    regions=["australiaeast"]
)

# Generate diagram
diagram = client.diagrams.generate_mermaid(
    resources=resources,
    theme="enterprise"
)
```

### JavaScript/Node.js SDK

```javascript
const { CloudVizClient } = require('cloudviz-sdk');

const client = new CloudVizClient({
  baseUrl: 'http://localhost:8000',
  token: 'your-jwt-token'
});

// Discover resources
const resources = await client.azure.discoverResources({
  resourceGroup: 'production',
  regions: ['australiaeast']
});

// Generate diagram
const diagram = await client.diagrams.generateMermaid({
  resources,
  theme: 'enterprise'
});
```

## 🧪 Testing the API

### Using curl

```bash
# Set base URL and token
BASE_URL="http://localhost:8000"
TOKEN="your-jwt-token"

# Test resource discovery
curl -H "Authorization: Bearer $TOKEN" \
     "$BASE_URL/api/v1/azure/resources?resource_group=production"

# Test diagram generation
curl -X POST "$BASE_URL/api/v1/diagrams/mermaid" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -d @sample-resources.json
```

### Using Python requests

```python
import requests

BASE_URL = "http://localhost:8000"
TOKEN = "your-jwt-token"

headers = {"Authorization": f"Bearer {TOKEN}"}

# Discover resources
response = requests.get(
    f"{BASE_URL}/api/v1/azure/resources",
    headers=headers,
    params={"resource_group": "production"}
)

resources = response.json()

# Generate diagram
diagram_response = requests.post(
    f"{BASE_URL}/api/v1/diagrams/mermaid",
    headers=headers,
    json={
        "resources": resources["resources"],
        "theme": "enterprise"
    }
)

diagram = diagram_response.json()
```

---

For more detailed examples and integration patterns, see our **[Examples](Examples)** page or **[n8n Integration Guide](n8n-Integration)**.