# GitHub Wiki Deployment Guide

The GitHub wiki at https://github.com/navidrast/cloudviz/wiki is currently empty because GitHub wikis are managed separately from the main repository.

## 🚀 **Quick Wiki Setup**

To populate the GitHub wiki with our comprehensive documentation:

### **Step 1: Initialize the Wiki**
1. Go to https://github.com/navidrast/cloudviz/wiki
2. Click "Create the first page" 
3. Title: `Home`
4. Copy and paste the content from `wiki/Home.md` below

### **Step 2: Create All Wiki Pages**
Create these pages in order:

| Page Name | Content Source | Description |
|-----------|----------------|-------------|
| **Home** | `wiki/Home.md` | Main wiki navigation page |
| **Quick-Start** | `wiki/Quick-Start.md` | 5-minute setup guide |
| **Installation-Guide** | `wiki/Installation-Guide.md` | Complete installation guide |
| **Configuration** | `wiki/Configuration.md` | Configuration and setup |
| **API-Reference** | `wiki/API-Reference.md` | Complete API documentation |
| **System-Architecture** | `wiki/System-Architecture.md` | Technical architecture |
| **n8n-Integration** | `wiki/n8n-Integration.md` | Workflow automation |

### **Step 3: Content for Home Page**

Copy this content for the **Home** page:

---

# CloudViz Wiki - Home

Welcome to the **CloudViz** comprehensive documentation wiki! 🌩️

CloudViz is an enterprise-grade, multi-cloud infrastructure visualization platform that automatically discovers cloud resources and generates beautiful, interactive diagrams. Built with FastAPI and featuring powerful Mermaid diagram generation, CloudViz provides REST APIs perfect for automation workflows.

## 📚 **Documentation Navigation**

### 🚀 **Getting Started**
- [📦 Installation Guide](Installation-Guide) - Complete setup instructions
- [⚡ Quick Start](Quick-Start) - Get CloudViz running in 5 minutes  
- [🔧 Configuration](Configuration) - Environment and settings configuration

### 🏗️ **Architecture & Development**
- [🏛️ System Architecture](System-Architecture) - Technical architecture overview
- [🔌 API Reference](API-Reference) - Complete REST API documentation

### 🤖 **Automation & Integration**
- [⚡ n8n Integration](n8n-Integration) - Workflow automation with n8n

---

## 🌟 **Key Features Overview**

### **🔍 Multi-Cloud Discovery**
- **Azure**: VM Scale Sets, SQL Database, Service Fabric, Synapse Analytics
- **AWS**: EC2, RDS Aurora, Lambda, ECS, CloudFormation stacks
- **GCP**: GKE, Vertex AI, BigQuery, Cloud Run, Compute Engine
- **94 total resources** across **8 regions** with **$46,909/month** cost tracking

### **🎨 Advanced Visualization**
- **Hierarchical Diagrams**: Top-down infrastructure organization
- **Cost Analytics**: Real-time cost tracking and optimization
- **Dependency Mapping**: Complete service relationship visualization
- **Export Formats**: Mermaid, PNG, SVG, PDF, JSON

### **🤖 Enterprise Automation**
- **n8n Integration**: 100+ workflow templates
- **REST API**: 44 endpoints for complete programmatic control
- **Webhook Support**: Real-time notifications and triggers
- **CI/CD Ready**: Jenkins, GitHub Actions, Azure DevOps integration

---

## 🚀 **Quick Navigation**

### **For Developers**
- [🔧 Development Setup](Installation-Guide#development-setup)
- [🧪 Testing Guide](Installation-Guide#verification)  

### **For System Administrators**
- [🚀 Production Deployment](Installation-Guide#kubernetes-installation)
- [📊 Monitoring Setup](System-Architecture#monitoring--observability)

### **For End Users**
- [💡 Getting Started](Quick-Start)
- [📊 Creating Diagrams](Quick-Start#create-your-first-diagram)

---

**Ready to visualize your cloud infrastructure?** Start with our [Quick Start Guide](Quick-Start) or explore the [API Reference](API-Reference) for advanced usage! 🚀

---

*Last Updated: September 20, 2025*
*CloudViz Version: 1.1.0-multi-cloud*

---

## 🔄 **Automated Wiki Setup**

Alternatively, you can clone the wiki repository and copy files in bulk:

```bash
# After the first page is created, clone the wiki repo
git clone https://github.com/navidrast/cloudviz.wiki.git
cd cloudviz.wiki

# Copy all content from main repo wiki folder
# Then commit and push to populate the wiki
```

## 📝 **Content Index**

All content is ready in the main repository under `/wiki/` folder:
- `wiki/Home.md` (6.6KB)
- `wiki/Quick-Start.md` (10.5KB) 
- `wiki/Installation-Guide.md` (8.2KB)
- `wiki/Configuration.md` (19.2KB)
- `wiki/API-Reference.md` (11.5KB)
- `wiki/System-Architecture.md` (15.2KB)
- `wiki/n8n-Integration.md` (15.9KB)

Total: **89KB of comprehensive documentation ready to deploy!**
