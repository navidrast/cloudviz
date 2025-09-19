# 🌩️ CloudViz - Multi-Cloud Infrastructure Visualization Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Mermaid](https://img.shields.io/badge/Mermaid-Diagrams-ff69b4.svg)](https://mermaid.js.org/)

**CloudViz** is an enterprise-grade, multi-cloud infrastructure visualization platform that automatically discovers cloud resources and generates beautiful, interactive diagrams. Built with FastAPI and featuring powerful Mermaid diagram generation, CloudViz provides REST APIs perfect for automation workflows, especially **n8n integration**.

## 🎨 **Live Infrastructure Visualization Demo**

CloudViz automatically generates comprehensive infrastructure diagrams from your cloud resources. Here's a real-world example:

### 📡 **Telecommunications Enterprise Multi-Cloud Architecture**
*Auto-generated from Azure subscription scan - realistic telecommunications industry dummy data*

```mermaid
%% CloudViz Auto-Generated Infrastructure Diagram
%% Scan Date: 2025-09-20 | Resources: 28 | Regions: 4 | Monthly Cost: $11,245.60
flowchart TD
    subgraph azure["🌟 Azure Subscription: TELECOM-GLOBAL-NETWORK-001"]
        subgraph eastus["🌍 East US Region (Core Network)"]
            subgraph core_rg["🔥 Core Network RG"]
                cdn["🚀 global-telecom-cdn<br/>CDN Profile<br/>Edge POP Network - $198.50/month"]
                firewall["🛡️ azure-firewall-premium<br/>Firewall Premium<br/>NGFW + IDPS - $1,456.80/month"]
                appgw["🔐 telecom-appgateway<br/>Application Gateway v2<br/>WAF + DDoS Protection - $378.90/month"]
            end
            
            subgraph bss_rg["💼 BSS/OSS Application RG"]
                vmss_billing["🔄 billing-vmss<br/>VM Scale Set<br/>5-15 instances - $1,234.70/month"]
                vmss_crm["🔄 crm-vmss<br/>VM Scale Set<br/>3-12 instances - $897.40/month"]
                redis_session["⚡ session-redis<br/>Redis Cache Premium<br/>52GB - $1,246.40/month"]
                service_fabric["🔗 oss-service-fabric<br/>Service Fabric Cluster<br/>6 nodes - $567.80/month"]
            end
            
            subgraph data_rg["🗄️ Telecom Data RG"]
                sqlserver["🏛️ telecom-sql-server<br/>SQL Server<br/>Business Critical"]
                sqldb_billing["💾 billing-database<br/>SQL Database<br/>5TB - $3,456.80/month"]
                sqldb_customer["💾 customer-database<br/>SQL Database<br/>2TB - $1,789.60/month"]
                cosmos_network["🌐 network-topology<br/>Cosmos DB<br/>Multi-master - $1,567.90/month"]
                synapse["📊 telecom-synapse<br/>Synapse Analytics<br/>DW1000c - $2,890.40/month"]
            end
            
            subgraph network_rg["🌐 Network Infrastructure RG"]
                vnet_hub["🔗 hub-vnet<br/>Hub Virtual Network<br/>10.0.0.0/16"]
                vnet_spoke1["🔗 spoke1-vnet<br/>BSS Virtual Network<br/>10.1.0.0/16"]
                vnet_spoke2["🔗 spoke2-vnet<br/>OSS Virtual Network<br/>10.2.0.0/16"]
                expressroute["⚡ expressroute-gateway<br/>ExpressRoute Gateway<br/>Ultra Performance - $445.60/month"]
                vpn_gateway["🔒 vpn-gateway<br/>VPN Gateway<br/>High Performance - $234.50/month"]
            end
        end

        subgraph westus["🌍 West US Region (5G Core)"]
            subgraph fiveg_rg["📶 5G Core Network RG"]
                amf["📡 5g-amf<br/>Access & Mobility Function<br/>Container Instance - $567.90/month"]
                smf["📡 5g-smf<br/>Session Management Function<br/>Container Instance - $456.70/month"]
                upf["📡 5g-upf<br/>User Plane Function<br/>Container Instance - $789.20/month"]
                ausf["🔐 5g-ausf<br/>Authentication Server Function<br/>Container Instance - $234.50/month"]
            end
            
            subgraph dr_rg["🔄 Disaster Recovery RG"]
                sqldb_replica["💾 billing-database-replica<br/>SQL Database<br/>Read-Only Replica - $1,728.40/month"]
                storage_dr["💾 telecom-backup<br/>Storage Account (Cool)<br/>50TB - $867.30/month"]
                keyvault["🔐 telecom-hsm<br/>Key Vault HSM<br/>FIPS 140-2 Level 3 - $1,890.40/month"]
            end
        end
    end

    %% Connections
    cdn --> appgw
    appgw --> vmss_billing
    appgw --> vmss_crm
    vmss_billing --> redis_session
    vmss_crm --> redis_session
    vmss_billing --> sqldb_billing
    vmss_crm --> sqldb_customer
    sqldb_billing --> sqldb_replica
    expressroute --> vnet_hub
    vnet_hub --> vnet_spoke1
    vnet_hub --> vnet_spoke2
    amf --> smf
    smf --> upf
    ausf --> amf
```

**Monthly Cost Breakdown:**
- **Core Infrastructure:** $3,234.20/month
- **5G Network Functions:** $2,048.30/month  
- **Data & Analytics:** $9,254.50/month
- **Security & Compliance:** $2,708.60/month

---

### 📶 **AWS Telecom Network Operations Center**
*Auto-generated from AWS account scan - telecommunications industry dummy data*

```mermaid
%% CloudViz Auto-Generated Infrastructure Diagram
%% Scan Date: 2025-09-20 | Account: TELECOM-NOC-789012345678 | Resources: 31 | Monthly Cost: $12,450.80
flowchart TD
    subgraph aws["🟠 AWS Account: TELECOM-NOC-789012345678"]
        subgraph us_east_1["🌍 US-East-1 (Network Operations)"]
            subgraph monitoring_rg["📊 Network Monitoring"]
                cloudwatch["📈 telecom-monitoring<br/>CloudWatch Dashboard<br/>Custom Metrics - $234.50/month"]
                sns_alerts["📢 network-alerts<br/>SNS Topic<br/>Critical Alerts - $12.30/month"]
                lambda_telemetry["⚡ telemetry-processor<br/>Lambda Function<br/>Real-time Processing - $156.70/month"]
            end
            
            subgraph network_rg["🌐 Network Telemetry"]
                vpc_monitoring["🔗 monitoring-vpc<br/>VPC<br/>172.16.0.0/16"]
                nat_gateway["🌐 monitoring-nat<br/>NAT Gateway<br/>High Availability - $345.60/month"]
                ec2_collectors["💻 telemetry-collectors<br/>EC2 Auto Scaling Group<br/>5-20 instances - $2,456.80/month"]
                elb_network["⚖️ network-nlb<br/>Network Load Balancer<br/>Cross-AZ - $234.90/month"]
            end
            
            subgraph data_processing["🗄️ Network Data Processing"]
                kinesis_stream["🌊 network-telemetry<br/>Kinesis Data Stream<br/>100 shards - $1,234.60/month"]
                s3_data_lake["🪣 telecom-data-lake<br/>S3 Bucket<br/>500TB Intelligent Tiering - $3,456.70/month"]
                redshift["📊 network-analytics<br/>Redshift Cluster<br/>dc2.8xlarge x3 nodes - $2,890.40/month"]
                glue_etl["🔄 network-etl<br/>AWS Glue<br/>ETL Jobs - $567.80/month"]
            end
            
            subgraph iot_devices["📱 IoT Device Management"]
                iot_core["📡 telecom-iot-core<br/>IoT Core<br/>Device Registry - $234.70/month"]
                iot_device_mgmt["🔧 device-management<br/>IoT Device Management<br/>Fleet Management - $456.80/month"]
                timestream["⏰ network-metrics<br/>Amazon Timestream<br/>Time Series DB - $789.20/month"]
            end
        end

        subgraph us_west_2["🌍 US-West-2 (Edge Processing)"]
            subgraph edge_rg["🌐 Edge Computing"]
                wavelength["📡 wavelength-zone<br/>AWS Wavelength<br/>5G Edge - $1,234.50/month"]
                local_zones["🏢 local-zone-compute<br/>Local Zones<br/>EC2 Instances - $678.90/month"]
                outposts["🏭 telecom-outpost<br/>AWS Outposts<br/>42U Rack - $2,890.00/month"]
            end
        end

        subgraph global["🌐 Global Telecom Services"]
            route53["🌍 telecom-dns<br/>Route 53 Health Checks<br/>$45.00/month"]
            cloudfront["🚀 edge-cdn<br/>CloudFront Distribution<br/>Global Edge - $567.80/month"]
            direct_connect["⚡ direct-connect<br/>Direct Connect Gateway<br/>10Gbps - $1,456.90/month"]
        end
    end

    %% Data Flow
    iot_core --> kinesis_stream
    kinesis_stream --> lambda_telemetry
    lambda_telemetry --> timestream
    lambda_telemetry --> s3_data_lake
    s3_data_lake --> redshift
    s3_data_lake --> glue_etl
    ec2_collectors --> cloudwatch
    cloudwatch --> sns_alerts
    wavelength --> local_zones
    local_zones --> outposts
```

**Monthly Cost Breakdown:**
- **Network Monitoring:** $403.50/month
- **Data Processing:** $8,149.50/month
- **IoT & Edge:** $4,897.80/month

---

### 🔵 **GCP Network Edge & Analytics Platform**
*Auto-generated from GCP project scan - telecommunications edge computing dummy data*

```mermaid
%% CloudViz Auto-Generated Infrastructure Diagram  
%% Scan Date: 2025-09-20 | Project: telecom-edge-analytics-001 | Resources: 28 | Regions: 3 | Monthly Cost: $15,890.40
flowchart TD
    subgraph gcp["🔵 GCP Project: telecom-edge-analytics-001"]
        subgraph us_central1["🌍 US-Central1 (Analytics Hub)"]
            subgraph ml_rg["🤖 AI/ML Network Analytics"]
                vertex_ai["🧠 network-ml-platform<br/>Vertex AI Platform<br/>Custom Training - $2,345.60/month"]
                automl["🎯 traffic-prediction<br/>AutoML Tables<br/>Demand Forecasting - $1,234.50/month"]
                ai_platform["🔮 anomaly-detection<br/>AI Platform<br/>Real-time Inference - $1,567.80/month"]
            end
            
            subgraph data_rg["🗄️ Network Data Platform"]
                bigquery["📈 telecom-datawarehouse<br/>BigQuery Dataset<br/>15TB Active Storage<br/>$300.00/month"]
                dataflow["🌊 real-time-processing<br/>Dataflow<br/>Streaming Pipeline - $2,890.40/month"]
                pub_sub["📢 network-events<br/>Pub/Sub Topics<br/>High Throughput - $234.70/month"]
                cloud_sql["💾 network-metadata<br/>Cloud SQL PostgreSQL<br/>High Availability - $1,456.80/month"]
            end
            
            subgraph compute_rg["💻 Edge Compute Platform"]
                gke_cluster["☸️ edge-processing-cluster<br/>GKE Cluster<br/>12 nodes - $3,456.70/month"]
                cloud_run["🏃 network-functions<br/>Cloud Run Services<br/>Auto-scaling - $678.90/month"]
                functions["⚡ event-processors<br/>Cloud Functions<br/>Event-driven - $345.60/month"]
            end
        end

        subgraph asia_southeast1["🌍 Asia-Southeast1 (Edge)"]
            subgraph edge_asia["🌐 Asia Pacific Edge"]
                anthos_edge["🔗 anthos-edge-clusters<br/>Anthos on Bare Metal<br/>Edge Locations - $2,890.40/month"]
                cdn_asia["🚀 asia-cdn<br/>Cloud CDN<br/>Regional Cache - $456.80/month"]
            end
        end

        subgraph global_services["🌐 Global Telecom Services"]
            cloud_armor["🛡️ ddos-protection<br/>Cloud Armor<br/>WAF Rules - $234.50/month"]
            dns["🌍 telecom-dns<br/>Cloud DNS<br/>Managed Zones<br/>$23.40/month"]
            load_balancer["⚖️ global-lb<br/>Global Load Balancer<br/>Multi-region - $567.80/month"]
        end
    end

    %% Data Pipeline
    pub_sub --> dataflow
    dataflow --> bigquery
    dataflow --> vertex_ai
    vertex_ai --> ai_platform
    gke_cluster --> cloud_run
    cloud_run --> functions
    anthos_edge --> gke_cluster
```

**Monthly Cost Breakdown:**
- **AI/ML Analytics:** $5,147.90/month
- **Data Platform:** $4,882.00/month  
- **Edge Computing:** $4,536.10/month
- **Global Services:** $1,324.40/month

---

## 📊 **Multi-Cloud Cost Comparison Dashboard**

| **Cloud Provider** | **Resources** | **Monthly Cost** | **Primary Focus** | **Regions** |
|-------------------|---------------|------------------|-------------------|-------------|
| **🌟 Azure** | **28 resources** | **$11,245.60** | **5G Core + BSS/OSS** | **4 regions** |
| **🟠 AWS** | **31 resources** | **$12,450.80** | **Network Operations Center** | **3 regions** |  
| **🔵 GCP** | **28 resources** | **$15,890.40** | **Edge Analytics + AI/ML** | **4 regions** |
| **🌐 Total** | **87 resources** | **$39,586.80** | **Telecom multi-cloud architecture** | **11 regions** |

---

## 🚀 **Quick Start**

### 🐳 **Docker Deployment** (Recommended)

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

### 📦 **Local Development Setup**

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

### ☸️ **Kubernetes Deployment**

```bash
# Apply the Kubernetes manifests
kubectl apply -f examples/configurations/k8s-deployment.example.yaml

# Check deployment status
kubectl get pods -l app=cloudviz
```

---

## 🔌 **API Endpoints**

CloudViz provides a comprehensive REST API perfect for automation workflows:

### 🏥 **Health & Monitoring**
- `GET /health` - Service health check
- `GET /health/detailed` - Detailed system health
- `GET /metrics` - Prometheus metrics

### 🔐 **Authentication**  
- `POST /auth/token` - Get access token
- `POST /auth/refresh` - Refresh token
- `GET /auth/validate` - Validate token

### 🌩️ **Cloud Resource Discovery**
- `POST /extract/azure/subscription` - Scan Azure subscription
- `POST /extract/aws/account` - Scan AWS account  
- `POST /extract/gcp/project` - Scan GCP project
- `GET /extract/status/{job_id}` - Check extraction status

### 🎨 **Diagram Generation**
- `POST /visualize/mermaid` - Generate Mermaid diagram
- `POST /visualize/graphviz` - Generate Graphviz diagram
- `POST /visualize/architecture` - Auto-detect and visualize
- `GET /visualize/themes` - Available themes

### ⚙️ **Administration**
- `GET /admin/stats` - Platform statistics
- `POST /admin/cache/clear` - Clear cache
- `GET /admin/logs` - Recent logs

---

## 🔧 **n8n Integration Workflows**

CloudViz is designed for seamless n8n automation. Here are some powerful workflow examples:

### 📅 **Daily Infrastructure Discovery**
Automatically scan your cloud resources every day and generate fresh diagrams:

```json
{
  "name": "Daily Infrastructure Scan",
  "nodes": [
    {
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.cron",
      "parameters": {
        "triggerTimes": {
          "hour": 6,
          "minute": 0
        }
      }
    },
    {
      "name": "CloudViz Azure Scan", 
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://cloudviz:8000/extract/azure/subscription",
        "method": "POST"
      }
    },
    {
      "name": "Generate Diagram",
      "type": "n8n-nodes-base.httpRequest", 
      "parameters": {
        "url": "http://cloudviz:8000/visualize/mermaid",
        "method": "POST"
      }
    }
  ]
}
```

### 🚨 **Incident Response Diagram**
Automatically generate infrastructure diagrams during incidents:

```json
{
  "name": "Incident Response Infrastructure",
  "trigger": "webhook",
  "steps": [
    "Receive incident webhook",
    "Scan affected resource groups", 
    "Generate emergency infrastructure diagram",
    "Send to incident response team"
  ]
}
```

---

## 🔧 **Configuration**

CloudViz uses YAML configuration files for different environments:

```yaml
# config/prod.yml
api:
  host: "0.0.0.0"
  port: 8000
  workers: 4

azure:
  subscription_id: "${AZURE_SUBSCRIPTION_ID}"
  client_id: "${AZURE_CLIENT_ID}"
  client_secret: "${AZURE_CLIENT_SECRET}"
  tenant_id: "${AZURE_TENANT_ID}"

visualization:
  default_theme: "azure"
  cache_ttl: 3600
  max_resources: 1000
```

---

## 🎯 **Key Features**

### 🌩️ **Multi-Cloud Support**
- **Azure**: Complete ARM template discovery
- **AWS**: CloudFormation and direct API scanning  
- **GCP**: Resource Manager and service-specific APIs

### 🎨 **Visualization Engines**
- **Mermaid**: Interactive diagrams with live editing
- **Graphviz**: Publication-quality network diagrams
- **Custom themes**: Azure, AWS, GCP, and dark themes

### 🔌 **API-First Design**
- RESTful APIs for all operations
- OpenAPI 3.0 documentation
- Rate limiting and authentication
- Prometheus metrics integration

### ⚡ **Performance & Reliability**
- Async/await throughout the stack
- Redis caching for expensive operations
- Background job processing
- Comprehensive error handling

---

## 🧪 **Testing**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=cloudviz

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

---

## 📈 **Monitoring & Observability**

CloudViz includes comprehensive monitoring capabilities:

### 📊 **Metrics**
- Request duration and count
- Error rates by endpoint
- Cache hit/miss ratios
- Resource discovery performance

### 📝 **Logging** 
- Structured JSON logging
- Correlation IDs for tracing
- Configurable log levels
- Integration with ELK stack

### 🏥 **Health Checks**
- Deep health checks for dependencies
- Kubernetes-ready liveness/readiness probes
- Database connection monitoring

---

## 🤝 **Contributing**

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### 🛠️ **Development Setup**

```bash
# Clone and setup
git clone https://github.com/navidrast/cloudviz.git
cd cloudviz

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements/dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- [Mermaid](https://mermaid.js.org/) - Diagrams and flowcharts from text
- [Azure SDK](https://azure.github.io/azure-sdk-for-python/) - Azure Python SDK
- [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) - AWS SDK for Python
- [Google Cloud SDK](https://cloud.google.com/python) - Google Cloud Python SDK

---

<div align="center">

**Built with ❤️ for the DevOps and Cloud Infrastructure community**

[🌟 Star us on GitHub](https://github.com/navidrast/cloudviz) | [🐛 Report Issues](https://github.com/navidrast/cloudviz/issues) | [💬 Join Discussions](https://github.com/navidrast/cloudviz/discussions)

</div>
