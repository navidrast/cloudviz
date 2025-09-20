# Deployment

This guide covers deploying CloudViz in various environments, from development to production. CloudViz supports multiple deployment methods including Docker, Kubernetes, and traditional server deployment.

## 🏗️ Deployment Options

| Method | Use Case | Complexity | Scalability | Management |
|--------|----------|------------|-------------|------------|
| **Local Development** | Development, testing | Low | Single instance | Manual |
| **Docker** | Small-medium deployments | Low-Medium | Limited | Docker Compose |
| **Kubernetes** | Production, enterprise | Medium-High | High | K8s operators |
| **Cloud Platforms** | Managed deployments | Medium | High | Cloud providers |
| **Traditional Server** | Legacy environments | Medium | Medium | System management |

## 🐳 Docker Deployment

### Quick Start with Docker

```bash
# Pull the latest CloudViz image
docker pull cloudviz:latest

# Run with basic configuration
docker run -d \
  --name cloudviz \
  -p 8000:8000 \
  -e AZURE_CLIENT_ID="your-client-id" \
  -e AZURE_CLIENT_SECRET="your-secret" \
  -e AZURE_TENANT_ID="your-tenant-id" \
  cloudviz:latest
```

### Docker Compose (Recommended)

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  cloudviz:
    image: cloudviz:latest
    container_name: cloudviz-api
    ports:
      - "8000:8000"
    environment:
      # Azure Configuration
      - AZURE_CLIENT_ID=${AZURE_CLIENT_ID}
      - AZURE_CLIENT_SECRET=${AZURE_CLIENT_SECRET}
      - AZURE_TENANT_ID=${AZURE_TENANT_ID}
      - AZURE_SUBSCRIPTION_ID=${AZURE_SUBSCRIPTION_ID}
      
      # API Configuration
      - API_HOST=0.0.0.0
      - API_PORT=8000
      - DEBUG=false
      - LOG_LEVEL=INFO
      
      # Database Configuration
      - DATABASE_URL=postgresql://cloudviz:password@postgres:5432/cloudviz
      
      # Cache Configuration
      - REDIS_URL=redis://redis:6379/0
      
      # Security
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - JWT_ALGORITHM=HS256
      - JWT_EXPIRATION=3600
    
    volumes:
      - ./config:/app/config
      - ./data:/app/data
      - ./logs:/app/logs
    
    depends_on:
      - postgres
      - redis
    
    restart: unless-stopped
    
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    image: postgres:15-alpine
    container_name: cloudviz-postgres
    environment:
      - POSTGRES_DB=cloudviz
      - POSTGRES_USER=cloudviz
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: cloudviz-redis
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: cloudviz-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - cloudviz
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:

networks:
  default:
    name: cloudviz-network
```

### Environment Configuration

Create a `.env` file:

```bash
# Azure Credentials
AZURE_CLIENT_ID=12345678-1234-1234-1234-123456789012
AZURE_CLIENT_SECRET=your-azure-secret
AZURE_TENANT_ID=87654321-4321-4321-4321-210987654321
AZURE_SUBSCRIPTION_ID=subscription-id

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key-min-32-chars

# Database (if using external)
DATABASE_URL=postgresql://user:password@host:5432/cloudviz

# Optional: AWS Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key

# Optional: GCP Configuration
GOOGLE_APPLICATION_CREDENTIALS=/app/config/gcp-service-account.json
GCP_PROJECT_ID=your-gcp-project
```

### Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f cloudviz

# Scale API instances
docker-compose up -d --scale cloudviz=3

# Update to latest version
docker-compose pull
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes (destructive)
docker-compose down -v
```

### NGINX Configuration

Create `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream cloudviz_backend {
        server cloudviz:8000;
        # Add more servers for load balancing
        # server cloudviz-2:8000;
        # server cloudviz-3:8000;
    }

    server {
        listen 80;
        server_name your-domain.com;
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/certificate.crt;
        ssl_certificate_key /etc/nginx/ssl/private.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Security Headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

        # Rate Limiting
        limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
        limit_req zone=api burst=20 nodelay;

        # Proxy Configuration
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

        # WebSocket support (if needed)
        location /ws {
            proxy_pass http://cloudviz_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        # Static files (if serving from nginx)
        location /static {
            alias /app/static;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

## ☸️ Kubernetes Deployment

### Basic Kubernetes Manifests

#### Namespace
```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: cloudviz
  labels:
    name: cloudviz
```

#### ConfigMap
```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cloudviz-config
  namespace: cloudviz
data:
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
  LOG_LEVEL: "INFO"
  DEBUG: "false"
  DATABASE_URL: "postgresql://cloudviz:password@postgres:5432/cloudviz"
  REDIS_URL: "redis://redis:6379/0"
```

#### Secret
```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: cloudviz-secrets
  namespace: cloudviz
type: Opaque
stringData:
  AZURE_CLIENT_ID: "your-client-id"
  AZURE_CLIENT_SECRET: "your-client-secret"
  AZURE_TENANT_ID: "your-tenant-id"
  JWT_SECRET_KEY: "your-jwt-secret-key"
```

#### Deployment
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cloudviz-api
  namespace: cloudviz
  labels:
    app: cloudviz-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cloudviz-api
  template:
    metadata:
      labels:
        app: cloudviz-api
    spec:
      containers:
      - name: cloudviz
        image: cloudviz:latest
        ports:
        - containerPort: 8000
          name: http
        
        envFrom:
        - configMapRef:
            name: cloudviz-config
        - secretRef:
            name: cloudviz-secrets
        
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        
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
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        
        volumeMounts:
        - name: config
          mountPath: /app/config
        - name: data
          mountPath: /app/data
        
      volumes:
      - name: config
        configMap:
          name: cloudviz-config
      - name: data
        persistentVolumeClaim:
          claimName: cloudviz-data
      
      imagePullSecrets:
      - name: docker-registry-secret
```

#### Service
```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: cloudviz-api-service
  namespace: cloudviz
  labels:
    app: cloudviz-api
spec:
  selector:
    app: cloudviz-api
  ports:
  - name: http
    port: 80
    targetPort: 8000
    protocol: TCP
  type: ClusterIP
```

#### Ingress
```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: cloudviz-ingress
  namespace: cloudviz
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
spec:
  tls:
  - hosts:
    - cloudviz.your-domain.com
    secretName: cloudviz-tls
  rules:
  - host: cloudviz.your-domain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: cloudviz-api-service
            port:
              number: 80
```

#### Horizontal Pod Autoscaler
```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: cloudviz-hpa
  namespace: cloudviz
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: cloudviz-api
  minReplicas: 2
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

### PostgreSQL Deployment
```yaml
# postgres.yaml
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
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: cloudviz
        - name: POSTGRES_USER
          value: cloudviz
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: cloudviz
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
  type: ClusterIP
```

### Redis Deployment
```yaml
# redis.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: cloudviz
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        command: ["redis-server", "--appendonly", "yes"]
        volumeMounts:
        - name: redis-storage
          mountPath: /data
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
      volumes:
      - name: redis-storage
        persistentVolumeClaim:
          claimName: redis-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: cloudviz
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
  type: ClusterIP
```

### Deployment Commands

```bash
# Apply all manifests
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f postgres.yaml
kubectl apply -f redis.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml
kubectl apply -f hpa.yaml

# Check deployment status
kubectl get pods -n cloudviz
kubectl get services -n cloudviz
kubectl get ingress -n cloudviz

# View logs
kubectl logs -n cloudviz deployment/cloudviz-api

# Scale deployment
kubectl scale deployment cloudviz-api --replicas=5 -n cloudviz

# Update image
kubectl set image deployment/cloudviz-api cloudviz=cloudviz:v1.1.0 -n cloudviz

# Check HPA status
kubectl get hpa -n cloudviz
```

## ☁️ Cloud Platform Deployments

### Azure Container Instances

```yaml
# azure-container-instance.yaml
apiVersion: 2019-12-01
location: australiaeast
name: cloudviz-aci
properties:
  containers:
  - name: cloudviz
    properties:
      image: cloudviz:latest
      ports:
      - port: 8000
        protocol: TCP
      resources:
        requests:
          cpu: 1.0
          memoryInGB: 2.0
      environmentVariables:
      - name: AZURE_CLIENT_ID
        secureValue: "your-client-id"
      - name: AZURE_CLIENT_SECRET
        secureValue: "your-client-secret"
      - name: AZURE_TENANT_ID
        value: "your-tenant-id"
  osType: Linux
  ipAddress:
    type: Public
    ports:
    - port: 8000
      protocol: TCP
    dnsNameLabel: cloudviz-demo
  restartPolicy: Always
type: Microsoft.ContainerInstance/containerGroups
```

### AWS ECS

```json
{
  "family": "cloudviz-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::ACCOUNT:role/cloudvizTaskRole",
  "containerDefinitions": [
    {
      "name": "cloudviz",
      "image": "cloudviz:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "AWS_DEFAULT_REGION",
          "value": "ap-southeast-2"
        }
      ],
      "secrets": [
        {
          "name": "AZURE_CLIENT_ID",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:cloudviz/azure:client_id::"
        },
        {
          "name": "AZURE_CLIENT_SECRET", 
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:cloudviz/azure:client_secret::"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/cloudviz",
          "awslogs-region": "ap-southeast-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Google Cloud Run

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: cloudviz
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "1"
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/cpu-throttling: "false"
    spec:
      containerConcurrency: 100
      timeoutSeconds: 300
      containers:
      - image: gcr.io/PROJECT_ID/cloudviz:latest
        ports:
        - containerPort: 8000
        resources:
          limits:
            cpu: "1"
            memory: "2Gi"
        env:
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: /app/config/gcp-service-account.json
        - name: GCP_PROJECT_ID
          value: "your-project-id"
        - name: AZURE_CLIENT_ID
          valueFrom:
            secretKeyRef:
              name: azure-credentials
              key: client_id
```

## 🖥️ Traditional Server Deployment

### System Requirements

**Minimum Requirements:**
- **OS**: Ubuntu 20.04+, CentOS 8+, or similar
- **CPU**: 2 cores
- **Memory**: 4GB RAM
- **Storage**: 20GB free space
- **Python**: 3.8 or higher

**Recommended for Production:**
- **OS**: Ubuntu 22.04 LTS
- **CPU**: 4+ cores
- **Memory**: 8GB+ RAM
- **Storage**: 50GB+ SSD
- **Python**: 3.11

### Installation Steps

1. **System Preparation**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install dependencies
   sudo apt install -y python3 python3-pip python3-venv nginx postgresql redis-server
   
   # Create cloudviz user
   sudo useradd -m -s /bin/bash cloudviz
   sudo usermod -aG sudo cloudviz
   ```

2. **Application Setup**
   ```bash
   # Switch to cloudviz user
   sudo su - cloudviz
   
   # Clone repository
   git clone https://github.com/navidrast/cloudviz.git
   cd cloudviz
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Database Setup**
   ```bash
   # Configure PostgreSQL
   sudo -u postgres createuser cloudviz
   sudo -u postgres createdb cloudviz -O cloudviz
   sudo -u postgres psql -c "ALTER USER cloudviz PASSWORD 'secure-password';"
   
   # Run migrations
   python scripts/migrate.py migrate
   ```

4. **Configuration**
   ```bash
   # Create configuration file
   cp config/production.yml.example config/production.yml
   
   # Edit configuration
   nano config/production.yml
   
   # Set environment variables
   echo "export CLOUDVIZ_ENV=production" >> ~/.bashrc
   echo "export DATABASE_URL=postgresql://cloudviz:secure-password@localhost/cloudviz" >> ~/.bashrc
   source ~/.bashrc
   ```

### Systemd Service Configuration

Create `/etc/systemd/system/cloudviz.service`:

```ini
[Unit]
Description=CloudViz API Server
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=notify
User=cloudviz
Group=cloudviz
WorkingDirectory=/home/cloudviz/cloudviz
Environment=PATH=/home/cloudviz/cloudviz/venv/bin
Environment=CLOUDVIZ_ENV=production
ExecStart=/home/cloudviz/cloudviz/venv/bin/uvicorn cloudviz.api.main:app --host 0.0.0.0 --port 8000 --workers 4
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5
KillMode=mixed
TimeoutStopSec=5

# Security settings
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/home/cloudviz/cloudviz/data /home/cloudviz/cloudviz/logs
PrivateTmp=yes

[Install]
WantedBy=multi-user.target
```

### NGINX Configuration

Create `/etc/nginx/sites-available/cloudviz`:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL configuration
    ssl_certificate /etc/ssl/certs/cloudviz.crt;
    ssl_certificate_key /etc/ssl/private/cloudviz.key;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

    location / {
        limit_req zone=api burst=20 nodelay;
        
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### Service Management

```bash
# Enable and start services
sudo systemctl enable cloudviz
sudo systemctl start cloudviz

# Enable NGINX site
sudo ln -s /etc/nginx/sites-available/cloudviz /etc/nginx/sites-enabled/
sudo systemctl restart nginx

# Check status
sudo systemctl status cloudviz
sudo systemctl status nginx

# View logs
sudo journalctl -u cloudviz -f
```

## 📊 Monitoring & Health Checks

### Health Check Endpoints

CloudViz provides several health check endpoints:

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed system status
curl http://localhost:8000/api/v1/system/status

# Metrics endpoint
curl http://localhost:8000/api/v1/system/metrics
```

### Monitoring Setup

#### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'cloudviz'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/api/v1/system/metrics'
    scrape_interval: 30s
```

#### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "CloudViz Monitoring",
    "panels": [
      {
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, cloudviz_request_duration_seconds_bucket)"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(cloudviz_request_errors_total[5m])"
          }
        ]
      },
      {
        "title": "Discovery Jobs",
        "type": "graph",
        "targets": [
          {
            "expr": "cloudviz_discovery_jobs_total"
          }
        ]
      }
    ]
  }
}
```

## 🔧 Production Configuration

### Performance Tuning

```yaml
# config/production.yml
api:
  host: "0.0.0.0"
  port: 8000
  workers: 4  # Number of CPU cores
  
database:
  pool_size: 20
  max_overflow: 30
  pool_timeout: 30
  
cache:
  redis_url: "redis://redis:6379/0"
  default_ttl: 3600
  max_connections: 50
  
discovery:
  timeout: 300
  batch_size: 100
  parallel_regions: true
  max_concurrent_jobs: 10

logging:
  level: "INFO"
  format: "json"
  file: "/app/logs/cloudviz.log"
  max_size: "100MB"
  backup_count: 5
```

### Security Hardening

```yaml
security:
  jwt:
    secret_key: "${JWT_SECRET_KEY}"
    algorithm: "HS256"
    expiration: 3600
    
  cors:
    allow_origins: ["https://your-domain.com"]
    allow_methods: ["GET", "POST", "PUT", "DELETE"]
    allow_headers: ["Authorization", "Content-Type"]
    
  rate_limiting:
    discovery: "10/minute"
    diagrams: "20/minute" 
    api: "100/minute"
    
  encryption:
    credentials_key: "${ENCRYPTION_KEY}"
    algorithm: "AES-256-GCM"
```

### Backup Strategy

```bash
#!/bin/bash
# backup.sh - Database backup script

BACKUP_DIR="/backups/cloudviz"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -h localhost -U cloudviz -d cloudviz > $BACKUP_DIR/cloudviz_$DATE.sql

# Backup configuration
tar -czf $BACKUP_DIR/config_$DATE.tar.gz /app/config

# Backup logs (last 7 days)
find /app/logs -name "*.log" -mtime -7 -exec cp {} $BACKUP_DIR/ \;

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

# Upload to cloud storage (optional)
# aws s3 sync $BACKUP_DIR s3://your-backup-bucket/cloudviz/
```

### Log Rotation

```bash
# /etc/logrotate.d/cloudviz
/home/cloudviz/cloudviz/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    postrotate
        systemctl reload cloudviz
    endscript
}
```

## 🚨 Troubleshooting

### Common Deployment Issues

1. **Database Connection Issues**
   ```bash
   # Check database connectivity
   psql -h localhost -U cloudviz -d cloudviz -c "SELECT 1;"
   
   # Check connection string
   echo $DATABASE_URL
   ```

2. **Redis Connection Issues**
   ```bash
   # Test Redis connectivity
   redis-cli ping
   
   # Check Redis configuration
   redis-cli config get "*"
   ```

3. **Permission Issues**
   ```bash
   # Fix file permissions
   sudo chown -R cloudviz:cloudviz /home/cloudviz/cloudviz
   sudo chmod -R 755 /home/cloudviz/cloudviz
   ```

4. **Memory Issues**
   ```bash
   # Check memory usage
   free -h
   
   # Check CloudViz memory usage
   ps aux | grep cloudviz
   ```

5. **Port Conflicts**
   ```bash
   # Check if port is in use
   sudo netstat -tlnp | grep 8000
   
   # Find process using port
   sudo lsof -i :8000
   ```

### Log Analysis

```bash
# View CloudViz logs
sudo journalctl -u cloudviz -n 100

# Follow logs in real-time
sudo journalctl -u cloudviz -f

# Search for errors
sudo journalctl -u cloudviz | grep ERROR

# Check NGINX logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

For more deployment examples and configurations, see our **[Configuration](Configuration)** guide or check the **[Troubleshooting](Troubleshooting)** page for common issues and solutions.