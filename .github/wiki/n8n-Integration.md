# ⚡ n8n Integration

CloudViz provides seamless integration with n8n (pronounced "n-eight-n"), a powerful workflow automation platform. This integration enables automated infrastructure discovery, diagram generation, and incident response workflows.

## 🚀 **Quick Start**

### **1. Install n8n Integration**
```bash
# Install n8n CLI
npm install -g n8n

# Start n8n
n8n start

# Import CloudViz workflows
n8n import:workflow examples/n8n-workflows/daily-infrastructure-discovery.json
```

### **2. Configure CloudViz Webhook**
```javascript
// n8n CloudViz webhook node configuration
{
  "httpMethod": "POST",
  "path": "cloudviz-webhook",
  "responseMode": "responseNode",
  "authentication": "headerAuth",
  "nodeCredentialType": "cloudVizApi"
}
```

## 🔗 **Available Workflows**

### **1. Daily Infrastructure Discovery**

Automatically discovers infrastructure changes every day at 6 AM and generates updated diagrams.

**Workflow Features:**
- **Scheduled Trigger**: Daily at 6:00 AM UTC
- **Multi-Cloud Discovery**: Azure, AWS, and GCP in parallel
- **Change Detection**: Compares with previous day's results
- **Slack Notifications**: Sends alerts for significant changes
- **Diagram Generation**: Creates updated visualization diagrams
- **Cost Analysis**: Tracks spending changes

**Workflow JSON:**
```json
{
  "name": "Daily Infrastructure Discovery",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "cronExpression",
              "cronExpression": "0 6 * * *"
            }
          ]
        }
      },
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.cronTrigger"
    },
    {
      "parameters": {
        "requestMethod": "POST",
        "url": "={{$env.CLOUDVIZ_URL}}/azure/discover",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "cloudVizApi",
        "sendBody": true,
        "bodyContentType": "json",
        "jsonBody": "={\"subscription_id\": \"{{$env.AZURE_SUBSCRIPTION_ID}}\", \"regions\": [\"eastus\", \"westus2\"]}"
      },
      "name": "Azure Discovery",
      "type": "n8n-nodes-base.httpRequest"
    }
  ]
}
```

### **2. Incident Response Diagram**

Triggered by monitoring alerts to automatically generate current state diagrams for incident response.

**Workflow Features:**
- **Webhook Trigger**: Responds to monitoring alerts
- **Rapid Discovery**: Quick resource discovery in affected regions
- **Incident Diagram**: Generates focused diagram for incident scope
- **Team Notifications**: Sends diagrams to incident response channels
- **Historical Snapshot**: Stores pre-incident state for comparison

**Trigger Example:**
```bash
# Trigger incident response workflow
curl -X POST https://your-n8n.com/webhook/incident-response \
  -H "Content-Type: application/json" \
  -d '{
    "alert_id": "alert_001",
    "severity": "critical",
    "affected_services": ["web-tier", "database"],
    "region": "eastus"
  }'
```

### **3. Cost Threshold Alert**

Monitors infrastructure costs and triggers alerts when thresholds are exceeded.

**Workflow Features:**
- **Hourly Monitoring**: Checks costs every hour
- **Threshold Detection**: Configurable cost thresholds
- **Breakdown Analysis**: Identifies cost increases by service
- **Executive Reporting**: Sends cost reports to finance team
- **Automatic Optimization**: Suggests cost-saving measures

### **4. Compliance Audit**

Regular compliance checks with automated reporting.

**Workflow Features:**
- **Weekly Audits**: Comprehensive compliance scanning
- **Policy Validation**: Checks against security policies
- **Report Generation**: Creates compliance reports
- **Remediation Workflows**: Automated fix suggestions
- **Stakeholder Notifications**: Alerts compliance team

## 🛠️ **Custom Workflow Creation**

### **CloudViz n8n Nodes**

#### **Discovery Node**
```javascript
// CloudViz Discovery Node Configuration
{
  "displayName": "CloudViz Discovery",
  "name": "cloudVizDiscovery",
  "group": ["cloudviz"],
  "description": "Discover cloud infrastructure resources",
  "defaults": {
    "name": "CloudViz Discovery"
  },
  "inputs": ["main"],
  "outputs": ["main"],
  "credentials": [
    {
      "name": "cloudVizApi",
      "required": true
    }
  ],
  "properties": [
    {
      "displayName": "Provider",
      "name": "provider",
      "type": "options",
      "options": [
        {"name": "Azure", "value": "azure"},
        {"name": "AWS", "value": "aws"},
        {"name": "GCP", "value": "gcp"}
      ],
      "default": "azure"
    },
    {
      "displayName": "Regions",
      "name": "regions",
      "type": "collection",
      "placeholder": "Add Region",
      "multipleValues": true,
      "default": {},
      "options": [
        {
          "displayName": "Region",
          "name": "region",
          "type": "string",
          "default": ""
        }
      ]
    }
  ]
}
```

#### **Visualization Node**
```javascript
// CloudViz Visualization Node
{
  "displayName": "CloudViz Visualization",
  "name": "cloudVizVisualization",
  "group": ["cloudviz"],
  "description": "Generate infrastructure diagrams",
  "properties": [
    {
      "displayName": "Discovery IDs",
      "name": "discoveryIds",
      "type": "string",
      "default": "",
      "description": "Comma-separated discovery IDs"
    },
    {
      "displayName": "Layout",
      "name": "layout",
      "type": "options",
      "options": [
        {"name": "Hierarchical", "value": "hierarchical"},
        {"name": "Force Directed", "value": "force-directed"},
        {"name": "Circular", "value": "circular"}
      ],
      "default": "hierarchical"
    },
    {
      "displayName": "Theme",
      "name": "theme",
      "type": "options",
      "options": [
        {"name": "Enterprise", "value": "enterprise"},
        {"name": "Modern", "value": "modern"},
        {"name": "Minimal", "value": "minimal"}
      ],
      "default": "enterprise"
    }
  ]
}
```

### **Custom Workflow Template**

```json
{
  "name": "Custom CloudViz Workflow",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "custom-trigger"
      },
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "position": [240, 300]
    },
    {
      "parameters": {
        "provider": "azure",
        "regions": ["{{$node.Webhook.json.region}}"]
      },
      "name": "CloudViz Discovery",
      "type": "cloudVizDiscovery",
      "position": [460, 300]
    },
    {
      "parameters": {
        "discoveryIds": "={{$node['CloudViz Discovery'].json.discovery_id}}",
        "layout": "hierarchical",
        "theme": "enterprise"
      },
      "name": "Generate Diagram",
      "type": "cloudVizVisualization",
      "position": [680, 300]
    },
    {
      "parameters": {
        "channel": "#infrastructure",
        "text": "Infrastructure diagram updated",
        "attachments": [
          {
            "fields": [
              {
                "title": "Resources Found",
                "value": "={{$node['CloudViz Discovery'].json.resources_found}}",
                "short": true
              },
              {
                "title": "Cost Estimate",
                "value": "={{$node['CloudViz Discovery'].json.cost_estimate}}",
                "short": true
              }
            ]
          }
        ]
      },
      "name": "Slack Notification",
      "type": "n8n-nodes-base.slack",
      "position": [900, 300]
    }
  ],
  "connections": {
    "Webhook": {
      "main": [
        [
          {
            "node": "CloudViz Discovery",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "CloudViz Discovery": {
      "main": [
        [
          {
            "node": "Generate Diagram",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Generate Diagram": {
      "main": [
        [
          {
            "node": "Slack Notification",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

## 🔧 **Configuration**

### **Environment Variables**
```bash
# CloudViz API Configuration
CLOUDVIZ_URL=https://your-cloudviz-instance.com
CLOUDVIZ_API_TOKEN=your-jwt-token

# Cloud Provider Credentials
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret

AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-west-2

GCP_PROJECT_ID=your-project-id
GCP_SERVICE_ACCOUNT_PATH=/path/to/service-account.json

# Notification Settings
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
TEAMS_WEBHOOK_URL=https://your-org.webhook.office.com/...
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
```

### **n8n Credentials Setup**

#### **CloudViz API Credential**
```json
{
  "name": "CloudViz API",
  "displayName": "CloudViz API",
  "properties": [
    {
      "displayName": "API URL",
      "name": "url",
      "type": "string",
      "default": "https://your-cloudviz-instance.com"
    },
    {
      "displayName": "API Token",
      "name": "token",
      "type": "string",
      "typeOptions": {
        "password": true
      }
    }
  ],
  "authenticate": {
    "type": "generic",
    "properties": {
      "headers": {
        "Authorization": "Bearer {{$credentials.token}}"
      }
    }
  }
}
```

## 📊 **Monitoring & Analytics**

### **Workflow Metrics**
```javascript
// n8n workflow execution tracking
{
  "name": "Workflow Analytics",
  "trigger": "workflowExecuted",
  "nodes": [
    {
      "name": "Track Execution",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "{{$env.ANALYTICS_URL}}/workflow-execution",
        "method": "POST",
        "body": {
          "workflow_id": "{{$workflow.id}}",
          "execution_id": "{{$execution.id}}",
          "status": "{{$execution.status}}",
          "duration": "{{$execution.duration}}",
          "nodes_executed": "{{$execution.nodesExecuted}}"
        }
      }
    }
  ]
}
```

### **Error Handling**
```javascript
// Error handling workflow
{
  "name": "Error Handler",
  "trigger": "workflowError",
  "nodes": [
    {
      "name": "Log Error",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "{{$env.LOGGING_URL}}/error",
        "method": "POST",
        "body": {
          "workflow": "{{$workflow.name}}",
          "error": "{{$execution.error}}",
          "timestamp": "{{$now}}"
        }
      }
    },
    {
      "name": "Notify Team",
      "type": "n8n-nodes-base.slack",
      "parameters": {
        "channel": "#alerts",
        "text": "Workflow failed: {{$workflow.name}}"
      }
    }
  ]
}
```

## 🎯 **Use Cases**

### **1. DevOps Automation**
- **Infrastructure Changes**: Automatic discovery after deployments
- **Drift Detection**: Identify unauthorized changes
- **Compliance Monitoring**: Regular policy compliance checks
- **Cost Optimization**: Automated cost analysis and recommendations

### **2. Incident Response**
- **Real-time Diagrams**: Generate current state during incidents
- **Impact Analysis**: Visualize affected services and dependencies
- **Recovery Planning**: Create recovery workflow diagrams
- **Post-incident Reports**: Automated incident documentation

### **3. Business Intelligence**
- **Executive Dashboards**: Regular infrastructure cost reports
- **Capacity Planning**: Growth trend analysis and forecasting
- **Vendor Analysis**: Multi-cloud cost and performance comparison
- **Budget Alerts**: Proactive spending notifications

### **4. Security Operations**
- **Security Posture**: Regular security configuration audits
- **Threat Detection**: Infrastructure anomaly detection
- **Compliance Reporting**: Automated compliance documentation
- **Incident Correlation**: Link security events to infrastructure

## 🔗 **Integration Examples**

### **Slack Integration**
```javascript
// Slack notification with diagram
{
  "name": "Send Infrastructure Update",
  "type": "n8n-nodes-base.slack",
  "parameters": {
    "channel": "#infrastructure",
    "text": "Infrastructure discovered {{$node.Discovery.json.resources_found}} resources",
    "attachments": [
      {
        "title": "Cost Analysis",
        "color": "{{$node.Discovery.json.cost_estimate > 50000 ? 'danger' : 'good'}}",
        "fields": [
          {
            "title": "Total Cost",
            "value": "${{$node.Discovery.json.cost_estimate}}/month",
            "short": true
          },
          {
            "title": "Resources",
            "value": "{{$node.Discovery.json.resources_found}}",
            "short": true
          }
        ],
        "image_url": "{{$node.Diagram.json.diagram_url}}"
      }
    ]
  }
}
```

### **Microsoft Teams Integration**
```javascript
// Teams adaptive card
{
  "name": "Teams Notification",
  "type": "n8n-nodes-base.microsoftTeams",
  "parameters": {
    "webhook": "{{$credentials.teamsWebhook}}",
    "message": {
      "@type": "MessageCard",
      "summary": "Infrastructure Update",
      "sections": [
        {
          "activityTitle": "CloudViz Discovery Complete",
          "activitySubtitle": "{{$now}}",
          "facts": [
            {
              "name": "Resources Found",
              "value": "{{$node.Discovery.json.resources_found}}"
            },
            {
              "name": "Cost Estimate",
              "value": "${{$node.Discovery.json.cost_estimate}}/month"
            }
          ]
        }
      ]
    }
  }
}
```

### **JIRA Integration**
```javascript
// Create JIRA ticket for cost threshold breach
{
  "name": "Create JIRA Ticket",
  "type": "n8n-nodes-base.jira",
  "parameters": {
    "operation": "create",
    "issueType": "Task",
    "project": "INFRA",
    "summary": "Infrastructure cost threshold exceeded",
    "description": "Monthly cost estimate: ${{$node.Discovery.json.cost_estimate}}\\n\\nDiagram: {{$node.Diagram.json.diagram_url}}",
    "priority": "High",
    "assignee": "infrastructure-team"
  }
}
```

## 📚 **Best Practices**

### **1. Workflow Design**
- **Modular Design**: Create reusable sub-workflows
- **Error Handling**: Always include error handling nodes
- **Logging**: Log important events and decisions
- **Testing**: Test workflows in development environment

### **2. Security**
- **Credential Management**: Use n8n credential system
- **Network Security**: Secure n8n instance with VPN/firewall
- **Audit Logging**: Track workflow executions
- **Access Control**: Limit workflow editing permissions

### **3. Performance**
- **Parallel Processing**: Use parallel branches for independent tasks
- **Caching**: Cache expensive operations
- **Rate Limiting**: Respect API rate limits
- **Resource Management**: Monitor n8n resource usage

### **4. Maintenance**
- **Version Control**: Export workflows to git
- **Documentation**: Document workflow purpose and logic
- **Monitoring**: Set up workflow health monitoring
- **Updates**: Keep CloudViz and n8n updated

---

**Ready to automate your infrastructure workflows?** Check out our [Quick Start Guide](Quick-Start) or explore the [Examples](Integration-Examples) for more automation ideas! 🚀
