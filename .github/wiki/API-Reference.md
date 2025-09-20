# 🔌 API Reference

Complete documentation for CloudViz REST API endpoints. All endpoints return JSON responses and support standard HTTP status codes.

## 🔐 **Authentication**

CloudViz uses JWT (JSON Web Token) authentication. Include the token in the `Authorization` header:

```bash
Authorization: Bearer <your-jwt-token>
```

### **Authentication Endpoints**

#### **POST /auth/login**
Authenticate user and receive JWT token.

**Request:**
```json
{
  "username": "admin",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### **POST /auth/logout**
Invalidate current JWT token.

#### **GET /auth/me**
Get current user information.

**Response:**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@company.com",
  "roles": ["admin"],
  "last_login": "2025-09-20T10:00:00Z"
}
```

---

## ☁️ **Cloud Provider Discovery**

### **Azure Endpoints**

#### **POST /azure/discover**
Discover Azure resources in subscription.

**Request:**
```json
{
  "subscription_id": "12345678-1234-1234-1234-123456789012",
  "resource_groups": ["production", "staging"],
  "regions": ["eastus", "westus2"],
  "resource_types": ["Microsoft.Compute/virtualMachines", "Microsoft.Storage/storageAccounts"]
}
```

**Response:**
```json
{
  "discovery_id": "disc_azure_001",
  "status": "completed",
  "resources_found": 156,
  "regions": ["East US", "West US 2"],
  "cost_estimate": "$12,450/month",
  "resources": [
    {
      "id": "/subscriptions/.../resourceGroups/prod/providers/Microsoft.Compute/virtualMachines/web-vm-01",
      "name": "web-vm-01",
      "type": "Microsoft.Compute/virtualMachines",
      "location": "eastus",
      "properties": {
        "size": "Standard_D4s_v3",
        "status": "Running"
      }
    }
  ]
}
```

#### **GET /azure/resources**
List discovered Azure resources.

#### **GET /azure/cost-analysis**
Get Azure cost breakdown by resource group.

#### **POST /azure/vm-scale-sets/discover**
Specific discovery for VM Scale Sets.

#### **GET /azure/sql-databases**
List Azure SQL databases.

### **AWS Endpoints**

#### **POST /aws/discover**
Discover AWS resources in account.

**Request:**
```json
{
  "regions": ["us-west-2", "us-east-1"],
  "services": ["ec2", "rds", "lambda", "ecs"],
  "include_stopped": false
}
```

**Response:**
```json
{
  "discovery_id": "disc_aws_001",
  "status": "completed",
  "resources_found": 89,
  "regions": ["us-west-2", "us-east-1"],
  "cost_estimate": "$18,234/month",
  "resources": [
    {
      "id": "i-0123456789abcdef0",
      "name": "web-server-01",
      "type": "EC2Instance",
      "region": "us-west-2",
      "properties": {
        "instance_type": "t3.large",
        "state": "running"
      }
    }
  ]
}
```

#### **GET /aws/ec2/instances**
List EC2 instances.

#### **GET /aws/rds/clusters**
List RDS Aurora clusters.

#### **GET /aws/lambda/functions**
List Lambda functions.

#### **POST /aws/cloudformation/discover**
Discover CloudFormation stacks.

### **GCP Endpoints**

#### **POST /gcp/discover**
Discover Google Cloud Platform resources.

**Request:**
```json
{
  "project_id": "my-project-12345",
  "regions": ["us-central1", "us-west1"],
  "services": ["compute", "gke", "bigquery"]
}
```

**Response:**
```json
{
  "discovery_id": "disc_gcp_001",
  "status": "completed",
  "resources_found": 67,
  "regions": ["us-central1", "us-west1"],
  "cost_estimate": "$16,225/month",
  "resources": [
    {
      "id": "projects/my-project/zones/us-central1-a/instances/web-vm-1",
      "name": "web-vm-1",
      "type": "ComputeInstance",
      "zone": "us-central1-a",
      "properties": {
        "machine_type": "n1-standard-4",
        "status": "RUNNING"
      }
    }
  ]
}
```

#### **GET /gcp/gke/clusters**
List GKE clusters.

#### **GET /gcp/bigquery/datasets**
List BigQuery datasets.

#### **GET /gcp/vertex-ai/models**
List Vertex AI models.

---

## 🎨 **Visualization Endpoints**

### **Diagram Generation**

#### **POST /visualization/generate**
Generate Mermaid diagram from discovered resources.

**Request:**
```json
{
  "discovery_ids": ["disc_azure_001", "disc_aws_001"],
  "layout": "hierarchical",
  "theme": "enterprise",
  "include_costs": true,
  "include_dependencies": true,
  "max_nodes": 100
}
```

**Response:**
```json
{
  "diagram_id": "diag_001",
  "mermaid_code": "flowchart TD\n  subgraph Production\n    VM1[Web Server]\n    DB1[(Database)]\n  end",
  "metadata": {
    "nodes": 45,
    "connections": 67,
    "cost_total": "$46,909/month"
  }
}
```

#### **GET /visualization/diagrams/{diagram_id}**
Retrieve generated diagram.

#### **POST /visualization/export**
Export diagram to various formats.

**Request:**
```json
{
  "diagram_id": "diag_001",
  "format": "png",
  "width": 1920,
  "height": 1080,
  "quality": "high"
}
```

### **Themes & Layouts**

#### **GET /visualization/themes**
List available themes.

**Response:**
```json
{
  "themes": [
    {
      "name": "enterprise",
      "description": "Professional enterprise theme",
      "colors": {
        "primary": "#2E86AB",
        "secondary": "#A23B72",
        "success": "#F18F01",
        "warning": "#C73E1D"
      }
    }
  ]
}
```

#### **GET /visualization/layouts**
List available diagram layouts.

---

## 🔍 **Resource Management**

### **Resource Operations**

#### **GET /resources**
List all discovered resources across providers.

**Query Parameters:**
- `provider`: azure, aws, gcp
- `type`: resource type filter
- `region`: region filter
- `status`: running, stopped, etc.
- `page`: pagination
- `limit`: results per page

#### **GET /resources/{resource_id}**
Get detailed resource information.

#### **POST /resources/search**
Advanced resource search.

**Request:**
```json
{
  "query": "web server",
  "filters": {
    "provider": "azure",
    "type": "VirtualMachine",
    "status": "running"
  },
  "sort": "cost_desc"
}
```

### **Cost Analysis**

#### **GET /costs/summary**
Get cost summary across all providers.

**Response:**
```json
{
  "total_monthly": "$46,909",
  "by_provider": {
    "azure": "$19,234",
    "aws": "$18,675",
    "gcp": "$9,000"
  },
  "by_region": {
    "East US": "$15,234",
    "West US 2": "$12,675"
  }
}
```

#### **POST /costs/forecast**
Generate cost forecasting.

---

## 🤖 **Automation & Integration**

### **Webhook Endpoints**

#### **POST /webhooks/register**
Register webhook for events.

**Request:**
```json
{
  "url": "https://your-app.com/cloudviz-webhook",
  "events": ["discovery.completed", "cost.threshold"],
  "secret": "webhook_secret_key"
}
```

#### **GET /webhooks**
List registered webhooks.

### **Background Jobs**

#### **POST /jobs/schedule**
Schedule background discovery job.

**Request:**
```json
{
  "job_type": "discovery",
  "provider": "azure",
  "schedule": "0 6 * * *",
  "parameters": {
    "subscription_id": "12345",
    "regions": ["eastus"]
  }
}
```

#### **GET /jobs/{job_id}**
Get job status and results.

---

## 👥 **User Management**

### **User Operations**

#### **GET /users**
List users (admin only).

#### **POST /users**
Create new user (admin only).

**Request:**
```json
{
  "username": "newuser",
  "email": "user@company.com",
  "password": "secure_password",
  "roles": ["viewer"]
}
```

#### **PUT /users/{user_id}**
Update user (admin only).

#### **DELETE /users/{user_id}**
Delete user (admin only).

### **Role Management**

#### **GET /roles**
List available roles.

**Response:**
```json
{
  "roles": [
    {
      "name": "admin",
      "permissions": ["read", "write", "delete", "manage_users"]
    },
    {
      "name": "operator",
      "permissions": ["read", "write"]
    },
    {
      "name": "viewer",
      "permissions": ["read"]
    }
  ]
}
```

---

## 🔧 **System Management**

### **Health & Status**

#### **GET /health**
System health check.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.1.0",
  "timestamp": "2025-09-20T10:00:00Z",
  "components": {
    "database": "healthy",
    "redis": "healthy",
    "azure_api": "healthy",
    "aws_api": "healthy",
    "gcp_api": "healthy"
  }
}
```

#### **GET /metrics**
System metrics (Prometheus format).

### **Configuration**

#### **GET /config**
Get current configuration.

#### **PUT /config**
Update configuration (admin only).

---

## 📊 **Response Codes**

| Code | Description |
|------|-------------|
| `200` | Success |
| `201` | Created successfully |
| `400` | Bad request - invalid parameters |
| `401` | Unauthorized - invalid or missing token |
| `403` | Forbidden - insufficient permissions |
| `404` | Resource not found |
| `429` | Too many requests - rate limited |
| `500` | Internal server error |
| `503` | Service unavailable |

## 🔒 **Rate Limits**

| Endpoint Type | Limit | Window |
|---------------|-------|--------|
| Authentication | 10 requests | 1 minute |
| Discovery | 100 requests | 1 hour |
| Visualization | 200 requests | 1 hour |
| General API | 1000 requests | 1 hour |

## 📚 **SDKs & Examples**

### **Python SDK**
```python
from cloudviz_sdk import CloudVizClient

client = CloudVizClient(
    base_url="https://your-cloudviz.com",
    token="your-jwt-token"
)

# Discover Azure resources
discovery = client.azure.discover(
    subscription_id="12345",
    regions=["eastus"]
)

# Generate diagram
diagram = client.visualization.generate(
    discovery_ids=[discovery.id],
    layout="hierarchical"
)
```

### **cURL Examples**
```bash
# Authenticate
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}' | \
  jq -r '.access_token')

# Discover resources
curl -X POST http://localhost:8000/azure/discover \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"subscription_id":"12345","regions":["eastus"]}'

# Generate diagram
curl -X POST http://localhost:8000/visualization/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"discovery_ids":["disc_001"],"layout":"hierarchical"}'
```

### **JavaScript/Node.js**
```javascript
const axios = require('axios');

const client = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});

// Discover AWS resources
const discovery = await client.post('/aws/discover', {
  regions: ['us-west-2'],
  services: ['ec2', 'rds']
});

// Generate visualization
const diagram = await client.post('/visualization/generate', {
  discovery_ids: [discovery.data.discovery_id],
  theme: 'enterprise'
});
```

---

**Need more details?** Check out our [Integration Examples](Integration-Examples) or explore the interactive API documentation at `/docs` when CloudViz is running! 🚀
