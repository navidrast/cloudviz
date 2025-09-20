# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with CloudViz.

## 🚨 Common Issues

### 1. Installation Problems

#### Problem: Dependencies fail to install
```bash
ERROR: Could not find a version that satisfies the requirement google-cloud-sql
```

**Solutions:**
```bash
# Solution 1: Update pip
pip install --upgrade pip

# Solution 2: Use specific Python version
python3.9 -m pip install -r requirements.txt

# Solution 3: Install without problematic dependencies
pip install -r requirements.txt --ignore-installed
```

#### Problem: Docker container won't start
```bash
docker: Error response from daemon: port is already allocated
```

**Solutions:**
```bash
# Check what's using the port
lsof -i :8000
netstat -tulpn | grep :8000

# Use different port
docker run -p 8080:8000 cloudviz:latest

# Stop conflicting service
docker stop $(docker ps -q --filter "publish=8000")
```

### 2. Authentication Issues

#### Problem: Azure authentication fails
```json
{
  "error": "AUTHENTICATION_FAILED",
  "message": "Invalid Azure credentials"
}
```

**Diagnosis:**
```bash
# Check environment variables
echo $AZURE_CLIENT_ID
echo $AZURE_TENANT_ID

# Test Azure CLI authentication
az account show
az account list

# Test service principal
az login --service-principal \
  --username $AZURE_CLIENT_ID \
  --password $AZURE_CLIENT_SECRET \
  --tenant $AZURE_TENANT_ID
```

**Solutions:**
```bash
# Recreate service principal
az ad sp create-for-rbac --name cloudviz-sp --role Contributor

# Check required permissions
az role assignment list --assignee $AZURE_CLIENT_ID

# Update environment variables
export AZURE_CLIENT_ID=new-client-id
export AZURE_CLIENT_SECRET=new-client-secret
```

#### Problem: AWS authentication fails
```json
{
  "error": "AWS_AUTH_ERROR",
  "message": "Unable to locate credentials"
}
```

**Diagnosis:**
```bash
# Check AWS credentials
aws sts get-caller-identity
aws configure list

# Check environment variables
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
```

**Solutions:**
```bash
# Configure AWS credentials
aws configure

# Use IAM role (if on EC2)
# Remove AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY

# Check permissions
aws iam get-user
aws iam list-attached-user-policies --user-name your-user
```

#### Problem: GCP authentication fails
```json
{
  "error": "GCP_AUTH_ERROR",
  "message": "Service account key not found"
}
```

**Diagnosis:**
```bash
# Check service account file
ls -la $GOOGLE_APPLICATION_CREDENTIALS
cat $GOOGLE_APPLICATION_CREDENTIALS | jq .

# Test gcloud authentication
gcloud auth list
gcloud auth application-default print-access-token
```

**Solutions:**
```bash
# Create new service account key
gcloud iam service-accounts keys create key.json \
  --iam-account=cloudviz@project.iam.gserviceaccount.com

# Set correct environment variable
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json

# Activate service account
gcloud auth activate-service-account \
  --key-file=$GOOGLE_APPLICATION_CREDENTIALS
```

### 3. API Issues

#### Problem: API returns 500 errors
```json
{
  "error": "INTERNAL_ERROR",
  "message": "An internal server error occurred"
}
```

**Diagnosis:**
```bash
# Check CloudViz logs
docker logs cloudviz
tail -f /var/log/cloudviz/api.log

# Check system resources
free -h
df -h
top
```

**Solutions:**
```bash
# Restart the service
docker restart cloudviz
systemctl restart cloudviz

# Check configuration
cat config/production.yml
python -c "import yaml; print(yaml.safe_load(open('config/production.yml')))"

# Enable debug logging
export CLOUDVIZ_LOG_LEVEL=DEBUG
```

#### Problem: Rate limit exceeded
```json
{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "API rate limit exceeded. Try again in 60 seconds"
}
```

**Solutions:**
```bash
# Wait for rate limit reset
sleep 60

# Use different API key
export CLOUDVIZ_API_KEY=different-key

# Configure higher rate limits (if self-hosted)
# Edit config/production.yml:
# rate_limiting:
#   requests_per_minute: 200
```

### 4. Resource Discovery Issues

#### Problem: No resources found
```json
{
  "resources": [],
  "total": 0
}
```

**Diagnosis:**
```bash
# Check permissions
# Azure
az resource list --subscription $AZURE_SUBSCRIPTION_ID

# AWS
aws ec2 describe-instances
aws rds describe-db-instances

# GCP
gcloud compute instances list
gcloud sql instances list
```

**Solutions:**
```bash
# Verify subscription/account IDs
# Azure
az account show --subscription $AZURE_SUBSCRIPTION_ID

# AWS
aws sts get-caller-identity

# GCP
gcloud config get-value project

# Check resource group/region filters
curl -X POST http://localhost:8000/api/v1/azure/extract \
  -d '{"subscription_id": "'$AZURE_SUBSCRIPTION_ID'", "resource_groups": null}'
```

#### Problem: Partial resource discovery
```json
{
  "resources": 5,
  "errors": ["Failed to discover SQL databases", "Network timeout"]
}
```

**Solutions:**
```bash
# Increase timeout
export CLOUDVIZ_TIMEOUT=600

# Retry specific resource types
curl -X POST http://localhost:8000/api/v1/azure/extract \
  -d '{"resource_types": ["VirtualMachine", "StorageAccount"]}'

# Check network connectivity
ping management.azure.com
ping ec2.amazonaws.com
ping compute.googleapis.com
```

### 5. Visualization Issues

#### Problem: Diagram generation fails
```json
{
  "error": "DIAGRAM_GENERATION_FAILED",
  "message": "Failed to generate Mermaid diagram"
}
```

**Diagnosis:**
```bash
# Check available resources
curl http://localhost:8000/api/v1/resources

# Check diagram request
curl -X POST http://localhost:8000/api/v1/visualization/generate \
  -d '{"providers": ["azure"], "format": "mermaid"}'
```

**Solutions:**
```bash
# Reduce resource count
curl -X POST http://localhost:8000/api/v1/visualization/generate \
  -d '{
    "providers": ["azure"],
    "format": "mermaid",
    "filters": {"resource_types": ["VirtualMachine"]}
  }'

# Use simpler layout
curl -X POST http://localhost:8000/api/v1/visualization/generate \
  -d '{"layout": "simple", "include_dependencies": false}'
```

#### Problem: Diagram export fails
```bash
curl http://localhost:8000/api/v1/visualization/export/diagram-123?format=png
# Returns 404 Not Found
```

**Solutions:**
```bash
# Check if diagram exists
curl http://localhost:8000/api/v1/visualization/diagrams

# Check diagram ID
curl http://localhost:8000/api/v1/visualization/export/diagram-123?format=mermaid

# Regenerate diagram if needed
curl -X POST http://localhost:8000/api/v1/visualization/generate \
  -d '{"providers": ["azure"]}'
```

### 6. Performance Issues

#### Problem: Slow resource discovery
```bash
# Takes > 10 minutes to discover resources
```

**Diagnosis:**
```bash
# Check CloudViz performance metrics
curl http://localhost:8000/metrics

# Monitor system resources
htop
iotop
```

**Solutions:**
```bash
# Increase worker count
export CLOUDVIZ_WORKERS=8

# Use filters to reduce scope
curl -X POST http://localhost:8000/api/v1/azure/extract \
  -d '{
    "subscription_id": "'$AZURE_SUBSCRIPTION_ID'",
    "regions": ["australiaeast"],
    "resource_groups": ["production"]
  }'

# Enable caching
export CLOUDVIZ_CACHE_ENABLED=true
export CLOUDVIZ_CACHE_TTL=3600
```

#### Problem: High memory usage
```bash
# CloudViz using > 4GB RAM
```

**Solutions:**
```bash
# Reduce batch size
export CLOUDVIZ_BATCH_SIZE=50

# Clear cache
curl -X POST http://localhost:8000/api/v1/admin/cache/clear

# Restart service periodically
# Add to crontab:
# 0 2 * * * docker restart cloudviz
```

## 🔧 Debugging Tools

### 1. Enable Debug Logging

```bash
# Set debug level
export CLOUDVIZ_LOG_LEVEL=DEBUG

# View logs in real-time
docker logs -f cloudviz

# Save logs to file
docker logs cloudviz > debug.log 2>&1
```

### 2. Health Check Diagnostics

```bash
# Detailed health check
curl http://localhost:8000/health?detailed=true

# Component status
curl http://localhost:8000/health/components

# Check dependencies
curl http://localhost:8000/health/dependencies
```

### 3. API Testing

```bash
# Test authentication
curl -H "X-API-Key: test-key" http://localhost:8000/api/v1/resources

# Test with verbose output
curl -v -X POST http://localhost:8000/api/v1/azure/extract \
  -H "Content-Type: application/json" \
  -d '{"subscription_id": "test"}'

# Check API response time
time curl http://localhost:8000/health
```

### 4. Database Diagnostics

```bash
# Check database connection
docker exec cloudviz python -c "
from cloudviz.core.database import get_connection
conn = get_connection()
print('Database connected:', conn is not None)
"

# Check database tables
docker exec cloudviz python -c "
from cloudviz.core.database import engine
from sqlalchemy import inspect
inspector = inspect(engine)
print('Tables:', inspector.get_table_names())
"
```

## 📊 Monitoring and Alerting

### 1. System Metrics

```bash
# CPU and memory usage
docker stats cloudviz

# Disk usage
df -h

# Network connections
ss -tuln | grep :8000
```

### 2. Application Metrics

```bash
# Prometheus metrics
curl http://localhost:8000/metrics

# Custom CloudViz metrics
curl http://localhost:8000/api/v1/admin/stats

# Job status
curl http://localhost:8000/api/v1/admin/jobs
```

### 3. Log Analysis

```bash
# Error count in logs
docker logs cloudviz 2>&1 | grep ERROR | wc -l

# Recent errors
docker logs cloudviz 2>&1 | grep ERROR | tail -10

# Response time analysis
docker logs cloudviz 2>&1 | grep "response_time" | awk '{print $NF}' | sort -n
```

## 🚨 Emergency Procedures

### 1. Service Recovery

```bash
# Quick restart
docker restart cloudviz

# Full restart with cleanup
docker stop cloudviz
docker rm cloudviz
docker run -d --name cloudviz -p 8000:8000 cloudviz:latest

# Rollback to previous version
docker run -d --name cloudviz -p 8000:8000 cloudviz:v1.0.0
```

### 2. Data Recovery

```bash
# Backup current state
docker exec cloudviz python -c "
from cloudviz.core.database import backup_database
backup_database('emergency_backup.sql')
"

# Restore from backup
docker exec cloudviz python -c "
from cloudviz.core.database import restore_database
restore_database('backup.sql')
"
```

### 3. Cache Management

```bash
# Clear all caches
curl -X POST http://localhost:8000/api/v1/admin/cache/clear

# Clear specific provider cache
curl -X POST http://localhost:8000/api/v1/admin/cache/clear \
  -d '{"provider": "azure"}'

# Disable cache temporarily
export CLOUDVIZ_CACHE_ENABLED=false
```

## 📞 Getting Help

If you can't resolve the issue:

1. **Check the FAQ**: [FAQ](../reference/faq.md)
2. **Search Issues**: [GitHub Issues](https://github.com/navidrast/cloudviz/issues)
3. **Create Issue**: Include logs, configuration, and steps to reproduce
4. **Discord Support**: Join our Discord for real-time help
5. **Email Support**: support@cloudviz.dev for critical issues

### Issue Report Template

When reporting issues, please include:

```markdown
**Environment:**
- OS: Ubuntu 22.04
- Python: 3.9.0
- CloudViz version: 1.0.0
- Deployment: Docker

**Problem:**
[Describe the issue]

**Steps to Reproduce:**
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happens]

**Logs:**
```
[Include relevant logs]
```

**Configuration:**
```yaml
[Include configuration files without secrets]
```
```

## 🔄 Preventive Measures

### 1. Regular Maintenance

```bash
# Weekly tasks
docker system prune -f
curl -X POST http://localhost:8000/api/v1/admin/cache/clear

# Monthly tasks
docker pull cloudviz:latest
docker system df
```

### 2. Monitoring Setup

```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

### 3. Backup Strategy

```bash
#!/bin/bash
# backup.sh - Daily backup script

# Backup database
docker exec cloudviz python -c "
from cloudviz.core.database import backup_database
backup_database('/backups/cloudviz_$(date +%Y%m%d).sql')
"

# Backup configuration
tar -czf /backups/config_$(date +%Y%m%d).tar.gz config/

# Keep only last 7 days
find /backups -name "*.sql" -mtime +7 -delete
find /backups -name "*.tar.gz" -mtime +7 -delete
```

---

**Remember**: When in doubt, check the logs first! Most issues can be diagnosed from the application logs.