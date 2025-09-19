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
%% CloudViz Auto-Generated Infrastructure Diagram
%% Scan Date: 2025-09-20 | Resources: 35 | Regions: 4 | Monthly Cost: $18,567.80
flowchart TD
    %% Internet Entry Point
    INTERNET[🌍 Internet Users]
    
    %% Global CDN Layer
    INTERNET --> CDN_LAYER[🚀 Global CDN Layer]
    
    %% Azure Cloud Platform
    CDN_LAYER --> AZURE_CLOUD{🔷 Azure Cloud Platform}
    
    AZURE_CLOUD --> AU_EAST[🌏 Australia East - Primary]
    AZURE_CLOUD --> AU_SOUTHEAST[🌏 Australia Southeast - DR]
    
    %% Australia East - Primary Hub Tiers
    AU_EAST --> NETWORK_TIER[🌐 Network & Security Tier]
    AU_EAST --> APPLICATION_TIER[💼 Application Services Tier]
    AU_EAST --> DATA_TIER[🗄️ Data & Analytics Tier]
    AU_EAST --> SECURITY_TIER[🔐 Security & Compliance Tier]
    
    %% Network & Security Layer
    NETWORK_TIER --> firewall[🛡️ Azure Firewall Premium<br/>NGFW + IDPS<br/>$1,456.80/month]
    NETWORK_TIER --> appgw[🌐 Application Gateway v2<br/>WAF + DDoS Protection<br/>$378.90/month]
    NETWORK_TIER --> cdn[🚀 Global Telecom CDN<br/>Edge POP Network<br/>$198.50/month]
    NETWORK_TIER --> vnet_hub[🔗 Hub VNet<br/>10.0.0.0/16]
    NETWORK_TIER --> expressroute[⚡ ExpressRoute Gateway<br/>Ultra Performance<br/>$445.60/month]
    NETWORK_TIER --> vpn_gateway[🔒 VPN Gateway<br/>High Performance<br/>$234.50/month]
    
    %% Application Services Layer  
    APPLICATION_TIER --> vmss_billing[🔄 Billing VMSS<br/>5-15 instances<br/>$1,234.70/month]
    APPLICATION_TIER --> vmss_crm[🔄 CRM VMSS<br/>3-12 instances<br/>$897.40/month]
    APPLICATION_TIER --> redis_session[⚡ Session Redis Cache<br/>Premium 52GB<br/>$1,246.40/month]
    APPLICATION_TIER --> service_fabric[⚙️ OSS Service Fabric<br/>6 node cluster<br/>$567.80/month]
    
    %% Data & Analytics Layer
    DATA_TIER --> sqlserver[🏛️ Telecom SQL Server<br/>Business Critical]
    DATA_TIER --> sqldb_billing[💾 Billing Database<br/>SQL Database 5TB<br/>$3,456.80/month]
    DATA_TIER --> sqldb_customer[💾 Customer Database<br/>SQL Database 2TB<br/>$1,789.60/month]
    DATA_TIER --> cosmos_network[🌐 Network Topology DB<br/>Cosmos Multi-master<br/>$1,567.90/month]
    DATA_TIER --> synapse[📊 Telecom Synapse<br/>Analytics DW1000c<br/>$2,890.40/month]
    
    %% Security & Compliance Layer
    SECURITY_TIER --> sentinel[🛡️ Azure Sentinel<br/>SIEM + SOAR<br/>$890.40/month]
    SECURITY_TIER --> keyvault[🔐 Telecom HSM<br/>Key Vault FIPS 140-2<br/>$1,890.40/month]
    SECURITY_TIER --> backup_vault[💾 Backup Vault<br/>Cross-Region Recovery<br/>$567.80/month]
    
    %% Australia Southeast - DR Site
    AU_SOUTHEAST --> DR_TIER[🔄 Disaster Recovery Tier]
    DR_TIER --> asr[🔄 Site Recovery<br/>VM Replication<br/>$234.50/month]
    DR_TIER --> dr_storage[💾 DR Storage<br/>Geo-Redundant 500TB<br/>$1,234.60/month]
    DR_TIER --> dr_sql[💾 SQL Read Replica<br/>Cross-region backup<br/>$2,456.80/month]
    
    %% Hierarchical Data Flow
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
    
    %% Security Flow
    sentinel --> firewall
    sentinel --> vmss_billing
    sentinel --> vmss_crm
    keyvault --> service_fabric
    keyvault --> appgw
    
    %% Network Flow
    vnet_hub --> vmss_billing
    vnet_hub --> vmss_crm
    expressroute --> vnet_hub
    vpn_gateway --> vnet_hub
    
    %% Disaster Recovery Flow
    sqldb_billing -.-> dr_sql
    sqldb_customer -.-> dr_sql
    vmss_billing -.-> asr
    vmss_crm -.-> asr
    backup_vault -.-> dr_storage
    
    %% Styling for Hierarchical Organization
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
%% CloudViz Auto-Generated AWS Infrastructure Diagram
%% Scan Date: 2025-09-20 | Account: 123456789012 | Resources: 31 | Monthly Cost: $12,450.80
flowchart TD
    %% Global Entry Points
    GLOBAL_USERS[🌍 Global Users]
    
    %% Global Services Layer
    GLOBAL_USERS --> GLOBAL_SERVICES{🌐 AWS Global Services}
    
    %% Regional Distribution
    GLOBAL_SERVICES --> AP_SE_2[🌏 AP-Southeast-2 Sydney]
    GLOBAL_SERVICES --> AP_SE_1[🌏 AP-Southeast-1 Singapore DR]
    GLOBAL_SERVICES --> US_EAST_1[🌏 US-East-1 Global Hub]
    
    %% Global Services in US-East-1
    US_EAST_1 --> GLOBAL_TIER[🌍 Global Services Tier]
    GLOBAL_TIER --> route53[🌍 Route 53 DNS<br/>Health checks + Geolocation<br/>$123.40/month]
    GLOBAL_TIER --> cloudfront[🚀 CloudFront CDN<br/>Global Edge Locations<br/>$567.80/month]
    GLOBAL_TIER --> acm[🔐 Certificate Manager<br/>SSL/TLS Certificates<br/>$0.00/month]
    GLOBAL_TIER --> iam[🔐 Identity & Access<br/>Users + Roles + Policies<br/>$0.00/month]
    
    %% AP-Southeast-2 Primary Region
    AP_SE_2 --> COMPUTE_LAYER[💻 Compute Layer]
    AP_SE_2 --> DATA_LAYER[🗄️ Data Layer]
    AP_SE_2 --> NETWORK_LAYER[🌐 Network Layer]
    AP_SE_2 --> SECURITY_LAYER[🔐 Security Layer]
    
    %% Compute Layer
    COMPUTE_LAYER --> ec2_monitoring[🔍 Network Monitoring ASG<br/>c5.2xlarge x 8 instances<br/>$1,456.80/month]
    COMPUTE_LAYER --> ec2_analytics[📈 Traffic Analytics ASG<br/>r5.xlarge x 6 instances<br/>$1,234.40/month]
    COMPUTE_LAYER --> lambda_processors[⚡ Data Processors<br/>Lambda Python 3.9<br/>$567.80/month]
    COMPUTE_LAYER --> ecs_cluster[🐳 Microservices ECS<br/>Fargate 12 services<br/>$1,890.40/month]
    
    %% Data Layer
    DATA_LAYER --> rds_aurora[🌟 Customer Aurora Cluster<br/>PostgreSQL Multi-AZ<br/>$2,890.60/month]
    DATA_LAYER --> elasticache[⚡ Session ElastiCache<br/>Redis cluster<br/>$756.80/month]
    DATA_LAYER --> s3_data[📦 Telecom Data Lake<br/>S3 45TB Intelligent<br/>$890.40/month]
    DATA_LAYER --> opensearch[🔍 Log Analytics<br/>OpenSearch cluster<br/>$1,245.70/month]
    
    %% Network Layer
    NETWORK_LAYER --> vpc_main[🔗 Main VPC<br/>10.0.0.0/16]
    NETWORK_LAYER --> alb_public[🌐 Public ALB<br/>Internet-facing<br/>$345.60/month]
    NETWORK_LAYER --> alb_internal[🔗 Internal ALB<br/>Private routing<br/>$234.50/month]
    NETWORK_LAYER --> nat_gateway[🌍 NAT Gateway<br/>Multi-AZ outbound<br/>$156.90/month]
    
    %% Security Layer
    SECURITY_LAYER --> waf[🛡️ Web Application Firewall<br/>Rate Limiting + Bot Control<br/>$234.50/month]
    SECURITY_LAYER --> shield[🛡️ DDoS Protection<br/>Shield Advanced<br/>$3,000.00/month]
    SECURITY_LAYER --> cloudwatch[📊 CloudWatch<br/>Metrics + Logs + Alarms<br/>$445.60/month]
    SECURITY_LAYER --> secrets_manager[🔐 Secrets Manager<br/>Database credentials<br/>$67.80/month]
    
    %% AP-Southeast-1 DR Region
    AP_SE_1 --> DR_SERVICES[🔄 DR Services Tier]
    DR_SERVICES --> rds_replica[🔄 Aurora Read Replica<br/>Cross-region backup<br/>$1,445.30/month]
    DR_SERVICES --> s3_replica[💾 DR Data Backup<br/>Cross-region replication<br/>$445.60/month]
    DR_SERVICES --> lambda_failover[⚡ Failover Automation<br/>DR orchestration<br/>$89.40/month]
    
    %% Hierarchical Traffic Flow
    route53 --> cloudfront
    cloudfront --> waf
    waf --> alb_public
    alb_public --> ec2_monitoring
    alb_public --> ec2_analytics
    alb_internal --> ecs_cluster
    
    %% Data Processing Flow
    ec2_monitoring --> opensearch
    ec2_analytics --> s3_data
    lambda_processors --> rds_aurora
    lambda_processors --> elasticache
    ecs_cluster --> rds_aurora
    
    %% Network Architecture Flow
    nat_gateway --> ec2_monitoring
    nat_gateway --> ec2_analytics
    vpc_main --> ec2_monitoring
    vpc_main --> ec2_analytics
    
    %% Security & Management Flow
    secrets_manager --> rds_aurora
    secrets_manager --> ecs_cluster
    cloudwatch --> ec2_monitoring
    cloudwatch --> rds_aurora
    cloudwatch --> lambda_processors
    shield --> cloudfront
    
    %% Cross-Region DR Flow
    rds_aurora -.-> rds_replica
    s3_data -.-> s3_replica
    cloudwatch -.-> lambda_failover
    
    %% Styling for AWS Hierarchy
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
%% CloudViz Auto-Generated GCP Infrastructure Diagram  
%% Scan Date: 2025-09-20 | Project: telecom-edge-analytics-001 | Resources: 28 | Monthly Cost: $15,890.40
flowchart TD
    %% Global Entry Point
    GLOBAL_TRAFFIC[🌍 Global Traffic]
    
    %% GCP Global Network
    GLOBAL_TRAFFIC --> GCP_GLOBAL{🔵 GCP Global Network}
    
    %% Regional Distribution
    GCP_GLOBAL --> AU_SE_1[🌏 australia-southeast1 Sydney]
    GCP_GLOBAL --> AU_SE_2[🌏 australia-southeast2 Melbourne DR]
    GCP_GLOBAL --> US_CENTRAL[🌏 us-central1 Global Analytics]
    
    %% Global Load Balancing
    GCP_GLOBAL --> GLOBAL_LB[🌐 Global Load Balancer<br/>HTTP(S) Distribution<br/>$234.50/month]
    GCP_GLOBAL --> CDN_GLOBAL[🚀 Cloud CDN<br/>Global Edge Cache<br/>$156.45/month]
    GCP_GLOBAL --> DNS_GLOBAL[🌍 Cloud DNS<br/>Managed Zones<br/>$23.40/month]
    
    %% Australia Southeast 1 - Primary
    AU_SE_1 --> CONTAINER_PLATFORM[🐳 Container Platform]
    AU_SE_1 --> COMPUTE_ANALYTICS[💻 Compute & Analytics]
    AU_SE_1 --> STORAGE_LAYER[📦 Storage Layer]
    AU_SE_1 --> AI_ML_PLATFORM[🤖 AI/ML Platform]
    
    %% Container Platform Tier
    CONTAINER_PLATFORM --> gke_primary[⚙️ Edge Computing GKE<br/>Autopilot 25 nodes<br/>$3,456.80/month]
    CONTAINER_PLATFORM --> registry[📦 Artifact Registry<br/>Container Images<br/>$189.60/month]
    CONTAINER_PLATFORM --> cloud_run[⚡ Microservices Platform<br/>12 serverless services<br/>$756.70/month]
    CONTAINER_PLATFORM --> istio_mesh[🕸️ Service Mesh<br/>Istio Traffic Management<br/>$323.40/month]
    
    %% Compute & Analytics Tier
    COMPUTE_ANALYTICS --> vm_monitoring[📊 Network Monitoring VMs<br/>c2-standard-16 x 8<br/>$2,890.40/month]
    COMPUTE_ANALYTICS --> sql_primary[🗄️ Network Analytics DB<br/>Cloud SQL PostgreSQL<br/>$4,123.70/month]
    COMPUTE_ANALYTICS --> memorystore[⚡ Real-time Cache<br/>Redis 100GB<br/>$567.80/month]
    COMPUTE_ANALYTICS --> bigtable[⚡ TimeSeries Database<br/>Bigtable SSD Cluster<br/>$1,290.40/month]
    
    %% Storage Layer Tier
    STORAGE_LAYER --> storage_telemetry[📊 Network Telemetry<br/>45TB Regional Storage<br/>$900.00/month]
    STORAGE_LAYER --> storage_configs[⚙️ Device Configurations<br/>2.1TB Standard<br/>$42.00/month]
    STORAGE_LAYER --> storage_backup[💾 Disaster Recovery<br/>25TB Coldline<br/>$175.00/month]
    
    %% AI/ML Platform Tier
    AI_ML_PLATFORM --> vertex_ai[🧠 Network AI Platform<br/>Vertex AI Training<br/>$2,890.80/month]
    AI_ML_PLATFORM --> pubsub_events[📡 Network Events<br/>Pub/Sub 5M messages<br/>$345.70/month]
    AI_ML_PLATFORM --> dataflow[🌊 Stream Analytics<br/>Dataflow Apache Beam<br/>$1,567.50/month]
    AI_ML_PLATFORM --> cloud_functions[⚡ Event Processors<br/>Python 3.9 Runtime<br/>$256.40/month]
    
    %% Australia Southeast 2 - DR
    AU_SE_2 --> DR_ANALYTICS[🔄 DR Analytics Tier]
    DR_ANALYTICS --> sql_replica[📋 Analytics Replica<br/>Cross-region backup<br/>$2,061.85/month]
    DR_ANALYTICS --> gke_standby[⚙️ Standby GKE Cluster<br/>Minimal DR nodes<br/>$567.80/month]
    DR_ANALYTICS --> storage_dr[💾 DR Backup Storage<br/>Multi-region backup<br/>$445.60/month]
    
    %% US Central 1 - Global Analytics
    US_CENTRAL --> GLOBAL_ANALYTICS[📈 Global Analytics Tier]
    US_CENTRAL --> MONITORING_OPS[📊 Operations Tier]
    
    GLOBAL_ANALYTICS --> bigquery[📈 Telecom Datawarehouse<br/>BigQuery 15TB<br/>$300.00/month]
    GLOBAL_ANALYTICS --> looker[📊 Business Intelligence<br/>Looker Studio<br/>$456.60/month]
    GLOBAL_ANALYTICS --> dataproc[⚙️ Batch Processing<br/>Dataproc Spark Jobs<br/>$434.80/month]
    GLOBAL_ANALYTICS --> cloud_armor[🛡️ DDoS Protection<br/>Security Policies<br/>$234.60/month]
    
    MONITORING_OPS --> monitoring[📊 Operations Suite<br/>Monitoring & Alerting<br/>$289.80/month]
    MONITORING_OPS --> trace[🔍 Distributed Tracing<br/>Request Tracing<br/>$45.60/month]
    MONITORING_OPS --> scheduler[⏰ Job Scheduler<br/>Cron Automation<br/>$12.30/month]
    MONITORING_OPS --> iam[🔐 Identity Platform<br/>Zero-Trust Security<br/>$0.00/month]
    
    %% Hierarchical Data Pipeline Flow
    pubsub_events --> dataflow
    dataflow --> sql_primary
    dataflow --> bigtable
    dataflow --> storage_telemetry
    cloud_functions --> pubsub_events
    
    %% Container Platform Flow
    gke_primary --> vertex_ai
    gke_primary --> DNS_GLOBAL
    istio_mesh --> cloud_run
    registry --> gke_primary
    registry --> cloud_run
    
    %% Analytics Pipeline Flow
    sql_primary --> bigquery
    bigtable --> bigquery
    bigquery --> looker
    bigquery --> dataproc
    vertex_ai --> storage_configs
    
    %% Global Services Flow
    GLOBAL_LB --> gke_primary
    GLOBAL_LB --> cloud_run
    CDN_GLOBAL --> storage_telemetry
    DNS_GLOBAL --> GLOBAL_LB
    
    %% Security & Monitoring Flow
    cloud_armor --> GLOBAL_LB
    gke_primary --> monitoring
    sql_primary --> trace
    vertex_ai --> monitoring
    cloud_run --> monitoring
    
    %% Cross-Region DR Flow
    sql_primary -.-> sql_replica
    storage_telemetry -.-> storage_dr
    gke_primary -.-> gke_standby
    monitoring -.-> scheduler
    
    %% Compute Integration Flow
    vm_monitoring --> sql_primary
    vm_monitoring --> memorystore
    gke_primary --> storage_telemetry
    cloud_run --> storage_configs
    
    %% Styling for GCP Hierarchy
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

print("README.md created successfully with hierarchical diagrams!")
