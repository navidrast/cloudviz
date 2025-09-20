# CloudViz Troubleshooting Guide

Comprehensive troubleshooting guide for CloudViz platform covering common issues, error resolution procedures, diagnostic tools, and best practices for maintaining optimal system performance.

## Table of Contents

1. [Overview](#overview)
2. [Quick Diagnostic Tools](#quick-diagnostic-tools)
3. [Installation Issues](#installation-issues)
4. [Authentication and Authorization](#authentication-and-authorization)
5. [Cloud Provider Issues](#cloud-provider-issues)
6. [API and Connectivity Issues](#api-and-connectivity-issues)
7. [Database and Storage Issues](#database-and-storage-issues)
8. [Performance Issues](#performance-issues)
9. [Visualization and Rendering Issues](#visualization-and-rendering-issues)
10. [Docker and Container Issues](#docker-and-container-issues)
11. [Kubernetes Issues](#kubernetes-issues)
12. [Network and Security Issues](#network-and-security-issues)
13. [Logging and Monitoring](#logging-and-monitoring)
14. [Error Code Reference](#error-code-reference)
15. [Support and Escalation](#support-and-escalation)

## Overview

This guide provides systematic approaches to diagnosing and resolving common CloudViz issues. Each section includes:
- **Problem identification** techniques
- **Step-by-step solutions** with commands
- **Prevention strategies** for future issues
- **When to escalate** to support

### General Troubleshooting Approach

1. **Identify the Problem**: Gather error messages, logs, and system state
2. **Isolate the Issue**: Determine if it's configuration, network, or code-related
3. **Apply Solutions**: Use systematic approach starting with simplest fixes
4. **Verify Resolution**: Test the fix and monitor for recurrence
5. **Document**: Record the solution for future reference

## Quick Diagnostic Tools

### Health Check Commands

```bash
# Basic health check
curl -f http://localhost:8000/health

# Detailed health status
curl http://localhost:8000/health/detailed

# Component status
curl http://localhost:8000/health/components

# API status with authentication
curl -H "Authorization: Bearer $API_TOKEN" \
  http://localhost:8000/api/v1/status
```

### System Information

```bash
# CloudViz version and configuration
cloudviz --version
cloudviz config show

# System resources
df -h                    # Disk space
free -h                  # Memory usage
docker stats             # Container resources (if using Docker)

# Process status
ps aux | grep cloudviz   # CloudViz processes
netstat -tulpn | grep 8000  # Port usage
```

### Log Analysis

```bash
# Application logs
tail -f /var/log/cloudviz/app.log

# Docker logs
docker logs cloudviz-app --tail 100 -f

# Kubernetes logs
kubectl logs -f deployment/cloudviz -n cloudviz

# Search for errors
grep -i error /var/log/cloudviz/app.log | tail -20
```

### Database Connectivity

```bash
# Test PostgreSQL connection
psql "$DATABASE_URL" -c "SELECT version();"

# Check database status
cloudviz db status

# Verify tables exist
cloudviz db check-tables
```

### Cache Connectivity

```bash
# Test Redis connection
redis-cli -u "$REDIS_URL" ping

# Check cache statistics
redis-cli -u "$REDIS_URL" info stats
```

## Installation Issues

### Python Environment Issues

#### Issue: Module Not Found Errors
```
ModuleNotFoundError: No module named 'cloudviz'
```

**Diagnosis**:
```bash
# Check Python version
python --version

# Check installed packages
pip list | grep cloudviz

# Check Python path
python -c "import sys; print(sys.path)"
```

**Solutions**:
```bash
# Reinstall CloudViz
pip uninstall cloudviz
pip install -e .

# Or install from PyPI
pip install cloudviz

# For development
pip install -e ".[dev]"
```

#### Issue: Permission Denied During Installation
```
ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
```

**Solutions**:
```bash
# Use user installation
pip install --user cloudviz

# Or use virtual environment
python -m venv cloudviz-env
source cloudviz-env/bin/activate  # Linux/Mac
# cloudviz-env\Scripts\activate   # Windows
pip install cloudviz
```

### Docker Installation Issues

#### Issue: Docker Container Won't Start
```
Error response from daemon: driver failed programming external connectivity
```

**Diagnosis**:
```bash
# Check port conflicts
netstat -tulpn | grep 8000
lsof -i :8000

# Check Docker status
docker ps -a
docker logs cloudviz-app
```

**Solutions**:
```bash
# Use different port
docker run -p 8001:8000 cloudviz/cloudviz

# Kill conflicting processes
sudo kill $(sudo lsof -t -i:8000)

# Restart Docker service
sudo systemctl restart docker
```

#### Issue: Container Memory Issues
```
docker: Error response from daemon: Container killed by SIGKILL
```

**Solutions**:
```bash
# Increase memory limits
docker run --memory=4g --memory-swap=4g cloudviz/cloudviz

# Or in docker-compose.yml
services:
  cloudviz:
    mem_limit: 4g
    memswap_limit: 4g
```

### Package Dependencies

#### Issue: Conflicting Dependencies
```
ERROR: pip's dependency resolver does not currently consider all the packages
```

**Solutions**:
```bash
# Create clean environment
python -m venv clean-env
source clean-env/bin/activate
pip install --upgrade pip
pip install cloudviz

# Or use conda
conda create -n cloudviz python=3.9
conda activate cloudviz
pip install cloudviz
```

## Authentication and Authorization

### JWT Token Issues

#### Issue: Invalid or Expired Tokens
```
{
  "error": "Token has expired",
  "code": 401
}
```

**Diagnosis**:
```bash
# Decode JWT token (without verification)
echo "eyJ..." | base64 -d | jq .

# Check token expiration
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/auth/verify
```

**Solutions**:
```bash
# Refresh token
curl -X POST http://localhost:8000/auth/refresh \
  -H "Authorization: Bearer $REFRESH_TOKEN"

# Login again
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Update token in environment
export API_TOKEN="new-token-here"
```

### API Key Authentication

#### Issue: Invalid API Key
```
{
  "error": "Invalid API key",
  "code": 403
}
```

**Solutions**:
```bash
# Generate new API key
curl -X POST http://localhost:8000/api/v1/auth/api-keys \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{"name": "my-api-key", "permissions": ["read", "write"]}'

# Verify API key format
echo $API_KEY | wc -c  # Should be appropriate length

# Test API key
curl -H "X-API-Key: $API_KEY" \
  http://localhost:8000/api/v1/health
```

### Permission Issues

#### Issue: Insufficient Permissions
```
{
  "error": "Insufficient permissions",
  "code": 403
}
```

**Diagnosis**:
```bash
# Check user permissions
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/auth/permissions

# Check role assignments
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/auth/roles
```

**Solutions**:
```bash
# Update user role
curl -X PUT http://localhost:8000/api/v1/users/{user_id}/roles \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"roles": ["admin", "user"]}'

# Grant specific permissions
curl -X POST http://localhost:8000/api/v1/users/{user_id}/permissions \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"permissions": ["extract", "visualize"]}'
```

## Cloud Provider Issues

### Azure Authentication

#### Issue: Service Principal Authentication Failure
```
azure.core.exceptions.ClientAuthenticationError: authentication failed
```

**Diagnosis**:
```bash
# Test Azure CLI authentication
az login --service-principal \
  -u $AZURE_CLIENT_ID \
  -p $AZURE_CLIENT_SECRET \
  --tenant $AZURE_TENANT_ID

# Check service principal
az ad sp show --id $AZURE_CLIENT_ID

# Verify permissions
az role assignment list --assignee $AZURE_CLIENT_ID
```

**Solutions**:
```bash
# Reset client secret
az ad sp credential reset --id $AZURE_CLIENT_ID

# Add required permissions
az role assignment create \
  --assignee $AZURE_CLIENT_ID \
  --role "Reader" \
  --scope "/subscriptions/$AZURE_SUBSCRIPTION_ID"

# Test CloudViz connection
cloudviz provider test azure
```

#### Issue: Subscription Access Denied
```
The client does not have authorization to perform action 'Microsoft.Resources/subscriptions/read'
```

**Solutions**:
```bash
# Grant subscription reader access
az role assignment create \
  --assignee $AZURE_CLIENT_ID \
  --role "Reader" \
  --scope "/subscriptions/$AZURE_SUBSCRIPTION_ID"

# For specific resource groups
az role assignment create \
  --assignee $AZURE_CLIENT_ID \
  --role "Reader" \
  --scope "/subscriptions/$AZURE_SUBSCRIPTION_ID/resourceGroups/MyResourceGroup"
```

### AWS Authentication

#### Issue: Invalid AWS Credentials
```
botocore.exceptions.NoCredentialsError: Unable to locate credentials
```

**Diagnosis**:
```bash
# Check AWS configuration
aws configure list

# Test credentials
aws sts get-caller-identity

# Check environment variables
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
```

**Solutions**:
```bash
# Set credentials
aws configure set aws_access_key_id YOUR_ACCESS_KEY
aws configure set aws_secret_access_key YOUR_SECRET_KEY
aws configure set default.region us-east-1

# Or use environment variables
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_DEFAULT_REGION=us-east-1

# Test CloudViz connection
cloudviz provider test aws
```

#### Issue: Permission Denied for AWS Resources
```
botocore.exceptions.ClientError: An error occurred (AccessDenied) when calling the DescribeInstances operation
```

**Solutions**:
```bash
# Attach ReadOnlyAccess policy
aws iam attach-user-policy \
  --user-name cloudviz \
  --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess

# Or create custom policy with minimal permissions
aws iam put-user-policy \
  --user-name cloudviz \
  --policy-name CloudVizPolicy \
  --policy-document file://minimal-policy.json
```

### GCP Authentication

#### Issue: Service Account Key Not Found
```
google.auth.exceptions.DefaultCredentialsError: Could not automatically determine credentials
```

**Diagnosis**:
```bash
# Check service account key file
ls -la $GOOGLE_APPLICATION_CREDENTIALS
cat $GOOGLE_APPLICATION_CREDENTIALS | jq .

# Test gcloud authentication
gcloud auth application-default login
gcloud auth list
```

**Solutions**:
```bash
# Create new service account key
gcloud iam service-accounts keys create cloudviz-key.json \
  --iam-account=cloudviz@$PROJECT_ID.iam.gserviceaccount.com

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/cloudviz-key.json

# Test CloudViz connection
cloudviz provider test gcp
```

## API and Connectivity Issues

### HTTP Connection Errors

#### Issue: Connection Refused
```
requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=8000): Max retries exceeded
```

**Diagnosis**:
```bash
# Check if service is running
curl -f http://localhost:8000/health
netstat -tulpn | grep 8000
ps aux | grep cloudviz
```

**Solutions**:
```bash
# Start CloudViz server
cloudviz server start

# Or with Docker
docker-compose up -d cloudviz

# Check firewall
sudo ufw status
sudo iptables -L
```

#### Issue: Timeout Errors
```
requests.exceptions.Timeout: HTTPSConnectionPool: Read timed out
```

**Solutions**:
```bash
# Increase timeout in configuration
api:
  timeout: 600  # 10 minutes

# Or in API calls
curl --connect-timeout 30 --max-time 600 \
  http://localhost:8000/api/v1/extract/azure
```

### SSL/TLS Issues

#### Issue: SSL Certificate Verification Failed
```
requests.exceptions.SSLError: HTTPSConnectionPool: certificate verify failed
```

**Solutions**:
```bash
# For development, disable SSL verification (not recommended for production)
export PYTHONHTTPSVERIFY=0

# Or provide proper certificate
api:
  ssl_cert_file: /path/to/cert.pem
  ssl_key_file: /path/to/key.pem

# Update CA certificates
sudo apt-get update && sudo apt-get install ca-certificates
```

### Rate Limiting

#### Issue: Rate Limit Exceeded
```
{
  "error": "Rate limit exceeded",
  "code": 429,
  "retry_after": 60
}
```

**Solutions**:
```bash
# Check rate limit headers
curl -I http://localhost:8000/api/v1/health

# Increase rate limits in configuration
api:
  rate_limiting:
    default_rate: "1000/minute"
    burst_rate: "2000/minute"

# Implement exponential backoff in client code
```

## Database and Storage Issues

### PostgreSQL Connection Issues

#### Issue: Database Connection Failed
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server
```

**Diagnosis**:
```bash
# Test direct connection
psql "postgresql://user:pass@host:5432/cloudviz" -c "SELECT 1;"

# Check PostgreSQL status
sudo systemctl status postgresql
docker logs cloudviz-postgres

# Check network connectivity
telnet postgres-host 5432
```

**Solutions**:
```bash
# Start PostgreSQL
sudo systemctl start postgresql

# Or with Docker
docker-compose up -d postgres

# Check configuration
cat /etc/postgresql/*/main/postgresql.conf | grep listen_addresses
cat /etc/postgresql/*/main/pg_hba.conf
```

#### Issue: Database Does Not Exist
```
sqlalchemy.exc.OperationalError: database "cloudviz" does not exist
```

**Solutions**:
```bash
# Create database
createdb cloudviz

# Or using SQL
psql -c "CREATE DATABASE cloudviz;"

# Initialize CloudViz database
cloudviz db init
cloudviz db migrate
```

#### Issue: Migration Failures
```
alembic.util.exc.CommandError: Target database is not up to date
```

**Solutions**:
```bash
# Check migration status
cloudviz db current
cloudviz db history

# Run migrations
cloudviz db upgrade head

# Force migration (caution: may lose data)
cloudviz db stamp head
cloudviz db upgrade
```

### Redis Cache Issues

#### Issue: Redis Connection Failed
```
redis.exceptions.ConnectionError: Error connecting to Redis
```

**Diagnosis**:
```bash
# Test Redis connection
redis-cli -h redis-host -p 6379 ping

# Check Redis status
sudo systemctl status redis
docker logs cloudviz-redis
```

**Solutions**:
```bash
# Start Redis
sudo systemctl start redis

# Or with Docker
docker-compose up -d redis

# Disable cache if not critical
cache:
  enabled: false
```

### Disk Space Issues

#### Issue: No Space Left on Device
```
OSError: [Errno 28] No space left on device
```

**Diagnosis**:
```bash
# Check disk usage
df -h
du -sh /var/log/cloudviz/*
du -sh /app/output/*

# Check inodes
df -i
```

**Solutions**:
```bash
# Clean up logs
sudo logrotate -f /etc/logrotate.d/cloudviz
find /var/log/cloudviz -name "*.log.*" -mtime +7 -delete

# Clean up temporary files
rm -rf /tmp/cloudviz/*
rm -rf /app/output/temp/*

# Configure log rotation
logging:
  max_file_size: 10485760  # 10MB
  backup_count: 5
```

## Performance Issues

### Slow API Responses

#### Issue: High Response Times
```
Average response time > 5 seconds
```

**Diagnosis**:
```bash
# Monitor API performance
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/v1/health

# Check system resources
top
htop
iotop

# Database query analysis
cloudviz db analyze-queries
```

**Solutions**:
```bash
# Increase worker processes
api:
  workers: 8

# Enable caching
cache:
  enabled: true
  default_ttl: 3600

# Database optimization
database:
  pool_size: 20
  max_overflow: 50

# Add database indexes
cloudviz db optimize-indexes
```

### Memory Issues

#### Issue: High Memory Usage
```
Process killed by OOM killer
```

**Diagnosis**:
```bash
# Monitor memory usage
free -h
cat /proc/meminfo
ps aux --sort=-%mem | head

# Check for memory leaks
valgrind --tool=memcheck cloudviz server start
```

**Solutions**:
```bash
# Increase system memory
# Or adjust application limits
performance:
  memory:
    max_memory_per_worker: "1GB"
    gc_threshold: 0.8

# Process large datasets in chunks
api:
  max_request_size: 1048576  # 1MB
  
# Enable streaming for large responses
```

### CPU Performance

#### Issue: High CPU Usage
```
CPU usage consistently > 80%
```

**Diagnosis**:
```bash
# Monitor CPU usage
top -p $(pgrep cloudviz)
perf top -p $(pgrep cloudviz)

# Profile application
cloudviz --profile server start
```

**Solutions**:
```bash
# Optimize worker configuration
api:
  workers: $(nproc)
  worker_class: "uvicorn.workers.UvicornWorker"

# Async processing for heavy operations
background_jobs:
  enabled: true
  max_concurrent_jobs: 4

# Database query optimization
database:
  enable_query_cache: true
```

## Visualization and Rendering Issues

### Diagram Generation Failures

#### Issue: Mermaid Rendering Failed
```
MermaidError: Parse error on line X
```

**Diagnosis**:
```bash
# Test Mermaid syntax
node -e "console.log(require('mermaid').parse('graph TD; A-->B'))"

# Check Mermaid installation
npm list mermaid
```

**Solutions**:
```bash
# Install/update Mermaid
npm install -g @mermaid-js/mermaid-cli

# Validate diagram syntax
cloudviz validate --format mermaid diagram.md

# Use alternative format
cloudviz render inventory.json --format graphviz
```

#### Issue: Graphviz Not Found
```
graphviz.backend.ExecutableNotFound: failed to execute 'dot'
```

**Solutions**:
```bash
# Install Graphviz
# Ubuntu/Debian
sudo apt-get install graphviz

# CentOS/RHEL
sudo yum install graphviz

# macOS
brew install graphviz

# Windows
choco install graphviz
```

#### Issue: Large Diagram Timeout
```
TimeoutError: Diagram generation timed out after 300 seconds
```

**Solutions**:
```bash
# Increase timeout
visualization:
  limits:
    timeout: 600  # 10 minutes

# Filter large datasets
cloudviz extract azure --resource-groups "prod-*" --max-resources 1000

# Use pagination
cloudviz render large-inventory.json --paginate --max-nodes-per-page 100
```

### Image Export Issues

#### Issue: Cairo/PIL Import Error
```
ImportError: No module named 'cairo'
```

**Solutions**:
```bash
# Install Cairo
# Ubuntu/Debian
sudo apt-get install libcairo2-dev

# CentOS/RHEL
sudo yum install cairo-devel

# macOS
brew install cairo

# Reinstall Python bindings
pip install pycairo pillow
```

## Docker and Container Issues

### Container Build Issues

#### Issue: Docker Build Failed
```
Step 5/10 : RUN pip install -r requirements.txt
 ---> Running in abc123
ERROR: Could not find a version that satisfies the requirement
```

**Solutions**:
```bash
# Clear Docker build cache
docker builder prune

# Use specific Python version
FROM python:3.9-slim

# Update requirements.txt
pip freeze > requirements.txt

# Multi-stage build
FROM python:3.9-slim as builder
RUN pip install --user cloudviz
FROM python:3.9-slim
COPY --from=builder /root/.local /root/.local
```

#### Issue: Container Startup Failed
```
docker: Error response from daemon: OCI runtime create failed
```

**Diagnosis**:
```bash
# Check container logs
docker logs container-name

# Inspect container
docker inspect container-name

# Check Docker daemon
systemctl status docker
journalctl -u docker.service
```

**Solutions**:
```bash
# Restart Docker service
sudo systemctl restart docker

# Remove and recreate container
docker rm -f container-name
docker-compose up -d

# Check SELinux/AppArmor restrictions
sudo setsebool -P container_manage_cgroup true
```

### Docker Compose Issues

#### Issue: Service Dependencies Failed
```
ERROR: for cloudviz  Cannot start service cloudviz: driver failed programming external connectivity
```

**Solutions**:
```bash
# Check port conflicts
docker-compose down
netstat -tulpn | grep 8000

# Use different ports
services:
  cloudviz:
    ports:
      - "8001:8000"

# Check network configuration
docker network ls
docker network inspect cloudviz_default
```

#### Issue: Volume Mount Issues
```
docker: Error response from daemon: invalid mount config for type "bind"
```

**Solutions**:
```bash
# Check volume paths exist
mkdir -p ./data ./logs ./config

# Fix permissions
sudo chown -R 1000:1000 ./data
chmod -R 755 ./data

# Use named volumes instead of bind mounts
volumes:
  cloudviz_data:
    driver: local
```

## Kubernetes Issues

### Pod Startup Issues

#### Issue: ImagePullBackOff
```
Failed to pull image "cloudviz/cloudviz:latest": rpc error: code = Unknown desc = Error response from daemon
```

**Solutions**:
```bash
# Check image exists
docker pull cloudviz/cloudviz:latest

# Use specific tag
image: cloudviz/cloudviz:v1.0.0

# Check image pull secrets
kubectl create secret docker-registry regcred \
  --docker-server=registry.example.com \
  --docker-username=user \
  --docker-password=password
```

#### Issue: CrashLoopBackOff
```
Pod "cloudviz-xxx" has restarted 5 times
```

**Diagnosis**:
```bash
# Check pod logs
kubectl logs -f pod/cloudviz-xxx

# Describe pod
kubectl describe pod cloudviz-xxx

# Check events
kubectl get events --sort-by=.metadata.creationTimestamp
```

**Solutions**:
```bash
# Add health checks
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5

# Increase resources
resources:
  requests:
    memory: "1Gi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "1000m"
```

### Service Discovery Issues

#### Issue: Service Not Accessible
```
dial tcp: lookup cloudviz-service on X.X.X.X:53: no such host
```

**Solutions**:
```bash
# Check service exists
kubectl get services
kubectl describe service cloudviz-service

# Check endpoints
kubectl get endpoints cloudviz-service

# Verify DNS
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup cloudviz-service
```

### ConfigMap and Secret Issues

#### Issue: ConfigMap Not Found
```
configmaps "cloudviz-config" is forbidden: User "system:serviceaccount:default:default" cannot get resource "configmaps"
```

**Solutions**:
```bash
# Create ConfigMap
kubectl create configmap cloudviz-config --from-file=config.yml

# Check RBAC permissions
kubectl auth can-i get configmaps --as=system:serviceaccount:default:default

# Create proper service account
apiVersion: v1
kind: ServiceAccount
metadata:
  name: cloudviz
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: cloudviz-role
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list"]
```

## Network and Security Issues

### Firewall Issues

#### Issue: Connection Blocked by Firewall
```
telnet: Unable to connect to remote host: Connection timed out
```

**Diagnosis**:
```bash
# Check firewall status
sudo ufw status
sudo iptables -L

# Test connectivity
telnet target-host 8000
nc -zv target-host 8000
```

**Solutions**:
```bash
# Open required ports
sudo ufw allow 8000/tcp
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT

# For cloud providers, update security groups/NSGs
# AWS
aws ec2 authorize-security-group-ingress \
  --group-id sg-12345678 \
  --protocol tcp \
  --port 8000 \
  --cidr 0.0.0.0/0

# Azure
az network nsg rule create \
  --resource-group myResourceGroup \
  --nsg-name myNSG \
  --name allow-cloudviz \
  --protocol tcp \
  --priority 100 \
  --destination-port-range 8000
```

### SSL/TLS Certificate Issues

#### Issue: Certificate Expired
```
ssl.SSLCertVerificationError: certificate verify failed: certificate has expired
```

**Solutions**:
```bash
# Check certificate expiration
openssl x509 -in cert.pem -text -noout | grep "Not After"

# Renew certificate (Let's Encrypt)
certbot renew

# Update certificate in configuration
api:
  ssl_cert_file: /path/to/new-cert.pem
  ssl_key_file: /path/to/new-key.pem
```

### DNS Resolution Issues

#### Issue: DNS Resolution Failed
```
gaierror: [Errno -2] Name or service not known
```

**Solutions**:
```bash
# Check DNS configuration
cat /etc/resolv.conf
nslookup cloudviz.example.com

# Use IP address temporarily
DATABASE_URL=postgresql://user:pass@10.0.0.5:5432/cloudviz

# Update /etc/hosts if needed
echo "10.0.0.5 cloudviz.example.com" >> /etc/hosts
```

## Logging and Monitoring

### Log Analysis

#### Common Log Patterns

**Authentication Errors**:
```bash
grep -i "authentication\|unauthorized\|forbidden" /var/log/cloudviz/app.log
```

**Database Errors**:
```bash
grep -i "database\|postgres\|connection" /var/log/cloudviz/app.log
```

**Performance Issues**:
```bash
grep -i "timeout\|slow\|performance" /var/log/cloudviz/app.log
```

**API Errors**:
```bash
grep -E "4[0-9]{2}|5[0-9]{2}" /var/log/cloudviz/app.log
```

### Log Levels and Configuration

```yaml
# Increase log verbosity for debugging
logging:
  level: DEBUG
  handlers:
    file:
      level: DEBUG
    console:
      level: INFO

# Enable SQL query logging
database:
  echo: true
  echo_pool: true

# Enable request logging
api:
  access_log: true
  log_requests: true
```

### Monitoring Setup

```bash
# Install monitoring stack
docker-compose -f monitoring-stack.yml up -d

# Configure Prometheus
prometheus:
  enabled: true
  port: 9090

# Configure Grafana dashboards
grafana:
  enabled: true
  port: 3000
  dashboards:
    - cloudviz-overview
    - cloudviz-performance
    - cloudviz-errors
```

## Error Code Reference

### HTTP Status Codes

| Code | Meaning | Common Causes | Solutions |
|------|---------|---------------|-----------|
| 400 | Bad Request | Invalid JSON, missing parameters | Validate request format |
| 401 | Unauthorized | Invalid/expired token | Refresh authentication |
| 403 | Forbidden | Insufficient permissions | Check user roles |
| 404 | Not Found | Invalid endpoint, missing resource | Verify URL and resource existence |
| 429 | Too Many Requests | Rate limit exceeded | Implement backoff strategy |
| 500 | Internal Server Error | Application error | Check logs for stack trace |
| 502 | Bad Gateway | Upstream service down | Check dependent services |
| 503 | Service Unavailable | Service overloaded | Scale resources |
| 504 | Gateway Timeout | Request timeout | Increase timeout limits |

### CloudViz Error Codes

| Code | Category | Description | Solution |
|------|----------|-------------|----------|
| CV001 | Authentication | Invalid API key | Regenerate API key |
| CV002 | Authorization | Insufficient permissions | Update user role |
| CV003 | Configuration | Invalid configuration | Validate config file |
| CV004 | Provider | Cloud provider auth failed | Check provider credentials |
| CV005 | Database | Database connection failed | Check database status |
| CV006 | Cache | Cache connection failed | Check Redis status |
| CV007 | Visualization | Rendering failed | Check rendering engine |
| CV008 | Network | Network connectivity issue | Check network configuration |
| CV009 | Resource | Resource not found | Verify resource exists |
| CV010 | Validation | Input validation failed | Check input format |

### Provider-Specific Errors

**Azure Errors**:
```json
{
  "error_code": "InvalidAuthenticationTokenTenant",
  "message": "The access token is from the wrong issuer"
}
```
Solution: Verify tenant ID in configuration

**AWS Errors**:
```json
{
  "error_code": "InvalidUserID.NotFound",
  "message": "The user with name 'cloudviz' cannot be found"
}
```
Solution: Create IAM user or check user name

**GCP Errors**:
```json
{
  "error_code": "PERMISSION_DENIED",
  "message": "The caller does not have permission"
}
```
Solution: Grant required IAM roles

## Support and Escalation

### Before Escalating

1. **Gather Information**:
   ```bash
   # System information
   cloudviz --version
   python --version
   docker --version
   
   # Configuration
   cloudviz config show --sanitized
   
   # Recent logs
   tail -100 /var/log/cloudviz/app.log > logs.txt
   
   # Error reproduction steps
   ```

2. **Attempt Basic Solutions**:
   - Restart services
   - Clear cache
   - Check configuration
   - Review recent changes

3. **Search Documentation**:
   - Check this troubleshooting guide
   - Review API documentation
   - Search GitHub issues

### Escalation Channels

1. **GitHub Issues**: https://github.com/your-org/cloudviz/issues
   - Include: version, configuration, logs, reproduction steps
   - Use appropriate labels: bug, question, enhancement

2. **Discord Community**: https://discord.gg/cloudviz
   - For general questions and community support
   - Share error messages and get quick help

3. **Support Email**: support@cloudviz.com
   - For enterprise customers
   - Include all diagnostic information

4. **Emergency Support**: For critical production issues
   - Call enterprise support hotline
   - Include impact assessment and urgency

### Information to Include

When reporting issues, always include:

1. **Environment Details**:
   - CloudViz version
   - Operating system
   - Deployment method (Docker, Kubernetes, bare metal)
   - Cloud provider (if applicable)

2. **Configuration**:
   - Sanitized configuration file
   - Environment variables (without secrets)
   - Command-line arguments used

3. **Error Information**:
   - Exact error messages
   - Stack traces
   - Log entries around the time of error
   - HTTP status codes and responses

4. **Reproduction Steps**:
   - Step-by-step instructions to reproduce
   - Expected vs actual behavior
   - Frequency of occurrence

5. **Impact Assessment**:
   - Affected functionality
   - Number of users impacted
   - Business impact level

Remember: The more information you provide, the faster we can help resolve your issue!
