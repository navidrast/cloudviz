# CloudViz Wiki - Home

Welcome to the **CloudViz** comprehensive documentation wiki!

CloudViz is an enterprise-grade, multi-cloud infrastructure visualization platform that automatically discovers cloud resources and generates beautiful, interactive diagrams. Built with FastAPI and featuring powerful Mermaid diagram generation, CloudViz provides REST APIs perfect for automation workflows.

## Documentation Navigation

### Getting Started
- [Installation Guide](Installation-Guide) - Complete setup instructions
- [Quick Start](Quick-Start) - Get CloudViz running in 5 minutes  
- [Configuration](Configuration) - Environment and settings configuration

### Architecture & Development
- [System Architecture](System-Architecture) - Technical architecture overview
- [API Reference](API-Reference) - Complete REST API documentation
- [Security](Security) - Authentication, authorization, and security features

### Cloud Providers
- [Azure Integration](Azure-Integration) - Azure resource discovery and visualization
- [AWS Integration](AWS-Integration) - AWS resource discovery and visualization  
- [GCP Integration](GCP-Integration) - Google Cloud Platform integration
- [Multi-Cloud Setup](Multi-Cloud-Setup) - Managing multiple cloud providers

### Automation & Integration
- [n8n Integration](n8n-Integration) - Workflow automation with n8n
- [CI/CD Pipelines](CI-CD-Pipelines) - DevOps integration and automation
- [Monitoring](Monitoring) - System monitoring and observability

### Administration
- [User Management](User-Management) - User roles and permissions
- [Troubleshooting](Troubleshooting) - Common issues and solutions

---

## Key Features Overview

### Multi-Cloud Discovery
- **Azure**: VM Scale Sets, SQL Database, Service Fabric, Synapse Analytics
- **AWS**: EC2, RDS Aurora, Lambda, ECS, CloudFormation stacks
- **GCP**: GKE, Vertex AI, BigQuery, Cloud Run, Compute Engine
- **Enterprise Scale**: Support for large infrastructures across multiple regions

### Advanced Visualization
- **Hierarchical Diagrams**: Top-down infrastructure organization
- **Cost Analytics**: Real-time cost tracking and optimization
- **Dependency Mapping**: Complete service relationship visualization
- **Security Analysis**: Network security groups and firewall rules
- **Export Formats**: Mermaid, PNG, SVG, PDF, JSON

### Enterprise Automation
- **n8n Integration**: Workflow templates for automation
- **REST API**: Complete programmatic control
- **Webhook Support**: Real-time notifications and triggers
- **Background Jobs**: Async processing for large infrastructures
- **CI/CD Ready**: Jenkins, GitHub Actions, Azure DevOps integration

### Enterprise Security
- **JWT Authentication**: Token-based security
- **RBAC**: Role-based access control
- **Audit Logging**: Complete activity tracking
- **API Rate Limiting**: Protection against abuse
- **Secret Management**: Secure credential handling

---

## System Overview

| Component | Technology | Purpose |
|-----------|------------|---------|
| **API Server** | FastAPI + Python 3.8+ | REST API and business logic |
| **Visualization** | Mermaid.js + Custom Themes | Diagram generation and rendering |
| **Database** | PostgreSQL/SQLite | Resource metadata and configuration |
| **Cache** | Redis | Performance optimization |
| **Queue** | Celery + Redis | Background job processing |
| **Authentication** | JWT + OAuth2 | Security and user management |
| **Monitoring** | Prometheus + Grafana | System observability |

---

## Quick Navigation

### For Developers
- [Development Setup](Development-Setup)
- [Testing Guide](Testing-Guide)  
- [Contributing](Contributing)
- [Bug Reports](Bug-Reports)

### For System Administrators
- [Production Deployment](Production-Deployment)
- [Monitoring Setup](Monitoring-Setup)
- [Security Configuration](Security-Configuration)
- [Scaling Guide](Scaling-Guide)

### For End Users
- [Getting Started](User-Getting-Started)
- [Dashboard Guide](Dashboard-Guide)
- [Creating Diagrams](Creating-Diagrams)
- [Exporting Results](Exporting-Results)

---

## Community & Support

- **Documentation**: This wiki and inline code documentation
- **Issues**: [GitHub Issues](https://github.com/navidrast/cloudviz/issues)
- **Discussions**: [GitHub Discussions](https://github.com/navidrast/cloudviz/discussions)  
- **Email**: For enterprise support inquiries
- **Updates**: Follow repository for latest features and updates

---

## Recent Updates

- **Hierarchical Mermaid Diagrams** - Improved visualization layout
- **Enhanced Documentation** - Comprehensive README and wiki
- **n8n Integration** - Complete workflow automation examples
- **Multi-Cloud Support** - Azure, AWS, and GCP integration ready
- **Professional Formatting** - Emoji-free, enterprise-ready documentation

---

**Ready to visualize your cloud infrastructure?** Start with our [Quick Start Guide](Quick-Start) or explore the [API Reference](API-Reference) for advanced usage!

---

*Last Updated: September 22, 2025*
*CloudViz Version: 1.2.0-enterprise*
