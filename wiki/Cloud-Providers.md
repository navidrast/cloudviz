# Cloud Providers

CloudViz supports multiple cloud providers through a unified interface. This guide covers configuration, authentication, and usage for each supported cloud platform.

## 🌍 Supported Providers

| Provider | Status | Resources | Authentication | Cost Analysis |
|----------|--------|-----------|----------------|---------------|
| **Microsoft Azure** | ✅ Production Ready | 50+ resource types | Service Principal, CLI | ✅ Enabled |
| **Amazon AWS** | 🔄 In Development | 30+ resource types | IAM, Profiles | 🔄 Planned |
| **Google Cloud** | 🔄 Planned | 25+ resource types | Service Account | 🔄 Planned |

## 🔷 Microsoft Azure

Azure is the primary and most mature cloud provider integration in CloudViz.

### Prerequisites

1. **Azure Subscription**: Active Azure subscription with resources
2. **Service Principal**: Application registration with appropriate permissions
3. **Azure CLI** (optional): For easier authentication during development

### Authentication Setup

#### Method 1: Service Principal (Recommended for Production)

1. **Create Service Principal**
   ```bash
   # Create service principal
   az ad sp create-for-rbac --name "cloudviz-sp" --role "Reader" --scopes "/subscriptions/YOUR_SUBSCRIPTION_ID"
   ```

   Output:
   ```json
   {
     "appId": "12345678-1234-1234-1234-123456789012",
     "displayName": "cloudviz-sp", 
     "password": "your-secret-value",
     "tenant": "87654321-4321-4321-4321-210987654321"
   }
   ```

2. **Grant Additional Permissions** (if needed)
   ```bash
   # Network topology reading
   az role assignment create \
     --assignee "12345678-1234-1234-1234-123456789012" \
     --role "Network Contributor" \
     --scope "/subscriptions/YOUR_SUBSCRIPTION_ID"
   
   # Cost management
   az role assignment create \
     --assignee "12345678-1234-1234-1234-123456789012" \
     --role "Cost Management Reader" \
     --scope "/subscriptions/YOUR_SUBSCRIPTION_ID"
   ```

3. **Configure CloudViz**
   ```bash
   export AZURE_CLIENT_ID="12345678-1234-1234-1234-123456789012"
   export AZURE_CLIENT_SECRET="your-secret-value"
   export AZURE_TENANT_ID="87654321-4321-4321-4321-210987654321"
   export AZURE_SUBSCRIPTION_ID="your-subscription-id"
   ```

#### Method 2: Azure CLI Authentication (Development)

```bash
# Login with Azure CLI
az login

# Set default subscription
az account set --subscription "your-subscription-id"

# CloudViz will use CLI credentials automatically
```

#### Method 3: Managed Identity (Azure-hosted)

When running CloudViz on Azure (VM, Container Instance, etc.):

```yaml
# Configuration for managed identity
cloud_providers:
  azure:
    enabled: true
    use_managed_identity: true
    subscription_id: "your-subscription-id"
```

### Configuration Options

#### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `AZURE_CLIENT_ID` | Yes* | Service principal client ID | `12345678-1234-...` |
| `AZURE_CLIENT_SECRET` | Yes* | Service principal secret | `your-secret-value` |
| `AZURE_TENANT_ID` | Yes* | Azure tenant ID | `87654321-4321-...` |
| `AZURE_SUBSCRIPTION_ID` | No | Default subscription ID | `subscription-id` |
| `AZURE_USE_CLI` | No | Use Azure CLI authentication | `true` |
| `AZURE_USE_MANAGED_IDENTITY` | No | Use managed identity | `true` |

*Required unless using CLI or managed identity

#### YAML Configuration

```yaml
# config/azure.yml
cloud_providers:
  azure:
    enabled: true
    
    # Authentication
    client_id: "${AZURE_CLIENT_ID}"
    client_secret: "${AZURE_CLIENT_SECRET}" 
    tenant_id: "${AZURE_TENANT_ID}"
    
    # Scope Configuration
    subscription_ids:
      - "subscription-1"
      - "subscription-2"
    
    # Regional Configuration  
    regions:
      - "australiaeast"
      - "australiasoutheast"
      - "eastus"
      - "westeurope"
    
    # Resource Filtering
    resource_groups:
      - "production"
      - "staging"
      - "development"
    
    # Resource Types to Include
    resource_types:
      - "Microsoft.Compute/virtualMachines"
      - "Microsoft.Network/virtualNetworks"
      - "Microsoft.Storage/storageAccounts"
      - "Microsoft.Sql/servers"
    
    # Discovery Options
    discovery:
      include_dependencies: true
      include_costs: true
      parallel_regions: true
      batch_size: 100
      timeout: 300
    
    # Cost Analysis
    cost_analysis:
      enabled: true
      currency: "USD"
      billing_period: "monthly"
      include_estimates: true
```

### Supported Azure Resources

#### Compute Resources
- **Virtual Machines**: `Microsoft.Compute/virtualMachines`
- **VM Scale Sets**: `Microsoft.Compute/virtualMachineScaleSets`
- **Container Instances**: `Microsoft.ContainerInstance/containerGroups`
- **App Services**: `Microsoft.Web/sites`
- **Function Apps**: `Microsoft.Web/sites` (kind: functionapp)
- **Kubernetes Service**: `Microsoft.ContainerService/managedClusters`

#### Network Resources
- **Virtual Networks**: `Microsoft.Network/virtualNetworks`
- **Subnets**: Virtual network subnets
- **Network Security Groups**: `Microsoft.Network/networkSecurityGroups`
- **Load Balancers**: `Microsoft.Network/loadBalancers`
- **Application Gateways**: `Microsoft.Network/applicationGateways`
- **VPN Gateways**: `Microsoft.Network/virtualNetworkGateways`
- **Express Route**: `Microsoft.Network/expressRouteCircuits`
- **Public IP Addresses**: `Microsoft.Network/publicIPAddresses`
- **Network Interfaces**: `Microsoft.Network/networkInterfaces`

#### Storage Resources
- **Storage Accounts**: `Microsoft.Storage/storageAccounts`
- **Managed Disks**: `Microsoft.Compute/disks`
- **File Shares**: Azure Files
- **Blob Containers**: Blob storage containers

#### Database Resources
- **SQL Servers**: `Microsoft.Sql/servers`
- **SQL Databases**: `Microsoft.Sql/servers/databases`
- **Cosmos DB**: `Microsoft.DocumentDB/databaseAccounts`
- **MySQL**: `Microsoft.DBforMySQL/servers`
- **PostgreSQL**: `Microsoft.DBforPostgreSQL/servers`
- **Redis Cache**: `Microsoft.Cache/Redis`

#### Security Resources
- **Key Vaults**: `Microsoft.KeyVault/vaults`
- **Security Center**: Security policies and recommendations
- **Azure Firewall**: `Microsoft.Network/azureFirewalls`

#### Management Resources
- **Resource Groups**: `Microsoft.Resources/resourceGroups`
- **Subscriptions**: Azure subscriptions
- **Management Groups**: Subscription organization

### Usage Examples

#### Basic Resource Discovery

```bash
# Discover all resources in subscription
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8000/api/v1/azure/resources"

# Discover resources in specific resource group
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8000/api/v1/azure/resources?resource_group=production"

# Discover resources in specific regions
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8000/api/v1/azure/resources?regions=australiaeast,australiasoutheast"
```

#### Filtered Discovery

```bash
# Only virtual machines
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8000/api/v1/azure/resources?resource_types=Microsoft.Compute/virtualMachines"

# Resources with specific tags
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8000/api/v1/azure/resources?tags=environment=production"

# Resources with cost analysis
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8000/api/v1/azure/resources?include_costs=true"
```

#### Network Topology

```bash
# Get network topology
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8000/api/v1/azure/network-topology"

# Network topology for specific resource group
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8000/api/v1/azure/network-topology?resource_group=production"
```

### Azure-Specific Features

#### Resource Dependencies
CloudViz automatically discovers Azure resource dependencies:

```json
{
  "id": "/subscriptions/.../virtualMachines/web-vm-01",
  "name": "web-vm-01",
  "type": "Microsoft.Compute/virtualMachines",
  "dependencies": [
    {
      "id": "/subscriptions/.../networkInterfaces/web-vm-01-nic",
      "type": "network_interface",
      "relationship": "attached"
    },
    {
      "id": "/subscriptions/.../disks/web-vm-01-osdisk", 
      "type": "managed_disk",
      "relationship": "os_disk"
    },
    {
      "id": "/subscriptions/.../networkSecurityGroups/web-nsg",
      "type": "network_security_group", 
      "relationship": "associated"
    }
  ]
}
```

#### Cost Integration
Integrates with Azure Cost Management API:

```json
{
  "resource": {
    "id": "/subscriptions/.../virtualMachines/web-vm-01",
    "cost": {
      "monthly_estimate": 245.60,
      "currency": "USD",
      "breakdown": {
        "compute": 180.40,
        "storage": 45.20,
        "network": 20.00
      },
      "trend": "increasing",
      "last_updated": "2024-01-15T10:30:00Z"
    }
  }
}
```

#### Security Analysis
Analyzes Azure security configurations:

```json
{
  "security_analysis": {
    "network_security_groups": {
      "total": 5,
      "issues": [
        {
          "severity": "high",
          "resource": "web-nsg",
          "issue": "Allows inbound traffic from 0.0.0.0/0 on port 22"
        }
      ]
    },
    "public_ips": {
      "count": 3,
      "exposed_services": ["SSH", "RDP", "HTTP"]
    }
  }
}
```

## 🟠 Amazon AWS (In Development)

AWS integration is currently in development. The following features are planned:

### Planned Authentication Methods
- **IAM User**: Access key and secret key
- **IAM Roles**: Cross-account access
- **AWS CLI Profiles**: Development authentication
- **Instance Profiles**: EC2-based authentication

### Planned Resource Types
- **EC2**: Instances, security groups, key pairs
- **VPC**: Virtual private clouds, subnets, route tables
- **RDS**: Database instances and clusters
- **S3**: Buckets and objects
- **Load Balancing**: ALB, NLB, CLB
- **Lambda**: Serverless functions
- **IAM**: Users, roles, policies

### Configuration Preview

```yaml
# Planned AWS configuration
cloud_providers:
  aws:
    enabled: true
    
    # Authentication
    access_key_id: "${AWS_ACCESS_KEY_ID}"
    secret_access_key: "${AWS_SECRET_ACCESS_KEY}"
    region: "ap-southeast-2"
    
    # Multi-account support
    accounts:
      - account_id: "123456789012"
        role_arn: "arn:aws:iam::123456789012:role/CloudVizRole"
        regions: ["ap-southeast-2", "us-east-1"]
    
    # Resource filtering
    resource_types:
      - "AWS::EC2::Instance"
      - "AWS::EC2::VPC"
      - "AWS::RDS::DBInstance"
    
    discovery:
      include_costs: true
      parallel_regions: true
```

## 🔵 Google Cloud Platform (Planned)

GCP integration is planned for future releases.

### Planned Authentication Methods
- **Service Account**: JSON key file authentication
- **Application Default Credentials**: gcloud CLI authentication
- **Workload Identity**: GKE-based authentication

### Planned Resource Types
- **Compute Engine**: Instances, instance groups
- **VPC**: Networks, subnets, firewall rules
- **Cloud SQL**: Database instances
- **Cloud Storage**: Buckets and objects
- **Cloud Load Balancing**: HTTP(S), TCP, UDP load balancers
- **Cloud Functions**: Serverless functions
- **IAM**: Service accounts, roles, policies

### Configuration Preview

```yaml
# Planned GCP configuration
cloud_providers:
  gcp:
    enabled: true
    
    # Authentication
    service_account_path: "/path/to/service-account.json"
    project_id: "my-gcp-project"
    
    # Multi-project support
    projects:
      - project_id: "production-project"
        regions: ["australia-southeast1", "us-central1"]
      - project_id: "staging-project"
        regions: ["australia-southeast1"]
    
    discovery:
      include_costs: true
      include_iam: true
```

## 🔧 Multi-Provider Configuration

Configure multiple cloud providers simultaneously:

```yaml
# Multi-cloud configuration
cloud_providers:
  azure:
    enabled: true
    subscription_ids: ["azure-sub-1"]
    regions: ["australiaeast"]
  
  aws:
    enabled: true
    accounts: ["123456789012"]
    regions: ["ap-southeast-2"]
  
  gcp:
    enabled: true
    projects: ["gcp-project-1"]
    regions: ["australia-southeast1"]

# Unified visualization
visualization:
  multi_cloud:
    enabled: true
    group_by_provider: true
    show_inter_cloud_connections: false
    theme: "multi_cloud"
```

## 🔍 Discovery Strategies

### Parallel Discovery
Discover resources from multiple providers simultaneously:

```python
# API call for multi-cloud discovery
curl -X POST "http://localhost:8000/api/v1/discovery/multi-cloud" \
     -H "Content-Type: application/json" \
     -d '{
       "providers": ["azure", "aws"],
       "regions": {
         "azure": ["australiaeast"],
         "aws": ["ap-southeast-2"]
       },
       "resource_types": {
         "azure": ["Microsoft.Compute/virtualMachines"],
         "aws": ["AWS::EC2::Instance"]
       }
     }'
```

### Incremental Discovery
Update only changed resources:

```bash
# Incremental discovery with change detection
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8000/api/v1/azure/resources?since=2024-01-15T00:00:00Z&detect_changes=true"
```

### Filtered Discovery
Apply complex filters across providers:

```json
{
  "filters": {
    "tags": {
      "environment": "production",
      "owner": "platform-team"
    },
    "regions": ["australiaeast", "ap-southeast-2"],
    "cost_threshold": {
      "min": 100,
      "max": 10000,
      "currency": "USD"
    },
    "resource_types": [
      "compute",
      "database"
    ]
  }
}
```

## 🚨 Troubleshooting

### Azure Authentication Issues

**Problem**: `AuthenticationError: The provided credentials are invalid`

**Solutions**:
1. Verify service principal credentials:
   ```bash
   az login --service-principal \
     --username $AZURE_CLIENT_ID \
     --password $AZURE_CLIENT_SECRET \
     --tenant $AZURE_TENANT_ID
   ```

2. Check role assignments:
   ```bash
   az role assignment list --assignee $AZURE_CLIENT_ID --all
   ```

3. Test API access directly:
   ```bash
   curl -H "Authorization: Bearer $(az account get-access-token --query accessToken -o tsv)" \
        "https://management.azure.com/subscriptions/$AZURE_SUBSCRIPTION_ID/resources?api-version=2021-04-01"
   ```

### Permission Issues

**Problem**: `403 Forbidden` when accessing certain resources

**Solutions**:
1. Grant appropriate Azure roles:
   ```bash
   # Reader role for basic resource discovery
   az role assignment create \
     --assignee $AZURE_CLIENT_ID \
     --role "Reader" \
     --scope "/subscriptions/$AZURE_SUBSCRIPTION_ID"
   
   # Network Contributor for network topology
   az role assignment create \
     --assignee $AZURE_CLIENT_ID \
     --role "Network Contributor" \
     --scope "/subscriptions/$AZURE_SUBSCRIPTION_ID"
   
   # Cost Management Reader for cost data
   az role assignment create \
     --assignee $AZURE_CLIENT_ID \
     --role "Cost Management Reader" \
     --scope "/subscriptions/$AZURE_SUBSCRIPTION_ID"
   ```

### Rate Limiting

**Problem**: `429 Too Many Requests` from Azure API

**Solutions**:
1. Implement exponential backoff (automatically handled)
2. Reduce batch size in configuration:
   ```yaml
   discovery:
     batch_size: 50  # Reduce from default 100
     parallel_regions: false  # Disable parallel processing
   ```

### Network Connectivity

**Problem**: Cannot reach cloud APIs

**Solutions**:
1. Check firewall rules and proxy settings
2. Verify DNS resolution
3. Test connectivity:
   ```bash
   # Test Azure connectivity
   curl -I https://management.azure.com/
   
   # Test AWS connectivity (when implemented)
   curl -I https://ec2.amazonaws.com/
   ```

---

For more specific configuration examples and troubleshooting, see the **[Configuration](Configuration)** and **[Troubleshooting](Troubleshooting)** guides.