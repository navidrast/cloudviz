# CloudViz n8n Integration Guide

Complete guide for integrating CloudViz with n8n workflow automation platform, including pre-built workflows, custom automation scenarios, and advanced integration patterns.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation and Setup](#installation-and-setup)
4. [Available Workflows](#available-workflows)
5. [Custom Workflow Examples](#custom-workflow-examples)
6. [Advanced Integration Patterns](#advanced-integration-patterns)
7. [Authentication and Security](#authentication-and-security)
8. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

## Overview

CloudViz provides comprehensive integration with n8n, enabling automated infrastructure management workflows including:

- **Scheduled Infrastructure Discovery**: Automated resource discovery and inventory updates
- **Change Detection and Alerting**: Real-time notifications for infrastructure changes
- **Incident Response Automation**: Automatic diagram generation during incidents
- **Compliance Monitoring**: Scheduled compliance checks and reporting
- **Cost Optimization**: Automated cost analysis and alerts
- **Multi-Cloud Orchestration**: Coordinated operations across cloud providers

### Integration Benefits

- **Zero-Code Automation**: Visual workflow builder with drag-and-drop interface
- **200+ Pre-built Integrations**: Connect CloudViz with Slack, Teams, email, databases, and more
- **Custom Logic**: Advanced conditional workflows and data processing
- **Scalable Execution**: Parallel processing and queue management
- **Error Handling**: Robust retry mechanisms and error notifications

## Prerequisites

### Required Software
- **n8n**: Version 1.0+ (latest recommended)
- **Node.js**: Version 16+ 
- **CloudViz**: Running instance with API access
- **Docker** (recommended for production deployments)

### Cloud Provider Access
- Active subscriptions and credentials for target cloud providers
- Appropriate permissions for resource discovery and monitoring

### External Services (Optional)
- **Slack/Microsoft Teams**: For notifications
- **SMTP Server**: For email alerts
- **Database**: For storing workflow results and history

## Installation and Setup

### Method 1: Docker Compose (Recommended)

Create `docker-compose.n8n.yml`:
```yaml
version: '3.8'

services:
  n8n:
    image: n8nio/n8n:latest
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=n8n
      - DB_POSTGRESDB_PASSWORD=n8n
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=changeme
      - WEBHOOK_URL=https://your-domain.com/
      - GENERIC_TIMEZONE=UTC
    volumes:
      - n8n_data:/home/node/.n8n
      - ./n8n-workflows:/home/node/.n8n/workflows
    depends_on:
      - postgres
    networks:
      - cloudviz-network

  postgres:
    image: postgres:13
    restart: unless-stopped
    environment:
      - POSTGRES_DB=n8n
      - POSTGRES_USER=n8n
      - POSTGRES_PASSWORD=n8n
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - cloudviz-network

volumes:
  n8n_data:
  postgres_data:

networks:
  cloudviz-network:
    external: true
```

Start the services:
```bash
docker-compose -f docker-compose.n8n.yml up -d
```

### Method 2: Local Installation

```bash
# Install n8n globally
npm install -g n8n

# Start n8n
n8n start

# Access n8n interface
open http://localhost:5678
```

### Method 3: Kubernetes Deployment

Create `k8s-n8n-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: n8n
  namespace: cloudviz
spec:
  replicas: 1
  selector:
    matchLabels:
      app: n8n
  template:
    metadata:
      labels:
        app: n8n
    spec:
      containers:
      - name: n8n
        image: n8nio/n8n:latest
        ports:
        - containerPort: 5678
        env:
        - name: DB_TYPE
          value: "postgresdb"
        - name: DB_POSTGRESDB_HOST
          value: "postgres-service"
        - name: N8N_BASIC_AUTH_ACTIVE
          value: "true"
        - name: N8N_BASIC_AUTH_USER
          valueFrom:
            secretKeyRef:
              name: n8n-secret
              key: username
        - name: N8N_BASIC_AUTH_PASSWORD
          valueFrom:
            secretKeyRef:
              name: n8n-secret
              key: password
        volumeMounts:
        - name: n8n-data
          mountPath: /home/node/.n8n
      volumes:
      - name: n8n-data
        persistentVolumeClaim:
          claimName: n8n-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: n8n-service
  namespace: cloudviz
spec:
  selector:
    app: n8n
  ports:
  - port: 5678
    targetPort: 5678
  type: LoadBalancer
```

### Initial Configuration

1. **Access n8n Interface**: Navigate to http://localhost:5678
2. **Set up Authentication**: Configure basic auth or OAuth
3. **Install CloudViz Credentials**: Add CloudViz API credentials
4. **Import Workflows**: Load pre-built CloudViz workflows

## Available Workflows

### 1. Daily Infrastructure Discovery

**Purpose**: Automated daily discovery of infrastructure resources across all cloud providers

**Schedule**: Daily at 6:00 AM UTC

**Features**:
- Multi-cloud parallel discovery (Azure, AWS, GCP)
- Change detection and comparison
- Automated diagram generation
- Slack/Teams notifications
- Cost analysis and trending

**Workflow Configuration**:
```json
{
  "name": "Daily Infrastructure Discovery",
  "active": true,
  "nodes": [
    {
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.cron",
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "cronExpression",
              "expression": "0 6 * * *"
            }
          ]
        }
      }
    },
    {
      "name": "Parallel Discovery",
      "type": "n8n-nodes-base.splitInBatches",
      "parameters": {
        "batchSize": 3,
        "options": {}
      }
    },
    {
      "name": "Azure Discovery",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "={{$env.CLOUDVIZ_URL}}/api/v1/extract/azure",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "cloudVizApi",
        "method": "POST",
        "body": {
          "subscription_id": "={{$env.AZURE_SUBSCRIPTION_ID}}",
          "resource_groups": "all",
          "include_tags": true,
          "include_cost_data": true
        }
      }
    },
    {
      "name": "AWS Discovery",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "={{$env.CLOUDVIZ_URL}}/api/v1/extract/aws",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "cloudVizApi",
        "method": "POST",
        "body": {
          "regions": ["us-east-1", "us-west-2", "eu-west-1"],
          "include_cost_data": true
        }
      }
    },
    {
      "name": "GCP Discovery",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "={{$env.CLOUDVIZ_URL}}/api/v1/extract/gcp",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "cloudVizApi",
        "method": "POST",
        "body": {
          "project_id": "={{$env.GCP_PROJECT_ID}}",
          "include_cost_data": true
        }
      }
    },
    {
      "name": "Merge Results",
      "type": "n8n-nodes-base.merge",
      "parameters": {
        "mode": "combine",
        "combineBy": "combineAll"
      }
    },
    {
      "name": "Generate Diagram",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "={{$env.CLOUDVIZ_URL}}/api/v1/render",
        "authentication": "predefinedCredentialType",
        "nodeCredentialType": "cloudVizApi",
        "method": "POST",
        "body": {
          "format": "mermaid",
          "theme": "professional",
          "layout": "hierarchical",
          "group_by": "provider"
        }
      }
    },
    {
      "name": "Slack Notification",
      "type": "n8n-nodes-base.slack",
      "parameters": {
        "channel": "#infrastructure",
        "text": "Daily infrastructure discovery completed",
        "attachments": [
          {
            "color": "good",
            "title": "Infrastructure Discovery Report",
            "fields": [
              {
                "title": "Total Resources",
                "value": "={{$json.total_resources}}",
                "short": true
              },
              {
                "title": "Changes",
                "value": "={{$json.changes_detected}}",
                "short": true
              }
            ]
          }
        ]
      }
    }
  ],
  "connections": {
    "Schedule Trigger": {
      "main": [
        [
          {
            "node": "Parallel Discovery",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

### 2. Incident Response Diagram Generation

**Purpose**: Automatically generates infrastructure diagrams during incident response

**Trigger**: Webhook from monitoring system (PagerDuty, Datadog, etc.)

**Features**:
- Immediate diagram generation for affected resources
- Automated incident documentation
- Team notifications with diagrams
- Historical incident tracking

**Usage Example**:
```bash
# Trigger from PagerDuty webhook
curl -X POST https://your-n8n-instance.com/webhook/incident-response \
  -H "Content-Type: application/json" \
  -d '{
    "incident_id": "INC-12345",
    "affected_services": ["web-app", "database"],
    "severity": "high",
    "description": "Database connection timeout"
  }'
```

### 3. Compliance Monitoring

**Purpose**: Scheduled compliance checks and reporting

**Schedule**: Weekly on Sunday at 2:00 AM UTC

**Features**:
- Security group analysis
- Public IP exposure detection
- Encryption status verification
- Compliance report generation
- Automated remediation suggestions

### 4. Cost Optimization Alerts

**Purpose**: Monitor and alert on unexpected cost increases

**Schedule**: Daily at 8:00 AM UTC

**Features**:
- Daily cost analysis
- Anomaly detection
- Resource optimization suggestions
- Executive dashboard updates

### 5. Resource Lifecycle Management

**Purpose**: Automated resource cleanup and optimization

**Schedule**: Weekly on Saturday at 1:00 AM UTC

**Features**:
- Identify unused resources
- Suggest rightsizing opportunities
- Generate cleanup recommendations
- Automated tagging compliance

## Custom Workflow Examples

### 1. Multi-Environment Comparison

Compare infrastructure between development, staging, and production environments:

```json
{
  "name": "Environment Comparison",
  "nodes": [
    {
      "name": "Manual Trigger",
      "type": "n8n-nodes-base.manualTrigger"
    },
    {
      "name": "Extract Production",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "={{$env.CLOUDVIZ_URL}}/api/v1/extract/azure",
        "method": "POST",
        "body": {
          "subscription_id": "={{$env.AZURE_PROD_SUBSCRIPTION}}",
          "resource_groups": ["prod-*"]
        }
      }
    },
    {
      "name": "Extract Staging",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "={{$env.CLOUDVIZ_URL}}/api/v1/extract/azure",
        "method": "POST",
        "body": {
          "subscription_id": "={{$env.AZURE_STAGING_SUBSCRIPTION}}",
          "resource_groups": ["staging-*"]
        }
      }
    },
    {
      "name": "Compare Environments",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "={{$env.CLOUDVIZ_URL}}/api/v1/compare",
        "method": "POST",
        "body": {
          "baseline_inventory": "={{$node['Extract Production'].json.inventory_id}}",
          "comparison_inventory": "={{$node['Extract Staging'].json.inventory_id}}"
        }
      }
    }
  ]
}
```

### 2. Security Audit Automation

Automated security assessment workflow:

```json
{
  "name": "Security Audit",
  "nodes": [
    {
      "name": "Weekly Schedule",
      "type": "n8n-nodes-base.cron",
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "cronExpression", 
              "expression": "0 2 * * 0"
            }
          ]
        }
      }
    },
    {
      "name": "Security Scan",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "={{$env.CLOUDVIZ_URL}}/api/v1/extract/azure",
        "method": "POST",
        "body": {
          "include_security_info": true,
          "include_compliance_status": true,
          "security_focus": true
        }
      }
    },
    {
      "name": "Analyze Security",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "// Custom security analysis logic\nconst resources = items[0].json.resources;\nconst securityIssues = [];\n\nresources.forEach(resource => {\n  if (resource.public_ip && !resource.firewall_rules) {\n    securityIssues.push({\n      resource_id: resource.id,\n      issue: 'Public IP without firewall',\n      severity: 'high'\n    });\n  }\n});\n\nreturn [{json: {security_issues: securityIssues}}];"
        }
      }
    },
    {
      "name": "Security Report",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "={{$env.CLOUDVIZ_URL}}/api/v1/render",
        "method": "POST",
        "body": {
          "format": "mermaid",
          "theme": "security",
          "highlight_security_issues": true
        }
      }
    }
  ]
}
```

### 3. Disaster Recovery Testing

Automated DR readiness validation:

```json
{
  "name": "DR Readiness Check",
  "nodes": [
    {
      "name": "Monthly Trigger",
      "type": "n8n-nodes-base.cron",
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "cronExpression",
              "expression": "0 0 1 * *"
            }
          ]
        }
      }
    },
    {
      "name": "Primary Region Scan",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "={{$env.CLOUDVIZ_URL}}/api/v1/extract/aws",
        "method": "POST",
        "body": {
          "regions": ["us-east-1"],
          "include_backup_info": true,
          "include_replication_status": true
        }
      }
    },
    {
      "name": "DR Region Scan",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "={{$env.CLOUDVIZ_URL}}/api/v1/extract/aws",
        "method": "POST",
        "body": {
          "regions": ["us-west-2"],
          "include_backup_info": true,
          "include_replication_status": true
        }
      }
    },
    {
      "name": "DR Analysis",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "// DR readiness analysis\nconst primary = items[0].json;\nconst dr = items[1].json;\n\nconst drReadiness = {\n  backup_coverage: calculateBackupCoverage(primary, dr),\n  rto_compliance: checkRTOCompliance(primary, dr),\n  rpo_compliance: checkRPOCompliance(primary, dr)\n};\n\nreturn [{json: drReadiness}];"
        }
      }
    }
  ]
}
```

## Advanced Integration Patterns

### 1. Multi-Cloud Orchestration

Coordinate operations across multiple cloud providers:

```json
{
  "name": "Multi-Cloud Resource Provisioning",
  "nodes": [
    {
      "name": "Webhook Trigger",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "provision-resources",
        "httpMethod": "POST"
      }
    },
    {
      "name": "Validate Request",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "// Validate provisioning request\nconst request = items[0].json;\nif (!request.environment || !request.resource_specs) {\n  throw new Error('Invalid request format');\n}\nreturn items;"
        }
      }
    },
    {
      "name": "Azure Provisioning",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "={{$env.CLOUDVIZ_URL}}/api/v1/provision/azure",
        "method": "POST"
      }
    },
    {
      "name": "AWS Provisioning",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "={{$env.CLOUDVIZ_URL}}/api/v1/provision/aws",
        "method": "POST"
      }
    },
    {
      "name": "Update Inventory",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "={{$env.CLOUDVIZ_URL}}/api/v1/extract/all",
        "method": "POST"
      }
    }
  ]
}
```

### 2. Event-Driven Architecture

React to cloud events in real-time:

```json
{
  "name": "Cloud Event Handler",
  "nodes": [
    {
      "name": "Event Grid Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "azure-events",
        "httpMethod": "POST"
      }
    },
    {
      "name": "Parse Event",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "// Parse Azure Event Grid event\nconst event = items[0].json;\nconst eventType = event.eventType;\nconst resourceId = event.data.resourceUri;\n\nreturn [{\n  json: {\n    event_type: eventType,\n    resource_id: resourceId,\n    timestamp: event.eventTime\n  }\n}];"
        }
      }
    },
    {
      "name": "Update Diagram",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "={{$env.CLOUDVIZ_URL}}/api/v1/extract/resource",
        "method": "POST",
        "body": {
          "resource_id": "={{$json.resource_id}}"
        }
      }
    }
  ]
}
```

### 3. Continuous Compliance Monitoring

Real-time compliance validation:

```json
{
  "name": "Continuous Compliance",
  "nodes": [
    {
      "name": "Resource Change Event",
      "type": "n8n-nodes-base.webhook"
    },
    {
      "name": "Compliance Check",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "={{$env.CLOUDVIZ_URL}}/api/v1/compliance/check",
        "method": "POST"
      }
    },
    {
      "name": "Non-Compliant?",
      "type": "n8n-nodes-base.if",
      "parameters": {
        "conditions": {
          "boolean": [
            {
              "value1": "={{$json.compliant}}",
              "value2": false
            }
          ]
        }
      }
    },
    {
      "name": "Alert Security Team",
      "type": "n8n-nodes-base.slack",
      "parameters": {
        "channel": "#security-alerts",
        "text": "Compliance violation detected"
      }
    }
  ]
}
```

## Authentication and Security

### CloudViz API Credentials

Set up CloudViz API credentials in n8n:

1. **Navigate to Credentials**: Settings > Credentials
2. **Create New Credential**: Click "Add Credential"
3. **Select HTTP Header Auth**:
   ```json
   {
     "name": "CloudViz API",
     "headerAuth": {
       "name": "Authorization",
       "value": "Bearer {{$env.CLOUDVIZ_API_TOKEN}}"
     }
   }
   ```

### Environment Variables

Configure secure environment variables:

```bash
# CloudViz Configuration
CLOUDVIZ_URL=https://your-cloudviz-instance.com
CLOUDVIZ_API_TOKEN=your-secure-api-token

# Cloud Provider Credentials
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_SUBSCRIPTION_ID=your-subscription-id

AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=us-east-1

GCP_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Notification Services
SLACK_WEBHOOK_URL=your-slack-webhook-url
TEAMS_WEBHOOK_URL=your-teams-webhook-url
SMTP_HOST=your-smtp-server
SMTP_USER=your-smtp-username
SMTP_PASS=your-smtp-password
```

### Security Best Practices

1. **Use HTTPS**: Always use HTTPS for webhook endpoints
2. **Validate Webhooks**: Implement signature validation for external webhooks
3. **Rotate Credentials**: Regularly rotate API keys and tokens
4. **Limit Permissions**: Use principle of least privilege for service accounts
5. **Monitor Access**: Log and monitor all workflow executions

## Monitoring and Troubleshooting

### Workflow Monitoring

Monitor workflow execution and performance:

```json
{
  "name": "Workflow Monitor",
  "nodes": [
    {
      "name": "Schedule Monitor",
      "type": "n8n-nodes-base.cron",
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "cronExpression",
              "expression": "*/15 * * * *"
            }
          ]
        }
      }
    },
    {
      "name": "Check Workflow Status",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "url": "={{$env.N8N_URL}}/api/v1/executions",
        "method": "GET",
        "headers": {
          "Authorization": "Bearer {{$env.N8N_API_TOKEN}}"
        }
      }
    },
    {
      "name": "Failed Workflows?",
      "type": "n8n-nodes-base.if",
      "parameters": {
        "conditions": {
          "number": [
            {
              "value1": "={{$json.failed_count}}",
              "operation": "larger",
              "value2": 0
            }
          ]
        }
      }
    },
    {
      "name": "Alert on Failures",
      "type": "n8n-nodes-base.slack",
      "parameters": {
        "channel": "#devops-alerts",
        "text": "n8n workflow failures detected"
      }
    }
  ]
}
```

### Error Handling

Implement robust error handling:

```json
{
  "name": "Error Handling Example",
  "nodes": [
    {
      "name": "CloudViz API Call",
      "type": "n8n-nodes-base.httpRequest",
      "onError": "continueRegularOutput",
      "parameters": {
        "url": "={{$env.CLOUDVIZ_URL}}/api/v1/extract/azure"
      }
    },
    {
      "name": "Check for Errors",
      "type": "n8n-nodes-base.if",
      "parameters": {
        "conditions": {
          "boolean": [
            {
              "value1": "={{$json.error}}",
              "value2": true
            }
          ]
        }
      }
    },
    {
      "name": "Retry Logic",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "// Implement exponential backoff\nconst maxRetries = 3;\nconst baseDelay = 1000;\nconst retryCount = $json.retry_count || 0;\n\nif (retryCount < maxRetries) {\n  const delay = baseDelay * Math.pow(2, retryCount);\n  setTimeout(() => {\n    // Retry the operation\n  }, delay);\n}\n\nreturn items;"
        }
      }
    }
  ]
}
```

### Logging and Debugging

Enable comprehensive logging:

```json
{
  "name": "Debug Workflow",
  "nodes": [
    {
      "name": "Log Input",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "console.log('Workflow input:', JSON.stringify(items, null, 2));\nreturn items;"
      }
    },
    {
      "name": "Main Logic",
      "type": "n8n-nodes-base.httpRequest"
    },
    {
      "name": "Log Output",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "console.log('Workflow output:', JSON.stringify(items, null, 2));\nreturn items;"
      }
    }
  ]
}
```

## Best Practices

### 1. Workflow Design

- **Modular Design**: Create reusable sub-workflows
- **Error Handling**: Implement comprehensive error handling
- **Monitoring**: Add monitoring and alerting to critical workflows
- **Documentation**: Document workflow purpose and configuration
- **Testing**: Test workflows in development before production deployment

### 2. Performance Optimization

- **Parallel Processing**: Use parallel execution where possible
- **Caching**: Cache frequently accessed data
- **Batch Operations**: Process multiple items in batches
- **Resource Limits**: Set appropriate timeout and memory limits
- **Queue Management**: Use queues for high-volume operations

### 3. Security Considerations

- **Credential Management**: Use secure credential storage
- **Network Security**: Implement proper network security
- **Access Control**: Limit workflow execution permissions
- **Audit Logging**: Maintain comprehensive audit logs
- **Regular Updates**: Keep n8n and dependencies updated

### 4. Maintenance and Operations

- **Version Control**: Version control workflow definitions
- **Backup**: Regular backup of workflow configurations
- **Monitoring**: Monitor workflow execution and performance
- **Documentation**: Maintain up-to-date documentation
- **Testing**: Regular testing of critical workflows

## Troubleshooting

### Common Issues

#### 1. Authentication Failures

**Problem**: CloudViz API authentication failing
```json
{
  "error": "Authentication failed",
  "code": 401
}
```

**Solution**:
```bash
# Verify API token
curl -H "Authorization: Bearer $CLOUDVIZ_API_TOKEN" \
  $CLOUDVIZ_URL/api/v1/health

# Update n8n credentials if needed
```

#### 2. Webhook Timeout Issues

**Problem**: Webhooks timing out during long operations
```json
{
  "error": "Request timeout",
  "timeout": 30000
}
```

**Solution**:
```json
{
  "name": "Async Webhook Handler",
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "responseMode": "onReceived",
        "responseData": "firstEntryJson",
        "options": {
          "asyncResponse": true
        }
      }
    },
    {
      "name": "Background Processing",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "timeout": 300000
      }
    }
  ]
}
```

#### 3. Memory Issues with Large Datasets

**Problem**: Out of memory errors with large inventories
```json
{
  "error": "JavaScript heap out of memory"
}
```

**Solution**:
```json
{
  "name": "Batch Processing",
  "nodes": [
    {
      "name": "Split in Batches",
      "type": "n8n-nodes-base.splitInBatches",
      "parameters": {
        "batchSize": 100
      }
    },
    {
      "name": "Process Batch",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "// Process items in smaller batches\nconst processedItems = items.map(item => {\n  return processItem(item);\n});\n\nreturn processedItems;"
        }
      }
    }
  ]
}
```

### Debugging Tips

1. **Use Debug Mode**: Enable debug logging in n8n
2. **Test Individual Nodes**: Test nodes individually before full workflow
3. **Check Logs**: Review n8n and CloudViz logs for errors
4. **Validate Data**: Verify data format between nodes
5. **Network Connectivity**: Ensure network connectivity between services

### Getting Help

- **n8n Community**: https://community.n8n.io/
- **CloudViz Documentation**: [API Reference](API-Reference.md)
- **GitHub Issues**: Report bugs and feature requests
- **Discord Support**: Join our Discord community

For additional workflow examples and templates, see the [n8n Workflows Directory](../examples/n8n-workflows/) in the repository.
