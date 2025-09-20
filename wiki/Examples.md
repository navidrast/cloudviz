# Examples

This page provides real-world examples, use cases, and configurations for CloudViz across different scenarios and industries.

## 🏢 Enterprise Use Cases

### 1. Financial Services - Compliance & Security

**Scenario**: A financial services company needs to visualize their Azure infrastructure for SOX compliance and security audits.

**Configuration**:
```yaml
# config/financial-services.yml
cloud_providers:
  azure:
    enabled: true
    discovery:
      include_security_analysis: true
      include_compliance_tags: true
      
visualization:
  default_theme: "security"
  security_focus:
    highlight_public_endpoints: true
    show_encryption_status: true
    compliance_annotations: true
    
audit:
  enabled: true
  log_all_access: true
  compliance_reports: true
```

**API Usage**:
```bash
# Generate security-focused diagram
curl -X POST "http://localhost:8000/api/v1/diagrams/mermaid" \
     -H "Content-Type: application/json" \
     -d '{
       "resources": [...],
       "theme": "security",
       "annotations": {
         "compliance": true,
         "pci_dss": true,
         "sox": true
       },
       "highlight_rules": [
         {"type": "public_endpoint", "severity": "critical"},
         {"type": "unencrypted_storage", "severity": "high"},
         {"type": "weak_authentication", "severity": "medium"}
       ]
     }'
```

**Generated Diagram**:
```mermaid
flowchart TD
    INTERNET[🌍 Internet] -->|HTTPS:443| WAF[🛡️ WAF - PCI Compliant]
    WAF -->|Filtered| ALB[⚖️ Load Balancer]
    
    ALB --> WEB1[🖥️ Web Server 1<br/>SOX Compliant]
    ALB --> WEB2[🖥️ Web Server 2<br/>SOX Compliant]
    
    WEB1 -->|Encrypted TLS 1.3| APP[⚙️ App Server<br/>Private Subnet]
    WEB2 -->|Encrypted TLS 1.3| APP
    
    APP -->|Encrypted at Rest| DB[🔒 SQL Database<br/>Always Encrypted]
    
    classDef compliant fill:#27ae60,stroke:#1e8449,color:#fff
    classDef warning fill:#f39c12,stroke:#d68910,color:#fff
    classDef critical fill:#e74c3c,stroke:#c0392b,color:#fff
    
    class WAF,WEB1,WEB2,APP,DB compliant
```

### 2. Healthcare - HIPAA Compliance

**Scenario**: Healthcare organization needs to ensure HIPAA compliance across their cloud infrastructure.

**Configuration**:
```yaml
# config/healthcare-hipaa.yml
cloud_providers:
  azure:
    enabled: true
    regions: ["eastus", "westus2"]  # HIPAA-compliant regions only
    
    discovery:
      include_phi_analysis: true
      hipaa_compliance_check: true
      
    filters:
      exclude_non_compliant_regions: true
      require_encryption: true
      
visualization:
  theme: "security"
  hipaa_annotations: true
  data_flow_tracking: true
  
compliance:
  frameworks: ["HIPAA", "HITECH"]
  audit_logs: true
  access_tracking: true
```

**Workflow Integration**:
```python
# n8n workflow for HIPAA compliance monitoring
async def check_hipaa_compliance():
    # Discover resources
    resources = await discovery.azure.discover_resources(
        filters={
            "compliance_required": "HIPAA",
            "data_classification": "PHI"
        }
    )
    
    # Generate compliance report
    compliance_report = await analysis.run_hipaa_check(resources)
    
    # Generate visualization
    diagram = await visualization.generate_diagram(
        resources=resources,
        theme="security",
        highlight_compliance_issues=True
    )
    
    # Send alerts for non-compliant resources
    if compliance_report.issues:
        await alerts.send_compliance_alert(
            issues=compliance_report.issues,
            diagram=diagram
        )
```

### 3. E-commerce - Cost Optimization

**Scenario**: E-commerce company wants to optimize their cloud costs and visualize spending patterns.

**Configuration**:
```yaml
# config/ecommerce-cost.yml
cloud_providers:
  azure:
    enabled: true
    cost_analysis:
      enabled: true
      currency: "USD"
      billing_period: "monthly"
      cost_alerts:
        threshold: 10000
        percentage_increase: 20
        
visualization:
  default_theme: "cost"
  cost_optimization:
    show_recommendations: true
    highlight_expensive_resources: true
    group_by_cost_tier: true
    
analytics:
  cost_trends: true
  usage_patterns: true
  optimization_suggestions: true
```

**Cost Analysis Example**:
```bash
# Generate cost-focused infrastructure diagram
curl -X POST "http://localhost:8000/api/v1/diagrams/mermaid" \
     -H "Content-Type: application/json" \
     -d '{
       "resources": [...],
       "theme": "cost",
       "cost_analysis": {
         "show_monthly_costs": true,
         "highlight_threshold": 1000,
         "show_optimization_opportunities": true,
         "cost_breakdown": true
       }
     }'
```

**Cost Dashboard Integration**:
```python
# PowerBI/Grafana integration
def generate_cost_dashboard():
    # Get cost data
    cost_data = cloudviz_api.get_cost_analysis(
        timeframe="30d",
        group_by=["resource_group", "resource_type"]
    )
    
    # Generate visualization
    diagram = cloudviz_api.generate_diagram(
        theme="cost",
        annotations=cost_data
    )
    
    return {
        "cost_summary": cost_data.summary,
        "infrastructure_diagram": diagram,
        "recommendations": cost_data.optimization_suggestions
    }
```

## 🏭 Industry-Specific Examples

### Manufacturing - IoT Infrastructure

**Scenario**: Manufacturing company with IoT sensors and edge computing infrastructure.

```yaml
# config/manufacturing-iot.yml
cloud_providers:
  azure:
    enabled: true
    iot_focus: true
    
    discovery:
      include_iot_devices: true
      edge_computing: true
      
visualization:
  custom_icons:
    iot_sensor: "📡"
    edge_device: "🔧"
    factory_gateway: "🏭"
    
  layout: "network"  # Show physical connections
  
iot_integration:
  device_telemetry: true
  edge_mapping: true
  connectivity_analysis: true
```

**IoT Infrastructure Diagram**:
```mermaid
flowchart LR
    FACTORY[🏭 Factory Floor] --> GATEWAY[📡 IoT Gateway]
    
    GATEWAY --> SENSOR1[📊 Temperature Sensor]
    GATEWAY --> SENSOR2[⚡ Vibration Sensor]
    GATEWAY --> SENSOR3[🔧 Machine Status]
    
    GATEWAY -->|5G/WiFi| EDGE[🖥️ Edge Computing]
    EDGE -->|Preprocessed Data| IOT_HUB[☁️ Azure IoT Hub]
    
    IOT_HUB --> STREAM[🌊 Stream Analytics]
    STREAM --> STORAGE[💾 Time Series DB]
    STREAM --> ALERTS[🚨 Alert System]
    
    STORAGE --> ANALYTICS[📈 ML Analytics]
    ANALYTICS --> DASHBOARD[📊 Factory Dashboard]
```

### Retail - Multi-Region E-commerce

**Scenario**: Global retail company with multi-region deployment for low latency.

```yaml
# config/retail-global.yml
cloud_providers:
  azure:
    enabled: true
    regions:
      - "eastus"        # North America
      - "westeurope"    # Europe
      - "australiaeast" # Asia Pacific
      - "brazilsouth"   # South America
      
    discovery:
      include_cdn: true
      global_load_balancing: true
      regional_failover: true
      
visualization:
  theme: "enterprise"
  global_view: true
  region_grouping: true
  traffic_flow: true
  
performance:
  latency_analysis: true
  cdn_optimization: true
  failover_paths: true
```

**Global Infrastructure Example**:
```mermaid
flowchart TD
    USERS[🌍 Global Users] --> TM[🌐 Azure Traffic Manager]
    
    TM --> NA_REGION[🇺🇸 North America]
    TM --> EU_REGION[🇪🇺 Europe]
    TM --> APAC_REGION[🇦🇺 Asia Pacific]
    TM --> SA_REGION[🇧🇷 South America]
    
    NA_REGION --> NA_CDN[🚀 CDN - East US]
    EU_REGION --> EU_CDN[🚀 CDN - West Europe]
    APAC_REGION --> APAC_CDN[🚀 CDN - Australia East]
    SA_REGION --> SA_CDN[🚀 CDN - Brazil South]
    
    NA_CDN --> NA_APP[💼 App Services]
    EU_CDN --> EU_APP[💼 App Services]
    APAC_CDN --> APAC_APP[💼 App Services]
    SA_CDN --> SA_APP[💼 App Services]
    
    NA_APP --> GLOBAL_DB[🗄️ Global Database<br/>Multi-Master]
    EU_APP --> GLOBAL_DB
    APAC_APP --> GLOBAL_DB
    SA_APP --> GLOBAL_DB
```

### Education - Research Computing

**Scenario**: University with high-performance computing resources for research.

```yaml
# config/university-hpc.yml
cloud_providers:
  azure:
    enabled: true
    hpc_focus: true
    
    discovery:
      include_batch_computing: true
      research_storage: true
      gpu_clusters: true
      
    resource_types:
      - "Microsoft.Batch/batchAccounts"
      - "Microsoft.Compute/virtualMachineScaleSets"
      - "Microsoft.Storage/storageAccounts"
      - "Microsoft.Network/virtualNetworks"
      
visualization:
  theme: "enterprise"
  hpc_layout: true
  compute_intensive_focus: true
  
research:
  department_grouping: true
  project_tagging: true
  resource_allocation: true
```

## 🔄 Automation Examples

### 1. Daily Infrastructure Reports

**n8n Workflow**:
```json
{
  "name": "Daily Infrastructure Report",
  "nodes": [
    {
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "parameters": {
        "rule": {
          "interval": [{"field": "cronExpression", "value": "0 8 * * *"}]
        }
      }
    },
    {
      "name": "Discover Azure Resources",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://cloudviz:8000/api/v1/azure/resources",
        "method": "GET",
        "qs": {
          "include_costs": "true",
          "include_security_analysis": "true"
        }
      }
    },
    {
      "name": "Generate Executive Summary",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "jsCode": `
          const resources = $input.first().json.resources;
          
          const summary = {
            total_resources: resources.length,
            total_monthly_cost: resources.reduce((sum, r) => sum + (r.cost || 0), 0),
            by_type: {},
            by_region: {},
            security_issues: 0
          };
          
          resources.forEach(resource => {
            // Count by type
            summary.by_type[resource.type] = (summary.by_type[resource.type] || 0) + 1;
            
            // Count by region
            summary.by_region[resource.region] = (summary.by_region[resource.region] || 0) + 1;
            
            // Count security issues
            if (resource.security_issues && resource.security_issues.length > 0) {
              summary.security_issues += resource.security_issues.length;
            }
          });
          
          return [{ json: { summary, resources } }];
        `
      }
    },
    {
      "name": "Generate Infrastructure Diagram",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "http://cloudviz:8000/api/v1/diagrams/mermaid/png",
        "method": "POST",
        "body": {
          "resources": "={{$node['Discover Azure Resources'].json.resources}}",
          "theme": "enterprise",
          "include_costs": true
        }
      }
    },
    {
      "name": "Send Executive Report",
      "type": "n8n-nodes-base.emailSend",
      "parameters": {
        "fromEmail": "cloudviz@company.com",
        "toEmail": "executives@company.com",
        "subject": "Daily Infrastructure Report - {{$now.format('YYYY-MM-DD')}}",
        "html": `
          <h1>Daily Infrastructure Report</h1>
          <p>Generated on: {{$now.format('YYYY-MM-DD HH:mm:ss')}}</p>
          
          <h2>Summary</h2>
          <ul>
            <li>Total Resources: {{$node['Generate Executive Summary'].json.summary.total_resources}}</li>
            <li>Monthly Cost: ${{$node['Generate Executive Summary'].json.summary.total_monthly_cost}}</li>
            <li>Security Issues: {{$node['Generate Executive Summary'].json.summary.security_issues}}</li>
          </ul>
          
          <h2>Infrastructure Diagram</h2>
          <img src="cid:infrastructure-diagram" alt="Infrastructure Diagram" style="max-width: 100%;">
        `,
        "attachments": [
          {
            "name": "infrastructure-diagram.png",
            "content": "={{$node['Generate Infrastructure Diagram'].binary}}",
            "cid": "infrastructure-diagram"
          }
        ]
      }
    }
  ]
}
```

### 2. Incident Response Automation

**Automated Incident Response**:
```python
# incident_response.py
async def handle_incident(incident_data):
    """
    Automated incident response with infrastructure visualization.
    """
    
    # Step 1: Identify affected resources
    affected_resources = await identify_affected_resources(
        incident_data.resource_ids,
        incident_data.region
    )
    
    # Step 2: Discover dependencies
    all_resources = await cloudviz.azure.discover_resources(
        filters={
            "regions": [incident_data.region],
            "include_dependencies": True
        }
    )
    
    # Step 3: Build impact graph
    impact_graph = build_dependency_graph(
        all_resources,
        affected_resources
    )
    
    # Step 4: Generate impact diagram
    impact_diagram = await cloudviz.diagrams.generate_mermaid(
        resources=impact_graph.nodes,
        theme="security",
        highlight_resources=affected_resources,
        show_impact_radius=True
    )
    
    # Step 5: Send to incident response team
    await send_incident_notification(
        incident=incident_data,
        impact_diagram=impact_diagram,
        affected_count=len(impact_graph.affected_resources),
        estimated_users_impacted=impact_graph.user_impact_estimate
    )
    
    return {
        "incident_id": incident_data.id,
        "impact_analysis": impact_graph.summary,
        "diagram_url": impact_diagram.url,
        "response_time": "< 2 minutes"
    }
```

### 3. Cost Optimization Workflows

**Weekly Cost Review**:
```javascript
// n8n Cost Optimization Workflow
const costAnalysis = await $this.helpers.httpRequest({
  method: 'GET',
  url: '/api/v1/analytics/costs',
  qs: {
    timeframe: '7d',
    compare_previous: 'true',
    include_recommendations: 'true'
  }
});

const recommendations = costAnalysis.optimization_recommendations;
const alerts = [];

// Check for cost spikes
if (costAnalysis.week_over_week_change > 0.15) {  // 15% increase
  alerts.push({
    type: 'cost_spike',
    message: `Weekly costs increased by ${(costAnalysis.week_over_week_change * 100).toFixed(1)}%`,
    amount: costAnalysis.current_week_cost - costAnalysis.previous_week_cost
  });
}

// Check for optimization opportunities
recommendations.forEach(rec => {
  if (rec.potential_savings > 500) {  // $500+ savings
    alerts.push({
      type: 'optimization_opportunity',
      message: rec.description,
      potential_savings: rec.potential_savings,
      resource: rec.resource_id
    });
  }
});

// Generate cost-focused diagram if alerts exist
if (alerts.length > 0) {
  const costDiagram = await $this.helpers.httpRequest({
    method: 'POST',
    url: '/api/v1/diagrams/mermaid',
    body: {
      resources: costAnalysis.resources,
      theme: 'cost',
      highlight_expensive: true,
      annotations: recommendations
    }
  });
  
  // Send to FinOps team
  await sendCostAlert(alerts, costDiagram);
}
```

## 📱 Integration Examples

### 1. Slack Bot Integration

```python
# slack_bot.py
from slack_bolt import App
from cloudviz_client import CloudVizClient

app = App(token="xoxb-your-token")
cloudviz = CloudVizClient("http://cloudviz:8000")

@app.command("/infrastructure")
def show_infrastructure(ack, command, respond):
    ack()
    
    try:
        # Parse command parameters
        params = parse_slack_command(command['text'])
        
        # Discover resources
        resources = cloudviz.azure.discover_resources(
            filters=params.get('filters', {})
        )
        
        # Generate diagram
        diagram = cloudviz.diagrams.generate_mermaid_png(
            resources=resources,
            theme=params.get('theme', 'enterprise')
        )
        
        # Upload to Slack
        response = app.client.files_upload(
            channels=command['channel_id'],
            file=diagram,
            filename="infrastructure.png",
            title=f"Infrastructure Overview - {params.get('environment', 'All')}"
        )
        
        respond(
            f"Infrastructure diagram generated! "
            f"Found {len(resources)} resources. "
            f"<{response['file']['permalink']}|View Diagram>"
        )
        
    except Exception as e:
        respond(f"Error generating diagram: {str(e)}")

@app.command("/costs")
def show_costs(ack, command, respond):
    ack()
    
    try:
        cost_analysis = cloudviz.analytics.get_cost_analysis(
            timeframe="30d"
        )
        
        # Format cost summary
        summary = f"""
💰 *Monthly Cost Summary*
• Total: ${cost_analysis.total_cost:,.2f}
• Compute: ${cost_analysis.compute_cost:,.2f}
• Storage: ${cost_analysis.storage_cost:,.2f}
• Network: ${cost_analysis.network_cost:,.2f}

📈 *Trends*
• Week over week: {cost_analysis.wow_change:+.1%}
• Month over month: {cost_analysis.mom_change:+.1%}

💡 *Top 3 Optimization Opportunities*
"""
        
        for i, rec in enumerate(cost_analysis.recommendations[:3], 1):
            summary += f"{i}. {rec.description} (Save ${rec.potential_savings:,.2f})\n"
        
        respond(summary)
        
    except Exception as e:
        respond(f"Error getting cost analysis: {str(e)}")
```

### 2. Microsoft Teams Integration

```python
# teams_bot.py
from botbuilder.core import ActivityHandler, MessageFactory
from botbuilder.schema import ChannelAccount, Attachment

class InfrastructureBot(ActivityHandler):
    
    async def on_message_activity(self, turn_context):
        text = turn_context.activity.text.lower()
        
        if "show infrastructure" in text:
            await self.show_infrastructure(turn_context)
        elif "cost report" in text:
            await self.show_cost_report(turn_context)
        elif "security scan" in text:
            await self.show_security_scan(turn_context)
    
    async def show_infrastructure(self, turn_context):
        # Generate infrastructure diagram
        resources = await cloudviz.azure.discover_resources()
        diagram_url = await cloudviz.diagrams.generate_and_upload(
            resources=resources,
            theme="enterprise"
        )
        
        # Create adaptive card
        card = {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.2",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "Infrastructure Overview",
                    "weight": "Bolder",
                    "size": "Medium"
                },
                {
                    "type": "FactSet",
                    "facts": [
                        {"title": "Total Resources", "value": str(len(resources))},
                        {"title": "Resource Groups", "value": str(len(set(r.resource_group for r in resources)))},
                        {"title": "Regions", "value": str(len(set(r.region for r in resources)))}
                    ]
                },
                {
                    "type": "Image",
                    "url": diagram_url,
                    "size": "Large"
                }
            ]
        }
        
        attachment = MessageFactory.attachment(
            Attachment(
                content_type="application/vnd.microsoft.card.adaptive",
                content=card
            )
        )
        
        await turn_context.send_activity(attachment)
```

### 3. PowerBI Dashboard Integration

```python
# powerbi_integration.py
import requests
from powerbi import PowerBIClient

class PowerBIIntegration:
    
    def __init__(self, workspace_id, dataset_id):
        self.client = PowerBIClient()
        self.workspace_id = workspace_id
        self.dataset_id = dataset_id
    
    async def update_infrastructure_data(self):
        """Update PowerBI dataset with latest infrastructure data."""
        
        # Get latest resource data
        resources = await cloudviz.azure.discover_resources(
            include_costs=True,
            include_security_analysis=True
        )
        
        # Transform data for PowerBI
        resource_data = []
        cost_data = []
        security_data = []
        
        for resource in resources:
            resource_data.append({
                "ResourceId": resource.id,
                "Name": resource.name,
                "Type": resource.type,
                "Region": resource.region,
                "ResourceGroup": resource.resource_group,
                "Tags": json.dumps(resource.tags),
                "LastUpdated": datetime.utcnow().isoformat()
            })
            
            if resource.cost:
                cost_data.append({
                    "ResourceId": resource.id,
                    "MonthlyCost": resource.cost.monthly_estimate,
                    "Currency": resource.cost.currency,
                    "CostCenter": resource.tags.get("cost_center"),
                    "Environment": resource.tags.get("environment")
                })
            
            if resource.security_issues:
                for issue in resource.security_issues:
                    security_data.append({
                        "ResourceId": resource.id,
                        "IssueType": issue.type,
                        "Severity": issue.severity,
                        "Description": issue.description,
                        "Recommendation": issue.recommendation
                    })
        
        # Update PowerBI tables
        await self.client.datasets.post_rows(
            workspace_id=self.workspace_id,
            dataset_id=self.dataset_id,
            table_name="Resources",
            rows=resource_data
        )
        
        await self.client.datasets.post_rows(
            workspace_id=self.workspace_id,
            dataset_id=self.dataset_id,
            table_name="Costs",
            rows=cost_data
        )
        
        await self.client.datasets.post_rows(
            workspace_id=self.workspace_id,
            dataset_id=self.dataset_id,
            table_name="SecurityIssues",
            rows=security_data
        )
        
        # Trigger dataset refresh
        await self.client.datasets.refresh_dataset(
            workspace_id=self.workspace_id,
            dataset_id=self.dataset_id
        )
```

### 4. Grafana Dashboard

```python
# grafana_metrics.py
from prometheus_client import Gauge, Counter, Histogram, start_http_server
import asyncio

# Prometheus metrics
resource_count = Gauge('cloudviz_resources_total', 'Total number of discovered resources', ['provider', 'region', 'type'])
discovery_duration = Histogram('cloudviz_discovery_duration_seconds', 'Time spent discovering resources', ['provider'])
api_requests = Counter('cloudviz_api_requests_total', 'Total API requests', ['endpoint', 'method', 'status'])
cost_total = Gauge('cloudviz_monthly_cost_usd', 'Total monthly cost in USD', ['provider', 'resource_group'])

async def update_metrics():
    """Update Prometheus metrics with current infrastructure state."""
    
    while True:
        try:
            # Discover resources and measure time
            start_time = time.time()
            resources = await cloudviz.azure.discover_resources()
            discovery_duration.labels(provider='azure').observe(time.time() - start_time)
            
            # Update resource counts
            resource_counts = {}
            cost_totals = {}
            
            for resource in resources:
                # Count resources by type and region
                key = (resource.provider, resource.region, resource.type)
                resource_counts[key] = resource_counts.get(key, 0) + 1
                
                # Sum costs by resource group
                if resource.cost:
                    cost_key = (resource.provider, resource.resource_group)
                    cost_totals[cost_key] = cost_totals.get(cost_key, 0) + resource.cost.monthly_estimate
            
            # Update Prometheus metrics
            for (provider, region, resource_type), count in resource_counts.items():
                resource_count.labels(provider=provider, region=region, type=resource_type).set(count)
            
            for (provider, resource_group), cost in cost_totals.items():
                cost_total.labels(provider=provider, resource_group=resource_group).set(cost)
            
        except Exception as e:
            print(f"Error updating metrics: {e}")
        
        await asyncio.sleep(300)  # Update every 5 minutes

# Start Prometheus metrics server
start_http_server(8001)
asyncio.run(update_metrics())
```

### 5. GitLab CI/CD Integration

```yaml
# .gitlab-ci.yml
stages:
  - infrastructure-scan
  - security-analysis
  - cost-analysis
  - documentation

infrastructure-scan:
  stage: infrastructure-scan
  image: python:3.11
  script:
    - pip install cloudviz-cli
    - cloudviz discover --provider azure --output infrastructure.json
    - cloudviz diagram --input infrastructure.json --theme enterprise --output infrastructure.png
  artifacts:
    paths:
      - infrastructure.json
      - infrastructure.png
    expire_in: 1 week

security-analysis:
  stage: security-analysis
  image: python:3.11
  dependencies:
    - infrastructure-scan
  script:
    - cloudviz analyze security --input infrastructure.json --output security-report.json
    - cloudviz diagram --input infrastructure.json --theme security --output security-diagram.png
  artifacts:
    paths:
      - security-report.json
      - security-diagram.png
    reports:
      security: security-report.json

cost-analysis:
  stage: cost-analysis
  image: python:3.11
  dependencies:
    - infrastructure-scan
  script:
    - cloudviz analyze costs --input infrastructure.json --output cost-report.json
    - cloudviz diagram --input infrastructure.json --theme cost --output cost-diagram.png
  artifacts:
    paths:
      - cost-report.json
      - cost-diagram.png

update-documentation:
  stage: documentation
  image: python:3.11
  dependencies:
    - infrastructure-scan
    - security-analysis
    - cost-analysis
  script:
    - python scripts/update_architecture_docs.py
    - git add docs/architecture/
    - git commit -m "Update architecture documentation [skip ci]" || true
    - git push origin $CI_COMMIT_REF_NAME
  only:
    - main
```

## 📊 Configuration Templates

### 1. Startup Company Configuration

```yaml
# config/startup.yml - Lean configuration for startups
api:
  workers: 2  # Start small
  debug: false

database:
  url: "sqlite:///data/cloudviz.db"  # Simple SQLite for start

cache:
  backend: "memory"  # No Redis dependency

cloud_providers:
  azure:
    enabled: true
    discovery:
      batch_size: 50
      parallel_regions: false  # Reduce API calls
      timeout: 180

visualization:
  default_theme: "minimal"
  include_costs: true

rate_limiting:
  enabled: false  # No rate limiting for small teams

monitoring:
  enabled: false  # Simple setup
```

### 2. Enterprise Configuration

```yaml
# config/enterprise.yml - Full enterprise setup
api:
  workers: 8
  debug: false
  log_level: "INFO"

database:
  url: "${DATABASE_URL}"
  pool_size: 50
  max_overflow: 100

cache:
  backend: "redis"
  redis_url: "${REDIS_URL}"
  default_ttl: 3600

security:
  jwt:
    secret_key: "${JWT_SECRET_KEY}"
  rate_limiting:
    enabled: true
    strict_mode: true
  encryption:
    enabled: true

cloud_providers:
  azure:
    enabled: true
    discovery:
      parallel_regions: true
      batch_size: 100
      include_security_analysis: true
      include_compliance_check: true
  
  aws:
    enabled: true
    multi_account: true
  
  gcp:
    enabled: true
    multi_project: true

visualization:
  themes:
    enterprise: {...}
    security: {...}
    compliance: {...}
    cost: {...}

monitoring:
  enabled: true
  metrics_endpoint: "/metrics"
  health_checks:
    detailed: true

audit:
  enabled: true
  log_all_access: true
  compliance_reporting: true

backup:
  enabled: true
  schedule: "0 2 * * *"
  retention: "90d"
```

---

These examples provide a comprehensive foundation for implementing CloudViz across various scenarios. Adapt the configurations and integrations to match your specific requirements and infrastructure setup.