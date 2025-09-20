# CloudViz Installation Guide

This comprehensive guide covers all installation methods, configuration options, and troubleshooting for the CloudViz multi-cloud infrastructure visualization platform.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
3. [Docker Installation (Recommended)](#docker-installation)
4. [Python Development Setup](#python-development-setup)
5. [Configuration](#configuration)
6. [Verification & Testing](#verification--testing)
7. [Troubleshooting](#troubleshooting)
8. [Production Deployment](#production-deployment)

## Prerequisites

### System Requirements

#### Minimum Requirements
- **CPU**: 2 cores
- **Memory**: 4GB RAM
- **Storage**: 10GB available disk space
- **Operating System**: Linux, macOS, or Windows 10+

#### Recommended Requirements (Production)
- **CPU**: 4+ cores
- **Memory**: 8GB+ RAM
- **Storage**: 50GB+ available disk space
- **Operating System**: Ubuntu 20.04+, macOS 11+, Windows 11+

### Software Dependencies

#### For Docker Installation (Recommended)
- **Docker Desktop 4.10+** or **Docker Engine 20.10+**
- **Docker Compose 2.0+** (included with Docker Desktop)
- **Git** (for cloning repository)

#### For Python Development Setup
- **Python 3.8+** (Python 3.13+ recommended)
- **pip** (Python package manager)
- **Git** (for cloning repository)

### Network Requirements
- **Outbound HTTPS (443)**: Access to cloud provider APIs
- **Port 8000**: CloudViz API (configurable)
- **Port 8080**: Nginx proxy (Docker deployment only)

## Installation Methods

### Method 1: Docker Installation (Recommended)

**Advantages:**
- ✅ Production-ready configuration
- ✅ All dependencies handled automatically
- ✅ Database persistence included
- ✅ Redis caching configured
- ✅ Nginx reverse proxy
- ✅ Health checks and auto-restart
- ✅ Easy scaling and updates

**Steps:**

1. **Clone Repository**
   ```bash
   git clone https://github.com/navidrast/cloudviz.git
   cd cloudviz
   ```

2. **Start Services**
   ```bash
   docker compose up -d
   ```

3. **Verify Installation**
   ```bash
   # Check container status
   docker compose ps
   
   # Test API health
   curl http://localhost:8000/health
   
   # View API documentation
   # Visit: http://localhost:8000/docs
   ```

### Method 2: Python Development Setup

**Advantages:**
- ✅ Full development control
- ✅ Direct code access
- ✅ Custom configurations
- ✅ Debugging capabilities

**Steps:**

1. **Clone Repository**
   ```bash
   git clone https://github.com/navidrast/cloudviz.git
   cd cloudviz
   ```

2. **Create Virtual Environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start Development Server**
   ```bash
   uvicorn cloudviz.api.main:app --reload --host 0.0.0.0 --port 8000
   ```
- **Outbound HTTP/HTTPS**: Package downloads and updates
- **Inbound HTTP (8000)**: API server access
- **Inbound HTTPS (443)**: Production web interface

## Installation Methods

CloudViz supports multiple installation methods to accommodate different environments and use cases:

1. **Docker Compose** (Recommended for most users)
2. **Docker** (Single container deployment)
3. **Python Package** (Local development)
4. **Source Installation** (Development and customization)
5. **Kubernetes** (Production environments)

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/navidrast/cloudviz.git
cd cloudviz

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# Access the API
curl http://localhost:8000/health
```

### Option 2: Docker (Single Container)

```bash
# Pull the latest image
docker pull cloudviz/cloudviz:latest

# Run with basic configuration
docker run -d \
  --name cloudviz \
  -p 8000:8000 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/output:/app/output \
  cloudviz/cloudviz:latest
```

### Option 3: Python Package

```bash
# Install from PyPI
pip install cloudviz

# Run the server
cloudviz serve --host 0.0.0.0 --port 8000
```

## Docker Installation

### Production Docker Compose Setup

1. **Download the Docker Compose configuration:**

```bash
# Create project directory
mkdir cloudviz-production
cd cloudviz-production

# Download configuration files
curl -O https://raw.githubusercontent.com/navidrast/cloudviz/main/docker-compose.yml
curl -O https://raw.githubusercontent.com/navidrast/cloudviz/main/.env.example
```

2. **Configure environment variables:**

```bash
# Copy and edit environment file
cp .env.example .env
nano .env
```

Required environment variables:
```bash
# Application
CLOUDVIZ_ENV=production
CLOUDVIZ_SECRET_KEY=your-secret-key-here
CLOUDVIZ_JWT_SECRET=your-jwt-secret-here

# Database
DATABASE_URL=postgresql://cloudviz:cloudviz@db:5432/cloudviz
POSTGRES_DB=cloudviz
POSTGRES_USER=cloudviz
POSTGRES_PASSWORD=your-db-password-here

# Cache
REDIS_URL=redis://redis:6379/0

# Optional: SSL Configuration
SSL_CERT_FILE=/app/ssl/cert.pem
SSL_KEY_FILE=/app/ssl/key.pem
```

3. **Start the services:**

```bash
# Create necessary directories
mkdir -p logs output config ssl

# Generate SSL certificates (optional)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f cloudviz
```

### Custom Docker Configuration

Create a custom `docker-compose.override.yml`:

```yaml
version: '3.8'

services:
  cloudviz:
    environment:
      - CLOUDVIZ_LOG_LEVEL=DEBUG
      - CLOUDVIZ_API_WORKERS=8
    volumes:
      - ./custom-config:/app/config
    ports:
      - "443:443"

  db:
    volumes:
      - /data/postgres:/var/lib/postgresql/data
    environment:
      - POSTGRES_SHARED_PRELOAD_LIBRARIES=pg_stat_statements

  redis:
    command: redis-server --maxmemory 1gb --maxmemory-policy allkeys-lru
```

## Local Development Setup

### Prerequisites Installation

#### macOS (using Homebrew)
```bash
# Install system dependencies
brew install python@3.11 postgresql redis node graphviz

# Install Python dependencies
pip3 install --upgrade pip setuptools wheel

# Install Node.js dependencies
npm install -g @mermaid-js/mermaid-cli
```

#### Ubuntu/Debian
```bash
# Update package list
sudo apt update

# Install system dependencies
sudo apt install -y python3.11 python3.11-dev python3.11-venv \
  postgresql postgresql-contrib redis-server nodejs npm \
  graphviz libgraphviz-dev pkg-config

# Install Mermaid CLI
sudo npm install -g @mermaid-js/mermaid-cli

# Install Python build tools
sudo apt install -y build-essential libssl-dev libffi-dev
```

#### Windows
```powershell
# Install using Chocolatey
choco install python postgresql redis nodejs graphviz

# Install Mermaid CLI
npm install -g @mermaid-js/mermaid-cli

# Install Visual C++ Build Tools
choco install visualstudio2019buildtools
```

### Source Installation

1. **Clone and setup the repository:**

```bash
# Clone repository
git clone https://github.com/navidrast/cloudviz.git
cd cloudviz

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements/dev.txt

# Install CloudViz in development mode
pip install -e .
```

2. **Setup databases:**

```bash
# Start PostgreSQL (adjust for your system)
sudo systemctl start postgresql  # Linux
brew services start postgresql  # macOS

# Start Redis
sudo systemctl start redis-server  # Linux
brew services start redis  # macOS

# Create database
sudo -u postgres createuser cloudviz
sudo -u postgres createdb cloudviz -O cloudviz
sudo -u postgres psql -c "ALTER USER cloudviz WITH PASSWORD 'cloudviz';"
```

3. **Initialize the application:**

```bash
# Set environment variables
export DATABASE_URL="postgresql://cloudviz:cloudviz@localhost:5432/cloudviz"
export REDIS_URL="redis://localhost:6379/0"
export CLOUDVIZ_SECRET_KEY="dev-secret-key"

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn cloudviz.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Development Configuration

Create `config/dev.yml`:

```yaml
api:
  host: "0.0.0.0"
  port: 8000
  reload: true
  log_level: "debug"
  cors_enabled: true
  cors_origins: ["*"]

database:
  url: "postgresql://cloudviz:cloudviz@localhost:5432/cloudviz"
  echo: true

cache:
  enabled: true
  backend: "redis"
  url: "redis://localhost:6379/0"

logging:
  level: "DEBUG"
  json_format: false

visualization:
  default_theme: "dark"
  output_directory: "./output"

providers:
  azure:
    enabled: true
    authentication_method: "interactive"
  aws:
    enabled: false
  gcp:
    enabled: false
```

## Production Deployment

### Kubernetes Deployment

1. **Create namespace and secrets:**

```bash
# Create namespace
kubectl create namespace cloudviz

# Create secret for database
kubectl create secret generic cloudviz-db-secret \
  --from-literal=username=cloudviz \
  --from-literal=password=your-secure-password \
  -n cloudviz

# Create secret for application
kubectl create secret generic cloudviz-app-secret \
  --from-literal=secret-key=your-secret-key \
  --from-literal=jwt-secret=your-jwt-secret \
  -n cloudviz
```

2. **Deploy PostgreSQL:**

```yaml
# postgres-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: cloudviz
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        env:
        - name: POSTGRES_DB
          value: cloudviz
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: cloudviz-db-secret
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: cloudviz-db-secret
              key: password
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: cloudviz
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
```

3. **Deploy CloudViz application:**

```yaml
# cloudviz-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cloudviz
  namespace: cloudviz
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cloudviz
  template:
    metadata:
      labels:
        app: cloudviz
    spec:
      containers:
      - name: cloudviz
        image: cloudviz/cloudviz:latest
        env:
        - name: DATABASE_URL
          value: "postgresql://$(DB_USER):$(DB_PASSWORD)@postgres-service:5432/cloudviz"
        - name: DB_USER
          valueFrom:
            secretKeyRef:
              name: cloudviz-db-secret
              key: username
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: cloudviz-db-secret
              key: password
        - name: CLOUDVIZ_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: cloudviz-app-secret
              key: secret-key
        - name: CLOUDVIZ_JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: cloudviz-app-secret
              key: jwt-secret
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30

---
apiVersion: v1
kind: Service
metadata:
  name: cloudviz-service
  namespace: cloudviz
spec:
  selector:
    app: cloudviz
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### High Availability Setup

For production environments requiring high availability:

1. **Multi-region deployment**
2. **Database clustering with read replicas**
3. **Redis clustering for cache**
4. **Load balancing across multiple instances**
5. **Automated backup and disaster recovery**

## Configuration

### Configuration File Structure

CloudViz uses YAML configuration files with the following structure:

```yaml
# config/production.yml
api:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  cors_enabled: true
  rate_limit_requests: 1000
  rate_limit_window: 60
  jwt_expiration: 3600

database:
  url: "postgresql://user:pass@host:5432/cloudviz"
  pool_size: 20
  max_overflow: 30

cache:
  enabled: true
  backend: "redis"
  url: "redis://host:6379/0"
  default_ttl: 3600

logging:
  level: "INFO"
  file_path: "/var/log/cloudviz/app.log"
  json_format: true

visualization:
  default_theme: "professional"
  default_format: "mermaid"
  output_directory: "/app/output"
  render_settings:
    mermaid:
      theme: "professional"
      width: 1920
      height: 1080

providers:
  azure:
    enabled: true
    authentication_method: "service_principal"
    tenant_id: "${AZURE_TENANT_ID}"
    client_id: "${AZURE_CLIENT_ID}"
    client_secret: "${AZURE_CLIENT_SECRET}"
    rate_limits:
      requests_per_minute: 100
  
  aws:
    enabled: true
    authentication_method: "access_key"
    region: "us-east-1"
    rate_limits:
      requests_per_minute: 200
  
  gcp:
    enabled: true
    authentication_method: "service_account"
    project_id: "${GCP_PROJECT_ID}"
    credentials_path: "/app/config/gcp-service-account.json"
```

### Environment Variables

All configuration options can be overridden using environment variables:

```bash
# API Configuration
CLOUDVIZ_API_HOST=0.0.0.0
CLOUDVIZ_API_PORT=8000
CLOUDVIZ_API_WORKERS=4

# Database
DATABASE_URL=postgresql://user:pass@host:5432/cloudviz

# Cache
REDIS_URL=redis://host:6379/0

# Security
CLOUDVIZ_SECRET_KEY=your-secret-key
CLOUDVIZ_JWT_SECRET=your-jwt-secret

# Cloud Providers
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret

AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=us-east-1

GCP_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

## Cloud Provider Setup

### Azure Configuration

#### Service Principal Authentication (Recommended)
```bash
# Create service principal
az ad sp create-for-rbac --name cloudviz-sp --role Reader --scopes /subscriptions/your-subscription-id

# Output will contain:
# - appId (client_id)
# - password (client_secret)
# - tenant (tenant_id)
```

#### Required Azure Permissions
- **Reader**: Subscription or Resource Group level
- **Security Reader**: For security-related resources
- **Monitoring Reader**: For monitoring and diagnostic resources

#### Configuration:
```yaml
providers:
  azure:
    enabled: true
    authentication_method: "service_principal"
    tenant_id: "your-tenant-id"
    client_id: "your-client-id"
    client_secret: "your-client-secret"
    subscription_id: "your-subscription-id"
```

### AWS Configuration

#### IAM User/Role Authentication
```bash
# Create IAM user with programmatic access
aws iam create-user --user-name cloudviz-user

# Create access key
aws iam create-access-key --user-name cloudviz-user

# Attach read-only policy
aws iam attach-user-policy --user-name cloudviz-user --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess
```

#### Required AWS Permissions
Minimum required permissions for resource discovery:
- ec2:Describe*
- s3:ListAllMyBuckets
- s3:GetBucketLocation
- rds:Describe*
- elasticloadbalancing:Describe*
- autoscaling:Describe*
- iam:List*
- iam:Get*

#### Configuration:
```yaml
providers:
  aws:
    enabled: true
    authentication_method: "access_key"
    access_key_id: "your-access-key"
    secret_access_key: "your-secret-key"
    region: "us-east-1"
```

### GCP Configuration

#### Service Account Authentication
```bash
# Create service account
gcloud iam service-accounts create cloudviz-sa --display-name="CloudViz Service Account"

# Grant necessary roles
gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:cloudviz-sa@your-project-id.iam.gserviceaccount.com" \
  --role="roles/viewer"

# Create key file
gcloud iam service-accounts keys create cloudviz-sa-key.json \
  --iam-account=cloudviz-sa@your-project-id.iam.gserviceaccount.com
```

#### Required GCP Permissions
- **Viewer**: Project level
- **Compute Viewer**: For Compute Engine resources
- **Storage Object Viewer**: For Cloud Storage
- **Cloud SQL Viewer**: For Cloud SQL instances

#### Configuration:
```yaml
providers:
  gcp:
    enabled: true
    authentication_method: "service_account"
    project_id: "your-project-id"
    credentials_path: "/app/config/cloudviz-sa-key.json"
```

## Verification

### Health Check
```bash
# Check API health
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "cache": "connected",
  "providers": {
    "azure": "configured",
    "aws": "not_configured",
    "gcp": "not_configured"
  }
}
```

### Provider Authentication Test
```bash
# Test Azure authentication
curl -X POST http://localhost:8000/api/v1/providers/azure/test-auth \
  -H "Authorization: Bearer your-jwt-token"

# Test extraction
curl -X POST http://localhost:8000/api/v1/extract \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-jwt-token" \
  -d '{
    "provider": "azure",
    "scope": "subscription",
    "scope_identifier": "your-subscription-id"
  }'
```

### Visualization Test
```bash
# Test diagram generation
curl -X POST http://localhost:8000/api/v1/render \
  -H "Content-Type: application/json" \
  -d '{
    "inventory": {...},
    "format": "mermaid",
    "theme": "professional"
  }'
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Issues
**Symptoms:**
- "Connection refused" errors
- "Authentication failed" messages

**Solutions:**
```bash
# Check PostgreSQL status
docker-compose ps db
sudo systemctl status postgresql

# Verify connection string
echo $DATABASE_URL

# Test connection manually
psql postgresql://cloudviz:cloudviz@localhost:5432/cloudviz

# Reset database password
sudo -u postgres psql -c "ALTER USER cloudviz WITH PASSWORD 'newpassword';"
```

#### 2. Redis Connection Issues
**Symptoms:**
- Caching not working
- Session errors

**Solutions:**
```bash
# Check Redis status
docker-compose ps redis
sudo systemctl status redis-server

# Test Redis connection
redis-cli ping

# Clear Redis cache
redis-cli flushall
```

#### 3. Cloud Provider Authentication Issues

**Azure Authentication Failures:**
```bash
# Verify service principal
az ad sp show --id your-client-id

# Test authentication
az login --service-principal -u your-client-id -p your-client-secret --tenant your-tenant-id

# Check permissions
az role assignment list --assignee your-client-id
```

**AWS Authentication Failures:**
```bash
# Verify credentials
aws configure list
aws sts get-caller-identity

# Test permissions
aws ec2 describe-regions
aws s3 ls
```

**GCP Authentication Failures:**
```bash
# Verify service account
gcloud auth activate-service-account --key-file=path/to/key.json

# Test authentication
gcloud projects list
gcloud compute instances list
```

#### 4. Visualization Rendering Issues
**Symptoms:**
- Diagram generation failures
- Image rendering errors

**Solutions:**
```bash
# Check Mermaid CLI
mmdc --version

# Test Mermaid rendering
echo "graph TD; A-->B" | mmdc -i - -o test.png

# Check Graphviz
dot -V

# Verify system dependencies
sudo apt install graphviz libgraphviz-dev  # Ubuntu
brew install graphviz  # macOS
```

### Debug Mode

Enable debug logging:
```bash
# Environment variable
export CLOUDVIZ_LOG_LEVEL=DEBUG

# Configuration file
logging:
  level: "DEBUG"
  json_format: false

# Docker Compose
docker-compose -f docker-compose.yml -f docker-compose.debug.yml up
```

### Log Analysis

```bash
# View application logs
docker-compose logs -f cloudviz

# View specific service logs
docker logs cloudviz_cloudviz_1

# Search for errors
grep -i error /var/log/cloudviz/app.log

# Monitor real-time logs
tail -f /var/log/cloudviz/app.log | grep ERROR
```

### Performance Troubleshooting

#### Memory Issues
```bash
# Check memory usage
docker stats

# Increase memory limits
# In docker-compose.yml:
services:
  cloudviz:
    deploy:
      resources:
        limits:
          memory: 4G
```

#### Slow Extraction Performance
```bash
# Enable extraction profiling
export CLOUDVIZ_PROFILE_EXTRACTION=true

# Optimize database
# Increase connection pool
database:
  pool_size: 20
  max_overflow: 50

# Enable Redis caching
cache:
  enabled: true
  default_ttl: 3600
```

## Upgrading

### Docker Upgrade
```bash
# Pull latest images
docker-compose pull

# Backup database
docker-compose exec db pg_dump -U cloudviz cloudviz > backup.sql

# Stop services
docker-compose down

# Start with new images
docker-compose up -d

# Run migrations if needed
docker-compose exec cloudviz alembic upgrade head
```

### Source Upgrade
```bash
# Backup configuration
cp config/production.yml config/production.yml.bak

# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements/prod.txt

# Run migrations
alembic upgrade head

# Restart services
sudo systemctl restart cloudviz
```

### Migration Notes

**Version 1.0 to 1.1:**
- Updated database schema
- New visualization themes
- Enhanced security features

**Breaking Changes:**
- Configuration file format updated
- API endpoint changes for authentication
- New required environment variables

For detailed migration instructions, see the [Upgrade Guide](Upgrade-Guide.md).
