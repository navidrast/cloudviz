import os

readme_content = """# 🌩️ CloudViz - Multi-Cloud Infrastructure Visualization Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Mermaid](https://img.shields.io/badge/Mermaid-Diagrams-ff69b4.svg)](https://mermaid.js.org/)

**CloudViz** is an enterprise-grade, multi-cloud infrastructure visualization platform that automatically discovers cloud resources and generates beautiful, interactive diagrams. Built with FastAPI and featuring powerful Mermaid diagram generation, CloudViz provides REST APIs perfect for automation workflows, especially **n8n integration**.

## 🎨 **Live Infrastructure Visualization Demo**

CloudViz automatically generates comprehensive infrastructure diagrams from your cloud resources. Here's a real-world example:

### 🏢 **Enterprise Multi-Cloud Architecture**
*Auto-generated from Azure subscription scan - enterprise infrastructure example*

```mermaid
%% CloudViz Auto-Generated Infrastructure Diagram
%% Scan Date: 2025-09-20 | Resources: 35 | Regions: 4 | Monthly Cost: $18,567.80
flowchart LR
    subgraph azure["🔷 Azure Subscription: ENTERPRISE-PROD-001"]
        subgraph au_east["🌏 Australia East (Primary Hub)"]
            subgraph core_rg["🛡️ Core Network RG"]
                cdn["🚀 global-telecom-cdn<br/>CDN Profile<br/>Edge POP Network<br/>$198.50/month"]
                firewall["🛡️ azure-firewall-premium<br/>Firewall Premium<br/>NGFW + IDPS<br/>$1,456.80/month"]
                appgw["🌐 telecom-appgateway<br/>Application Gateway v2<br/>WAF + DDoS Protection<br/>$378.90/month"]
            end
            
            subgraph bss_rg["💼 BSS/OSS Application RG"]
                vmss_billing["🔄 billing-vmss<br/>VM Scale Set<br/>5-15 instances<br/>$1,234.70/month"]
                vmss_crm["🔄 crm-vmss<br/>VM Scale Set<br/>3-12 instances<br/>$897.40/month"]
                redis_session["⚡ session-redis<br/>Redis Cache Premium<br/>52GB<br/>$1,246.40/month"]
                service_fabric["⚙️ oss-service-fabric<br/>Service Fabric Cluster<br/>6 nodes<br/>$567.80/month"]
            end
            
            subgraph data_rg["🗄️ Telecom Data RG"]
                sqlserver["🏛️ telecom-sql-server<br/>SQL Server<br/>Business Critical"]
                sqldb_billing["💾 billing-database<br/>SQL Database<br/>5TB<br/>$3,456.80/month"]
                sqldb_customer["💾 customer-database<br/>SQL Database<br/>2TB<br/>$1,789.60/month"]
                cosmos_network["🌐 network-topology<br/>Cosmos DB<br/>Multi-master<br/>$1,567.90/month"]
                synapse["📊 telecom-synapse<br/>Synapse Analytics<br/>DW1000c<br/>$2,890.40/month"]
            end
            
            subgraph network_rg["🌐 Network Infrastructure RG"]
                vnet_hub["🔗 hub-vnet<br/>Hub Virtual Network<br/>10.0.0.0/16"]
                vnet_spoke1["🔗 spoke1-vnet<br/>BSS Virtual Network<br/>10.1.0.0/16"]
                vnet_spoke2["🔗 spoke2-vnet<br/>OSS Virtual Network<br/>10.2.0.0/16"]
                expressroute["⚡ expressroute-gateway<br/>ExpressRoute Gateway<br/>Ultra Performance<br/>$445.60/month"]
                vpn_gateway["🔒 vpn-gateway<br/>VPN Gateway<br/>High Performance<br/>$234.50/month"]
            end
            
            subgraph security_rg["🔐 Security & Compliance RG"]
                sentinel["🛡️ azure-sentinel<br/>SIEM + SOAR<br/>Log Analytics Workspace<br/>$890.40/month"]
                keyvault["🔐 telecom-hsm<br/>Key Vault HSM<br/>FIPS 140-2 Level 3<br/>$1,890.40/month"]
                backup_vault["💾 backup-vault<br/>Recovery Services Vault<br/>Cross-Region Backup<br/>$567.80/month"]
            end
        end
        
        subgraph au_southeast["🌏 Australia Southeast (DR Site)"]
            subgraph dr_rg["🔄 Disaster Recovery RG"]
                asr["🔄 site-recovery<br/>Azure Site Recovery<br/>VM Replication<br/>$234.50/month"]
                dr_storage["💾 dr-backup-storage<br/>Geo-Redundant Storage<br/>500TB<br/>$1,234.60/month"]
                dr_sql["💾 dr-sql-replica<br/>SQL Database<br/>Read Replica<br/>$2,456.80/month"]
            end
        end
    end
    
    %% Data Flow Connections
    firewall -->|"Traffic Inspection"| appgw
    appgw -->|"Load Balance"| vmss_billing
    appgw -->|"Load Balance"| vmss_crm
    vmss_billing -->|"Session State"| redis_session
    vmss_crm -->|"Session State"| redis_session
    vmss_billing -->|"Database Access"| sqldb_billing
    vmss_crm -->|"Database Access"| sqldb_customer
    service_fabric -->|"Microservices"| cosmos_network
    sqldb_billing -->|"Data Warehouse ETL"| synapse
    sqldb_customer -->|"Data Warehouse ETL"| synapse
    
    %% Network Connectivity
    vnet_hub -->|"Peering"| vnet_spoke1
    vnet_hub -->|"Peering"| vnet_spoke2
    expressroute -->|"Hybrid Connectivity"| vnet_hub
    vpn_gateway -->|"Site-to-Site VPN"| vnet_hub
    
    %% Security Flow
    sentinel -->|"Security Monitoring"| firewall
    sentinel -->|"Log Collection"| vmss_billing
    sentinel -->|"Log Collection"| vmss_crm
    keyvault -->|"Certificate Management"| service_fabric
    keyvault -->|"TLS Certificates"| appgw
    
    %% Disaster Recovery
    sqldb_billing -.->|"Geo-Replication"| dr_sql
    sqldb_customer -.->|"Geo-Replication"| dr_sql
    vmss_billing -.->|"VM Replication"| asr
    vmss_crm -.->|"VM Replication"| asr
    backup_vault -.->|"Cross-Region Backup"| dr_storage
    
    style azure fill:#e1f5fe
    style au_east fill:#bbdefb
    style au_southeast fill:#ffecb3
```

---

### 🚀 **AWS Cloud Infrastructure - Multi-Region Deployment**
*Auto-generated from AWS account scan across multiple regions*

```mermaid
%% CloudViz Auto-Generated AWS Infrastructure Diagram
%% Scan Date: 2025-09-20 | Account: 123456789012 | Resources: 31 | Monthly Cost: $12,450.80
flowchart LR
    subgraph aws["🟠 AWS Account: TELECOM-PROD-INFRASTRUCTURE"]
        subgraph ap_southeast_2["🌏 AP-Southeast-2 (Sydney)"]
            subgraph compute_layer["💻 Compute & Application Layer"]
                ec2_monitoring["🔍 network-monitoring-asg<br/>EC2 Auto Scaling Group<br/>c5.2xlarge x 8 instances<br/>$1,456.80/month"]
                ec2_analytics["📈 traffic-analytics-asg<br/>EC2 Auto Scaling Group<br/>r5.xlarge x 6 instances<br/>$1,234.40/month"]
                lambda_processors["⚡ data-processors<br/>Lambda Functions<br/>Python 3.9 Runtime<br/>$567.80/month"]
                ecs_cluster["🐳 microservices-ecs<br/>ECS Fargate Cluster<br/>12 services running<br/>$1,890.40/month"]
            end
            
            subgraph data_layer["🗄️ Data & Analytics Layer"]
                rds_aurora["🌟 customer-aurora-cluster<br/>RDS Aurora PostgreSQL<br/>Multi-AZ, 3 read replicas<br/>$2,890.60/month"]
                elasticache["⚡ session-elasticache<br/>ElastiCache Redis<br/>cache.r6g.xlarge cluster<br/>$756.80/month"]
                s3_data["📦 telecom-data-lake<br/>S3 Bucket<br/>45TB Intelligent Tiering<br/>$890.40/month"]
                opensearch["🔍 log-analytics<br/>OpenSearch Service<br/>m6g.large.search cluster<br/>$1,245.70/month"]
            end
            
            subgraph network_layer["🌐 Network & Security Layer"]
                vpc_main["🔗 main-vpc<br/>VPC Network<br/>10.0.0.0/16"]
                alb_public["🌐 public-alb<br/>Application Load Balancer<br/>Internet-facing<br/>$345.60/month"]
                alb_internal["🔗 internal-alb<br/>Application Load Balancer<br/>Internal<br/>$234.50/month"]
                nat_gateway["🌍 nat-gateway<br/>NAT Gateway<br/>Multi-AZ<br/>$156.90/month"]
                cloudfront["🚀 global-cdn<br/>CloudFront Distribution<br/>Global Edge Locations<br/>$567.80/month"]
            end
            
            subgraph security_layer["🔐 Security & Monitoring Layer"]
                waf["🛡️ web-application-firewall<br/>AWS WAF<br/>Rate Limiting + Bot Control<br/>$234.50/month"]
                shield["🛡️ ddos-protection<br/>AWS Shield Advanced<br/>DDoS Protection<br/>$3,000.00/month"]
                cloudwatch["📊 monitoring<br/>CloudWatch<br/>Metrics + Logs + Alarms<br/>$445.60/month"]
                secrets_manager["🔐 app-secrets<br/>Secrets Manager<br/>Database credentials<br/>$67.80/month"]
            end
        end
        
        subgraph ap_southeast_1["🌏 AP-Southeast-1 (Singapore DR)"]
            subgraph dr_services["🔄 Disaster Recovery Services"]
                rds_replica["🔄 aurora-read-replica<br/>RDS Aurora Read Replica<br/>Cross-region replica<br/>$1,445.30/month"]
                s3_replica["💾 dr-data-backup<br/>S3 Bucket<br/>Cross-region replication<br/>$445.60/month"]
                lambda_failover["⚡ failover-automation<br/>Lambda Functions<br/>DR orchestration<br/>$89.40/month"]
            end
        end
        
        subgraph us_east_1["🌏 US-East-1 (Global Services)"]
            subgraph global_services["🌍 Global Services Hub"]
                route53["🌍 telecom-dns<br/>Route 53<br/>Health checks + Geolocation<br/>$123.40/month"]
                acm["🔐 ssl-certificates<br/>Certificate Manager<br/>SSL/TLS Certificates<br/>$0.00/month"]
                iam["🔐 identity-access<br/>IAM<br/>Users + Roles + Policies<br/>$0.00/month"]
            end
        end
    end
    
    %% Application Traffic Flow
    cloudfront -->|"Cache & Accelerate"| alb_public
    alb_public -->|"Distribute Load"| ec2_monitoring
    alb_public -->|"Distribute Load"| ec2_analytics
    alb_internal -->|"Internal Services"| ecs_cluster
    waf -->|"Security Filtering"| alb_public
    shield -->|"DDoS Protection"| cloudfront
    
    %% Data Processing Pipeline
    ec2_monitoring -->|"Metrics Collection"| opensearch
    ec2_analytics -->|"Traffic Analysis"| s3_data
    lambda_processors -->|"Real-time Processing"| rds_aurora
    lambda_processors -->|"Cache Updates"| elasticache
    ecs_cluster -->|"Microservice Data"| rds_aurora
    
    %% Network Architecture
    nat_gateway -->|"Outbound Internet"| ec2_monitoring
    nat_gateway -->|"Outbound Internet"| ec2_analytics
    vpc_main -->|"Network Isolation"| ec2_monitoring
    vpc_main -->|"Network Isolation"| ec2_analytics
    
    %% Security & Secrets Management
    secrets_manager -->|"Database Credentials"| rds_aurora
    secrets_manager -->|"API Keys"| ecs_cluster
    cloudwatch -->|"Monitoring"| ec2_monitoring
    cloudwatch -->|"Monitoring"| rds_aurora
    cloudwatch -->|"Monitoring"| lambda_processors
    
    %% DNS & Global Routing
    route53 -->|"DNS Resolution"| cloudfront
    route53 -->|"Health Checks"| alb_public
    acm -->|"SSL Certificates"| alb_public
    acm -->|"SSL Certificates"| cloudfront
    
    %% Cross-Region Disaster Recovery
    rds_aurora -.->|"Cross-Region Replica"| rds_replica
    s3_data -.->|"Cross-Region Replication"| s3_replica
    cloudwatch -.->|"Failover Trigger"| lambda_failover
    
    style aws fill:#fff3e0
    style ap_southeast_2 fill:#ffcc80
    style ap_southeast_1 fill:#ffe0b2
    style us_east_1 fill:#fff8e1
```

---

### 🌐 **Google Cloud Platform - Edge Computing & Analytics**
*Auto-generated from GCP project scan across multiple regions*

```mermaid
%% CloudViz Auto-Generated GCP Infrastructure Diagram  
%% Scan Date: 2025-09-20 | Project: telecom-edge-analytics-001 | Resources: 28 | Regions: 3 | Monthly Cost: $15,890.40
flowchart LR
    subgraph gcp["🔵 GCP Project: telecom-edge-analytics-001"]
        subgraph australia_southeast1["🌏 australia-southeast1 (Sydney)"]
            subgraph container_platform["🐳 Container & Microservices Platform"]
                gke_primary["⚙️ edge-computing-gke<br/>GKE Autopilot Cluster<br/>25 nodes, 120 pods<br/>$3,456.80/month"]
                registry["📦 container-registry<br/>Artifact Registry<br/>Container Images & Helm Charts<br/>$189.60/month"]
                cloud_run["⚡ microservices-platform<br/>Cloud Run Services<br/>12 serverless services<br/>$756.70/month"]
                istio_mesh["🕸️ service-mesh<br/>Istio on GKE<br/>Traffic Management & Security<br/>$323.40/month"]
            end
            
            subgraph compute_analytics["💻 Compute & Analytics Layer"]
                vm_monitoring["📊 network-monitoring-vms<br/>Compute Engine<br/>c2-standard-16 x 8 instances<br/>$2,890.40/month"]
                sql_primary["🗄️ network-analytics-db<br/>Cloud SQL PostgreSQL<br/>db-custom-32-209715200<br/>$4,123.70/month"]
                memorystore["⚡ real-time-cache<br/>Memorystore Redis<br/>Standard Tier 100GB<br/>$567.80/month"]
                bigtable["⚡ timeseries-database<br/>Cloud Bigtable<br/>SSD Cluster for IoT data<br/>$1,290.40/month"]
            end
            
            subgraph storage_layer["📦 Storage & Data Lake"]
                storage_telemetry["📊 network-telemetry<br/>Cloud Storage<br/>45TB Regional Storage<br/>$900.00/month"]
                storage_configs["⚙️ device-configurations<br/>Cloud Storage<br/>2.1TB Standard Storage<br/>$42.00/month"]
                storage_backup["💾 disaster-recovery<br/>Cloud Storage<br/>25TB Coldline Backup<br/>$175.00/month"]
            end
            
            subgraph ai_ml_platform["🤖 AI/ML & Real-time Processing"]
                vertex_ai["🧠 network-ai-platform<br/>Vertex AI Training<br/>Custom ML Models<br/>$2,890.80/month"]
                pubsub_events["📡 network-events<br/>Pub/Sub Topics<br/>5M messages/day<br/>$345.70/month"]
                dataflow["🌊 stream-analytics<br/>Dataflow Jobs<br/>Apache Beam Processing<br/>$1,567.50/month"]
                cloud_functions["⚡ event-processors<br/>Cloud Functions<br/>Python 3.9 Runtime<br/>$256.40/month"]
            end
        end
        
        subgraph australia_southeast2["🌏 australia-southeast2 (Melbourne DR)"]
            subgraph dr_analytics["🔄 Disaster Recovery & Analytics"]
                sql_replica["📋 analytics-replica<br/>Cloud SQL Read Replica<br/>Cross-region backup<br/>$2,061.85/month"]
                gke_standby["⚙️ standby-gke-cluster<br/>GKE Standard Cluster<br/>Minimal nodes for DR<br/>$567.80/month"]
                storage_dr["💾 dr-backup-storage<br/>Cloud Storage<br/>Multi-region backup<br/>$445.60/month"]
            end
        end
        
        subgraph us_central1["🌏 us-central1 (Global Services)"]
            subgraph global_platform["🌍 Global Platform Services"]
                bigquery["📈 telecom-datawarehouse<br/>BigQuery Dataset<br/>15TB Active Storage<br/>$300.00/month"]
                looker["📊 business-intelligence<br/>Looker Studio<br/>Executive Dashboards<br/>$456.60/month"]
                dataproc["⚙️ batch-processing<br/>Dataproc Cluster<br/>Spark Jobs<br/>$434.80/month"]
                cloud_armor["🛡️ ddos-protection<br/>Cloud Armor<br/>Security Policies<br/>$234.60/month"]
            end
            
            subgraph monitoring_ops["📊 Operations & Monitoring"]
                monitoring["📊 operations-suite<br/>Cloud Operations<br/>Monitoring & Alerting<br/>$289.80/month"]
                trace["🔍 distributed-tracing<br/>Cloud Trace<br/>Request Tracing<br/>$45.60/month"]
                scheduler["⏰ job-scheduler<br/>Cloud Scheduler<br/>Cron Jobs & Automation<br/>$12.30/month"]
            end
        end
        
        subgraph global_network["🌐 Global Network & Security"]
            cdn["🚀 edge-acceleration<br/>Cloud CDN<br/>Global Edge Cache<br/>$156.45/month"]
            dns["🌍 managed-dns<br/>Cloud DNS<br/>Managed Zones & Records<br/>$23.40/month"]
            iam["🔐 identity-platform<br/>IAM & Service Accounts<br/>Zero-Trust Security<br/>$0.00/month"]
            load_balancer["🌐 global-load-balancer<br/>HTTP(S) Load Balancer<br/>Global Traffic Distribution<br/>$234.50/month"]
        end
    end
    
    %% Real-time Data Pipeline
    pubsub_events -->|"Event Streaming"| dataflow
    dataflow -->|"Processed Data"| sql_primary
    dataflow -->|"Time Series Data"| bigtable
    dataflow -->|"Raw Telemetry"| storage_telemetry
    cloud_functions -->|"Event Processing"| pubsub_events
    
    %% Container & Microservices Flow
    gke_primary -->|"ML Workloads"| vertex_ai
    gke_primary -->|"Service Discovery"| dns
    istio_mesh -->|"Traffic Management"| cloud_run
    registry -->|"Container Images"| gke_primary
    registry -->|"Container Images"| cloud_run
    
    %% Analytics & Business Intelligence
    sql_primary -->|"Data Export"| bigquery
    bigtable -->|"Time Series Analytics"| bigquery
    bigquery -->|"Business Intelligence"| looker
    bigquery -->|"Batch Processing"| dataproc
    vertex_ai -->|"Model Artifacts"| storage_configs
    
    %% Global Services & CDN
    load_balancer -->|"Traffic Distribution"| gke_primary
    load_balancer -->|"Service Routing"| cloud_run
    cdn -->|"Static Content"| storage_telemetry
    dns -->|"Service Discovery"| load_balancer
    
    %% Security & Monitoring
    cloud_armor -->|"DDoS Protection"| load_balancer
    gke_primary -->|"Metrics & Logs"| monitoring
    sql_primary -->|"Query Performance"| trace
    vertex_ai -->|"Training Metrics"| monitoring
    cloud_run -->|"Service Metrics"| monitoring
    
    %% Cross-Region Disaster Recovery
    sql_primary -.->|"Read Replica"| sql_replica
    storage_telemetry -.->|"Multi-region Backup"| storage_dr
    gke_primary -.->|"Cluster Backup"| gke_standby
    monitoring -.->|"DR Alerting"| scheduler
    
    %% Compute & Storage Integration
    vm_monitoring -->|"Network Data"| sql_primary
    vm_monitoring -->|"Real-time Cache"| memorystore
    gke_primary -->|"Persistent Storage"| storage_telemetry
    cloud_run -->|"Configuration Data"| storage_configs
    
    style gcp fill:#e8f5e8
    style australia_southeast1 fill:#c8e6c9
    style australia_southeast2 fill:#fff3e0
    style us_central1 fill:#e1f5fe
```

---

## 📊 **Multi-Cloud Infrastructure Summary**

| **Cloud Provider** | **Resources** | **Monthly Cost** | **Key Services** | **Regions** |
|-------------------|---------------|------------------|------------------|-------------|
| **🔷 Azure** | 35 resources | $18,567.80 | VM Scale Sets, SQL Database, Service Fabric, Synapse | 2 regions |
| **🟠 AWS** | 31 resources | $12,450.80 | EC2, RDS Aurora, Lambda, ECS | 4 regions |
| **🔵 GCP** | 28 resources | $15,890.40 | GKE, Vertex AI, BigQuery, Cloud Run | 3 regions |
| **📊 Total** | **94 resources** | **$46,909.00** | **Multi-cloud enterprise platform** | **9 regions** |

---

## 🚀 **Key Features**

- **🔍 Multi-Cloud Discovery**: Comprehensive resource extraction across Azure, AWS, and GCP
- **🎨 Beautiful Visualizations**: Interactive diagrams with real-time data
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
        "include_dependencies": true
      },
      "name": "Generate Infrastructure Diagram"
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
- `POST /api/v1/visualization/generate` - Generate infrastructure diagrams
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
  include_costs: true
  include_dependencies: true
  
cache:
  ttl: 3600
  redis_url: "redis://localhost:6379"
```

## 🏗️ **Architecture**

CloudViz is built with a modern, scalable architecture:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend UI   │    │   n8n Workflows │    │  External APIs  │
│   (Optional)    │    │   (Automation)  │    │  (Monitoring)   │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼───────────────┐
                    │     CloudViz API Server     │
                    │      (FastAPI + Async)      │
                    └─────────────┬───────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
┌─────────▼───────┐    ┌─────────▼───────┐    ┌─────────▼───────┐
│ Azure Extractor │    │  AWS Extractor  │    │  GCP Extractor  │
│   (Azure SDK)   │    │   (Boto3 SDK)   │    │ (Google Cloud)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
          │                       │                       │
          └───────────────────────┼───────────────────────┘
                                  │
                    ┌─────────────▼───────────────┐
                    │    Visualization Engine     │
                    │   (Mermaid + GraphViz)      │
                    └─────────────────────────────┘
```

## 📈 **Enterprise Benefits**

- **🔍 Complete Visibility**: Full infrastructure overview across all cloud providers
- **💰 Cost Optimization**: Identify unused resources and cost optimization opportunities
- **🔒 Security Compliance**: Visualize security policies, compliance gaps, and risk areas
- **⚡ Performance Optimization**: Optimize network paths, dependencies, and bottlenecks
- **📋 Automated Documentation**: Auto-generated, always up-to-date architecture documentation
- **🚨 Incident Response**: Rapid dependency impact analysis during outages
- **🤖 Workflow Automation**: Perfect integration with n8n for automated infrastructure management

---

**🌟 CloudViz - Professional multi-cloud infrastructure visualization for enterprise environments**

[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/navidrast/cloudviz?style=flat-square)](https://github.com/navidrast/cloudviz/stargazers)
[![Enterprise Ready](https://img.shields.io/badge/Enterprise-Ready-gold?style=flat-square)](https://github.com/navidrast/cloudviz)"""

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme_content)

print("README.md created successfully with improved formatting!")
