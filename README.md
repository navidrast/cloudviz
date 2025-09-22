# CloudViz - Multi-Cloud Infrastructure Visualization Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Mermaid](https://img.shields.io/badge/Mermaid-Diagrams-ff69b4.svg)](https://mermaid.js.org/)

**CloudViz** is an enterprise-grade, multi-cloud infrastructure visualization platform that automatically discovers cloud resources and generates beautiful, interactive diagrams. Built with FastAPI and featuring powerful Mermaid diagram generation, CloudViz provides REST APIs perfect for automation workflows.

## Key Features

- **Multi-Cloud Discovery**: Automatically scan Azure, AWS, and GCP resources
- **Interactive Diagrams**: Generate Mermaid, Graphviz, and custom visualizations  
- **REST API**: Complete API for automation and integration workflows
- **n8n Integration**: Pre-built workflows for automation platforms
- **Enterprise Ready**: Production deployment with Docker and comprehensive documentation
- **Multiple Formats**: Export diagrams as SVG, PNG, PDF, and interactive HTML

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

## Requirements

- **Python**: 3.8 or higher
- **Cloud Access**: Valid credentials for Azure, AWS, or GCP
- **Docker**: For containerized deployment (optional)
- **Node.js**: For Mermaid diagram generation (optional)

## Architecture

CloudViz follows a modular architecture with clear separation of concerns:

- **API Layer**: FastAPI-based REST API
- **Extraction Engine**: Multi-cloud resource discovery
- **Visualization Engine**: Diagram generation and rendering
- **Storage Layer**: PostgreSQL for persistence, Redis for caching

## Configuration

Copy `.env.example` to `.env` and configure your cloud provider credentials:

```bash
# Azure
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id  
AZURE_CLIENT_SECRET=your-client-secret

# AWS
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=us-east-1

# GCP
GCP_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

## API Usage

### Extract Infrastructure
```bash
# Extract Azure resources
curl -X POST "http://localhost:8000/api/v1/extract/azure" \
  -H "Content-Type: application/json" \
  -d '{"subscription_ids": ["your-subscription-id"]}'

# Extract AWS resources  
curl -X POST "http://localhost:8000/api/v1/extract/aws" \
  -H "Content-Type: application/json" \
  -d '{"regions": ["us-east-1", "us-west-2"]}'
```

### Generate Diagrams
```bash
# Generate Mermaid diagram
curl -X POST "http://localhost:8000/api/v1/render/mermaid" \
  -H "Content-Type: application/json" \
  -d '{"inventory_file": "inventory.json", "layout": "hierarchical"}'
```

## Documentation

- **[Installation Guide](docs/wiki/Installation-Guide.md)** - Complete setup instructions
- **[API Reference](docs/wiki/API-Reference.md)** - Complete API documentation  
- **[Configuration](docs/wiki/Configuration.md)** - Configuration options
- **[Production Deployment](docs/PRODUCTION-DEPLOYMENT.md)** - Production setup guide
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[n8n Integration](docs/wiki/n8n-Integration.md)** - Automation workflows

## Multi-Cloud Architecture Examples

CloudViz can generate comprehensive infrastructure diagrams for complex multi-cloud environments. Here are some examples of what the platform can visualize:

### Azure Enterprise Architecture
- Resource Groups and Subscriptions
- Virtual Networks and Subnets
- Application Gateways and Load Balancers
- VM Scale Sets and Service Fabric
- SQL Database with Synapse Analytics
- Security services (Sentinel, Key Vault)
- Disaster Recovery configurations

### AWS Hierarchical Architecture
- Multi-region deployments
- Auto Scaling Groups and ECS clusters
- RDS Aurora with read replicas
- Lambda functions and API Gateway
- CloudFront and Route 53
- Cross-region disaster recovery

### Google Cloud Platform
- GKE clusters and Cloud Run services
- Vertex AI and BigQuery analytics
- Pub/Sub messaging and Cloud Functions
- Multi-region storage and backup
- Cloud Armor security policies

## n8n Workflow Integration

CloudViz provides seamless integration with n8n automation workflows for:

- **Scheduled Infrastructure Scans**: Daily discovery of new resources
- **Change Detection**: Monitor infrastructure changes and send alerts
- **Cost Monitoring**: Track spend across multiple cloud providers
- **Compliance Reporting**: Generate regular compliance and security reports
- **Incident Response**: Automated diagram generation during outages

## Development

### Local Development Setup
```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run linting
black cloudviz/
isort cloudviz/
flake8 cloudviz/
```

### Project Structure
```
cloudviz/
├── api/           # FastAPI application
├── core/          # Core business logic
├── providers/     # Cloud provider integrations
├── visualization/ # Diagram generation
└── utils/         # Shared utilities
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/navidrast/cloudviz/issues)
- **API Docs**: http://localhost:8000/docs (when running)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**CloudViz - Professional multi-cloud infrastructure visualization for the enterprise**
