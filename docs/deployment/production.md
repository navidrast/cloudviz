# Production Deployment Guide

This guide covers deploying CloudViz in production environments with high availability, security, and scalability.

## 🎯 Production Requirements

### Infrastructure Requirements
- **CPU**: 4+ cores (8+ recommended)
- **Memory**: 8GB RAM minimum (16GB+ recommended)
- **Storage**: 100GB+ SSD storage
- **Network**: Reliable internet connection for cloud API access
- **Load Balancer**: For high availability (nginx, ALB, etc.)

### Database Requirements
- **PostgreSQL 12+**: Primary database
- **Redis 6+**: Caching and session storage
- **Backup Strategy**: Daily automated backups
- **High Availability**: Master-slave or cluster setup

## 🏗️ Architecture Overview

```mermaid
graph TB
    subgraph "Load Balancer Layer"
        LB[Load Balancer<br/>nginx/ALB]
    end
    
    subgraph "Application Layer"
        APP1[CloudViz Instance 1]
        APP2[CloudViz Instance 2]
        APP3[CloudViz Instance 3]
    end
    
    subgraph "Data Layer"
        DB_PRIMARY[PostgreSQL Primary]
        DB_REPLICA[PostgreSQL Replica]
        REDIS_CLUSTER[Redis Cluster]
    end
    
    subgraph "Storage Layer"
        FILES[File Storage<br/>S3/Azure Blob]
        BACKUP[Backup Storage]
    end
    
    subgraph "Monitoring"
        PROMETHEUS[Prometheus]
        GRAFANA[Grafana]
        ALERTS[AlertManager]
    end
    
    INTERNET[Internet] --> LB
    LB --> APP1
    LB --> APP2
    LB --> APP3
    
    APP1 --> DB_PRIMARY
    APP2 --> DB_PRIMARY
    APP3 --> DB_PRIMARY
    
    APP1 --> REDIS_CLUSTER
    APP2 --> REDIS_CLUSTER
    APP3 --> REDIS_CLUSTER
    
    DB_PRIMARY --> DB_REPLICA
    DB_PRIMARY --> BACKUP
    
    APP1 --> FILES
    APP2 --> FILES
    APP3 --> FILES
    
    APP1 --> PROMETHEUS
    APP2 --> PROMETHEUS
    APP3 --> PROMETHEUS
    
    PROMETHEUS --> GRAFANA
    PROMETHEUS --> ALERTS
    
    classDef lb fill:#e3f2fd,stroke:#1976d2
    classDef app fill:#e8f5e8,stroke:#388e3c
    classDef data fill:#fce4ec,stroke:#c2185b
    classDef storage fill:#fff3e0,stroke:#f57c00
    classDef monitoring fill:#f3e5f5,stroke:#7b1fa2
    
    class LB lb
    class APP1,APP2,APP3 app
    class DB_PRIMARY,DB_REPLICA,REDIS_CLUSTER data
    class FILES,BACKUP storage
    class PROMETHEUS,GRAFANA,ALERTS monitoring
```

## 🐳 Docker Production Setup

### 1. Production Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  cloudviz:
    image: cloudviz:latest
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    environment:
      - CLOUDVIZ_ENV=production
      - DATABASE_URL=postgresql://cloudviz:${DB_PASSWORD}@postgres:5432/cloudviz
      - REDIS_URL=redis://redis-cluster:6379
      - CLOUDVIZ_WORKERS=4
      - CLOUDVIZ_LOG_LEVEL=INFO
    secrets:
      - azure_credentials
      - aws_credentials
      - gcp_credentials
    networks:
      - cloudviz_network
    depends_on:
      - postgres
      - redis-cluster

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    networks:
      - cloudviz_network
    depends_on:
      - cloudviz

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: cloudviz
      POSTGRES_USER: cloudviz
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgres/postgresql.conf:/etc/postgresql/postgresql.conf:ro
    networks:
      - cloudviz_network
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G

  postgres-replica:
    image: postgres:15-alpine
    environment:
      PGUSER: replica
      POSTGRES_PASSWORD: ${REPLICA_PASSWORD}
      PGPASSWORD: ${REPLICA_PASSWORD}
    volumes:
      - postgres_replica_data:/var/lib/postgresql/data
    networks:
      - cloudviz_network
    depends_on:
      - postgres

  redis-cluster:
    image: redis:7-alpine
    command: redis-server /etc/redis/redis.conf
    volumes:
      - ./redis/redis.conf:/etc/redis/redis.conf:ro
      - redis_data:/data
    networks:
      - cloudviz_network
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    networks:
      - cloudviz_network

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - cloudviz_network

volumes:
  postgres_data:
  postgres_replica_data:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  cloudviz_network:
    driver: overlay
    attachable: true

secrets:
  azure_credentials:
    external: true
  aws_credentials:
    external: true
  gcp_credentials:
    external: true
```

### 2. Nginx Configuration

```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream cloudviz_backend {
        least_conn;
        server cloudviz:8000 max_fails=3 fail_timeout=30s;
        server cloudviz:8000 max_fails=3 fail_timeout=30s;
        server cloudviz:8000 max_fails=3 fail_timeout=30s;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_conn_zone $binary_remote_addr zone=conn:10m;

    server {
        listen 80;
        server_name cloudviz.company.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name cloudviz.company.com;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/cloudviz.crt;
        ssl_certificate_key /etc/nginx/ssl/cloudviz.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # Security Headers
        add_header X-Content-Type-Options nosniff;
        add_header X-Frame-Options DENY;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # Rate Limiting
        limit_req zone=api burst=20 nodelay;
        limit_conn conn 10;

        location / {
            proxy_pass http://cloudviz_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        location /health {
            proxy_pass http://cloudviz_backend/health;
            access_log off;
        }

        location /metrics {
            proxy_pass http://cloudviz_backend/metrics;
            allow 10.0.0.0/8;
            allow 172.16.0.0/12;
            allow 192.168.0.0/16;
            deny all;
        }
    }
}
```

## ☸️ Kubernetes Deployment

### 1. Namespace and ConfigMap

```yaml
# k8s/namespace.yml
apiVersion: v1
kind: Namespace
metadata:
  name: cloudviz
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: cloudviz-config
  namespace: cloudviz
data:
  config.yml: |
    api:
      host: "0.0.0.0"
      port: 8000
      workers: 4
    
    database:
      url: "postgresql://cloudviz:password@postgres:5432/cloudviz"
      pool_size: 20
      max_overflow: 30
    
    cache:
      enabled: true
      backend: "redis"
      url: "redis://redis:6379"
      ttl: 3600
    
    logging:
      level: "INFO"
      format: "json"
```

### 2. Application Deployment

```yaml
# k8s/deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cloudviz
  namespace: cloudviz
  labels:
    app: cloudviz
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
        - name: CLOUDVIZ_CONFIG_FILE
          value: "/app/config/config.yml"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: cloudviz-secrets
              key: database-url
        - name: AZURE_CLIENT_ID
          valueFrom:
            secretKeyRef:
              name: cloudviz-secrets
              key: azure-client-id
        volumeMounts:
        - name: config
          mountPath: /app/config
        - name: logs
          mountPath: /app/logs
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
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
      volumes:
      - name: config
        configMap:
          name: cloudviz-config
      - name: logs
        emptyDir: {}
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
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
```

### 3. Ingress Configuration

```yaml
# k8s/ingress.yml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: cloudviz-ingress
  namespace: cloudviz
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - cloudviz.company.com
    secretName: cloudviz-tls
  rules:
  - host: cloudviz.company.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: cloudviz-service
            port:
              number: 80
```

### 4. Database StatefulSet

```yaml
# k8s/postgres.yml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: cloudviz
spec:
  serviceName: postgres
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
        image: postgres:15-alpine
        env:
        - name: POSTGRES_DB
          value: cloudviz
        - name: POSTGRES_USER
          value: cloudviz
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: cloudviz-secrets
              key: postgres-password
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "2Gi"
            cpu: "500m"
          limits:
            memory: "4Gi"
            cpu: "1000m"
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 100Gi
```

## 🔧 Configuration Management

### 1. Environment Variables

```bash
# .env.prod
# API Configuration
CLOUDVIZ_ENV=production
CLOUDVIZ_HOST=0.0.0.0
CLOUDVIZ_PORT=8000
CLOUDVIZ_WORKERS=4
CLOUDVIZ_LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://cloudviz:${DB_PASSWORD}@postgres:5432/cloudviz
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Cache
REDIS_URL=redis://redis:6379
CACHE_TTL=3600

# Security
JWT_SECRET=${JWT_SECRET}
API_KEY_SALT=${API_KEY_SALT}

# Cloud Providers (use secrets manager in production)
AZURE_CLIENT_ID=${AZURE_CLIENT_ID}
AZURE_CLIENT_SECRET=${AZURE_CLIENT_SECRET}
AZURE_TENANT_ID=${AZURE_TENANT_ID}

AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}

GOOGLE_APPLICATION_CREDENTIALS=/app/secrets/gcp-key.json

# Monitoring
PROMETHEUS_ENABLED=true
METRICS_PORT=9090

# Features
CACHE_ENABLED=true
BACKGROUND_JOBS=true
WEBHOOK_ENABLED=true
```

### 2. Production Configuration

```yaml
# config/production.yml
api:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  reload: false
  log_level: "INFO"
  cors_enabled: true
  cors_origins: ["https://cloudviz.company.com"]
  
  # Security
  enable_https: true
  ssl_cert_file: "/app/ssl/cert.pem"
  ssl_key_file: "/app/ssl/key.pem"
  
  # Rate limiting
  rate_limit_requests: 100
  rate_limit_window: 60
  max_request_size: 10485760
  request_timeout: 300

database:
  url: "postgresql://cloudviz:password@postgres:5432/cloudviz"
  pool_size: 20
  max_overflow: 30
  echo: false

cache:
  enabled: true
  backend: "redis"
  url: "redis://redis-cluster:6379"
  default_ttl: 3600
  max_size: 10000

logging:
  level: "INFO"
  format: "json"
  file: "/app/logs/cloudviz.log"
  max_size: "100MB"
  backup_count: 10

monitoring:
  prometheus_enabled: true
  metrics_port: 9090
  health_check_interval: 30
  
security:
  jwt_expiration: 3600
  api_key_required: true
  audit_logging: true
  
cloud_providers:
  azure:
    enabled: true
    timeout: 300
    retry_attempts: 3
    
  aws:
    enabled: true
    timeout: 300
    retry_attempts: 3
    
  gcp:
    enabled: true
    timeout: 300
    retry_attempts: 3

visualization:
  default_theme: "professional"
  default_format: "mermaid"
  default_layout: "hierarchical"
  output_directory: "/app/output"
  max_resources_per_diagram: 1000
```

## 🔍 Monitoring & Observability

### 1. Prometheus Configuration

```yaml
# prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "cloudviz_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'cloudviz'
    static_configs:
      - targets: ['cloudviz:9090']
    scrape_interval: 5s
    metrics_path: /metrics

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx-exporter:9113']
```

### 2. Grafana Dashboards

```json
{
  "dashboard": {
    "title": "CloudViz Production Dashboard",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(cloudviz_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph", 
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(cloudviz_request_duration_seconds_bucket[5m]))"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(cloudviz_errors_total[5m])"
          }
        ]
      }
    ]
  }
}
```

### 3. Alerting Rules

```yaml
# prometheus/cloudviz_rules.yml
groups:
- name: cloudviz
  rules:
  - alert: CloudVizDown
    expr: up{job="cloudviz"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "CloudViz instance is down"
      description: "CloudViz instance {{ $labels.instance }} has been down for more than 1 minute."

  - alert: HighErrorRate
    expr: rate(cloudviz_errors_total[5m]) > 0.1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} errors per second."

  - alert: HighResponseTime
    expr: histogram_quantile(0.95, rate(cloudviz_request_duration_seconds_bucket[5m])) > 5
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High response time detected"
      description: "95th percentile response time is {{ $value }} seconds."

  - alert: DatabaseConnectionIssue
    expr: cloudviz_database_connections_active / cloudviz_database_connections_max > 0.8
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "Database connection pool nearly exhausted"
      description: "Database connection usage is at {{ $value }}%."
```

## 🔒 Security Configuration

### 1. SSL/TLS Setup

```bash
# Generate SSL certificates (or use Let's Encrypt)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout cloudviz.key \
  -out cloudviz.crt \
  -subj "/C=AU/ST=NSW/L=Sydney/O=Company/OU=IT/CN=cloudviz.company.com"
```

### 2. Secrets Management

```yaml
# k8s/secrets.yml
apiVersion: v1
kind: Secret
metadata:
  name: cloudviz-secrets
  namespace: cloudviz
type: Opaque
data:
  database-url: <base64-encoded-database-url>
  azure-client-id: <base64-encoded-azure-client-id>
  azure-client-secret: <base64-encoded-azure-client-secret>
  aws-access-key: <base64-encoded-aws-access-key>
  aws-secret-key: <base64-encoded-aws-secret-key>
  jwt-secret: <base64-encoded-jwt-secret>
```

### 3. Network Policies

```yaml
# k8s/network-policy.yml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: cloudviz-network-policy
  namespace: cloudviz
spec:
  podSelector:
    matchLabels:
      app: cloudviz
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: cloudviz
    ports:
    - protocol: TCP
      port: 5432  # PostgreSQL
    - protocol: TCP
      port: 6379  # Redis
  - to: []  # Allow external cloud API access
    ports:
    - protocol: TCP
      port: 443
```

## 🔄 Backup & Recovery

### 1. Database Backup Script

```bash
#!/bin/bash
# backup-database.sh

set -e

BACKUP_DIR="/backup/cloudviz"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="cloudviz_backup_${DATE}.sql"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -h postgres -U cloudviz -d cloudviz > "${BACKUP_DIR}/${BACKUP_FILE}"

# Compress backup
gzip "${BACKUP_DIR}/${BACKUP_FILE}"

# Upload to cloud storage (example with AWS S3)
aws s3 cp "${BACKUP_DIR}/${BACKUP_FILE}.gz" "s3://cloudviz-backups/database/"

# Keep only last 7 days locally
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup completed: ${BACKUP_FILE}.gz"
```

### 2. Disaster Recovery Plan

```yaml
# Disaster Recovery Procedures
disaster_recovery:
  rto: "4 hours"  # Recovery Time Objective
  rpo: "1 hour"   # Recovery Point Objective
  
  backup_strategy:
    database:
      frequency: "every 6 hours"
      retention: "30 days"
      storage: "S3 cross-region replication"
    
    application:
      docker_images: "ECR/ACR registry"
      configuration: "Git repository"
      certificates: "Key vault"
  
  recovery_steps:
    1. "Provision new infrastructure"
    2. "Restore database from latest backup"
    3. "Deploy application containers"
    4. "Update DNS records"
    5. "Verify functionality"
    6. "Notify stakeholders"
```

## 📊 Performance Tuning

### 1. Application Optimization

```python
# Production optimizations
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "cloudviz.api.main:app",
        host="0.0.0.0",
        port=8000,
        workers=4,
        worker_class="uvicorn.workers.UvicornWorker",
        loop="uvloop",
        http="httptools",
        access_log=False,  # Disable in production
        server_header=False,
        date_header=False
    )
```

### 2. Database Optimization

```sql
-- PostgreSQL optimization
-- postgresql.conf
shared_buffers = 2GB
effective_cache_size = 6GB
work_mem = 256MB
maintenance_work_mem = 1GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200

-- Performance indexes
CREATE INDEX CONCURRENTLY idx_resources_provider ON resources(provider);
CREATE INDEX CONCURRENTLY idx_resources_region ON resources(region);
CREATE INDEX CONCURRENTLY idx_resources_created_at ON resources(created_at);
```

### 3. Redis Configuration

```conf
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
tcp-keepalive 300
timeout 0
```

## 🔄 CI/CD Pipeline

### 1. GitHub Actions Workflow

```yaml
# .github/workflows/deploy-production.yml
name: Deploy to Production

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          docker-compose -f docker-compose.test.yml up --abort-on-container-exit
          docker-compose -f docker-compose.test.yml down

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and push Docker image
        run: |
          docker build -t cloudviz:${{ github.sha }} .
          docker tag cloudviz:${{ github.sha }} cloudviz:latest
          docker push cloudviz:${{ github.sha }}
          docker push cloudviz:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/cloudviz cloudviz=cloudviz:${{ github.sha }}
          kubectl rollout status deployment/cloudviz
```

## 📈 Scaling Strategies

### 1. Horizontal Pod Autoscaler

```yaml
# k8s/hpa.yml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: cloudviz-hpa
  namespace: cloudviz
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: cloudviz
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 2. Cluster Autoscaler

```yaml
# k8s/cluster-autoscaler.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cluster-autoscaler
  namespace: kube-system
spec:
  template:
    spec:
      containers:
      - image: k8s.gcr.io/autoscaling/cluster-autoscaler:v1.21.0
        name: cluster-autoscaler
        command:
        - ./cluster-autoscaler
        - --v=4
        - --stderrthreshold=info
        - --cloud-provider=aws
        - --skip-nodes-with-local-storage=false
        - --expander=least-waste
        - --node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/cloudviz-cluster
```

## 🚨 Health Checks & Readiness

### 1. Application Health Checks

```python
@app.get("/health")
async def health_check():
    """Comprehensive health check."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "checks": {}
    }
    
    # Database check
    try:
        await database.fetch_one("SELECT 1")
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {e}"
        health_status["status"] = "unhealthy"
    
    # Redis check
    try:
        await redis.ping()
        health_status["checks"]["cache"] = "healthy"
    except Exception as e:
        health_status["checks"]["cache"] = f"unhealthy: {e}"
        health_status["status"] = "unhealthy"
    
    # Cloud provider checks
    for provider in ["azure", "aws", "gcp"]:
        try:
            await check_provider_connectivity(provider)
            health_status["checks"][provider] = "healthy"
        except Exception as e:
            health_status["checks"][provider] = f"unhealthy: {e}"
    
    return health_status
```

### 2. Liveness and Readiness Probes

```yaml
# k8s deployment probes
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3
```

---

This production deployment guide provides a comprehensive foundation for running CloudViz in enterprise environments with high availability, security, and scalability requirements.