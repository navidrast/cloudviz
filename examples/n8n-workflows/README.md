# CloudViz n8n Integration Examples

This directory contains example n8n workflows that demonstrate how to integrate CloudViz with various automation and monitoring systems.

## Available Workflows

### 1. Daily Infrastructure Discovery (`daily-infrastructure-discovery.json`)
Automatically discovers and visualizes your infrastructure on a daily schedule.

**Features:**
- Scheduled daily execution
- Azure resource extraction
- Mermaid diagram generation
- PNG/Markdown file export
- Webhook notifications

**Use Cases:**
- Daily infrastructure reports
- Change tracking
- Compliance documentation
- Team dashboards

### 2. Incident Response Diagram (`incident-response-diagram.json`)
Generates infrastructure diagrams when incidents are detected for rapid impact analysis.

**Features:**
- Webhook-triggered execution
- Severity-based filtering
- Affected resource analysis
- Alert-themed visualizations
- Multi-channel notifications (Slack, Email)

**Use Cases:**
- Incident response automation
- Impact analysis visualization
- Alert enrichment
- Post-incident documentation

## Prerequisites

1. **CloudViz API Access:**
   - CloudViz server running and accessible
   - Valid authentication credentials
   - API endpoint URL

2. **n8n Environment:**
   - n8n instance (cloud or self-hosted)
   - Required environment variables configured
   - Webhook endpoints accessible

3. **Integration Services:**
   - Slack webhook URL (for notifications)
   - Email server configuration
   - File storage access

## Environment Variables

Configure these environment variables in your n8n instance:

```bash
# CloudViz Configuration
CLOUDVIZ_API_URL=https://your-cloudviz-instance.com
CLOUDVIZ_USERNAME=your-username
CLOUDVIZ_PASSWORD=your-password

# Azure Configuration (for Azure workflows)
AZURE_SUBSCRIPTION_ID=your-subscription-id

# n8n Configuration
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook

# Notification Configuration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your/slack/webhook
INCIDENT_EMAIL=incidents@your-company.com
```

## Installation Instructions

### Import Workflows

1. **Access n8n Interface:**
   - Open your n8n instance
   - Navigate to "Workflows"

2. **Import Workflow:**
   - Click "Import from file"
   - Select the desired `.json` file
   - Review and save the workflow

3. **Configure Credentials:**
   - Set up required credentials
   - Configure webhook URLs
   - Test connections

### Configure Webhooks

1. **Copy Webhook URLs:**
   ```bash
   # From your n8n workflow
   https://your-n8n-instance.com/webhook/extraction-complete
   https://your-n8n-instance.com/webhook/incident-alert
   ```

2. **Configure CloudViz Webhooks:**
   - Update CloudViz configuration
   - Set webhook endpoints for job completion
   - Test webhook delivery

### Test Workflows

1. **Manual Trigger:**
   - Use n8n test execution
   - Verify API connections
   - Check output formats

2. **End-to-End Testing:**
   - Trigger actual workflows
   - Verify notifications
   - Validate file outputs

## Customization Guide

### Modifying Extraction Parameters

```json
{
  "resource_types": ["VirtualMachine", "Database", "StorageAccount"],
  "include_metadata": true,
  "filter_criteria": {
    "tags": {"environment": "production"},
    "region": "eastus"
  }
}
```

### Customizing Visualization Themes

```json
{
  "theme": "professional",      // Options: default, professional, corporate, minimal, alert
  "layout": "hierarchical",     // Options: hierarchical, circular, force, grid, timeline
  "include_metadata": true,
  "annotations": {
    "resource-id": "Custom annotation"
  }
}
```

### Adding Custom Notifications

```javascript
// Slack notification customization
{
  "text": "🔍 *Infrastructure Discovery Complete*\n\nResources Found: {{$json.resource_count}}\nRegions: {{$json.regions}}\nDiagram: {{$json.diagram_url}}",
  "attachments": [
    {
      "color": "good",
      "fields": [
        {
          "title": "Execution Time",
          "value": "{{DateTime.now().toISO()}}",
          "short": true
        }
      ]
    }
  ]
}
```

## Advanced Workflows

### Multi-Cloud Discovery
Combine multiple cloud providers in a single workflow:

```json
{
  "parallel_extractions": [
    {"provider": "azure", "subscription": "azure-sub-id"},
    {"provider": "aws", "account": "aws-account-id"},
    {"provider": "gcp", "project": "gcp-project-id"}
  ]
}
```

### Conditional Visualization
Generate different diagrams based on conditions:

```javascript
// Conditional logic in n8n
if (resourceCount > 100) {
  theme = "minimal";
  layout = "grid";
} else {
  theme = "professional";
  layout = "hierarchical";
}
```

### Scheduled Reports
Create comprehensive reporting workflows:

```json
{
  "schedule": "0 6 * * 1",  // Every Monday at 6 AM
  "report_types": ["summary", "detailed", "compliance"],
  "recipients": ["team@company.com", "management@company.com"],
  "formats": ["pdf", "png", "mermaid"]
}
```

## Troubleshooting

### Common Issues

1. **Authentication Failures:**
   - Verify CloudViz credentials
   - Check API endpoint accessibility
   - Validate token expiration

2. **Webhook Timeouts:**
   - Increase n8n timeout settings
   - Check CloudViz processing time
   - Implement retry logic

3. **Large Diagram Rendering:**
   - Reduce resource scope
   - Use minimal themes
   - Implement pagination

### Error Handling

```javascript
// Example error handling in n8n
try {
  const response = await this.helpers.httpRequest(options);
  return response;
} catch (error) {
  // Log error and send notification
  await this.helpers.httpRequest({
    url: process.env.SLACK_WEBHOOK_URL,
    method: 'POST',
    body: {
      text: `❌ CloudViz workflow failed: ${error.message}`
    }
  });
  throw error;
}
```

## Performance Optimization

### Best Practices

1. **Resource Filtering:**
   - Use specific resource types
   - Apply region/tag filters
   - Limit extraction depth

2. **Caching Strategy:**
   - Cache authentication tokens
   - Store intermediate results
   - Use conditional execution

3. **Parallel Processing:**
   - Split large extractions
   - Process regions in parallel
   - Batch API calls

### Monitoring

```javascript
// Workflow performance tracking
const startTime = Date.now();
// ... workflow execution ...
const executionTime = Date.now() - startTime;

// Send metrics to monitoring system
await this.helpers.httpRequest({
  url: 'https://your-metrics-endpoint.com',
  method: 'POST',
  body: {
    workflow: 'cloudviz-discovery',
    execution_time: executionTime,
    resource_count: resourceCount,
    timestamp: new Date().toISOString()
  }
});
```

## Support and Documentation

- **CloudViz API Documentation:** [API Docs](../README.md#api-endpoints)
- **n8n Documentation:** [n8n.io/docs](https://docs.n8n.io/)
- **Mermaid Syntax:** [mermaid.js.org](https://mermaid.js.org/)

For additional examples and support, please refer to the main CloudViz documentation or contact the development team.
