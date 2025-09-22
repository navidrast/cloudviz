# CloudViz Troubleshooting Guide

This guide covers common issues encountered during installation and deployment of CloudViz, with solutions based on real-world experience.

## Quick Diagnostic Commands

### Check System Status
```powershell
# Windows PowerShell - Check Docker deployment
docker compose ps
docker compose logs --tail=50

# Check API health
Invoke-RestMethod -Uri "http://localhost:8000/health"

# Run automated verification
.\scripts\verify-installation.ps1 -Method docker
```

```bash
# Linux/Mac - Check Docker deployment
docker compose ps
docker compose logs --tail=50

# Check API health
curl http://localhost:8000/health

# Check Python installation
python -c "import cloudviz; print('CloudViz import successful')"
```

## Common Docker Issues

### 1. Nginx Container Restarting (SSL Certificate Error)

**Symptoms:**
- Nginx container constantly restarting
- Error: `cannot load certificate "/etc/nginx/ssl/nginx.crt"`

**Root Cause:**
- nginx.conf configured for SSL but certificates don't exist

**Solution:**
```bash
# Check nginx logs
docker compose logs nginx

# The fix: SSL is commented out by default in nginx.conf
# If you need SSL, create certificates first:
mkdir ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/nginx.key -out ssl/nginx.crt \
  -subj "/C=US/ST=State/L=City/O=Org/CN=localhost"

# Or use the default HTTP-only configuration (recommended for development)
```

**Prevention:**
- Use the provided nginx.conf with SSL commented out
- Only enable SSL in production with proper certificates

### 2. Port Conflicts

**Symptoms:**
- "Port already in use" errors
- Cannot bind to port 80, 8000, or 8080

**Solutions:**
```bash
# Windows - Check what's using the port
netstat -ano | findstr :8000
Get-Process -Id [PID]

# Linux/Mac - Check port usage
sudo lsof -i :8000
sudo netstat -tulpn | grep :8000

# Stop conflicting services
# For IIS on Windows (common port 80 conflict):
iisreset /stop

# Change ports in docker-compose.yml if needed:
ports:
  - "8081:8000"  # Change from 8080 to 8081
```

### 3. Docker PATH Issues (Windows)

**Symptoms:**
- "docker: command not found"
- Docker commands not recognized in PowerShell

**Solution:**
```powershell
# Check if Docker is in PATH
$env:PATH -split ';' | Select-String -Pattern 'docker'

# Manual PATH addition (if needed)
$dockerPath = "C:\Program Files\Docker\Docker\resources\bin"
if (Test-Path $dockerPath) {
    $env:PATH += ";$dockerPath"
}

# Restart PowerShell session
# Or use Docker Desktop from Windows Start Menu
```

### 4. Missing Dependencies in Container

**Symptoms:**
- Import errors for cloud provider libraries
- Missing email-validator package

**Solution:**
```bash
# Check if requirements are properly installed
docker compose exec cloudviz pip list | grep -E "(boto3|google-cloud|email-validator)"

# Rebuild container if packages missing
docker compose down
docker compose build --no-cache
docker compose up -d
```

## Python Development Issues

### 1. Virtual Environment Issues

**Symptoms:**
- Module not found errors
- Wrong Python version

**Solutions:**
```bash
# Verify virtual environment is activated
# Prompt should show (venv) prefix

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Verify Python version
python --version  # Should be 3.8+

# Reinstall dependencies in clean environment
pip install --force-reinstall -r requirements.txt
```

### 2. Import Errors

**Symptoms:**
- "ModuleNotFoundError: No module named 'cloudviz'"
- Path-related import issues

**Solutions:**
```bash
# Ensure you're in the project root directory
pwd  # Should end with 'cloudviz'

# Install in development mode
pip install -e .

# Verify installation
python -c "import cloudviz; print(cloudviz.__file__)"
```

### 3. Cloud Provider Authentication

**Symptoms:**
- Authentication errors when accessing cloud APIs
- "Credentials not found" errors

**Solutions:**
```bash
# Check environment variables
# Windows PowerShell
Get-ChildItem Env: | Where-Object {$_.Name -like "*AZURE*" -or $_.Name -like "*AWS*"}

# Linux/Mac
env | grep -E "(AZURE|AWS|GCP)"

# Test AWS credentials
aws sts get-caller-identity

# Test Azure credentials
az account show

# Test GCP credentials
gcloud auth list
```

## Performance Issues

### 1. Slow API Response

**Symptoms:**
- API calls taking longer than 5 seconds
- Timeout errors

**Solutions:**
```bash
# Check container resource usage
docker stats

# Increase memory limits in docker-compose.yml
services:
  cloudviz:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G

# Enable Redis caching (included in Docker deployment)
# Verify Redis is working
docker compose exec redis redis-cli ping
```

### 2. Database Connection Pool Exhaustion

**Symptoms:**
- "Too many connections" errors
- Database timeout errors

**Solutions:**
```bash
# Check active connections
docker compose exec db psql -U cloudviz -d cloudviz -c "SELECT count(*) FROM pg_stat_activity;"

# Adjust connection pool in environment variables
# In .env file:
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=0
```

## Network and Connectivity Issues

### 1. Cannot Access API

**Symptoms:**
- Connection refused to localhost:8000
- API not responding

**Troubleshooting Steps:**
```bash
# 1. Check if container is running
docker compose ps

# 2. Check container logs
docker compose logs cloudviz

# 3. Check port binding
docker port cloudviz-cloudviz-1

# 4. Test from within container
docker compose exec cloudviz curl http://localhost:8000/health

# 5. Check firewall settings (Windows)
# Open Windows Defender Firewall
# Allow Docker Desktop and related processes
```

### 2. Cloud API Connectivity

**Symptoms:**
- Cannot reach cloud provider APIs
- SSL/TLS errors

**Solutions:**
```bash
# Test connectivity to cloud endpoints
curl -I https://management.azure.com/
curl -I https://ec2.amazonaws.com/
curl -I https://compute.googleapis.com/

# Check proxy settings if behind corporate firewall
# Add proxy to docker-compose.yml if needed:
environment:
  - HTTP_PROXY=http://proxy.company.com:8080
  - HTTPS_PROXY=http://proxy.company.com:8080
```

## Automated Diagnosis

### Use the Verification Script

The included verification script can diagnose most common issues:

```powershell
# Windows PowerShell
.\scripts\verify-installation.ps1 -Method docker -Verbose

# Sample output for successful installation:
# [OK] Docker is available: Docker version 28.4.0
# [OK] Docker Compose is available
# [OK] Found 3 running Docker services
# [OK] CloudViz container is running
# [OK] Health endpoint is accessible
# [OK] API Status: healthy, Version: 1.0.0
# [OK] All tests passed! CloudViz environment is ready.
```

## Recovery Procedures

### Complete Docker Reset

If Docker deployment is corrupted:

```bash
# Stop all services
docker compose down

# Remove containers and volumes (WARNING: This deletes data)
docker compose down -v

# Remove images
docker system prune -a

# Rebuild from scratch
docker compose build --no-cache
docker compose up -d
```

### Reset Python Environment

If Python installation is corrupted:

```bash
# Remove virtual environment
rm -rf venv  # Linux/Mac
rmdir /s venv  # Windows

# Create fresh environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# Reinstall
pip install -r requirements.txt
```

## Getting Help

### Collect Diagnostic Information

Before requesting help, collect this information:

```bash
# System information
docker --version
docker compose version
python --version

# Container status
docker compose ps
docker compose logs --tail=100

# API status
curl -v http://localhost:8000/health

# Environment variables (sanitized)
env | grep -E "(CLOUDVIZ|DATABASE|REDIS)" | sed 's/=.*/=***/'
```

### Common Solutions Summary

| Issue | Quick Fix |
|-------|-----------|
| Nginx restarting | Check SSL certificates, use HTTP-only config |
| Port conflicts | Change ports in docker-compose.yml |
| Import errors | Activate virtual environment, reinstall dependencies |
| Auth errors | Check cloud provider credentials |
| Slow performance | Increase memory limits, verify Redis |
| Cannot access API | Check containers, ports, firewall |

### Support Resources

- 📋 [GitHub Issues](https://github.com/navidrast/cloudviz/issues)
- 📖 [Documentation Wiki](https://github.com/navidrast/cloudviz/wiki)
- 🔧 [Configuration Guide](Configuration.md)
- 🚀 [Quick Start Guide](Quick-Start.md)

---

*This troubleshooting guide is based on real deployment experiences and covers the most common issues encountered in production environments.*
