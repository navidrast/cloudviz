# CloudViz Production Deployment Guide

This guide provides comprehensive instructions for deploying CloudViz in production environments, incorporating lessons learned from real-world deployments.

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Docker Production Deployment](#docker-production-deployment)
3. [Environment Configuration](#environment-configuration)
4. [Security Considerations](#security-considerations)
5. [Monitoring & Health Checks](#monitoring--health-checks)
6. [Backup & Recovery](#backup--recovery)
7. [Scaling & Performance](#scaling--performance)
8. [Troubleshooting](#troubleshooting)

## Pre-Deployment Checklist

### Infrastructure Requirements

- [ ] **Server Specifications**
  - Minimum: 4 CPU cores, 8GB RAM, 50GB storage
  - Recommended: 8 CPU cores, 16GB RAM, 100GB SSD storage
  - Network: Outbound HTTPS (443) to cloud provider APIs

- [ ] **Software Prerequisites**
  - Docker Engine 20.10+ or Docker Desktop 4.10+
  - Docker Compose 2.0+
  - SSL certificates (for HTTPS)
  - Reverse proxy (nginx, included in Docker stack)

- [ ] **Network Configuration**
  - Domain name configured with DNS
  - SSL/TLS certificates obtained
  - Firewall rules configured
  - Load balancer configured (if needed)

### Cloud Provider Setup

- [ ] **AWS Configuration**
  - IAM user with appropriate permissions
  - Access keys generated and secured
  - Regions identified for scanning

- [ ] **Azure Configuration**
  - Service principal created
  - Client credentials generated
  - Tenant and subscription IDs noted

- [ ] **GCP Configuration**
  - Service account created
  - JSON key file generated
  - Project IDs identified

## Docker Production Deployment

### 1. Clone and Prepare Repository

```bash
# Clone repository
git clone https://github.com/navidrast/cloudviz.git
cd cloudviz

# Switch to main branch (if not already)
git checkout main

# Pull latest changes
git pull origin main
```

### 2. Configure Production Environment

```bash
# Copy environment template
cp .env.example .env

# Edit environment configuration
nano .env  # or your preferred editor
```

**Production .env Configuration:**

```bash
# Application Settings
CLOUDVIZ_ENV=production
DEBUG=false

# Database Configuration (PostgreSQL recommended for production)
DATABASE_URL=postgresql://cloudviz:${DB_PASSWORD}@db:5432/cloudviz
DB_PASSWORD=your-secure-database-password

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Security
JWT_SECRET_KEY=your-very-secure-jwt-secret-key-min-32-chars
SECRET_KEY=your-application-secret-key-min-32-chars

# Cloud Provider Credentials
# AWS
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_DEFAULT_REGION=us-east-1

# Azure
AZURE_CLIENT_ID=your-azure-client-id
AZURE_CLIENT_SECRET=your-azure-client-secret
AZURE_TENANT_ID=your-azure-tenant-id

# GCP
GOOGLE_APPLICATION_CREDENTIALS=/app/config/gcp-service-account.json
GCP_PROJECT_ID=your-gcp-project-id

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
WORKERS=4

# Logging
LOG_LEVEL=INFO
```

### 3. SSL Certificate Configuration

For production HTTPS, you have several options:

#### Option A: Let's Encrypt (Recommended)

```bash
# Install certbot
sudo apt-get install certbot

# Generate certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates
sudo mkdir -p ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/nginx.crt
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/nginx.key
sudo chown $USER:$USER ssl/*
```

#### Option B: Self-Signed (Development/Testing)

```bash
# Create SSL directory
mkdir ssl

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/nginx.key -out ssl/nginx.crt \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=your-domain.com"
```

#### Option C: Existing Certificates

```bash
# Copy your existing certificates
mkdir ssl
cp /path/to/your/certificate.crt ssl/nginx.crt
cp /path/to/your/private.key ssl/nginx.key
chmod 600 ssl/nginx.key
```

### 4. Configure Nginx for Production

Update `nginx.conf` to enable HTTPS:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream cloudviz_backend {
        server cloudviz:8000;
    }

    # HTTP to HTTPS redirect
    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/nginx.crt;
        ssl_certificate_key /etc/nginx/ssl/nginx.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

        # Proxy to CloudViz API
        location / {
            proxy_pass http://cloudviz_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto https;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Health check endpoint
        location /nginx-health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

### 5. Update Docker Compose for Production

Create `docker-compose.prod.yml`:

```yaml
services:
  cloudviz:
    build:
      context: .
      target: production
    ports:
      - "8000:8000"
    environment:
      - CLOUDVIZ_ENV=production
      - DATABASE_URL=postgresql://cloudviz:${DB_PASSWORD}@db:5432/cloudviz
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    volumes:
      - ./logs:/app/logs
      - ./output:/app/output
      - ./config:/app/config
      - ./ssl:/app/ssl:ro
    depends_on:
      - db
      - redis
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=cloudviz
      - POSTGRES_USER=cloudviz
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U cloudviz"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - cloudviz
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 256M
        reservations:
          memory: 128M

volumes:
  postgres_data:
```

### 6. Deploy the Application

```bash
# Start production deployment
docker compose -f docker-compose.prod.yml up -d

# Verify deployment
docker compose -f docker-compose.prod.yml ps

# Check logs
docker compose -f docker-compose.prod.yml logs -f

# Test health endpoint
curl -k https://your-domain.com/health
```

## Environment Configuration

### Development vs Production Settings

| Setting | Development | Production |
|---------|------------|------------|
| Debug Mode | `true` | `false` |
| Database | SQLite | PostgreSQL |
| Workers | 1 | 4+ |
| Log Level | DEBUG | INFO/WARNING |
| HTTPS | Optional | Required |
| CORS | Permissive | Restrictive |

### Environment Variables Reference

```bash
# Core Application
CLOUDVIZ_ENV=production|development|test
DEBUG=true|false
SECRET_KEY=secure-random-string
JWT_SECRET_KEY=secure-jwt-key

# Database
DATABASE_URL=postgresql://user:pass@host:port/db
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=0

# Redis Cache
REDIS_URL=redis://host:port/db
CACHE_TTL=3600

# API Server
API_HOST=0.0.0.0
API_PORT=8000
WORKERS=4
WORKER_TIMEOUT=120

# Logging
LOG_LEVEL=INFO|DEBUG|WARNING|ERROR
LOG_FORMAT=json|text
LOG_FILE=path/to/logfile

# Cloud Providers (see cloud provider sections)
AWS_ACCESS_KEY_ID=...
AZURE_CLIENT_ID=...
GCP_PROJECT_ID=...
```

## Security Considerations

### 1. Network Security

```bash
# Firewall configuration (Ubuntu/Debian)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Restrict database access
# PostgreSQL should only be accessible from application containers
# Redis should only be accessible from application containers
```

### 2. Application Security

- **Secret Management**: Use environment variables or secret management systems
- **Authentication**: Configure cloud provider service accounts with minimal permissions
- **HTTPS**: Always use SSL/TLS in production
- **Headers**: Security headers configured in nginx
- **Updates**: Keep base images and dependencies updated

### 3. Data Protection

```bash
# Database encryption at rest
# Configure PostgreSQL with encryption

# Backup encryption
# Encrypt database backups before storage

# Log sanitization
# Ensure no sensitive data in logs
```

## Monitoring & Health Checks

### Application Health Endpoints

```bash
# Primary health check
curl https://your-domain.com/health

# Detailed system status
curl https://your-domain.com/health/detailed

# Database connectivity
curl https://your-domain.com/health/db

# Cache status
curl https://your-domain.com/health/cache
```

### Monitoring Setup

```yaml
# Prometheus monitoring (optional)
# Add to docker-compose.prod.yml
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
```

### Log Monitoring

```bash
# Centralized logging with ELK stack or similar
# Configure log shipping to external systems

# Local log rotation
# Configure logrotate for application logs
```

## Backup & Recovery

### Database Backup

```bash
# Create backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="cloudviz_backup_${DATE}.sql"

# Create backup
docker compose exec db pg_dump -U cloudviz cloudviz > "${BACKUP_DIR}/${BACKUP_FILE}"

# Compress backup
gzip "${BACKUP_DIR}/${BACKUP_FILE}"

# Remove old backups (keep last 30 days)
find ${BACKUP_DIR} -name "cloudviz_backup_*.sql.gz" -mtime +30 -delete
```

### Automated Backup Schedule

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /path/to/backup-script.sh

# Weekly full backup
0 1 * * 0 /path/to/full-backup-script.sh
```

### Recovery Procedure

```bash
# Stop application
docker compose down

# Restore database
gunzip -c /backups/cloudviz_backup_YYYYMMDD_HHMMSS.sql.gz | \
  docker compose exec -T db psql -U cloudviz cloudviz

# Start application
docker compose up -d

# Verify recovery
curl https://your-domain.com/health
```

## Scaling & Performance

### Horizontal Scaling

```yaml
# Scale application containers
version: '3.8'
services:
  cloudviz:
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
```

### Load Balancing

```nginx
# Update nginx.conf for load balancing
upstream cloudviz_backend {
    least_conn;
    server cloudviz_1:8000;
    server cloudviz_2:8000;
    server cloudviz_3:8000;
}
```

### Performance Optimization

```yaml
# Production performance settings
services:
  cloudviz:
    environment:
      - WORKERS=8
      - WORKER_CLASS=uvicorn.workers.UvicornWorker
      - WORKER_CONNECTIONS=1000
      - MAX_REQUESTS=1000
      - MAX_REQUESTS_JITTER=100
```

## Troubleshooting

### Common Production Issues

1. **SSL Certificate Issues**
   - Verify certificate paths in nginx.conf
   - Check certificate expiration dates
   - Validate certificate chain

2. **Performance Issues**
   - Monitor resource usage with `docker stats`
   - Check database connection pool settings
   - Verify Redis cache is working

3. **Connectivity Issues**
   - Verify firewall rules
   - Check DNS resolution
   - Test cloud provider API connectivity

### Emergency Procedures

```bash
# Quick rollback
docker compose down
git checkout previous-working-commit
docker compose up -d

# Emergency scaling
docker compose up -d --scale cloudviz=5

# Database recovery mode
docker compose stop cloudviz nginx
# Perform database maintenance
docker compose start cloudviz nginx
```

## Deployment Checklist

### Pre-Deployment

- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Database backup completed
- [ ] Monitoring setup verified
- [ ] Security review completed

### Deployment

- [ ] Application deployed
- [ ] Health checks passing
- [ ] Database migrations completed
- [ ] SSL/HTTPS working
- [ ] Monitoring active

### Post-Deployment

- [ ] End-to-end testing completed
- [ ] Performance benchmarks met
- [ ] Backup procedures tested
- [ ] Documentation updated
- [ ] Team notified

## Support and Maintenance

### Regular Maintenance Tasks

- [ ] **Weekly**: Review logs for errors
- [ ] **Weekly**: Check backup integrity
- [ ] **Monthly**: Update dependencies
- [ ] **Monthly**: Security patch review
- [ ] **Quarterly**: Performance review
- [ ] **Quarterly**: Capacity planning

### Update Procedures

```bash
# Standard update procedure
git pull origin main
docker compose build --no-cache
docker compose down
docker compose up -d

# Verify deployment
curl https://your-domain.com/health
```

---

This deployment guide provides a comprehensive foundation for production CloudViz deployments. Adapt the configurations based on your specific infrastructure requirements and organizational policies.
