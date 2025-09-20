# 📦 Installation Guide

This guide covers all installation methods for CloudViz, from development setup to production deployment.

## 🚀 **Quick Installation (Docker)**

The fastest way to get CloudViz running:

```bash
# Clone the repository
git clone https://github.com/navidrast/cloudviz.git
cd cloudviz

# Start with Docker Compose
docker-compose up -d

# Access CloudViz
open http://localhost:8000
```

## 🐍 **Python Installation**

### **Prerequisites**
- Python 3.8 or higher
- pip package manager
- Git

### **Step 1: Clone Repository**
```bash
git clone https://github.com/navidrast/cloudviz.git
cd cloudviz
```

### **Step 2: Create Virtual Environment**
```bash
# Create virtual environment
python -m venv cloudviz-env

# Activate (Linux/Mac)
source cloudviz-env/bin/activate

# Activate (Windows)
cloudviz-env\Scripts\activate
```

### **Step 3: Install Dependencies**
```bash
# Install production dependencies
pip install -r requirements/prod.txt

# For development
pip install -r requirements/dev.txt

# Install CloudViz package
pip install -e .
```

### **Step 4: Configuration**
```bash
# Copy example configuration
cp config/dev.yml config/local.yml

# Edit configuration
nano config/local.yml
```

### **Step 5: Start CloudViz**
```bash
# Start the server
python -m cloudviz.api.main

# Or using uvicorn directly
uvicorn cloudviz.api.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🐳 **Docker Installation**

### **Using Docker Compose (Recommended)**

```yaml
# docker-compose.yml
version: '3.8'
services:
  cloudviz:
    build: .
    ports:
      - "8000:8000"
    environment:
      - CLOUDVIZ_ENV=production
      - DATABASE_URL=postgresql://user:pass@db:5432/cloudviz
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./config:/app/config
      - ./data:/app/data

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: cloudviz
      POSTGRES_USER: cloudviz
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### **Using Docker Only**

```bash
# Build the image
docker build -t cloudviz .

# Run the container
docker run -d \
  --name cloudviz \
  -p 8000:8000 \
  -e CLOUDVIZ_ENV=production \
  cloudviz
```

## ☸️ **Kubernetes Installation**

### **Using Helm Chart**

```bash
# Add CloudViz Helm repository
helm repo add cloudviz https://charts.cloudviz.io
helm repo update

# Install CloudViz
helm install cloudviz cloudviz/cloudviz \
  --set image.tag=latest \
  --set service.type=LoadBalancer
```

### **Manual Kubernetes Deployment**

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cloudviz
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
        image: cloudviz:latest
        ports:
        - containerPort: 8000
        env:
        - name: CLOUDVIZ_ENV
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: cloudviz-secrets
              key: database-url
---
apiVersion: v1
kind: Service
metadata:
  name: cloudviz-service
spec:
  selector:
    app: cloudviz
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## 🔧 **Configuration Setup**

### **Environment Variables**

| Variable | Description | Default |
|----------|-------------|---------|
| `CLOUDVIZ_ENV` | Environment (dev/prod) | `development` |
| `DATABASE_URL` | Database connection string | `sqlite:///./data/cloudviz.db` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `SECRET_KEY` | JWT secret key | *generated* |
| `AZURE_CLIENT_ID` | Azure service principal ID | *required for Azure* |
| `AWS_ACCESS_KEY_ID` | AWS access key | *required for AWS* |
| `GCP_SERVICE_ACCOUNT_PATH` | GCP service account file | *required for GCP* |

### **Configuration File**

```yaml
# config/local.yml
server:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  log_level: "info"

database:
  url: "postgresql://user:pass@localhost:5432/cloudviz"
  pool_size: 20
  max_overflow: 30

redis:
  url: "redis://localhost:6379"
  max_connections: 100

security:
  secret_key: "your-secret-key-here"
  algorithm: "HS256"
  access_token_expire_minutes: 30

cloud_providers:
  azure:
    enabled: true
    subscription_id: "your-subscription-id"
    tenant_id: "your-tenant-id"
    client_id: "your-client-id"
    client_secret: "your-client-secret"
    
  aws:
    enabled: true
    region: "us-west-2"
    access_key_id: "your-access-key"
    secret_access_key: "your-secret-key"
    
  gcp:
    enabled: true
    project_id: "your-project-id"
    service_account_path: "/path/to/service-account.json"

visualization:
  theme: "default"
  layout: "hierarchical"
  max_nodes: 1000
  cache_timeout: 3600
```

## 🔍 **Verification**

### **Health Check**
```bash
# Check if CloudViz is running
curl http://localhost:8000/health

# Expected response
{
  "status": "healthy",
  "version": "1.1.0",
  "timestamp": "2025-09-20T10:00:00Z"
}
```

### **API Endpoints**
```bash
# List available endpoints
curl http://localhost:8000/docs

# Test authentication
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'
```

### **Database Migration**
```bash
# Run database migrations
python scripts/migrate.py

# Verify database schema
python -c "from cloudviz.core.models import *; print('Database OK')"
```

## 🛠️ **Development Setup**

### **Additional Dependencies**
```bash
# Install development tools
pip install -r requirements/dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/

# Code formatting
black cloudviz/
isort cloudviz/
```

### **IDE Configuration**

#### **VS Code Settings**
```json
{
  "python.defaultInterpreterPath": "./cloudviz-env/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true
}
```

#### **PyCharm Settings**
- Set interpreter to `./cloudviz-env/bin/python`
- Enable Black formatter
- Configure pytest as test runner

## 🚨 **Common Issues**

### **Port Already in Use**
```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
uvicorn cloudviz.api.main:app --port 8001
```

### **Database Connection Issues**
```bash
# Check database connectivity
psql -h localhost -U cloudviz -d cloudviz

# Reset database
python scripts/migrate.py --reset
```

### **Redis Connection Issues**
```bash
# Check Redis status
redis-cli ping

# Expected response: PONG
```

### **Permission Issues**
```bash
# Fix file permissions
chmod +x scripts/*.py

# For Docker on Windows/Mac
docker run --privileged cloudviz
```

## 📚 **Next Steps**

After successful installation:

1. **[Configuration Guide](Configuration)** - Configure cloud providers
2. **[Quick Start](Quick-Start)** - Create your first diagram
3. **[API Reference](API-Reference)** - Explore available endpoints
4. **[Security Setup](Security)** - Configure authentication

## 💡 **Tips & Best Practices**

- Use Docker Compose for development
- Use Kubernetes for production
- Always use virtual environments for Python installation
- Keep sensitive data in environment variables
- Enable HTTPS in production
- Use a reverse proxy (nginx/traefik) for production
- Set up monitoring and logging
- Regular backups for production data

---

**Need help?** Check our [Troubleshooting Guide](Troubleshooting) or create an issue on [GitHub](https://github.com/navidrast/cloudviz/issues). 🆘
