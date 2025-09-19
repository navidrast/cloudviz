import os

readme_content = """# CloudViz - Enterprise Multi-Cloud Infrastructure Visualization Platform

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Multi-Cloud](https://img.shields.io/badge/Multi--Cloud-Azure%20%7C%20AWS%20%7C%20GCP-brightgreen?style=flat-square)](https://github.com/navidrast/cloudviz)
[![Enterprise](https://img.shields.io/badge/Enterprise-Ready-gold?style=flat-square)](https://github.com/navidrast/cloudviz)

🏢 **Professional cloud infrastructure visualization and dependency mapping for enterprise environments**

## 🌟 Enterprise Features

- **🔍 Multi-Cloud Discovery**: Comprehensive resource extraction across Azure, AWS, and GCP
- **🌐 Dependency Mapping**: Real connectivity, data flows, and service relationships
- **🎨 Beautiful Visualizations**: Portal-style colors matching official cloud interfaces
- **🏗️ Network Topology**: VPC peering, ExpressRoute, Direct Connect visualization
- **🔒 Security Analysis**: NSG rules, firewall policies, and access control mapping
- **📊 Real-time Analytics**: Live infrastructure monitoring and change detection
- **🌏 Australian Regions**: Optimized for AU-East, AU-Southeast deployments

## 🎯 Core Capabilities

### Multi-Cloud Resource Discovery
```bash
# Discover all resources across clouds
cloudviz discover --clouds azure,aws,gcp --regions au-east-1,australia-southeast
```

### Enterprise Dependency Mapping
- **Network Dependencies**: VPC connections, private endpoints, ExpressRoute circuits
- **Data Dependencies**: ETL pipelines, streaming flows, database relationships  
- **Security Dependencies**: Firewall rules, NSG policies, identity mappings
- **Service Dependencies**: API calls, microservice mesh, load balancer routing
- **Management Dependencies**: Monitoring, logging, alerting relationships
- **Disaster Recovery**: Geo-replication, backup policies, site recovery flows

### Real Infrastructure Examples

#### Azure Enterprise Architecture (67 Dependencies)
```mermaid
graph TB
    subgraph "Australia East"
        AZ_RG1[Resource Group: Production]
        AZ_VNET1[VNet: prod-network]
        AZ_VM1[VM: web-server-01]
        AZ_LB1[Load Balancer: prod-lb]
        AZ_NSG1[NSG: web-tier-security]
        AZ_KV1[Key Vault: prod-secrets]
        AZ_SQL1[SQL Database: customer-db]
        AZ_STORAGE1[Storage: backup-storage]
    end
    
    subgraph "Australia Southeast"
        AZ_RG2[Resource Group: DR-Site]
        AZ_VNET2[VNet: dr-network]
        AZ_VM2[VM: web-server-dr]
        AZ_SQL2[SQL Database: customer-db-dr]
    end
    
    %% Network Connectivity
    AZ_VNET1 -.->|VNet Peering| AZ_VNET2
    AZ_LB1 -->|Routes Traffic| AZ_VM1
    AZ_VM1 -.->|Connects To| AZ_SQL1
    
    %% Security Dependencies  
    AZ_NSG1 -.->|Protects| AZ_VM1
    AZ_KV1 -.->|Provides Secrets| AZ_VM1
    
    %% Data Dependencies
    AZ_SQL1 ==>|Geo-Replication| AZ_SQL2
    AZ_STORAGE1 ==>|Backup| AZ_SQL1
    
    %% Management Dependencies
    AZ_VM1 -.->|Monitored By| AZ_INSIGHTS[Application Insights]
    AZ_VM2 -.->|Monitored By| AZ_INSIGHTS
    
    classDef azure fill:#0078d4,stroke:#005a9e,color:#fff
    classDef network fill:#00bcf2,stroke:#0078d4,color:#fff
    classDef security fill:#ff6b35,stroke:#d63384,color:#fff
    classDef data fill:#20c997,stroke:#198754,color:#fff
```

#### AWS Enterprise Architecture (89 Dependencies)
```mermaid
graph TB
    subgraph "AP-Southeast-2 (Sydney)"
        AWS_VPC1[VPC: production-vpc]
        AWS_IGW1[Internet Gateway]
        AWS_ALB1[Application Load Balancer]
        AWS_EC2_1[EC2: web-server-01]
        AWS_EC2_2[EC2: web-server-02]
        AWS_RDS1[RDS: customer-database]
        AWS_S3_1[S3: application-data]
        AWS_CF1[CloudFront Distribution]
        AWS_R53[Route 53: company.com.au]
        AWS_SG1[Security Group: web-tier]
        AWS_SG2[Security Group: database-tier]
        AWS_NAT1[NAT Gateway]
        AWS_SUBNET_PUB[Public Subnet]
        AWS_SUBNET_PRIV[Private Subnet]
        AWS_SUBNET_DB[Database Subnet]
    end
    
    subgraph "AP-Southeast-1 (Singapore) - DR"
        AWS_VPC2[VPC: disaster-recovery]
        AWS_RDS2[RDS: customer-database-dr]
        AWS_S3_2[S3: backup-data]
    end
    
    %% Network Connectivity (Internet → CDN → Load Balancer → Web Tier)
    INTERNET[Internet Users] -->|HTTPS| AWS_CF1
    AWS_CF1 -->|Routes to| AWS_ALB1
    AWS_IGW1 -->|Internet Access| AWS_VPC1
    AWS_ALB1 -->|Distributes Load| AWS_EC2_1
    AWS_ALB1 -->|Distributes Load| AWS_EC2_2
    AWS_R53 -->|DNS Resolution| AWS_CF1
    
    %% Data Dependencies (Streams → ETL → Data Lake → Analytics)
    AWS_EC2_1 -.->|Database Connection| AWS_RDS1
    AWS_EC2_2 -.->|Database Connection| AWS_RDS1
    AWS_EC2_1 -.->|File Storage| AWS_S3_1
    AWS_EC2_2 -.->|File Storage| AWS_S3_1
    
    %% Security Dependencies (NSGs, Firewalls, Private Endpoints)
    AWS_SG1 -.->|Protects| AWS_EC2_1
    AWS_SG1 -.->|Protects| AWS_EC2_2
    AWS_SG2 -.->|Protects| AWS_RDS1
    
    %% Network Architecture
    AWS_VPC1 -->|Contains| AWS_SUBNET_PUB
    AWS_VPC1 -->|Contains| AWS_SUBNET_PRIV
    AWS_VPC1 -->|Contains| AWS_SUBNET_DB
    AWS_EC2_1 -.->|Deployed In| AWS_SUBNET_PRIV
    AWS_EC2_2 -.->|Deployed In| AWS_SUBNET_PRIV
    AWS_RDS1 -.->|Deployed In| AWS_SUBNET_DB
    AWS_ALB1 -.->|Deployed In| AWS_SUBNET_PUB
    AWS_NAT1 -.->|Provides Internet| AWS_SUBNET_PRIV
    
    %% Cross-Region Disaster Recovery
    AWS_VPC1 -.->|VPC Peering| AWS_VPC2
    AWS_RDS1 ==>|Read Replica| AWS_RDS2
    AWS_S3_1 ==>|Cross-Region Replication| AWS_S3_2
    
    %% Container Orchestration Dependencies (AKS, ECS, EKS)
    AWS_ECS[ECS Cluster] -.->|Runs On| AWS_EC2_1
    AWS_ECS -.->|Runs On| AWS_EC2_2
    AWS_ECS -.->|Service Discovery| AWS_R53
    
    classDef aws fill:#ff9900,stroke:#cc7a00,color:#fff
    classDef network fill:#4a90e2,stroke:#2e5c8a,color:#fff
    classDef security fill:#e74c3c,stroke:#c0392b,color:#fff
    classDef data fill:#2ecc71,stroke:#27ae60,color:#fff
    classDef compute fill:#9b59b6,stroke:#8e44ad,color:#fff
```

## 🚀 Quick Start

### Installation
```bash
# Clone the repository
git clone https://github.com/navidrast/cloudviz.git
cd cloudviz

# Install dependencies
pip install -r requirements.txt

# Start the API server
uvicorn cloudviz.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Enterprise Configuration
```yaml
# config/prod.yml
cloud_providers:
  azure:
    enabled: true
    regions: ["australiaeast", "australiasoutheast"]
    resource_groups: ["production", "staging", "development"]
  
  aws:
    enabled: true
    regions: ["ap-southeast-2", "ap-southeast-1"]
    
  gcp:
    enabled: true
    regions: ["australia-southeast1", "australia-southeast2"]

visualization:
  theme: "enterprise"
  colors:
    azure: "#0078d4"
    aws: "#ff9900"  
    gcp: "#4285f4"
  
dependencies:
  network_flows: true
  data_pipelines: true
  security_policies: true
  disaster_recovery: true
```

## 🔧 Advanced Features

### Real Connectivity Mapping
- **VPC Peering**: Cross-region network connections
- **ExpressRoute/Direct Connect**: Hybrid cloud connectivity  
- **Private Endpoints**: Secure service connections
- **API Gateway**: Microservice routing and policies

### Data Flow Analysis
- **ETL Pipelines**: Data transformation workflows
- **Streaming**: Real-time data flows (Kafka, Event Hubs)
- **Database Relationships**: Primary/foreign key mappings
- **Backup Flows**: Disaster recovery data paths

### Security Visualization
- **Network Security Groups**: Firewall rule visualization
- **Identity Mappings**: RBAC and access control
- **Compliance Boundaries**: Regulatory requirement mapping
- **Threat Modeling**: Security risk visualization

## 📊 Visualization Engines

### Mermaid Engine (8 Relationship Types)
- `CONTAINS` (-->) : Resource containment
- `CONNECTS_TO` (-.-) : Network connections  
- `DEPENDS_ON` (==>) : Service dependencies
- `MANAGED_BY` (-.->): Management relationships
- `SECURED_BY` (-.-): Security policies
- `ROUTES_TO` (-->): Traffic routing
- `REPLICATES_TO` (==>): Data replication
- `BACKS_UP_TO` (==>): Backup relationships

### Export Formats
- **Mermaid**: Interactive web diagrams
- **GraphViz**: Professional network topology
- **PNG/SVG**: High-resolution images
- **PDF**: Enterprise documentation
- **JSON**: API integration format

## 🌏 Australian Cloud Regions

### Azure Australia
- **Australia East** (Sydney): Primary production workloads
- **Australia Southeast** (Melbourne): Disaster recovery site
- **Australia Central** (Canberra): Government/compliance workloads

### AWS Asia Pacific
- **ap-southeast-2** (Sydney): Primary production region
- **ap-southeast-1** (Singapore): Disaster recovery region

### GCP Australia
- **australia-southeast1** (Sydney): Primary production zone
- **australia-southeast2** (Melbourne): Secondary availability zone

## 🎨 Portal-Style Colors

### Minimal Enterprise Theme
```css
/* Azure Services */
.azure { color: #0078d4; }      /* Azure Blue */
.azure-network { color: #00bcf2; } /* Light Blue */

/* AWS Services */  
.aws { color: #ff9900; }        /* AWS Orange */
.aws-compute { color: #f79400; } /* Darker Orange */

/* GCP Services */
.gcp { color: #4285f4; }        /* Google Blue */
.gcp-data { color: #34a853; }   /* Google Green */
```

## 📈 Enterprise Benefits

- **🔍 Visibility**: Complete infrastructure overview across all clouds
- **💰 Cost Optimization**: Identify unused and redundant resources
- **🔒 Security Compliance**: Visualize security policies and gaps
- **⚡ Performance**: Optimize network paths and dependencies
- **📋 Documentation**: Auto-generated architecture documentation
- **🚨 Incident Response**: Rapid dependency impact analysis

---

**🌟 Professional multi-cloud infrastructure visualization for enterprise environments**

[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/navidrast/cloudviz?style=flat-square)](https://github.com/navidrast/cloudviz/stargazers)
[![Enterprise Ready](https://img.shields.io/badge/Enterprise-Ready-gold?style=flat-square)](https://github.com/navidrast/cloudviz)"""

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme_content)

print("README.md created successfully!")
