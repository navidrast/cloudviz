# Troubleshooting

This guide helps you diagnose and resolve common issues with CloudViz deployment, configuration, and operation.

## 🔍 Diagnostic Tools

### Health Check Commands

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed system status
curl http://localhost:8000/api/v1/system/status

# Check specific components
curl http://localhost:8000/api/v1/system/status/database
curl http://localhost:8000/api/v1/system/status/cache
curl http://localhost:8000/api/v1/system/status/providers
```

### Log Analysis

```bash
# View CloudViz application logs
docker-compose logs -f cloudviz

# View specific service logs
docker-compose logs -f postgres
docker-compose logs -f redis

# System logs (if using systemd)
sudo journalctl -u cloudviz -f

# Search for errors
docker-compose logs cloudviz | grep ERROR
sudo journalctl -u cloudviz | grep ERROR
```

### Configuration Validation

```bash
# Validate current configuration
python -m cloudviz.cli config validate

# Test with specific environment
CLOUDVIZ_ENV=production python -m cloudviz.cli config validate

# Show current configuration
python -m cloudviz.cli config show
```

## 🚨 Common Issues

### 1. Authentication & Authorization Issues

#### **Problem**: `401 Unauthorized` errors when accessing Azure resources

**Symptoms**:
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "The provided credentials are invalid",
    "details": "Azure authentication failed"
  }
}
```

**Diagnosis**:
```bash
# Check environment variables
echo $AZURE_CLIENT_ID
echo $AZURE_TENANT_ID
# Don't echo client secret for security

# Test Azure CLI authentication
az login --service-principal \
  --username $AZURE_CLIENT_ID \
  --password $AZURE_CLIENT_SECRET \
  --tenant $AZURE_TENANT_ID

# Test Azure API access directly
curl -H "Authorization: Bearer $(az account get-access-token --query accessToken -o tsv)" \
     "https://management.azure.com/subscriptions/$AZURE_SUBSCRIPTION_ID/resources?api-version=2021-04-01"
```

**Solutions**:

1. **Verify Service Principal Credentials**:
   ```bash
   # Check if service principal exists
   az ad sp show --id $AZURE_CLIENT_ID
   
   # Verify credentials are correct
   az login --service-principal \
     --username $AZURE_CLIENT_ID \
     --password $AZURE_CLIENT_SECRET \
     --tenant $AZURE_TENANT_ID
   ```

2. **Check Role Assignments**:
   ```bash
   # List role assignments for service principal
   az role assignment list --assignee $AZURE_CLIENT_ID --all
   
   # Assign Reader role if missing
   az role assignment create \
     --assignee $AZURE_CLIENT_ID \
     --role "Reader" \
     --scope "/subscriptions/$AZURE_SUBSCRIPTION_ID"
   ```

3. **Verify Subscription Access**:
   ```bash
   # Check subscription permissions
   az account show --subscription $AZURE_SUBSCRIPTION_ID
   
   # List accessible subscriptions
   az account list --query "[].{name:name, id:id, state:state}"
   ```

#### **Problem**: JWT token validation failures

**Symptoms**:
```json
{
  "error": {
    "code": "INVALID_TOKEN",
    "message": "JWT token validation failed"
  }
}
```

**Solutions**:

1. **Check JWT Secret Key**:
   ```bash
   # Ensure JWT_SECRET_KEY is set and >= 32 characters
   echo ${#JWT_SECRET_KEY}  # Should be >= 32
   ```

2. **Verify Token Format**:
   ```bash
   # Test token generation
   curl -X POST "http://localhost:8000/api/v1/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"username": "admin", "password": "password"}'
   ```

3. **Check System Time**:
   ```bash
   # Ensure system time is synchronized
   date
   ntpdate -q pool.ntp.org
   ```

### 2. Database Connection Issues

#### **Problem**: Database connection failures

**Symptoms**:
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) 
could not connect to server: Connection refused
```

**Diagnosis**:
```bash
# Test database connectivity
psql -h localhost -U cloudviz -d cloudviz -c "SELECT 1;"

# Check database service status
docker-compose ps postgres
sudo systemctl status postgresql

# Verify database URL
echo $DATABASE_URL
```

**Solutions**:

1. **Check Database Service**:
   ```bash
   # Start database if stopped
   docker-compose up -d postgres
   sudo systemctl start postgresql
   
   # Check database logs
   docker-compose logs postgres
   sudo journalctl -u postgresql
   ```

2. **Verify Connection Parameters**:
   ```bash
   # Test connection manually
   psql "postgresql://cloudviz:password@localhost:5432/cloudviz"
   
   # Check if database exists
   psql -h localhost -U cloudviz -l
   ```

3. **Check Network Connectivity**:
   ```bash
   # Test port connectivity
   telnet localhost 5432
   nc -zv localhost 5432
   
   # Check firewall rules
   sudo ufw status
   sudo iptables -L
   ```

#### **Problem**: Database migration failures

**Symptoms**:
```
alembic.util.exc.CommandError: Can't locate revision identified by 'head'
```

**Solutions**:

1. **Initialize Database**:
   ```bash
   # Run database migrations
   python scripts/migrate.py init
   python scripts/migrate.py migrate
   
   # Or using alembic directly
   alembic init alembic
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

2. **Reset Database** (development only):
   ```bash
   # Drop and recreate database
   dropdb cloudviz
   createdb cloudviz
   python scripts/migrate.py migrate
   ```

### 3. Cache/Redis Issues

#### **Problem**: Redis connection failures

**Symptoms**:
```
redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379. Connection refused.
```

**Diagnosis**:
```bash
# Test Redis connectivity
redis-cli ping

# Check Redis service status
docker-compose ps redis
sudo systemctl status redis

# Verify Redis URL
echo $REDIS_URL
```

**Solutions**:

1. **Start Redis Service**:
   ```bash
   # Using Docker Compose
   docker-compose up -d redis
   
   # Using system service
   sudo systemctl start redis
   sudo systemctl enable redis
   ```

2. **Check Redis Configuration**:
   ```bash
   # Test Redis connection
   redis-cli -h localhost -p 6379 ping
   
   # Check Redis configuration
   redis-cli config get "*"
   
   # Monitor Redis activity
   redis-cli monitor
   ```

3. **Alternative Cache Backend**:
   ```yaml
   # config/local.yml - Use memory cache for development
   cache:
     backend: "memory"
     default_ttl: 3600
   ```

### 4. Cloud Provider Integration Issues

#### **Problem**: Azure resource discovery timeouts

**Symptoms**:
```json
{
  "error": {
    "code": "DISCOVERY_TIMEOUT",
    "message": "Azure resource discovery timed out after 300 seconds"
  }
}
```

**Solutions**:

1. **Increase Timeout**:
   ```yaml
   # config/production.yml
   cloud_providers:
     azure:
       discovery:
         timeout: 600  # Increase to 10 minutes
         batch_size: 50  # Reduce batch size
         parallel_regions: false  # Disable parallel processing
   ```

2. **Filter Resources**:
   ```bash
   # Discover specific resource types only
   curl "http://localhost:8000/api/v1/azure/resources?resource_types=Microsoft.Compute/virtualMachines"
   
   # Discover specific regions only
   curl "http://localhost:8000/api/v1/azure/resources?regions=australiaeast"
   ```

3. **Use Background Jobs**:
   ```bash
   # Start discovery as background job
   curl -X POST "http://localhost:8000/api/v1/jobs/discovery" \
        -H "Content-Type: application/json" \
        -d '{
          "provider": "azure",
          "subscription_id": "your-subscription-id"
        }'
   ```

#### **Problem**: Rate limiting from Azure APIs

**Symptoms**:
```json
{
  "error": {
    "code": "RATE_LIMITED",
    "message": "Too many requests to Azure API",
    "retry_after": 60
  }
}
```

**Solutions**:

1. **Implement Exponential Backoff** (automatic in CloudViz):
   ```yaml
   # config/production.yml
   cloud_providers:
     azure:
       discovery:
         retry_attempts: 5
         retry_delay: 10  # Base delay in seconds
         exponential_backoff: true
   ```

2. **Reduce Request Frequency**:
   ```yaml
   # Reduce discovery frequency
   cloud_providers:
     azure:
       discovery:
         batch_size: 25  # Smaller batches
         parallel_regions: false
         request_delay: 1  # 1 second between requests
   ```

### 5. Diagram Generation Issues

#### **Problem**: Mermaid diagram generation failures

**Symptoms**:
```json
{
  "error": {
    "code": "DIAGRAM_GENERATION_FAILED",
    "message": "Failed to generate Mermaid diagram"
  }
}
```

**Solutions**:

1. **Check Resource Data**:
   ```bash
   # Validate resource data format
   curl "http://localhost:8000/api/v1/azure/resources" | jq '.'
   
   # Test with minimal data
   curl -X POST "http://localhost:8000/api/v1/diagrams/mermaid" \
        -H "Content-Type: application/json" \
        -d '{
          "resources": [
            {
              "id": "test-resource",
              "name": "test",
              "type": "test",
              "provider": "azure"
            }
          ]
        }'
   ```

2. **Check Theme Configuration**:
   ```bash
   # List available themes
   curl "http://localhost:8000/api/v1/diagrams/themes"
   
   # Test with different theme
   curl -X POST "http://localhost:8000/api/v1/diagrams/mermaid" \
        -d '{"resources": [...], "theme": "minimal"}'
   ```

#### **Problem**: PNG/SVG export failures

**Symptoms**:
```json
{
  "error": {
    "code": "EXPORT_FAILED",
    "message": "Failed to export diagram to PNG"
  }
}
```

**Solutions**:

1. **Check mermaid-cli Installation**:
   ```bash
   # Install mermaid-cli if missing
   npm install -g @mermaid-js/mermaid-cli
   
   # Test mermaid-cli
   echo "graph TD; A-->B" | mmdc -i /dev/stdin -o test.png
   ```

2. **Alternative Export Method**:
   ```bash
   # Get Mermaid markdown and use external tool
   curl -X POST "http://localhost:8000/api/v1/diagrams/mermaid" \
        -d '{"resources": [...]}' > diagram.md
   ```

### 6. Performance Issues

#### **Problem**: Slow API responses

**Symptoms**:
- High response times (>5 seconds)
- Timeout errors
- High CPU/memory usage

**Diagnosis**:
```bash
# Check system resources
top
htop
free -h
df -h

# Monitor API response times
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8000/api/v1/azure/resources"

# curl-format.txt content:
#     time_namelookup:  %{time_namelookup}\n
#     time_connect:     %{time_connect}\n
#     time_appconnect:  %{time_appconnect}\n
#     time_pretransfer: %{time_pretransfer}\n
#     time_redirect:    %{time_redirect}\n
#     time_starttransfer: %{time_starttransfer}\n
#     ----------\n
#     time_total:       %{time_total}\n
```

**Solutions**:

1. **Scale API Workers**:
   ```yaml
   # docker-compose.yml
   services:
     cloudviz:
       command: uvicorn cloudviz.api.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

2. **Optimize Database Queries**:
   ```yaml
   # config/production.yml
   database:
     pool_size: 20
     max_overflow: 30
     echo: false  # Disable SQL logging in production
   ```

3. **Enable Caching**:
   ```yaml
   # Increase cache TTL
   cache:
     strategies:
       resources: 7200    # 2 hours
       diagrams: 14400    # 4 hours
   ```

4. **Use Background Jobs**:
   ```bash
   # Process heavy operations in background
   curl -X POST "http://localhost:8000/api/v1/jobs/discovery" \
        -d '{"provider": "azure", "async": true}'
   ```

### 7. Memory Issues

#### **Problem**: Out of memory errors

**Symptoms**:
```
MemoryError: Unable to allocate memory
RuntimeError: Resource temporarily unavailable
```

**Solutions**:

1. **Increase Memory Limits**:
   ```yaml
   # docker-compose.yml
   services:
     cloudviz:
       deploy:
         resources:
           limits:
             memory: 2G
           reservations:
             memory: 1G
   ```

2. **Optimize Resource Discovery**:
   ```yaml
   # config/production.yml
   cloud_providers:
     azure:
       discovery:
         batch_size: 25    # Smaller batches
         stream_results: true  # Stream instead of loading all
   ```

3. **Configure Garbage Collection**:
   ```bash
   # Set Python garbage collection environment variables
   export PYTHONMALLOC=malloc
   export PYTHONGC=1
   ```

### 8. Network Connectivity Issues

#### **Problem**: Cannot reach Azure/AWS/GCP APIs

**Symptoms**:
```
requests.exceptions.ConnectTimeout: HTTPSConnectionPool(host='management.azure.com', port=443)
```

**Diagnosis**:
```bash
# Test external connectivity
curl -I https://management.azure.com/
curl -I https://ec2.amazonaws.com/
nslookup management.azure.com

# Check proxy settings
echo $HTTP_PROXY
echo $HTTPS_PROXY
echo $NO_PROXY

# Test DNS resolution
dig management.azure.com
```

**Solutions**:

1. **Configure Proxy** (if behind corporate firewall):
   ```bash
   export HTTP_PROXY=http://proxy.company.com:8080
   export HTTPS_PROXY=http://proxy.company.com:8080
   export NO_PROXY=localhost,127.0.0.1,internal.company.com
   ```

2. **Firewall Configuration**:
   ```bash
   # Allow outbound HTTPS
   sudo ufw allow out 443
   
   # Check iptables rules
   sudo iptables -L OUTPUT
   ```

3. **DNS Configuration**:
   ```bash
   # Use public DNS servers
   echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
   echo "nameserver 8.8.4.4" | sudo tee -a /etc/resolv.conf
   ```

## 🔧 Debug Mode

### Enable Debug Logging

```yaml
# config/development.yml
api:
  debug: true
  log_level: "DEBUG"

logging:
  level: "DEBUG"
  format: "standard"
```

```bash
# Or via environment variable
export DEBUG=true
export LOG_LEVEL=DEBUG
```

### Verbose API Responses

```bash
# Enable detailed error responses
curl -H "X-Debug: true" "http://localhost:8000/api/v1/azure/resources"
```

### Request Tracing

```python
# Add request ID to all logs
import uuid
from fastapi import Request

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    with logger.contextualize(request_id=request_id):
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
```

## 📊 Performance Monitoring

### Built-in Metrics

```bash
# View current metrics
curl "http://localhost:8000/api/v1/system/metrics"

# Response includes:
# - API request counts and timings
# - Discovery job statistics
# - Database connection pool status
# - Cache hit/miss ratios
# - Memory usage
```

### External Monitoring

#### Prometheus Integration

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'cloudviz'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/api/v1/system/metrics'
    scrape_interval: 30s
```

#### Health Check Monitoring

```bash
#!/bin/bash
# health-check.sh - Simple health check script

ENDPOINT="http://localhost:8000/health"
TIMEOUT=10

if curl -f -s --max-time $TIMEOUT $ENDPOINT > /dev/null; then
    echo "$(date): CloudViz is healthy"
    exit 0
else
    echo "$(date): CloudViz health check failed"
    exit 1
fi
```

## 🛠️ Support Tools

### CloudViz CLI

```bash
# Check system status
python -m cloudviz.cli status

# Run diagnostics
python -m cloudviz.cli diagnose

# Test cloud provider connectivity
python -m cloudviz.cli test azure
python -m cloudviz.cli test aws
python -m cloudviz.cli test gcp

# Validate configuration
python -m cloudviz.cli config validate

# Clear cache
python -m cloudviz.cli cache clear
```

### Health Check Script

```python
#!/usr/bin/env python3
# health_check.py

import requests
import sys
from datetime import datetime

def check_cloudviz_health(base_url="http://localhost:8000"):
    checks = [
        ("Basic Health", f"{base_url}/health"),
        ("System Status", f"{base_url}/api/v1/system/status"),
        ("Database", f"{base_url}/api/v1/system/status/database"),
        ("Cache", f"{base_url}/api/v1/system/status/cache"),
    ]
    
    results = []
    
    for name, url in checks:
        try:
            response = requests.get(url, timeout=10)
            status = "✅ PASS" if response.status_code == 200 else "❌ FAIL"
            results.append(f"{status} {name}: {response.status_code}")
        except Exception as e:
            results.append(f"❌ FAIL {name}: {str(e)}")
    
    print(f"CloudViz Health Check - {datetime.now()}")
    print("=" * 50)
    for result in results:
        print(result)
    
    # Exit with error if any check failed
    if any("FAIL" in result for result in results):
        sys.exit(1)

if __name__ == "__main__":
    check_cloudviz_health()
```

### Log Analysis Script

```bash
#!/bin/bash
# analyze-logs.sh

LOG_FILE="/app/logs/cloudviz.log"

echo "CloudViz Log Analysis"
echo "===================="

echo "Error Summary (last 24 hours):"
grep "ERROR" $LOG_FILE | tail -20

echo -e "\nTop Error Types:"
grep "ERROR" $LOG_FILE | awk '{print $4}' | sort | uniq -c | sort -nr | head -10

echo -e "\nAPI Response Times (>1s):"
grep "duration" $LOG_FILE | awk '$6 > 1000 {print $0}' | tail -10

echo -e "\nMemory Usage Warnings:"
grep -i "memory" $LOG_FILE | grep -i "warning\|critical" | tail -5
```

## 📞 Getting Help

### Documentation Resources

- **[Getting Started](Getting-Started)** - Installation and basic setup
- **[Configuration](Configuration)** - Detailed configuration options
- **[API Documentation](API-Documentation)** - Complete API reference
- **[Deployment](Deployment)** - Production deployment guides

### Community Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/navidrast/cloudviz/issues)
- **Discussions**: [Community discussions](https://github.com/navidrast/cloudviz/discussions)
- **Documentation**: This wiki for comprehensive guides

### Enterprise Support

For enterprise customers:
- Priority support response
- Custom deployment assistance
- Advanced troubleshooting
- Performance optimization

### Providing Debug Information

When reporting issues, include:

1. **CloudViz Version**: `python -m cloudviz.cli version`
2. **Environment**: Development/staging/production
3. **Deployment Method**: Docker/Kubernetes/bare metal
4. **Configuration** (sanitized, no secrets)
5. **Error Logs** (last 50 lines with timestamps)
6. **System Information**: OS, Python version, available memory
7. **Steps to Reproduce**: Exact commands or API calls that trigger the issue

```bash
# Generate debug report
python -m cloudviz.cli debug-report --output debug-report.zip
```

---

**Still having issues?** Check our [GitHub Issues](https://github.com/navidrast/cloudviz/issues) for similar problems or create a new issue with the debug information above.