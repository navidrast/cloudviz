# Frequently Asked Questions (FAQ)

## 🤔 General Questions

### What is CloudViz?
CloudViz is an enterprise-grade, multi-cloud infrastructure visualization platform that automatically discovers cloud resources and generates beautiful, interactive diagrams. It supports Azure, AWS, and GCP with powerful REST APIs perfect for automation workflows.

### What cloud providers does CloudViz support?
- **Azure**: Full support with resource group scanning
- **AWS**: Complete support across all regions
- **GCP**: Comprehensive project and resource scanning
- **Multi-Cloud**: Unified visualization across all providers

### Is CloudViz free to use?
CloudViz is open-source and free under the MIT license. You can use it for personal, commercial, and enterprise projects without any licensing fees.

### How does CloudViz differ from other visualization tools?
- **Multi-cloud focus**: Native support for Azure, AWS, and GCP
- **Real-time discovery**: Live resource scanning and updates
- **Cost integration**: Built-in cost analysis and optimization
- **Automation-first**: REST APIs designed for n8n and CI/CD integration
- **Enterprise features**: Security, compliance, and audit capabilities

## 🛠️ Installation & Setup

### What are the system requirements?
- **Python**: 3.8 or higher
- **Memory**: 2GB minimum (4GB recommended)
- **Storage**: 10GB free disk space
- **Network**: Internet access for cloud API calls

### Can I run CloudViz without Docker?
Yes! CloudViz can be installed directly with Python:
```bash
pip install -r requirements.txt
uvicorn cloudviz.api.main:app --host 0.0.0.0 --port 8000
```

### How do I set up cloud provider credentials?

**Azure:**
```bash
export AZURE_CLIENT_ID=your-client-id
export AZURE_CLIENT_SECRET=your-client-secret
export AZURE_TENANT_ID=your-tenant-id
```

**AWS:**
```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
```

**GCP:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
```

### What permissions do I need for cloud providers?

**Azure:**
- Reader role on subscriptions
- Contributor role for resource groups (optional)

**AWS:**
- ReadOnlyAccess policy
- EC2DescribeInstances, RDSDescribeDBInstances permissions

**GCP:**
- Viewer role on projects
- Compute Viewer, Storage Viewer roles

## 🔐 Security & Authentication

### How does CloudViz handle my cloud credentials?
CloudViz never stores your cloud credentials. They are used only for API calls and are handled securely:
- Environment variables are read at runtime
- No credentials are logged or cached
- All API calls use official cloud provider SDKs
- Optional credential encryption at rest

### Can I use CloudViz with SSO/SAML?
CloudViz supports multiple authentication methods:
- API keys for service-to-service
- JWT tokens for user authentication
- OAuth integration (coming soon)
- SAML/SSO support (enterprise feature)

### Is my infrastructure data secure?
- **Data encryption**: All data encrypted in transit and at rest
- **No data persistence**: Resources are not stored by default
- **Local deployment**: Self-hosted option for complete control
- **Audit logging**: Complete audit trail of all operations

### Can I run CloudViz in an air-gapped environment?
Yes, CloudViz can run in isolated environments:
- Deploy locally without internet access
- Use private cloud APIs
- Offline diagram generation
- Local cache and storage

## 📊 Usage & Features

### How often should I scan my infrastructure?
Recommendations:
- **Production**: Daily scans for change tracking
- **Development**: Weekly scans or on-demand
- **Compliance**: Monthly comprehensive scans
- **Incident response**: On-demand as needed

### Can CloudViz handle large infrastructures?
Yes! CloudViz is designed for enterprise scale:
- **1000+ resources**: Optimized rendering and filtering
- **Multiple regions**: Parallel scanning across regions
- **Performance tuning**: Configurable batch sizes and workers
- **Caching**: Intelligent caching for faster subsequent scans

### What diagram formats are supported?
- **Mermaid**: Interactive web diagrams
- **PNG**: High-resolution images
- **SVG**: Scalable vector graphics
- **PDF**: Print-ready documents
- **DOT**: Graphviz format

### Can I customize diagram themes and colors?
Absolutely! CloudViz supports:
- **Built-in themes**: Professional, dark, light, minimal
- **Custom themes**: Define your own color schemes
- **Brand colors**: Match your organization's branding
- **Layout options**: Hierarchical, force-directed, circular

### How accurate are the cost estimates?
Cost estimates are based on:
- **Official pricing APIs**: Direct from cloud providers
- **Real-time rates**: Updated hourly
- **Regional pricing**: Accurate for each region
- **Reserved instances**: Support for RI and spot pricing
- **90% accuracy**: Typical accuracy rate

## 🔄 Automation & Integration

### How do I integrate CloudViz with n8n?
1. Import example workflows from `examples/n8n-workflows/`
2. Configure CloudViz API endpoint in n8n
3. Set up webhook triggers for automated scanning
4. Use CloudViz REST APIs in n8n HTTP nodes

Example n8n workflow:
```json
{
  "nodes": [
    {
      "type": "HTTP Request",
      "url": "http://cloudviz:8000/api/v1/azure/extract",
      "method": "POST"
    }
  ]
}
```

### Can CloudViz integrate with CI/CD pipelines?
Yes! CloudViz fits perfectly in DevOps workflows:
- **GitHub Actions**: Use CloudViz action for PR reviews
- **Jenkins**: Plugin for infrastructure verification
- **Azure DevOps**: Pipeline tasks for diagram generation
- **GitLab CI**: Integration for merge request validation

### Does CloudViz support webhooks?
CloudViz can send webhooks for:
- Scan completion notifications
- Diagram generation updates
- Error and failure alerts
- Cost threshold breaches

### Can I schedule automatic scans?
Use any scheduler with CloudViz REST API:
```bash
# Crontab example - daily at 6 AM
0 6 * * * curl -X POST http://cloudviz:8000/api/v1/azure/extract
```

## 🚨 Troubleshooting

### CloudViz returns "No resources found"
Check:
1. **Credentials**: Verify cloud provider authentication
2. **Permissions**: Ensure sufficient read permissions
3. **Regions**: Check if scanning correct regions
4. **Filters**: Remove restrictive resource filters

### API calls are timing out
Solutions:
1. **Increase timeout**: Set `CLOUDVIZ_TIMEOUT=600`
2. **Reduce scope**: Scan fewer resource groups/regions
3. **Use filters**: Limit to specific resource types
4. **Check network**: Verify connectivity to cloud APIs

### Diagrams are not generating
Troubleshoot:
1. **Check resources**: Ensure resources were discovered
2. **Verify format**: Use supported diagram formats
3. **Reduce complexity**: Filter resources for simpler diagrams
4. **Check logs**: Review CloudViz logs for errors

### High memory usage
Optimize:
1. **Reduce batch size**: Set `CLOUDVIZ_BATCH_SIZE=50`
2. **Clear cache**: POST to `/api/v1/admin/cache/clear`
3. **Limit workers**: Set `CLOUDVIZ_WORKERS=2`
4. **Filter resources**: Use resource type filters

## 🔧 Configuration

### How do I configure CloudViz for production?
Use YAML configuration files:
```yaml
# config/production.yml
api:
  host: "0.0.0.0"
  port: 8000
  workers: 4

cache:
  enabled: true
  backend: "redis"
  ttl: 3600

logging:
  level: "INFO"
  format: "json"
```

### Can I use a database other than SQLite?
CloudViz supports:
- **PostgreSQL**: Recommended for production
- **MySQL**: Supported with proper drivers
- **SQLite**: Default for development
- **Redis**: For caching and sessions

### How do I scale CloudViz horizontally?
Deploy multiple instances:
1. **Load balancer**: Use nginx or AWS ALB
2. **Shared database**: PostgreSQL or MySQL
3. **Shared cache**: Redis cluster
4. **Container orchestration**: Kubernetes deployment

### Can I customize the API endpoints?
CloudViz allows customization:
- **Custom routes**: Add organization-specific endpoints
- **Middleware**: Custom authentication and authorization
- **Plugins**: Extend functionality with custom providers
- **Webhooks**: Custom notification handlers

## 📈 Performance & Scaling

### How fast is resource discovery?
Typical performance:
- **Azure**: 100 resources in 2-3 minutes
- **AWS**: 100 resources in 1-2 minutes
- **GCP**: 100 resources in 2-4 minutes
- **Multi-cloud**: Parallel processing across providers

### What's the maximum number of resources CloudViz can handle?
CloudViz scales to:
- **10,000+ resources**: With proper configuration
- **Multiple subscriptions**: Parallel scanning
- **Large diagrams**: Intelligent filtering and grouping
- **Enterprise scale**: Tested with major organizations

### How do I improve performance?
Optimization tips:
1. **Use caching**: Enable Redis for faster subsequent scans
2. **Parallel processing**: Increase worker count
3. **Filter effectively**: Use resource type and region filters
4. **Batch processing**: Optimize batch sizes for your environment

## 🤝 Community & Support

### How do I get help?
Support channels:
1. **Documentation**: Check docs and troubleshooting guide
2. **GitHub Issues**: Search existing issues or create new ones
3. **Discord**: Join community for real-time help
4. **Email**: support@cloudviz.dev for critical issues

### How can I contribute to CloudViz?
Ways to contribute:
- **Bug reports**: Help us identify and fix issues
- **Feature requests**: Suggest new functionality
- **Code contributions**: Submit pull requests
- **Documentation**: Improve guides and examples
- **Community support**: Help others in Discord

### Is there a roadmap for CloudViz?
Yes! Our roadmap includes:
- **Additional cloud providers**: Oracle, IBM, Alibaba Cloud
- **AI-powered insights**: Intelligent recommendations
- **Advanced analytics**: Cost optimization and forecasting
- **Mobile app**: Mobile-friendly diagram viewing
- **Enterprise features**: Advanced security and compliance

### How often is CloudViz updated?
Release schedule:
- **Major releases**: Quarterly (new features)
- **Minor releases**: Monthly (improvements, bug fixes)
- **Patch releases**: As needed (critical bug fixes)
- **Security updates**: Immediate when required

## 💡 Best Practices

### What are the recommended scanning strategies?
**Production environments:**
- Daily comprehensive scans
- Resource type filtering for focused views
- Automated alerts for infrastructure changes
- Regular cost analysis reports

**Development environments:**
- Weekly or on-demand scans
- Feature branch validation
- Merge request diagram generation
- Cost tracking for development resources

### How should I organize my diagrams?
Organization strategies:
- **By environment**: Production, staging, development
- **By application**: Group related services
- **By team**: Separate diagrams for different teams
- **By region**: Geographic distribution views

### What security practices should I follow?
Security recommendations:
- **Least privilege**: Minimal required permissions
- **Credential rotation**: Regular rotation of API keys
- **Network security**: Deploy in private networks
- **Audit logging**: Enable comprehensive logging
- **Regular updates**: Keep CloudViz updated

---

## 📞 Still Need Help?

If your question isn't answered here:

1. **Search the documentation**: Use the search function in our docs
2. **Check GitHub Issues**: Look for similar questions
3. **Join Discord**: Get help from the community
4. **Create an issue**: Include detailed information about your question

**Common issue patterns we've seen:**
- 80% of issues are authentication/permissions related
- 15% are configuration problems
- 5% are actual bugs or missing features

Remember: Include your CloudViz version, cloud provider, and error logs when asking for help!