# 🔧 Configuration Guide

Comprehensive configuration guide for CloudViz. Learn how to configure cloud providers, customize settings, and optimize for your environment.

## 📋 **Configuration Overview**

CloudViz uses a hierarchical configuration system:
1. **Default values** (built into the application)
2. **Configuration files** (`config/*.yml`)
3. **Environment variables** (override everything)
4. **Runtime settings** (database-stored settings)

## 📁 **Configuration Files**

### **Directory Structure**
```
config/
├── dev.yml          # Development environment
├── prod.yml         # Production environment  
├── test.yml         # Test environment
├── local.yml        # Local overrides (git-ignored)
└── docker.yml       # Docker-specific settings
```

### **Base Configuration Template**

```yaml
# config/local.yml - Copy from dev.yml and customize
server:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  log_level: "info"
  reload: false
  debug: false

database:
  url: "postgresql://cloudviz:password@localhost:5432/cloudviz"
  echo: false
  pool_size: 20
  max_overflow: 30
  pool_timeout: 30
  pool_recycle: 3600

redis:
  url: "redis://localhost:6379/0"
  max_connections: 100
  retry_on_timeout: true
  socket_timeout: 30
  socket_connect_timeout: 30

security:
  secret_key: "your-super-secret-key-change-this-in-production"
  algorithm: "HS256"
  access_token_expire_minutes: 30
  refresh_token_expire_days: 7
  password_min_length: 8
  max_login_attempts: 5
  lockout_duration_minutes: 15

cors:
  allow_origins: ["http://localhost:3000", "https://yourdomain.com"]
  allow_credentials: true
  allow_methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
  allow_headers: ["*"]

rate_limiting:
  enabled: true
  requests_per_minute: 100
  burst_size: 200
  storage_url: "redis://localhost:6379/1"

logging:
  level: "INFO"
  format: "json"
  file_path: "/var/log/cloudviz/app.log"
  max_size_mb: 100
  backup_count: 5
  enable_file_logging: true
  enable_console_logging: true

monitoring:
  enable_metrics: true
  metrics_port: 9090
  enable_health_checks: true
  enable_profiling: false

cloud_providers:
  azure:
    enabled: true
    subscription_id: "${AZURE_SUBSCRIPTION_ID}"
    tenant_id: "${AZURE_TENANT_ID}"
    client_id: "${AZURE_CLIENT_ID}"
    client_secret: "${AZURE_CLIENT_SECRET}"
    timeout: 30
    retry_count: 3
    regions:
      - "eastus"
      - "westus2"
      - "centralus"
      - "northeurope"
      - "westeurope"
    resource_types:
      - "Microsoft.Compute/virtualMachines"
      - "Microsoft.Storage/storageAccounts"
      - "Microsoft.Sql/servers"
      - "Microsoft.Network/loadBalancers"
      
  aws:
    enabled: true
    region: "us-west-2"
    access_key_id: "${AWS_ACCESS_KEY_ID}"
    secret_access_key: "${AWS_SECRET_ACCESS_KEY}"
    session_token: "${AWS_SESSION_TOKEN}"  # Optional for temporary credentials
    timeout: 30
    retry_count: 3
    regions:
      - "us-west-2"
      - "us-east-1"
      - "eu-west-1"
      - "ap-southeast-1"
    services:
      - "ec2"
      - "rds"
      - "lambda"
      - "ecs"
      - "s3"
      
  gcp:
    enabled: true
    project_id: "${GCP_PROJECT_ID}"
    service_account_path: "${GCP_SERVICE_ACCOUNT_PATH}"
    timeout: 30
    retry_count: 3
    regions:
      - "us-central1"
      - "us-west1"
      - "europe-west1"
      - "asia-southeast1"
    services:
      - "compute"
      - "gke"
      - "bigquery"
      - "cloudsql"

visualization:
  default_theme: "enterprise"
  default_layout: "hierarchical"
  max_nodes_per_diagram: 1000
  cache_timeout_seconds: 3600
  enable_cost_display: true
  enable_dependency_mapping: true
  themes:
    enterprise:
      primary_color: "#2E86AB"
      secondary_color: "#A23B72"
      success_color: "#F18F01"
      warning_color: "#C73E1D"
      background_color: "#F8F9FA"
    modern:
      primary_color: "#6366F1"
      secondary_color: "#EC4899"
      success_color: "#10B981"
      warning_color: "#F59E0B"
      background_color: "#FFFFFF"

background_jobs:
  broker_url: "redis://localhost:6379/2"
  result_backend: "redis://localhost:6379/2"
  task_serializer: "json"
  result_serializer: "json"
  accept_content: ["json"]
  timezone: "UTC"
  enable_utc: true
  worker_concurrency: 4
  task_soft_time_limit: 300
  task_time_limit: 600

notifications:
  slack:
    enabled: false
    webhook_url: "${SLACK_WEBHOOK_URL}"
    default_channel: "#infrastructure"
  teams:
    enabled: false
    webhook_url: "${TEAMS_WEBHOOK_URL}"
  email:
    enabled: false
    smtp_host: "${EMAIL_SMTP_HOST}"
    smtp_port: 587
    username: "${EMAIL_USERNAME}"
    password: "${EMAIL_PASSWORD}"
    use_tls: true
    from_address: "cloudviz@yourcompany.com"

storage:
  backend: "local"  # Options: local, s3, azure_blob, gcp_storage
  local:
    base_path: "/var/lib/cloudviz/storage"
  s3:
    bucket_name: "${S3_BUCKET_NAME}"
    region: "${S3_REGION}"
    access_key_id: "${S3_ACCESS_KEY_ID}"
    secret_access_key: "${S3_SECRET_ACCESS_KEY}"
  azure_blob:
    account_name: "${AZURE_STORAGE_ACCOUNT}"
    account_key: "${AZURE_STORAGE_KEY}"
    container_name: "cloudviz"
  gcp_storage:
    bucket_name: "${GCP_STORAGE_BUCKET}"
    service_account_path: "${GCP_STORAGE_SERVICE_ACCOUNT}"
```

## 🌍 **Environment Variables**

### **Core Configuration**
```bash
# Application Settings
CLOUDVIZ_ENV=production
CLOUDVIZ_CONFIG_FILE=/app/config/prod.yml
CLOUDVIZ_SECRET_KEY=your-super-secret-key
CLOUDVIZ_DEBUG=false

# Database Configuration
DATABASE_URL=postgresql://user:pass@host:5432/dbname
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=100

# Security Settings
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### **Cloud Provider Credentials**
```bash
# Azure Configuration
AZURE_SUBSCRIPTION_ID=12345678-1234-1234-1234-123456789012
AZURE_TENANT_ID=87654321-4321-4321-4321-210987654321
AZURE_CLIENT_ID=abcdef12-3456-7890-abcd-ef1234567890
AZURE_CLIENT_SECRET=your-azure-client-secret

# AWS Configuration
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_DEFAULT_REGION=us-west-2
AWS_SESSION_TOKEN=optional-session-token

# GCP Configuration
GCP_PROJECT_ID=my-project-12345
GCP_SERVICE_ACCOUNT_PATH=/path/to/service-account.json
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

### **Optional Service Configuration**
```bash
# Monitoring & Logging
PROMETHEUS_METRICS_PORT=9090
LOG_LEVEL=INFO
LOG_FORMAT=json

# Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# Storage
STORAGE_BACKEND=s3
S3_BUCKET_NAME=cloudviz-storage
S3_REGION=us-west-2
S3_ACCESS_KEY_ID=your-s3-access-key
S3_SECRET_ACCESS_KEY=your-s3-secret-key
```

## ☁️ **Cloud Provider Setup**

### **Azure Configuration**

#### **1. Create Service Principal**
```bash
# Login to Azure
az login

# Create service principal with Reader role
az ad sp create-for-rbac \
  --name "CloudViz-Production" \
  --role "Reader" \
  --scopes "/subscriptions/YOUR_SUBSCRIPTION_ID"

# Output will provide credentials for configuration
```

#### **2. Required Permissions**
- **Reader**: For basic resource discovery
- **Cost Management Reader**: For cost analysis
- **Monitoring Reader**: For metrics and performance data

#### **3. Configuration Example**
```yaml
cloud_providers:
  azure:
    enabled: true
    subscription_id: "12345678-1234-1234-1234-123456789012"
    tenant_id: "87654321-4321-4321-4321-210987654321"
    client_id: "abcdef12-3456-7890-abcd-ef1234567890"
    client_secret: "your-client-secret"
    regions:
      - "eastus"
      - "westus2"
      - "northeurope"
    resource_groups:
      - "production"
      - "staging"
      - "development"
```

### **AWS Configuration**

#### **1. Create IAM User**
```bash
# Create IAM user
aws iam create-user --user-name cloudviz-readonly

# Attach ReadOnlyAccess policy
aws iam attach-user-policy \
  --user-name cloudviz-readonly \
  --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess

# Create access key
aws iam create-access-key --user-name cloudviz-readonly
```

#### **2. Required Permissions**
- **ReadOnlyAccess**: For resource discovery
- **BillingReadOnlyAccess**: For cost analysis
- **CloudWatchReadOnlyAccess**: For metrics

#### **3. Configuration Example**
```yaml
cloud_providers:
  aws:
    enabled: true
    region: "us-west-2"
    access_key_id: "AKIAIOSFODNN7EXAMPLE"
    secret_access_key: "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
    regions:
      - "us-west-2"
      - "us-east-1"
      - "eu-west-1"
    services:
      - "ec2"
      - "rds"
      - "lambda"
      - "ecs"
```

### **GCP Configuration**

#### **1. Create Service Account**
```bash
# Create service account
gcloud iam service-accounts create cloudviz-readonly \
  --display-name="CloudViz ReadOnly"

# Grant Viewer role
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:cloudviz-readonly@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/viewer"

# Download key file
gcloud iam service-accounts keys create cloudviz-key.json \
  --iam-account=cloudviz-readonly@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

#### **2. Required Roles**
- **Viewer**: For resource discovery
- **BigQuery Data Viewer**: For BigQuery analysis
- **Monitoring Viewer**: For metrics

#### **3. Configuration Example**
```yaml
cloud_providers:
  gcp:
    enabled: true
    project_id: "my-project-12345"
    service_account_path: "/path/to/cloudviz-key.json"
    regions:
      - "us-central1"
      - "us-west1"
      - "europe-west1"
```

## 🗄️ **Database Configuration**

### **PostgreSQL Setup (Recommended)**

#### **1. Installation**
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Docker
docker run -d \
  --name cloudviz-postgres \
  -e POSTGRES_DB=cloudviz \
  -e POSTGRES_USER=cloudviz \
  -e POSTGRES_PASSWORD=secure_password \
  -p 5432:5432 \
  postgres:13
```

#### **2. Database Setup**
```sql
-- Create database and user
CREATE DATABASE cloudviz;
CREATE USER cloudviz WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE cloudviz TO cloudviz;

-- Enable required extensions
\c cloudviz
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
```

#### **3. Configuration**
```yaml
database:
  url: "postgresql://cloudviz:secure_password@localhost:5432/cloudviz"
  echo: false  # Set to true for SQL debugging
  pool_size: 20
  max_overflow: 30
  pool_timeout: 30
  pool_recycle: 3600
```

### **SQLite Setup (Development)**

```yaml
database:
  url: "sqlite:///./data/cloudviz.db"
  echo: false
```

## 📦 **Redis Configuration**

### **Redis Setup**

#### **1. Installation**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Docker
docker run -d \
  --name cloudviz-redis \
  -p 6379:6379 \
  redis:6-alpine
```

#### **2. Configuration**
```yaml
redis:
  url: "redis://localhost:6379/0"
  max_connections: 100
  retry_on_timeout: true
  socket_timeout: 30
  socket_connect_timeout: 30
```

#### **3. Redis Cluster (Production)**
```yaml
redis:
  cluster_nodes:
    - "redis-node1:6379"
    - "redis-node2:6379"
    - "redis-node3:6379"
  max_connections: 100
  skip_full_coverage_check: true
```

## 🔐 **Security Configuration**

### **JWT Configuration**
```yaml
security:
  secret_key: "your-super-secret-key-minimum-32-characters"
  algorithm: "HS256"
  access_token_expire_minutes: 30
  refresh_token_expire_days: 7
  
  # Password requirements
  password_min_length: 8
  password_require_uppercase: true
  password_require_lowercase: true
  password_require_numbers: true
  password_require_special: true
  
  # Account lockout
  max_login_attempts: 5
  lockout_duration_minutes: 15
```

### **CORS Configuration**
```yaml
cors:
  allow_origins:
    - "https://yourdomain.com"
    - "https://app.yourdomain.com"
  allow_credentials: true
  allow_methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
  allow_headers: ["*"]
  expose_headers: ["X-Total-Count"]
  max_age: 86400
```

### **Rate Limiting**
```yaml
rate_limiting:
  enabled: true
  
  # Global limits
  global_limit: "1000/hour"
  
  # Per-endpoint limits
  endpoint_limits:
    "/auth/login": "10/minute"
    "/azure/discover": "100/hour"
    "/aws/discover": "100/hour"
    "/gcp/discover": "100/hour"
    "/visualization/generate": "200/hour"
  
  # Storage backend
  storage_url: "redis://localhost:6379/1"
  
  # Headers
  include_headers: true
  header_limit: "X-RateLimit-Limit"
  header_remaining: "X-RateLimit-Remaining"
  header_reset: "X-RateLimit-Reset"
```

## 📊 **Monitoring Configuration**

### **Prometheus Metrics**
```yaml
monitoring:
  enable_metrics: true
  metrics_port: 9090
  metrics_path: "/metrics"
  
  # Custom metrics
  custom_metrics:
    - name: "cloudviz_discoveries_total"
      type: "counter"
      description: "Total number of cloud discoveries"
    - name: "cloudviz_resources_discovered"
      type: "gauge"
      description: "Number of resources discovered"
    - name: "cloudviz_api_request_duration"
      type: "histogram"
      description: "API request duration in seconds"
```

### **Health Checks**
```yaml
monitoring:
  enable_health_checks: true
  health_check_interval: 30
  
  # Health check endpoints
  health_checks:
    - name: "database"
      endpoint: "SELECT 1"
      timeout: 5
    - name: "redis"
      endpoint: "PING"
      timeout: 3
    - name: "azure_api"
      endpoint: "https://management.azure.com/subscriptions"
      timeout: 10
```

## 🔄 **Background Jobs Configuration**

### **Celery Configuration**
```yaml
background_jobs:
  broker_url: "redis://localhost:6379/2"
  result_backend: "redis://localhost:6379/2"
  
  # Serialization
  task_serializer: "json"
  result_serializer: "json"
  accept_content: ["json"]
  
  # Timezone
  timezone: "UTC"
  enable_utc: true
  
  # Worker settings
  worker_concurrency: 4
  worker_prefetch_multiplier: 1
  worker_max_tasks_per_child: 1000
  
  # Task settings
  task_soft_time_limit: 300
  task_time_limit: 600
  task_acks_late: true
  task_reject_on_worker_lost: true
  
  # Routing
  task_routes:
    "cloudviz.tasks.discovery": {"queue": "discovery"}
    "cloudviz.tasks.visualization": {"queue": "visualization"}
    "cloudviz.tasks.notifications": {"queue": "notifications"}
```

## 🎨 **Visualization Configuration**

### **Theme Configuration**
```yaml
visualization:
  default_theme: "enterprise"
  default_layout: "hierarchical"
  max_nodes_per_diagram: 1000
  cache_timeout_seconds: 3600
  
  themes:
    enterprise:
      name: "Enterprise"
      description: "Professional enterprise theme"
      colors:
        primary: "#2E86AB"
        secondary: "#A23B72"
        success: "#F18F01"
        warning: "#C73E1D"
        danger: "#DC3545"
        info: "#6C757D"
        light: "#F8F9FA"
        dark: "#343A40"
      fonts:
        family: "Arial, sans-serif"
        size: "12px"
        weight: "normal"
      shapes:
        default: "rect"
        database: "cylinder"
        storage: "hexagon"
        network: "circle"
    
    modern:
      name: "Modern"
      description: "Modern colorful theme"
      colors:
        primary: "#6366F1"
        secondary: "#EC4899"
        success: "#10B981"
        warning: "#F59E0B"
        danger: "#EF4444"
        info: "#3B82F6"
        light: "#FFFFFF"
        dark: "#1F2937"
```

### **Layout Configuration**
```yaml
visualization:
  layouts:
    hierarchical:
      name: "Hierarchical"
      direction: "TD"  # Top-Down
      spacing:
        node: 50
        tier: 100
        rank: 80
      
    force_directed:
      name: "Force Directed"
      attraction: 0.1
      repulsion: 200
      iterations: 100
      
    circular:
      name: "Circular"
      radius: 300
      center_x: 500
      center_y: 400
```

## 📧 **Notification Configuration**

### **Slack Integration**
```yaml
notifications:
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
    default_channel: "#infrastructure"
    username: "CloudViz"
    icon_emoji: ":cloud:"
    
    # Message templates
    templates:
      discovery_complete: |
        :white_check_mark: *Infrastructure Discovery Complete*
        
        *Provider:* {{provider}}
        *Resources Found:* {{resources_found}}
        *Cost Estimate:* ${{cost_estimate}}/month
        *Regions:* {{regions}}
        
        <{{diagram_url}}|View Diagram>
```

### **Email Notifications**
```yaml
notifications:
  email:
    enabled: true
    smtp_host: "smtp.gmail.com"
    smtp_port: 587
    use_tls: true
    username: "your-email@gmail.com"
    password: "your-app-password"
    from_address: "cloudviz@yourcompany.com"
    
    # Templates
    templates:
      discovery_complete:
        subject: "CloudViz: Infrastructure Discovery Complete - {{provider}}"
        html_template: "templates/email/discovery_complete.html"
        text_template: "templates/email/discovery_complete.txt"
```

## 🔧 **Validation & Testing**

### **Configuration Validation**
```bash
# Validate configuration
python -m cloudviz.core.config validate

# Test cloud provider connections
python -m cloudviz.core.config test-connections

# Check database connectivity
python -m cloudviz.core.config test-database

# Test Redis connectivity
python -m cloudviz.core.config test-redis
```

### **Environment-Specific Testing**
```bash
# Test development environment
CLOUDVIZ_ENV=development python -m cloudviz.core.config validate

# Test production environment
CLOUDVIZ_ENV=production python -m cloudviz.core.config validate

# Test with specific config file
CLOUDVIZ_CONFIG_FILE=/path/to/config.yml python -m cloudviz.core.config validate
```

---

**Next Steps:**
- [🚀 Quick Start](Quick-Start) - Get CloudViz running with your configuration
- [🔐 Security Setup](Security) - Implement security best practices
- [📊 Monitoring Setup](Monitoring-Setup) - Set up comprehensive monitoring
- [🚨 Troubleshooting](Troubleshooting) - Resolve configuration issues
