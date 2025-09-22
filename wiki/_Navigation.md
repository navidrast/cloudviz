# Wiki Navigation Index

Welcome to the CloudViz Wiki! This comprehensive documentation covers everything you need to know about deploying, configuring, and using CloudViz for enterprise multi-cloud infrastructure visualization.

## 📖 Documentation Overview

### 🏁 Quick Start
- **[Home](Home)** - Project overview, key features, and quick navigation
- **[Getting Started](Getting-Started)** - Installation, setup, and first steps with CloudViz

### 📚 Core Documentation
- **[API Documentation](API-Documentation)** - Complete REST API reference with examples
- **[Architecture](Architecture)** - System design, components, and data flow
- **[Configuration](Configuration)** - Environment variables, YAML configs, and secrets management

### ☁️ Cloud Integration
- **[Cloud Providers](Cloud-Providers)** - Azure, AWS, GCP integration guides and authentication
- **[Visualization](Visualization)** - Mermaid diagrams, themes, layouts, and export options

### 🔧 Integration & Automation
- **[n8n Integration](n8n-Integration)** - Workflow automation, pre-built workflows, and custom integrations
- **[Deployment](Deployment)** - Docker, Kubernetes, cloud platforms, and production setup

### 🛠️ Development & Support
- **[Development](Development)** - Contributing, testing, extending CloudViz, and development environment
- **[Troubleshooting](Troubleshooting)** - Common issues, debugging, and diagnostic tools
- **[Examples](Examples)** - Real-world use cases, industry examples, and integration patterns

## 🎯 Common Tasks

### First Time Setup
1. [Install CloudViz](Getting-Started#installation) 
2. [Configure cloud authentication](Cloud-Providers#authentication-setup)
3. [Start the API server](Getting-Started#step-4-start-the-api-server)
4. [Generate your first diagram](Getting-Started#generate-your-first-diagram)

### Production Deployment
1. [Choose deployment method](Deployment#deployment-options)
2. [Configure environment](Configuration#environment-variables)
3. [Set up monitoring](Deployment#monitoring--health-checks)
4. [Configure security](Configuration#secrets-management)

### API Integration
1. [Authentication setup](API-Documentation#authentication)
2. [Resource discovery](API-Documentation#discover-resources)
3. [Diagram generation](API-Documentation#generate-mermaid-diagram)
4. [Export options](API-Documentation#generate-png-diagram)

### Automation Setup
1. [Install n8n](n8n-Integration#prerequisites)
2. [Import workflows](n8n-Integration#pre-built-workflows)
3. [Configure webhooks](n8n-Integration#custom-workflow-development)
4. [Set up notifications](n8n-Integration#notification-integrations)

## 🔍 Quick Reference

### Essential URLs (when running locally)
- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **OpenAPI Spec**: http://localhost:8000/openapi.json

### Key API Endpoints
```bash
# Health check
GET /health

# Resource discovery
GET /api/v1/azure/resources
GET /api/v1/aws/resources
GET /api/v1/gcp/resources

# Diagram generation
POST /api/v1/diagrams/mermaid
POST /api/v1/diagrams/mermaid/png
POST /api/v1/diagrams/mermaid/svg

# System information
GET /api/v1/system/status
GET /api/v1/system/metrics
```

### Common Configuration
```yaml
# Minimal configuration
cloud_providers:
  azure:
    enabled: true
    client_id: "${AZURE_CLIENT_ID}"
    client_secret: "${AZURE_CLIENT_SECRET}"
    tenant_id: "${AZURE_TENANT_ID}"

visualization:
  default_theme: "enterprise"
  include_costs: true
```

### Quick Commands
```bash
# Start development server
uvicorn cloudviz.api.main:app --reload

# Run with Docker
docker-compose up -d

# Health check
curl http://localhost:8000/health

# Discover resources
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8000/api/v1/azure/resources"
```

## 🏷️ Topics by Category

### 🔐 Security & Compliance
- [Authentication setup](Cloud-Providers#authentication-setup)
- [JWT configuration](Configuration#security-environment-variables)
- [Secrets management](Configuration#secrets-management)
- [Security themes](Visualization#security-theme)
- [Compliance examples](Examples#financial-services---compliance--security)

### 💰 Cost Management
- [Cost analysis](Cloud-Providers#cost-integration)
- [Cost themes](Visualization#cost-theme)
- [Cost monitoring workflows](Examples#cost-optimization-workflows)
- [Cost optimization examples](Examples#e-commerce---cost-optimization)

### 🎨 Visualization
- [Available themes](Visualization#themes)
- [Custom themes](Visualization#custom-themes)
- [Export formats](Visualization#export-options)
- [Dynamic diagrams](Visualization#dynamic-diagrams)

### 🔄 Automation
- [n8n workflows](n8n-Integration#pre-built-workflows)
- [Background jobs](API-Documentation#background-jobs)
- [Webhook integration](API-Documentation#webhook-integration)
- [CI/CD examples](Examples#gitlab-cicd-integration)

### 🏗️ Architecture
- [System overview](Architecture#system-overview)
- [Component design](Architecture#core-components)
- [Data flow](Architecture#data-flow)
- [Scaling considerations](Architecture#scalability-considerations)

### 🐛 Troubleshooting
- [Common issues](Troubleshooting#common-issues)
- [Debug mode](Troubleshooting#debug-mode)
- [Performance monitoring](Troubleshooting#performance-monitoring)
- [Log analysis](Troubleshooting#log-analysis)

## 📱 Mobile-Friendly Quick Access

### Essential Links
- [⚡ Quick Start](Getting-Started#quick-start)
- [🔧 API Docs](API-Documentation)
- [☁️ Cloud Setup](Cloud-Providers)
- [🎨 Themes](Visualization#themes)
- [🚨 Troubleshooting](Troubleshooting)

### Common Commands
```bash
# Test API
curl localhost:8000/health

# Get resources  
curl -H "Authorization: Bearer $TOKEN" \
     localhost:8000/api/v1/azure/resources

# Generate diagram
curl -X POST localhost:8000/api/v1/diagrams/mermaid \
     -d '{"resources":[...],"theme":"enterprise"}'
```

## 🆘 Need Help?

### Documentation Issues
- **Missing information?** [Create an issue](https://github.com/navidrast/cloudviz/issues/new?template=documentation.md)
- **Found an error?** [Submit a correction](https://github.com/navidrast/cloudviz/edit/main/wiki/)
- **Want to contribute?** [See Development Guide](Development#contributing-guidelines)

### Technical Support
- **Bug reports**: [GitHub Issues](https://github.com/navidrast/cloudviz/issues)
- **Feature requests**: [GitHub Discussions](https://github.com/navidrast/cloudviz/discussions)
- **Community help**: [Discussions Forum](https://github.com/navidrast/cloudviz/discussions)

### Enterprise Support
- Priority technical support
- Custom deployment assistance  
- Training and onboarding
- Performance optimization

---

**Ready to get started?** Begin with our **[Getting Started Guide](Getting-Started)** or explore specific topics using the navigation above.