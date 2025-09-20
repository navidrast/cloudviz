import os

readme_content = """# 🌩️ CloudViz - Multi-Cloud Infrastructure Visualization Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Mermaid](https://img.shields.io/badge/Mermaid-Diagrams-ff69b4.svg)](https://mermaid.js.org/)

**CloudViz** is an enterprise-grade, multi-cloud infrastructure visualization platform that automatically discovers cloud resources and generates beautiful, interactive diagrams. Built with FastAPI and featuring powerful Mermaid diagram generation, CloudViz provides REST APIs perfect for automation workflows, especially **n8n integration**.

## 🎨 **Live Infrastructure Visualization Demo**

CloudViz automatically generates comprehensive infrastructure diagrams from your cloud resources with hierarchical organization:

### 🏢 **Azure Enterprise Architecture - Hierarchical View**
*Auto-generated from Azure subscription scan - enterprise infrastructure example*

```mermaid
flowchart TD
    INTERNET[🌍 Internet Users]
    
    INTERNET --> CDN_LAYER[🚀 Global CDN Layer]
    
    CDN_LAYER --> AZURE_CLOUD{🔷 Azure Cloud Platform}
    
    AZURE_CLOUD --> AU_EAST[🌏 Australia East - Primary]
    AZURE_CLOUD --> AU_SOUTHEAST[🌏 Australia Southeast - DR]
    
    AU_EAST --> NETWORK_TIER[🌐 Network & Security Tier]
    AU_EAST --> APPLICATION_TIER[💼 Application Services Tier]
    AU_EAST --> DATA_TIER[🗄️ Data & Analytics Tier]
    AU_EAST --> SECURITY_TIER[🔐 Security & Compliance Tier]
    
    NETWORK_TIER --> firewall[🛡️ Azure Firewall Premium - $1456/month]
    NETWORK_TIER --> appgw[🌐 Application Gateway v2 - $378/month]
    NETWORK_TIER --> cdn[🚀 Global Telecom CDN - $198/month]
    NETWORK_TIER --> vnet_hub[🔗 Hub VNet 10.0.0.0/16]
    NETWORK_TIER --> expressroute[⚡ ExpressRoute Gateway - $445/month]
    NETWORK_TIER --> vpn_gateway[🔒 VPN Gateway - $234/month]
    
    APPLICATION_TIER --> vmss_billing[🔄 Billing VMSS 5-15 instances - $1234/month]
    APPLICATION_TIER --> vmss_crm[🔄 CRM VMSS 3-12 instances - $897/month]
    APPLICATION_TIER --> redis_session[⚡ Session Redis Cache 52GB - $1246/month]
    APPLICATION_TIER --> service_fabric[⚙️ OSS Service Fabric 6 nodes - $567/month]
    
    DATA_TIER --> sqlserver[🏛️ Telecom SQL Server Business Critical]
    DATA_TIER --> sqldb_billing[💾 Billing Database 5TB - $3456/month]
    DATA_TIER --> sqldb_customer[💾 Customer Database 2TB - $1789/month]
    DATA_TIER --> cosmos_network[🌐 Network Topology DB Multi-master - $1567/month]
    DATA_TIER --> synapse[📊 Telecom Synapse DW1000c - $2890/month]
    
    SECURITY_TIER --> sentinel[🛡️ Azure Sentinel SIEM - $890/month]
    SECURITY_TIER --> keyvault[🔐 Telecom HSM FIPS 140-2 - $1890/month]
    SECURITY_TIER --> backup_vault[💾 Backup Vault Cross-Region - $567/month]
    
    AU_SOUTHEAST --> DR_TIER[🔄 Disaster Recovery Tier]
    DR_TIER --> asr[🔄 Site Recovery VM Replication - $234/month]
    DR_TIER --> dr_storage[💾 DR Storage 500TB - $1234/month]
    DR_TIER --> dr_sql[💾 SQL Read Replica - $2456/month]
    
    firewall --> appgw
    appgw --> vmss_billing
    appgw --> vmss_crm
    vmss_billing --> redis_session
    vmss_crm --> redis_session
    vmss_billing --> sqldb_billing
    vmss_crm --> sqldb_customer
    service_fabric --> cosmos_network
    sqldb_billing --> synapse
    sqldb_customer --> synapse
    
    sentinel --> firewall
    sentinel --> vmss_billing
    sentinel --> vmss_crm
    keyvault --> service_fabric
    keyvault --> appgw
    
    vnet_hub --> vmss_billing
    vnet_hub --> vmss_crm
    expressroute --> vnet_hub
    vpn_gateway --> vnet_hub
    
    sqldb_billing -.-> dr_sql
    sqldb_customer -.-> dr_sql
    vmss_billing -.-> asr
    vmss_crm -.-> asr
    backup_vault -.-> dr_storage
    
    classDef internetClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef azureClass fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef tierClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef networkClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef appClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef dataClass fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef securityClass fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    classDef drClass fill:#f1f8e9,stroke:#689f38,stroke-width:2px
    
    class INTERNET internetClass
    class AZURE_CLOUD azureClass
    class NETWORK_TIER,APPLICATION_TIER,DATA_TIER,SECURITY_TIER,DR_TIER tierClass
    class firewall,appgw,cdn,vnet_hub,expressroute,vpn_gateway networkClass
    class vmss_billing,vmss_crm,redis_session,service_fabric appClass
    class sqlserver,sqldb_billing,sqldb_customer,cosmos_network,synapse dataClass
    class sentinel,keyvault,backup_vault securityClass
    class asr,dr_storage,dr_sql drClass
```

---

### 🚀 **AWS Infrastructure - Hierarchical Multi-Region Architecture**
*Auto-generated from AWS account scan across multiple regions*

```mermaid
flowchart TD
    GLOBAL_USERS[🌍 Global Users]
    
    GLOBAL_USERS --> GLOBAL_SERVICES{🌐 AWS Global Services}
    
    GLOBAL_SERVICES --> AP_SE_2[🌏 AP-Southeast-2 Sydney]
    GLOBAL_SERVICES --> AP_SE_1[🌏 AP-Southeast-1 Singapore DR]
    GLOBAL_SERVICES --> US_EAST_1[🌏 US-East-1 Global Hub]
    
    US_EAST_1 --> GLOBAL_TIER[🌍 Global Services Tier]
    GLOBAL_TIER --> route53[🌍 Route 53 DNS Health checks - $123/month]
    GLOBAL_TIER --> cloudfront[🚀 CloudFront CDN Global Edge - $567/month]
    GLOBAL_TIER --> acm[🔐 Certificate Manager SSL/TLS - Free]
    GLOBAL_TIER --> iam[🔐 Identity & Access Management - Free]
    
    AP_SE_2 --> COMPUTE_LAYER[💻 Compute Layer]
    AP_SE_2 --> DATA_LAYER[🗄️ Data Layer]
    AP_SE_2 --> NETWORK_LAYER[🌐 Network Layer]
    AP_SE_2 --> SECURITY_LAYER[🔐 Security Layer]
    
    COMPUTE_LAYER --> ec2_monitoring[🔍 Network Monitoring ASG c5.2xlarge x8 - $1456/month]
    COMPUTE_LAYER --> ec2_analytics[📈 Traffic Analytics ASG r5.xlarge x6 - $1234/month]
    COMPUTE_LAYER --> lambda_processors[⚡ Data Processors Lambda Python - $567/month]
    COMPUTE_LAYER --> ecs_cluster[🐳 Microservices ECS Fargate 12 services - $1890/month]
    
    DATA_LAYER --> rds_aurora[🌟 Customer Aurora PostgreSQL Multi-AZ - $2890/month]
    DATA_LAYER --> elasticache[⚡ Session ElastiCache Redis cluster - $756/month]
    DATA_LAYER --> s3_data[📦 Telecom Data Lake S3 45TB - $890/month]
    DATA_LAYER --> opensearch[🔍 Log Analytics OpenSearch cluster - $1245/month]
    
    NETWORK_LAYER --> vpc_main[🔗 Main VPC 10.0.0.0/16]
    NETWORK_LAYER --> alb_public[🌐 Public ALB Internet-facing - $345/month]
    NETWORK_LAYER --> alb_internal[🔗 Internal ALB Private routing - $234/month]
    NETWORK_LAYER --> nat_gateway[🌍 NAT Gateway Multi-AZ - $156/month]
    
    SECURITY_LAYER --> waf[🛡️ WAF Rate Limiting Bot Control - $234/month]
    SECURITY_LAYER --> shield[🛡️ DDoS Protection Shield Advanced - $3000/month]
    SECURITY_LAYER --> cloudwatch[📊 CloudWatch Metrics Logs Alarms - $445/month]
    SECURITY_LAYER --> secrets_manager[🔐 Secrets Manager DB credentials - $67/month]
    
    AP_SE_1 --> DR_SERVICES[🔄 DR Services Tier]
    DR_SERVICES --> rds_replica[🔄 Aurora Read Replica Cross-region - $1445/month]
    DR_SERVICES --> s3_replica[💾 DR Data Backup Cross-region - $445/month]
    DR_SERVICES --> lambda_failover[⚡ Failover Automation DR - $89/month]
    
    route53 --> cloudfront
    cloudfront --> waf
    waf --> alb_public
    alb_public --> ec2_monitoring
    alb_public --> ec2_analytics
    alb_internal --> ecs_cluster
    
    ec2_monitoring --> opensearch
    ec2_analytics --> s3_data
    lambda_processors --> rds_aurora
    lambda_processors --> elasticache
    ecs_cluster --> rds_aurora
    
    nat_gateway --> ec2_monitoring
    nat_gateway --> ec2_analytics
    vpc_main --> ec2_monitoring
    vpc_main --> ec2_analytics
    
    secrets_manager --> rds_aurora
    secrets_manager --> ecs_cluster
    cloudwatch --> ec2_monitoring
    cloudwatch --> rds_aurora
    cloudwatch --> lambda_processors
    shield --> cloudfront
    
    rds_aurora -.-> rds_replica
    s3_data -.-> s3_replica
    cloudwatch -.-> lambda_failover
    
    classDef globalClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef awsClass fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef tierClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef computeClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef dataClass fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef networkClass fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef securityClass fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    classDef drClass fill:#f1f8e9,stroke:#689f38,stroke-width:2px
    
    class GLOBAL_USERS globalClass
    class GLOBAL_SERVICES awsClass
    class COMPUTE_LAYER,DATA_LAYER,NETWORK_LAYER,SECURITY_LAYER,GLOBAL_TIER,DR_SERVICES tierClass
    class ec2_monitoring,ec2_analytics,lambda_processors,ecs_cluster computeClass
    class rds_aurora,elasticache,s3_data,opensearch dataClass
    class vpc_main,alb_public,alb_internal,nat_gateway networkClass
    class waf,shield,cloudwatch,secrets_manager securityClass
    class rds_replica,s3_replica,lambda_failover drClass
```

---

### 🌐 **Google Cloud Platform - Hierarchical Edge Computing Architecture**
*Auto-generated from GCP project scan across multiple regions*

```mermaid
flowchart TD
    GLOBAL_TRAFFIC[🌍 Global Traffic]
    
    GLOBAL_TRAFFIC --> GCP_GLOBAL{🔵 GCP Global Network}
    
    GCP_GLOBAL --> AU_SE_1[🌏 australia-southeast1 Sydney]
    GCP_GLOBAL --> AU_SE_2[🌏 australia-southeast2 Melbourne DR]
    GCP_GLOBAL --> US_CENTRAL[🌏 us-central1 Global Analytics]
    
    GCP_GLOBAL --> GLOBAL_LB[🌐 Global Load Balancer HTTP Distribution - $234/month]
    GCP_GLOBAL --> CDN_GLOBAL[🚀 Cloud CDN Global Edge Cache - $156/month]
    GCP_GLOBAL --> DNS_GLOBAL[🌍 Cloud DNS Managed Zones - $23/month]
    
    AU_SE_1 --> CONTAINER_PLATFORM[🐳 Container Platform]
    AU_SE_1 --> COMPUTE_ANALYTICS[💻 Compute & Analytics]
    AU_SE_1 --> STORAGE_LAYER[📦 Storage Layer]
    AU_SE_1 --> AI_ML_PLATFORM[🤖 AI/ML Platform]
    
    CONTAINER_PLATFORM --> gke_primary[⚙️ Edge Computing GKE Autopilot 25 nodes - $3456/month]
    CONTAINER_PLATFORM --> registry[📦 Artifact Registry Container Images - $189/month]
    CONTAINER_PLATFORM --> cloud_run[⚡ Microservices Platform 12 services - $756/month]
    CONTAINER_PLATFORM --> istio_mesh[🕸️ Service Mesh Istio Traffic - $323/month]
    
    COMPUTE_ANALYTICS --> vm_monitoring[📊 Network Monitoring VMs c2-standard-16 x8 - $2890/month]
    COMPUTE_ANALYTICS --> sql_primary[🗄️ Network Analytics DB PostgreSQL - $4123/month]
    COMPUTE_ANALYTICS --> memorystore[⚡ Real-time Cache Redis 100GB - $567/month]
    COMPUTE_ANALYTICS --> bigtable[⚡ TimeSeries Database Bigtable SSD - $1290/month]
    
    STORAGE_LAYER --> storage_telemetry[📊 Network Telemetry 45TB Regional - $900/month]
    STORAGE_LAYER --> storage_configs[⚙️ Device Configurations 2.1TB - $42/month]
    STORAGE_LAYER --> storage_backup[💾 Disaster Recovery 25TB Coldline - $175/month]
    
    AI_ML_PLATFORM --> vertex_ai[🧠 Network AI Platform Vertex Training - $2890/month]
    AI_ML_PLATFORM --> pubsub_events[📡 Network Events Pub/Sub 5M messages - $345/month]
    AI_ML_PLATFORM --> dataflow[🌊 Stream Analytics Dataflow Beam - $1567/month]
    AI_ML_PLATFORM --> cloud_functions[⚡ Event Processors Python 3.9 - $256/month]
    
    AU_SE_2 --> DR_ANALYTICS[🔄 DR Analytics Tier]
    DR_ANALYTICS --> sql_replica[📋 Analytics Replica Cross-region - $2061/month]
    DR_ANALYTICS --> gke_standby[⚙️ Standby GKE Cluster Minimal DR - $567/month]
    DR_ANALYTICS --> storage_dr[💾 DR Backup Storage Multi-region - $445/month]
    
    US_CENTRAL --> GLOBAL_ANALYTICS[📈 Global Analytics Tier]
    US_CENTRAL --> MONITORING_OPS[📊 Operations Tier]
    
    GLOBAL_ANALYTICS --> bigquery[📈 Telecom Datawarehouse BigQuery 15TB - $300/month]
    GLOBAL_ANALYTICS --> looker[📊 Business Intelligence Looker Studio - $456/month]
    GLOBAL_ANALYTICS --> dataproc[⚙️ Batch Processing Dataproc Spark - $434/month]
    GLOBAL_ANALYTICS --> cloud_armor[🛡️ DDoS Protection Security Policies - $234/month]
    
    MONITORING_OPS --> monitoring[📊 Operations Suite Monitoring Alerting - $289/month]
    MONITORING_OPS --> trace[🔍 Distributed Tracing Request Tracing - $45/month]
    MONITORING_OPS --> scheduler[⏰ Job Scheduler Cron Automation - $12/month]
    MONITORING_OPS --> iam[🔐 Identity Platform Zero-Trust - Free]
    
    pubsub_events --> dataflow
    dataflow --> sql_primary
    dataflow --> bigtable
    dataflow --> storage_telemetry
    cloud_functions --> pubsub_events
    
    gke_primary --> vertex_ai
    gke_primary --> DNS_GLOBAL
    istio_mesh --> cloud_run
    registry --> gke_primary
    registry --> cloud_run
    
    sql_primary --> bigquery
    bigtable --> bigquery
    bigquery --> looker
    bigquery --> dataproc
    vertex_ai --> storage_configs
    
    GLOBAL_LB --> gke_primary
    GLOBAL_LB --> cloud_run
    CDN_GLOBAL --> storage_telemetry
    DNS_GLOBAL --> GLOBAL_LB
    
    cloud_armor --> GLOBAL_LB
    gke_primary --> monitoring
    sql_primary --> trace
    vertex_ai --> monitoring
    cloud_run --> monitoring
    
    sql_primary -.-> sql_replica
    storage_telemetry -.-> storage_dr
    gke_primary -.-> gke_standby
    monitoring -.-> scheduler
    
    vm_monitoring --> sql_primary
    vm_monitoring --> memorystore
    gke_primary --> storage_telemetry
    cloud_run --> storage_configs
    
    classDef globalClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef gcpClass fill:#e8f5e8,stroke:#1976d2,stroke-width:2px
    classDef tierClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef containerClass fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef computeClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef storageClass fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef aimlClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef analyticsClass fill:#f1f8e9,stroke:#689f38,stroke-width:2px
    classDef drClass fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    
    class GLOBAL_TRAFFIC globalClass
    class GCP_GLOBAL gcpClass
    class CONTAINER_PLATFORM,COMPUTE_ANALYTICS,STORAGE_LAYER,AI_ML_PLATFORM,DR_ANALYTICS,GLOBAL_ANALYTICS,MONITORING_OPS tierClass
    class gke_primary,registry,cloud_run,istio_mesh containerClass
    class vm_monitoring,sql_primary,memorystore,bigtable computeClass
    class storage_telemetry,storage_configs,storage_backup storageClass
    class vertex_ai,pubsub_events,dataflow,cloud_functions aimlClass
    class bigquery,looker,dataproc,monitoring,trace,scheduler analyticsClass
    class sql_replica,gke_standby,storage_dr drClass
```

---

## 📊 **Multi-Cloud Infrastructure Summary**

| **Cloud Provider** | **Resources** | **Monthly Cost** | **Key Services** | **Regions** |
|-------------------|---------------|------------------|------------------|-------------|
| **🔷 Azure** | 35 resources | $18,567.80 | VM Scale Sets, SQL Database, Service Fabric, Synapse | 2 regions |
| **🟠 AWS** | 31 resources | $12,450.80 | EC2, RDS Aurora, Lambda, ECS | 3 regions |
| **🔵 GCP** | 28 resources | $15,890.40 | GKE, Vertex AI, BigQuery, Cloud Run | 3 regions |
| **📊 Total** | **94 resources** | **$46,909.00** | **Multi-cloud enterprise platform** | **8 regions** |

---

## 🚀 **Key Features**

- **🔍 Multi-Cloud Discovery**: Comprehensive resource extraction across Azure, AWS, and GCP
- **🎨 Hierarchical Visualizations**: Clear tier-based organization with dependency flows
- **📊 Cost Analytics**: Detailed cost breakdown and optimization recommendations
- **🌐 Network Topology**: Complete dependency mapping and connectivity visualization
- **🔒 Security Analysis**: Security groups, firewall rules, and compliance monitoring
- **⚡ Real-time Updates**: Live infrastructure monitoring and change detection
- **🤖 n8n Integration**: Perfect for automation workflows and CI/CD pipelines

## 🛠️ **n8n Workflow Integration**

CloudViz is designed for seamless integration with n8n automation workflows:

```json
{
  "nodes": [
    {
      "type": "HTTP Request",
      "url": "http://cloudviz-api:8000/api/v1/azure/extract",
      "method": "POST",
      "body": {
        "subscription_id": "{{ $env.AZURE_SUBSCRIPTION_ID }}",
        "resource_groups": ["production", "staging"],
        "webhook_url": "http://n8n:5678/webhook/azure-complete"
      },
      "name": "Scan Azure Resources",
      "credentials": "azure-service-principal"
    },
    {
      "type": "HTTP Request", 
      "url": "http://cloudviz-api:8000/api/v1/aws/extract",
      "method": "POST",
      "body": {
        "account_id": "{{ $env.AWS_ACCOUNT_ID }}",
        "regions": ["ap-southeast-2", "us-east-1"],
        "webhook_url": "http://n8n:5678/webhook/aws-complete"
      },
      "name": "Scan AWS Resources",
      "credentials": "aws-access-keys"
    },
    {
      "type": "HTTP Request",
      "url": "http://cloudviz-api:8000/api/v1/gcp/extract",
      "method": "POST",
      "body": {
        "project_id": "{{ $env.GCP_PROJECT_ID }}",
        "regions": ["australia-southeast1", "us-central1"],
        "webhook_url": "http://n8n:5678/webhook/gcp-complete"
      },
      "name": "Scan GCP Resources",
      "credentials": "gcp-service-account"
    },
    {
      "type": "HTTP Request",
      "url": "http://cloudviz-api:8000/api/v1/visualization/generate",
      "method": "POST",
      "body": {
        "providers": ["azure", "aws", "gcp"],
        "format": "mermaid",
        "include_costs": true,
        "include_dependencies": true,
        "layout": "hierarchical"
      },
      "name": "Generate Hierarchical Infrastructure Diagram"
    }
  ]
}
```

## ⚙️ **Quick Start**

### Environment Setup
```bash
# Clone repository
git clone https://github.com/navidrast/cloudviz.git
cd cloudviz

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export AZURE_CLIENT_ID=your-azure-client-id
export AZURE_CLIENT_SECRET=your-azure-client-secret
export AZURE_TENANT_ID=your-azure-tenant-id

# AWS Configuration
export AWS_ACCESS_KEY_ID=your-aws-access-key
export AWS_SECRET_ACCESS_KEY=your-aws-secret-key

# GCP Configuration
export GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
export GCP_PROJECT_ID=your-gcp-project-id

# Start the API server
uvicorn cloudviz.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Access the API
curl http://localhost:8000/health
```

## 📚 **API Endpoints**

### Health & System
- `GET /health` - System health check and version info
- `GET /metrics` - Prometheus metrics for monitoring
- `POST /admin/cache/clear` - Clear resource cache

### Multi-Cloud Resource Discovery
- `POST /api/v1/azure/extract` - Extract Azure subscription resources
- `POST /api/v1/aws/extract` - Extract AWS account resources  
- `POST /api/v1/gcp/extract` - Extract GCP project resources
- `GET /api/v1/resources` - List all discovered resources
- `GET /api/v1/resources/{provider}` - List resources by provider

### Visualization & Diagrams
- `POST /api/v1/visualization/generate` - Generate hierarchical infrastructure diagrams
- `GET /api/v1/visualization/export/{id}` - Export diagram in various formats
- `GET /api/v1/azure/project-info` - Get Azure subscription information
- `GET /api/v1/aws/account-info` - Get AWS account information  
- `GET /api/v1/gcp/project-info` - Get GCP project information  
- `GET /api/v1/gcp/regions` - List available GCP regions

## 🔧 **Configuration**

CloudViz supports multiple configuration methods:

### YAML Configuration
```yaml
# config/production.yml
api:
  host: "0.0.0.0"
  port: 8000
  workers: 4

cloud_providers:
  azure:
    enabled: true
    subscription_ids: ["sub-12345"]
    regions: ["australiaeast", "australiasoutheast"]
  
  aws:
    enabled: true
    account_ids: ["123456789012"]
    regions: ["ap-southeast-2", "us-east-1"]
    
  gcp:
    enabled: true
    project_ids: ["my-gcp-project"]
    regions: ["australia-southeast1", "us-central1"]

visualization:
  default_format: "mermaid"
  layout: "hierarchical"
  include_costs: true
  include_dependencies: true
  
cache:
  ttl: 3600
  redis_url: "redis://localhost:6379"
```

## 🏗️ **Hierarchical Architecture Benefits**

The hierarchical diagram approach provides:

- **🎯 Clear Organization**: Logical tier separation (Network → Application → Data → Security)
- **📊 Better Readability**: Top-down flow makes infrastructure easier to understand
- **🔍 Dependency Tracking**: Clear visualization of service dependencies and data flows
- **🏢 Enterprise Focus**: Professional presentation suitable for executive dashboards
- **🔄 Scalability**: Easy to extend with additional tiers and services
- **📈 Impact Analysis**: Quick identification of failure impact zones

---

**🌟 CloudViz - Professional hierarchical multi-cloud infrastructure visualization**

[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/navidrast/cloudviz?style=flat-square)](https://github.com/navidrast/cloudviz/stargazers)
[![Enterprise Ready](https://img.shields.io/badge/Enterprise-Ready-gold?style=flat-square)](https://github.com/navidrast/cloudviz)"""

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme_content)

print("README.md created successfully with fixed Mermaid syntax!")
