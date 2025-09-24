# CloudViz - Multi-Cloud Infrastructure Visualization Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Mermaid](https://img.shields.io/badge/Mermaid-Diagrams-ff69b4.svg)](https://mermaid.js.org/)

**CloudViz** is an enterprise-grade, multi-cloud infrastructure visualization platform that automatically discovers cloud resources and generates beautiful, interactive diagrams. Built with FastAPI and featuring powerful Mermaid diagram generation, CloudViz provides REST APIs perfect for automation workflows.

## Key Features

- **Multi-Cloud Discovery**: Automatically scan Azure, AWS, and GCP resources with comprehensive resource mapping
- **Interactive Diagrams**: Generate Mermaid, Graphviz, and custom visualizations with real-time updates
- **REST API**: Complete API for automation and integration workflows with n8n, Jenkins, and CI/CD pipelines
- **Cost Analytics**: Track spending across cloud providers with detailed cost breakdowns and optimization recommendations
- **Security Analysis**: Identify security groups, firewall rules, and compliance violations across your infrastructure
- **Real-time Monitoring**: Live infrastructure change detection with webhook notifications
- **Multiple Export Formats**: Export diagrams as SVG, PNG, PDF, and interactive HTML with embedded data
- **Enterprise Ready**: Production deployment with Docker, Kubernetes, and comprehensive documentation

## Quick Start

### Option 1: Docker (Recommended)
```bash
git clone https://github.com/navidrast/cloudviz.git
cd cloudviz
cp .env.example .env
# Edit .env with your cloud provider credentials
docker compose up -d
```

### Option 2: Python Development
```bash
git clone https://github.com/navidrast/cloudviz.git
cd cloudviz
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
cp .env.example .env
# Edit .env with your cloud provider credentials
uvicorn cloudviz.api.main:app --reload
```

**Access CloudViz at**: http://localhost:8000  
**API Documentation**: http://localhost:8000/docs  
**Health Check**: http://localhost:8000/health

## Architecture Overview

CloudViz follows a modular, microservices architecture with clear separation of concerns:

```mermaid
flowchart TD
    CLIENT[Client Applications] --> API[FastAPI Gateway]
    API --> AUTH[Authentication Service]
    API --> EXTRACT[Resource Extraction Engine]
    API --> VIZ[Visualization Engine]
    API --> CACHE[Redis Cache]
    
    EXTRACT --> AZURE[Azure Provider]
    EXTRACT --> AWS[AWS Provider]
    EXTRACT --> GCP[GCP Provider]
    
    VIZ --> MERMAID[Mermaid Generator]
    VIZ --> GRAPHVIZ[Graphviz Engine]
    VIZ --> EXPORT[Export Service]
    
    API --> DB[(PostgreSQL)]
    CACHE --> DB
    
    EXPORT --> SVG[SVG Files]
    EXPORT --> PNG[PNG Images]
    EXPORT --> PDF[PDF Reports]
    EXPORT --> HTML[Interactive HTML]
```

## Sample Infrastructure Visualizations

### Azure Enterprise Architecture Example
CloudViz automatically generates comprehensive infrastructure diagrams like this Azure enterprise setup:

```mermaid
flowchart TD
    INTERNET[Internet Traffic] --> AZURE[Azure Cloud]
    
    AZURE --> NETWORK_TIER[Network Security Tier]
    AZURE --> APPLICATION_TIER[Application Tier]
    AZURE --> DATA_TIER[Data & Analytics Tier]
    AZURE --> SECURITY_TIER[Security & Compliance Tier]
    
    NETWORK_TIER --> firewall[Azure Firewall - $567/month]
    NETWORK_TIER --> appgw[Application Gateway - $234/month]
    NETWORK_TIER --> vnet[Virtual Network Hub]
    
    APPLICATION_TIER --> vmss_web[Web Tier VMSS - $1234/month]
    APPLICATION_TIER --> vmss_api[API Tier VMSS - $890/month]
    APPLICATION_TIER --> sf[Service Fabric - $445/month]
    APPLICATION_TIER --> redis[Redis Cache - $234/month]
    
    DATA_TIER --> sqldb[SQL Database - $1890/month]
    DATA_TIER --> cosmos[Cosmos DB - $567/month]
    DATA_TIER --> synapse[Synapse Analytics - $2340/month]
    DATA_TIER --> storage[Blob Storage - $123/month]
    
    SECURITY_TIER --> sentinel[Azure Sentinel - $890/month]
    SECURITY_TIER --> keyvault[Key Vault - $45/month]
    SECURITY_TIER --> backup[Backup Vault - $234/month]
    
    firewall --> appgw
    appgw --> vmss_web
    appgw --> vmss_api
    vmss_web --> redis
    vmss_api --> redis
    vmss_api --> sqldb
    vmss_api --> cosmos
    sqldb --> synapse
    cosmos --> synapse
    
    classDef networkClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef appClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef dataClass fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef securityClass fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    
    class NETWORK_TIER,firewall,appgw,vnet networkClass
    class APPLICATION_TIER,vmss_web,vmss_api,sf,redis appClass
    class DATA_TIER,sqldb,cosmos,synapse,storage dataClass
    class SECURITY_TIER,sentinel,keyvault,backup securityClass
```

### AWS Multi-Region Architecture Example
Example of AWS infrastructure with disaster recovery across multiple regions:

```mermaid
flowchart TD
    USERS[Global Users] --> CF[CloudFront CDN]
    CF --> ALB_PRIMARY[Primary ALB - us-east-1]
    CF --> ALB_DR[DR ALB - us-west-2]
    
    ALB_PRIMARY --> PRIMARY[Primary Region - us-east-1]
    ALB_DR --> DR[DR Region - us-west-2]
    
    PRIMARY --> EC2_PRIMARY[EC2 Auto Scaling - $1456/month]
    PRIMARY --> RDS_PRIMARY[RDS Aurora Primary - $2890/month]
    PRIMARY --> S3_PRIMARY[S3 Data Lake - $567/month]
    PRIMARY --> LAMBDA_PRIMARY[Lambda Functions - $234/month]
    
    DR --> EC2_DR[EC2 Standby - $728/month]
    DR --> RDS_DR[RDS Read Replica - $1445/month]
    DR --> S3_DR[S3 Cross-Region Backup - $283/month]
    
    EC2_PRIMARY --> RDS_PRIMARY
    LAMBDA_PRIMARY --> RDS_PRIMARY
    RDS_PRIMARY -.-> RDS_DR
    S3_PRIMARY -.-> S3_DR
    
    classDef primaryClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef drClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef globalClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    
    class PRIMARY,EC2_PRIMARY,RDS_PRIMARY,S3_PRIMARY,LAMBDA_PRIMARY primaryClass
    class DR,EC2_DR,RDS_DR,S3_DR drClass
    class USERS,CF globalClass
```

### Google Cloud Platform Example
GCP infrastructure with AI/ML components and container orchestration:

```mermaid
flowchart TD
    TRAFFIC[Global Traffic] --> LB[Global Load Balancer]
    LB --> GKE[GKE Autopilot Cluster - $3456/month]
    LB --> RUN[Cloud Run Services - $567/month]
    
    GKE --> VERTEX[Vertex AI Platform - $2890/month]
    GKE --> BIGQUERY[BigQuery Analytics - $1234/month]
    GKE --> PUBSUB[Pub/Sub Messaging - $345/month]
    
    RUN --> SQL[Cloud SQL PostgreSQL - $890/month]
    RUN --> REDIS[Memorystore Redis - $234/month]
    RUN --> STORAGE[Cloud Storage - $456/month]
    
    PUBSUB --> FUNCTIONS[Cloud Functions - $123/month]
    FUNCTIONS --> BIGQUERY
    VERTEX --> STORAGE
    
    classDef containerClass fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef aimlClass fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef dataClass fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    classDef computeClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    
    class GKE,RUN containerClass
    class VERTEX,BIGQUERY,PUBSUB,FUNCTIONS aimlClass
    class SQL,REDIS,STORAGE dataClass
    class TRAFFIC,LB computeClass
```

## Configuration

### Environment Variables
Copy `.env.example` to `.env` and configure your cloud provider credentials:

```bash
# Azure Configuration
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id  
AZURE_CLIENT_SECRET=your-client-secret
AZURE_SUBSCRIPTION_IDS=sub-1,sub-2,sub-3

# AWS Configuration
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=us-east-1
AWS_REGIONS=us-east-1,us-west-2,ap-southeast-2

# GCP Configuration
GCP_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
GCP_REGIONS=us-central1,australia-southeast1

# Application Configuration
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
CACHE_TTL=3600

# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost:5432/cloudviz
REDIS_URL=redis://localhost:6379

# Export Configuration
EXPORT_PATH=/tmp/cloudviz-exports
MERMAID_THEME=default
INCLUDE_COSTS=true
INCLUDE_DEPENDENCIES=true
```

### YAML Configuration
Advanced configuration via `config/production.yml`:

```yaml
api:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  cors_origins: ["*"]

cloud_providers:
  azure:
    enabled: true
    parallel_subscriptions: 3
    rate_limit: 100
    timeout: 300
  
  aws:
    enabled: true
    parallel_regions: 5
    rate_limit: 200
    timeout: 300
    
  gcp:
    enabled: true
    parallel_projects: 2
    rate_limit: 150
    timeout: 300

visualization:
  default_format: "mermaid"
  layout: "hierarchical"
  themes: ["default", "dark", "neutral", "forest"]
  include_costs: true
  include_dependencies: true
  max_nodes: 1000
  
cache:
  ttl: 3600
  max_memory: "1GB"
  eviction_policy: "lru"

monitoring:
  enable_metrics: true
  enable_tracing: true
  log_requests: true
```

## API Reference

### Resource Discovery Endpoints

#### Extract Azure Resources
```bash
curl -X POST "http://localhost:8000/api/v1/azure/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "subscription_ids": ["sub-12345", "sub-67890"],
    "resource_groups": ["production", "staging"],
    "include_costs": true,
    "webhook_url": "http://your-app/webhook/azure-complete"
  }'
```

#### Extract AWS Resources
```bash
curl -X POST "http://localhost:8000/api/v1/aws/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "account_ids": ["123456789012"],
    "regions": ["us-east-1", "us-west-2"],
    "services": ["ec2", "rds", "s3", "lambda"],
    "include_costs": true,
    "webhook_url": "http://your-app/webhook/aws-complete"
  }'
```

#### Extract GCP Resources
```bash
curl -X POST "http://localhost:8000/api/v1/gcp/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "project_ids": ["my-project-123"],
    "regions": ["us-central1", "australia-southeast1"],
    "services": ["compute", "gke", "sql", "storage"],
    "include_costs": true,
    "webhook_url": "http://your-app/webhook/gcp-complete"
  }'
```

### Visualization Endpoints

#### Generate Infrastructure Diagram
```bash
curl -X POST "http://localhost:8000/api/v1/visualization/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "providers": ["azure", "aws", "gcp"],
    "format": "mermaid",
    "layout": "hierarchical",
    "theme": "default",
    "include_costs": true,
    "include_dependencies": true,
    "filter_by_tags": ["environment:production"],
    "export_formats": ["svg", "png", "pdf"]
  }'
```

#### Export Diagram
```bash
curl -X GET "http://localhost:8000/api/v1/visualization/export/{diagram_id}" \
  -H "Accept: application/json" \
  -o "infrastructure-diagram.svg"
```

### Cost Analysis Endpoints

#### Get Multi-Cloud Cost Summary
```bash
curl -X GET "http://localhost:8000/api/v1/costs/summary" \
  -H "Content-Type: application/json"
```

Response:
```json
{
  "total_monthly_cost": 46909.00,
  "providers": {
    "azure": {
      "cost": 18567.80,
      "resources": 35,
      "regions": 2
    },
    "aws": {
      "cost": 12450.80,
      "resources": 31,
      "regions": 3
    },
    "gcp": {
      "cost": 15890.40,
      "resources": 28,
      "regions": 3
    }
  },
  "cost_breakdown": {
    "compute": 22000.00,
    "storage": 8900.00,
    "networking": 5600.00,
    "databases": 7200.00,
    "security": 3209.00
  }
}
```

## n8n Workflow Integration

CloudViz provides seamless integration with n8n automation workflows. Here's a complete workflow for automated infrastructure discovery and reporting:

```json
{
  "name": "CloudViz Daily Infrastructure Scan",
  "nodes": [
    {
      "name": "Schedule Daily Scan",
      "type": "Cron",
      "cron": "0 6 * * *",
      "timezone": "UTC"
    },
    {
      "name": "Scan Azure Infrastructure",
      "type": "HTTP Request",
      "url": "http://cloudviz-api:8000/api/v1/azure/extract",
      "method": "POST",
      "body": {
        "subscription_ids": "{{ $env.AZURE_SUBSCRIPTION_IDS.split(',') }}",
        "include_costs": true,
        "webhook_url": "http://n8n:5678/webhook/azure-complete"
      }
    },
    {
      "name": "Scan AWS Infrastructure", 
      "type": "HTTP Request",
      "url": "http://cloudviz-api:8000/api/v1/aws/extract",
      "method": "POST",
      "body": {
        "regions": "{{ $env.AWS_REGIONS.split(',') }}",
        "include_costs": true,
        "webhook_url": "http://n8n:5678/webhook/aws-complete"
      }
    },
    {
      "name": "Scan GCP Infrastructure",
      "type": "HTTP Request", 
      "url": "http://cloudviz-api:8000/api/v1/gcp/extract",
      "method": "POST",
      "body": {
        "project_ids": "{{ $env.GCP_PROJECT_IDS.split(',') }}",
        "include_costs": true,
        "webhook_url": "http://n8n:5678/webhook/gcp-complete"
      }
    },
    {
      "name": "Generate Infrastructure Diagram",
      "type": "HTTP Request",
      "url": "http://cloudviz-api:8000/api/v1/visualization/generate",
      "method": "POST",
      "body": {
        "providers": ["azure", "aws", "gcp"],
        "format": "mermaid",
        "include_costs": true,
        "export_formats": ["svg", "pdf"]
      }
    },
    {
      "name": "Send Daily Report",
      "type": "Email",
      "to": "infrastructure-team@company.com",
      "subject": "Daily Infrastructure Report - {{ $now.format('YYYY-MM-DD') }}",
      "attachments": [
        "{{ $node['Generate Infrastructure Diagram'].json.export_files.pdf }}"
      ]
    }
  ]
}
```

## Multi-Cloud Cost Analysis

CloudViz provides comprehensive cost analysis across all cloud providers:

### Cost Optimization Recommendations
- **Azure**: Identify underutilized VM Scale Sets and recommend reserved instances
- **AWS**: Detect oversized EC2 instances and suggest spot instances for development workloads  
- **GCP**: Analyze Compute Engine usage patterns and recommend sustained use discounts

### Cost Alerting
Set up automated cost alerts when spending exceeds thresholds:

```bash
curl -X POST "http://localhost:8000/api/v1/alerts/cost" \
  -H "Content-Type: application/json" \
  -d '{
    "threshold": 50000,
    "period": "monthly",
    "providers": ["azure", "aws", "gcp"],
    "webhook_url": "http://your-app/webhook/cost-alert"
  }'
```

## Security and Compliance

### Security Analysis Features
- **Network Security Groups**: Analyze firewall rules and identify open ports
- **IAM Policies**: Review access permissions and identify overprivileged accounts
- **Encryption Status**: Check encryption at rest and in transit across all resources
- **Compliance Frameworks**: SOC2, PCI-DSS, HIPAA compliance checking

### Security Diagram Example
```mermaid
flowchart TD
    INTERNET[Internet] --> WAF[Web Application Firewall]
    WAF --> ALB[Application Load Balancer]
    ALB --> PRIVATE[Private Subnets]
    
    PRIVATE --> APP[Application Servers]
    PRIVATE --> DB[Database Servers]
    
    APP --> VAULT[Key Management]
    DB --> VAULT
    APP --> LOG[Security Logging]
    DB --> LOG
    
    classDef secure fill:#e8f5e8,stroke:#388e3c,stroke-width:3px
    classDef network fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef data fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    
    class WAF,VAULT,LOG secure
    class INTERNET,ALB,PRIVATE network
    class APP,DB data
```

## Development and Testing

### Local Development Setup
```bash
# Clone repository
git clone https://github.com/navidrast/cloudviz.git
cd cloudviz

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/ -v --cov=cloudviz

# Run linting
black cloudviz/
isort cloudviz/
flake8 cloudviz/
mypy cloudviz/

# Start development server
uvicorn cloudviz.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing Framework
```bash
# Run all tests
pytest

# Run unit tests
pytest tests/unit/

# Run tests with coverage
pytest --cov=cloudviz --cov-report=html
```

### Project Structure
```
cloudviz/
├── api/                    # FastAPI application
│   ├── main.py            # Application entry point
│   ├── routes/            # API route handlers
│   ├── middleware.py      # Custom middleware
│   └── dependencies.py    # Dependency injection
├── core/                   # Core business logic
│   ├── config.py          # Configuration management
│   ├── models.py          # Data models
│   └── utils/             # Shared utilities
├── providers/              # Cloud provider integrations
│   ├── azure/             # Azure resource extraction
│   ├── aws/               # AWS resource extraction
│   └── gcp/               # GCP resource extraction
├── visualization/          # Diagram generation
│   ├── engines/           # Rendering engines
│   ├── exporters.py       # Export functionality
│   ├── layouts.py         # Layout algorithms
│   └── themes.py          # Visual themes
├── tests/                  # Test suite
│   └── unit/              # Unit tests
├── docs/                   # Documentation
├── examples/              # Usage examples
└── scripts/               # Utility scripts
```

## Documentation

- **[Installation Guide](docs/wiki/Installation-Guide.md)** - Complete setup instructions
- **[API Reference](docs/wiki/API-Reference.md)** - Complete API documentation  
- **[Configuration](docs/wiki/Configuration.md)** - Configuration options and examples
- **[Production Deployment](docs/PRODUCTION-DEPLOYMENT.md)** - Production setup guide
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[n8n Integration](docs/wiki/n8n-Integration.md)** - Automation workflow examples
- **[System Architecture](docs/wiki/System-Architecture.md)** - Technical architecture details
- **[Contributing Guide](CONTRIBUTING.md)** - Development guidelines

## Production Deployment

### Docker Compose Production
```yaml
version: '3.8'
services:
  cloudviz-api:
    image: cloudviz:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/cloudviz
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: cloudviz
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
      
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cloudviz-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cloudviz-api
  template:
    metadata:
      labels:
        app: cloudviz-api
    spec:
      containers:
      - name: cloudviz-api
        image: cloudviz:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: cloudviz-secrets
              key: database-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
```

## Contributing

We welcome contributions! Please follow these guidelines:

### Getting Started
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Install development dependencies (`pip install -e ".[dev]"`)
4. Make your changes
5. Add tests for new functionality
6. Run the test suite (`pytest`)
7. Run linting (`black . && isort . && flake8`)
8. Commit your changes (`git commit -m 'Add amazing feature'`)
9. Push to the branch (`git push origin feature/amazing-feature`)
10. Open a Pull Request

### Code Standards
- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write comprehensive docstrings
- Maintain test coverage above 85%
- Update documentation for new features

### Pull Request Process
1. Update documentation if needed
2. Add tests for new functionality
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Request review from maintainers

## Support and Community

- **Documentation**: [docs/](docs/)
- **GitHub Issues**: [Issues](https://github.com/navidrast/cloudviz/issues)
- **API Documentation**: http://localhost:8000/docs (when running)
- **Community Forum**: [GitHub Discussions](https://github.com/navidrast/cloudviz/discussions)
- **Security Issues**: Email security@cloudviz.com

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) for high-performance APIs
- Visualization powered by [Mermaid](https://mermaid.js.org/) and [Graphviz](https://graphviz.org/)
- Cloud integrations using official SDKs: [Azure SDK](https://azure.microsoft.com/en-us/downloads/), [AWS SDK](https://aws.amazon.com/tools/), [Google Cloud SDK](https://cloud.google.com/sdk)
- Special thanks to the open-source community for their contributions

## Support This Project

If CloudViz has helped you visualize and manage your cloud infrastructure, consider supporting the project:

<a href="https://buymeacoffee.com/caveguru" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 40px !important;width: 144px !important;" ></a>

Your support helps maintain and improve CloudViz for the entire community!

---

**CloudViz - Professional multi-cloud infrastructure visualization for the enterprise**
