#  CloudViz - Multi-Cloud Infrastructure Visualization Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Mermaid](https://img.shields.io/badge/Mermaid-Diagrams-ff69b4.svg)](https://mermaid.js.org/)

**CloudViz** is an enterprise-grade, multi-cloud infrastructure visualization platform that automatically discovers cloud resources and generates beautiful, interactive diagrams. Built with FastAPI and featuring powerful Mermaid diagram generation, CloudViz provides REST APIs perfect for automation workflows, especially **n8n integration**.

##  **Live Infrastructure Visualization Demo**

CloudViz automatically generates comprehensive infrastructure diagrams from your cloud resources. Here's a real-world example showcasing enterprise infrastructure patterns:

###  **Enterprise Multi-Cloud Architecture**
*Auto-generated from Azure subscription scan - enterprise infrastructure example*

```mermaid
%% CloudViz Auto-Generated Infrastructure Diagram
%% Scan Date: 2025-09-20 | Resources: 38 | Regions: 4 | Monthly Cost: $24,567.80
flowchart TD
    subgraph azure[" Azure Subscription: ENTERPRISE-AUSTRALIA-001"]
        subgraph au_east[" Australia East (Primary Hub)"]
            subgraph core_rg[" Core Infrastructure RG"]
                cdn[" global-enterprise-cdn<br/>CDN Profile<br/>Global Distribution - $498.50/month"]
                firewall[" azure-firewall-premium<br/>Firewall Premium<br/>Advanced Threat Protection - $2,456.80/month"]
                appgw[" enterprise-appgateway<br/>Application Gateway v2<br/>WAF + Auto-scaling - $778.90/month"]
                frontdoor[" azure-front-door<br/>Front Door Premium<br/>Global Load Balancer - $556.70/month"]
            end
            
            subgraph app_rg[" Application Services RG"]
                vmss_web[" web-servers-vmss<br/>VM Scale Set<br/>Auto-scaling 8-30 instances - $3,234.70/month"]
                vmss_api[" api-services-vmss<br/>VM Scale Set<br/>High Performance 6-20 instances - $2,497.40/month"]
                redis_cache[" enterprise-redis<br/>Redis Cache Premium<br/>120GB Multi-AZ - $2,546.40/month"]
                service_fabric[" microservices-fabric<br/>Service Fabric Cluster<br/>15 nodes HA - $1,567.80/month"]
                aks_cluster[" enterprise-aks<br/>AKS Cluster<br/>25 nodes Premium - $4,456.90/month"]
            end
            
            subgraph data_rg[" Data Platform RG"]
                sqlserver[" enterprise-sql-cluster<br/>SQL Server<br/>Business Critical Always On"]
                sqldb_primary[" customer-data-primary<br/>SQL Database<br/>15TB Business Critical - $8,156.80/month"]
                sqldb_analytics[" analytics-warehouse<br/>SQL Database<br/>8TB General Purpose - $4,189.60/month"]
                cosmos_global[" global-document-store<br/>Cosmos DB<br/>Multi-region Write - $4,067.90/month"]
                synapse[" data-warehouse<br/>Synapse Analytics<br/>DW5000c - $6,890.40/month"]
                databricks[" analytics-workspace<br/>Azure Databricks<br/>Premium Tier - $3,345.60/month"]
                storage_data[" data-lake-premium<br/>Storage Account<br/>Premium Performance 200TB - $2,234.50/month"]
            end
            
            subgraph network_rg[" Network Infrastructure RG"]
                vnet_hub[" hub-vnet-au-east<br/>Hub Virtual Network<br/>10.1.0.0/16"]
                vnet_spoke1[" spoke-apps-vnet<br/>Applications Network<br/>10.1.1.0/24"]
                vnet_spoke2[" spoke-data-vnet<br/>Data Platform Network<br/>10.1.2.0/24"]
                vnet_spoke3[" spoke-aks-vnet<br/>Container Network<br/>10.1.3.0/24"]
                expressroute[" expressroute-gateway<br/>ExpressRoute Gateway<br/>Ultra Performance - $945.60/month"]
                vpn_gateway[" site-to-site-vpn<br/>VPN Gateway<br/>High Performance - $534.50/month"]
                bastion[" bastion-host<br/>Azure Bastion<br/>Standard SKU - $245.20/month"]
                private_endpoint[" private-endpoints<br/>Private Endpoint<br/>Data Services - $123.40/month"]
            end
        end

        subgraph au_se[" Australia Southeast (DR Site)"]
            subgraph dr_rg[" Disaster Recovery RG"]
                sqldb_replica[" customer-data-replica<br/>SQL Database<br/>Read-Only Geo-Replica - $4,128.40/month"]
                storage_dr[" enterprise-backup<br/>Storage Account<br/>GRS Cool Tier 150TB - $2,467.30/month"]
                keyvault_dr[" enterprise-keyvault-dr<br/>Key Vault Premium<br/>HSM Backup - $1,590.40/month"]
                vmss_dr[" dr-standby-vmss<br/>VM Scale Set<br/>Warm standby instances - $1,256.70/month"]
                site_recovery[" azure-site-recovery<br/>ASR Service<br/>VM Protection - $434.90/month"]
                backup_vault[" recovery-services-vault<br/>Backup Vault<br/>Enterprise Backup - $567.80/month"]
            end
        end
    end

    %% Multi-Cloud Styling and Flow
    classDef azureMain fill:#0078d4,stroke:#005a9e,stroke-width:3px,color:#fff
    classDef azureSecondary fill:#40e0d0,stroke:#20b2aa,stroke-width:2px,color:#000
    classDef criticalPath fill:#dc2626,stroke:#991b1b,stroke-width:4px,color:#fff
    classDef dataFlow fill:#16a085,stroke:#0e6b5d,stroke-width:3px,color:#fff
    classDef networkFlow fill:#8e44ad,stroke:#6a3093,stroke-width:2px,color:#fff

    %% Core Application Flow
    frontdoor --> cdn
    cdn --> appgw
    appgw --> vmss_web
    appgw --> vmss_api
    vmss_web --> redis_cache
    vmss_api --> redis_cache
    vmss_api --> sqldb_primary
    vmss_web --> sqldb_analytics
    aks_cluster --> service_fabric
    
    %% Data Platform Pipeline
    sqldb_primary --> storage_data
    storage_data --> synapse
    sqldb_analytics --> databricks
    cosmos_global --> synapse
    synapse --> databricks
    databricks --> storage_data
    
    %% Network Connectivity
    expressroute --> vnet_hub
    vnet_hub --> vnet_spoke1
    vnet_hub --> vnet_spoke2
    vnet_hub --> vnet_spoke3
    vpn_gateway --> vnet_hub
    bastion --> vmss_web
    private_endpoint --> sqldb_primary
    
    %% DR Strategy
    vmss_web -.-> vmss_dr
    sqldb_primary --> sqldb_replica
    storage_data -.-> storage_dr
    backup_vault --> vmss_web
    site_recovery --> vmss_dr
    
    %% Security Flow
    firewall --> appgw
    keyvault_dr --> service_fabric
    bastion --> aks_cluster

    %% Apply Styling
    class azure,au_east,au_se azureMain
    class core_rg,app_rg,data_rg,network_rg,dr_rg azureSecondary
    class frontdoor,expressroute,sqldb_primary,synapse criticalPath
    class storage_data,databricks,cosmos_global dataFlow
    class vnet_hub,vnet_spoke1,vnet_spoke2,vnet_spoke3 networkFlow
```

**Monthly Cost Breakdown:**
- **Core Infrastructure:** $6,290.90/month
- **Application Platform:** $14,302.20/month  
- **Data & Analytics:** $28,884.80/month
- **DR & Security:** $10,445.50/month

---

###  **AWS Multi-Region Enterprise Operations**
*Auto-generated from AWS account scan - enterprise operations and edge computing*

```mermaid
%% CloudViz Auto-Generated Infrastructure Diagram
%% Scan Date: 2025-09-20 | Account: ENTERPRISE-OPERATIONS-AU-456789 | Resources: 45 | Monthly Cost: $32,750.90
flowchart TD
    subgraph aws[" AWS Account: ENTERPRISE-OPERATIONS-AU-456789"]
        subgraph ap_southeast_2[" Asia Pacific Sydney (Primary Operations)"]
            subgraph ops_rg[" Enterprise Operations Center"]
                cloudwatch[" enterprise-monitoring<br/>CloudWatch + X-Ray<br/>Advanced Observability - $634.50/month"]
                sns_alerts[" enterprise-notifications<br/>SNS + SQS Topics<br/>Multi-channel Alerts - $56.30/month"]
                lambda_automation[" ops-automation<br/>Lambda Functions<br/>Event-driven Operations - $456.70/month"]
                systems_manager[" fleet-management<br/>Systems Manager<br/>Patch & Config Mgmt - $545.60/month"]
                config[" compliance-monitoring<br/>AWS Config<br/>Resource Compliance - $234.80/month"]
            end
            
            subgraph compute_rg[" Enterprise Compute Platform"]
                vpc_primary[" enterprise-vpc-sydney<br/>VPC<br/>172.20.0.0/16"]
                alb_external[" public-application-lb<br/>Application Load Balancer<br/>Multi-AZ with WAF - $534.90/month"]
                alb_internal[" internal-application-lb<br/>Internal Load Balancer<br/>Cross-AZ Distribution - $334.70/month"]
                ec2_web[" web-tier-asg<br/>EC2 Auto Scaling Group<br/>12-36 instances m5.4xlarge - $5,456.80/month"]
                ec2_app[" app-tier-asg<br/>EC2 Auto Scaling Group<br/>8-24 instances c5.8xlarge - $6,234.60/month"]
                ecs_cluster[" microservices-ecs<br/>ECS Fargate Cluster<br/>Containerized Services - $4,890.40/month"]
                eks_cluster[" kubernetes-platform<br/>EKS Cluster<br/>Managed Kubernetes - $3,567.90/month"]
            end
            
            subgraph data_rg[" Enterprise Data Platform"]
                rds_cluster[" aurora-postgresql<br/>RDS Aurora Cluster<br/>Multi-AZ r5.8xlarge x4 - $7,567.80/month"]
                rds_mysql[" application-database<br/>RDS MySQL<br/>Multi-AZ db.r5.4xlarge - $2,345.60/month"]
                elasticache[" redis-cluster<br/>ElastiCache Redis<br/>Cluster Mode 8 nodes - $1,834.60/month"]
                s3_primary[" enterprise-data-lake<br/>S3 Intelligent Tiering<br/>1.2PB Multi-region - $6,123.70/month"]
                redshift[" analytics-warehouse<br/>Redshift RA3 Cluster<br/>ra3.4xlarge x8 nodes - $7,890.40/month"]
                dynamodb[" high-performance-db<br/>DynamoDB<br/>On-Demand Billing - $2,456.80/month"]
                opensearch[" enterprise-search<br/>OpenSearch Service<br/>Multi-AZ m5.2xlarge x6 - $3,234.70/month"]
            end
        end
    end
```

**Monthly Cost Breakdown:**
- **Operations & Monitoring:** $1,927.90/month
- **Compute Platform:** $20,514.60/month
- **Data & Analytics:** $31,453.60/month
- **Network & Security:** $7,172.10/month


---

###  **GCP AI/ML and Hybrid Cloud Platform**
*Auto-generated from GCP project scan - enterprise AI/ML and hybrid infrastructure*

```mermaid
%% CloudViz Auto-Generated Infrastructure Diagram  
%% Scan Date: 2025-09-20 | Project: enterprise-ai-australia | Resources: 41 | Monthly Cost: $38,790.60
flowchart TD
    subgraph gcp[" GCP Project: enterprise-ai-australia"]
        subgraph australia_southeast1[" Australia Southeast1 (AI/ML Headquarters)"]
            subgraph ml_rg[" Enterprise AI/ML Platform"]
                vertex_ai[" enterprise-ml-platform<br/>Vertex AI Platform<br/>Custom Training & AutoML - $5,845.60/month"]
                ai_notebooks[" research-workbench<br/>AI Platform Notebooks<br/>JupyterLab Environment - $1,834.70/month"]
                automl[" predictive-analytics<br/>AutoML Tables & Vision<br/>Business Intelligence - $3,234.50/month"]
                ai_platform[" real-time-inference<br/>AI Platform Prediction<br/>High-throughput Serving - $3,567.80/month"]
                tpu_cluster[" tpu-training-cluster<br/>Cloud TPU v4<br/>Large Scale ML Training - $6,789.20/month"]
            end
            
            subgraph data_rg[" Enterprise Data & Analytics"]
                bigquery[" enterprise-datawarehouse<br/>BigQuery<br/>35TB Active + 200TB Archive - $1,290.00/month"]
                dataflow[" real-time-pipeline<br/>Dataflow<br/>Streaming + Batch Processing - $6,890.40/month"]
                pub_sub[" enterprise-messaging<br/>Pub/Sub<br/>High Throughput Messaging - $834.70/month"]
                cloud_sql[" operational-database<br/>Cloud SQL PostgreSQL<br/>High Availability Regional - $3,456.80/month"]
                spanner[" global-database<br/>Cloud Spanner<br/>Multi-region Strongly Consistent - $8,789.20/month"]
                dataproc[" big-data-processing<br/>Dataproc Cluster<br/>Hadoop & Spark - $2,345.60/month"]
                composer[" workflow-orchestration<br/>Cloud Composer<br/>Apache Airflow - $1,567.80/month"]
            end
        end
    end
```

**Monthly Cost Breakdown:**
- **AI/ML Platform:** $21,271.80/month
- **Data & Analytics:** $25,205.30/month
- **Global Services:** $3,917.50/month

---

##  **Multi-Cloud Enterprise Strategy Dashboard**

| **Cloud Provider** | **Resources** | **Monthly Cost** | **Primary Focus** | **AU Regions** | **Strategic Value** |
|-------------------|---------------|------------------|-------------------|----------------|---------------------|
| ** Azure** | **38 resources** | **$59,923.40** | **Enterprise Apps + DR** | **Australia East/Southeast** | **Hybrid + Data Platform** |
| ** AWS** | **45 resources** | **$74,750.90** | **Operations + Edge** | **Asia Pacific Sydney** | **Global Operations** |  
| ** GCP** | **41 resources** | **$87,545.30** | **AI/ML + Hybrid** | **Australia Southeast1** | **Innovation + Analytics** |
| ** Total** | **124 resources** | **$222,219.60** | **Hybrid Multi-Cloud** | **4 Australian regions** | **Digital Transformation** |

###  **Enterprise Architecture Highlights**

- ** Enterprise Scale**: Mission-critical workloads with 99.99% availability
- ** Australian Data Sovereignty**: Primary operations in Australian regions
- ** Hybrid Strategy**: Seamless on-premises and multi-cloud integration  
- ** Global Edge Network**: Ultra-low latency worldwide performance
- ** AI/ML Ready**: Advanced analytics and machine learning capabilities
- ** Zero Trust Security**: Enterprise-grade security and compliance
- ** Auto-scaling**: Dynamic resource allocation and cost optimization
- ** Data Residency**: Australian compliance with global replication
- ** Multi-Cloud Management**: Unified operations across cloud providers
- ** High Performance**: Optimized for demanding enterprise workloads

---

##  **Quick Start**

###  **Docker Deployment** (Recommended)

```bash
# Clone the repository
git clone https://github.com/navidrast/cloudviz.git
cd cloudviz

# Run with Docker Compose
docker-compose up -d

# Access the API
curl http://localhost:8000/health
```

The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.


###  **Local Development Setup**

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"  
export AZURE_TENANT_ID="your-tenant-id"

# Run the application
uvicorn cloudviz.api.main:app --reload --host 0.0.0.0 --port 8000
```

---

##  **API Endpoints**

CloudViz provides a comprehensive REST API perfect for automation workflows:

###  **Health & Monitoring**
- `GET /health` - Service health check
- `GET /health/detailed` - Detailed system health
- `GET /metrics` - Prometheus metrics

###  **Authentication**  
- `POST /auth/token` - Get access token
- `POST /auth/refresh` - Refresh token
- `GET /auth/validate` - Validate token

###  **Cloud Resource Discovery**
- `POST /extract/azure/subscription` - Scan Azure subscription
- `POST /extract/aws/account` - Scan AWS account  
- `POST /extract/gcp/project` - Scan GCP project
- `GET /extract/status/{job_id}` - Check extraction status

###  **Diagram Generation**
- `POST /visualize/mermaid` - Generate Mermaid diagram
- `POST /visualize/graphviz` - Generate Graphviz diagram
- `POST /visualize/architecture` - Auto-detect and visualize
- `GET /visualize/themes` - Available themes

###  **Administration**
- `GET /admin/stats` - Platform statistics
- `POST /admin/cache/clear` - Clear cache
- `GET /admin/logs` - Recent logs

---

##  **Key Features**

###  **Multi-Cloud Support**
- **Azure**: Complete ARM template discovery
- **AWS**: CloudFormation and direct API scanning  
- **GCP**: Resource Manager and service-specific APIs

###  **Visualization Engines**
- **Mermaid**: Interactive diagrams with live editing
- **Graphviz**: Publication-quality network diagrams
- **Custom themes**: Azure, AWS, GCP, and dark themes

###  **API-First Design**
- RESTful APIs for all operations
- OpenAPI 3.0 documentation
- Rate limiting and authentication
- Prometheus metrics integration

###  **Performance & Reliability**
- Async/await throughout the stack
- Redis caching for expensive operations
- Background job processing
- Comprehensive error handling

---

##  **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

##  **Acknowledgments**

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- [Mermaid](https://mermaid.js.org/) - Diagrams and flowcharts from text
- [Azure SDK](https://azure.github.io/azure-sdk-for-python/) - Azure Python SDK
- [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) - AWS SDK for Python
- [Google Cloud SDK](https://cloud.google.com/python) - Google Cloud Python SDK

---

<div align="center">

**Built with  for the DevOps and Cloud Infrastructure community**

[ Star us on GitHub](https://github.com/navidrast/cloudviz) | [ Report Issues](https://github.com/navidrast/cloudviz/issues) | [ Join Discussions](https://github.com/navidrast/cloudviz/discussions)

</div>
