# CloudViz Configuration Guide

Comprehensive configuration guide for the CloudViz multi-cloud infrastructure visualization platform covering all deployment scenarios, cloud provider setups, and advanced configuration options.

## Table of Contents

1. [Overview](#overview)
2. [Configuration File Structure](#configuration-file-structure)
3. [Environment Variables](#environment-variables)
4. [API Server Configuration](#api-server-configuration)
5. [Database Configuration](#database-configuration)
6. [Cache Configuration](#cache-configuration)
7. [Logging Configuration](#logging-configuration)
8. [Visualization Configuration](#visualization-configuration)
9. [Cloud Provider Configuration](#cloud-provider-configuration)
10. [Security Configuration](#security-configuration)
11. [Performance Tuning](#performance-tuning)
12. [Monitoring Configuration](#monitoring-configuration)
13. [Deployment-Specific Configurations](#deployment-specific-configurations)
14. [Configuration Validation](#configuration-validation)
15. [Troubleshooting](#troubleshooting)

## Overview

CloudViz supports flexible configuration through multiple methods:
- **YAML/JSON configuration files** (recommended for complex setups)
- **Environment variables** (recommended for containers and CI/CD)
- **Command-line arguments** (for development and testing)
- **Runtime configuration** (via API for dynamic updates)

Configuration precedence (highest to lowest):
1. Command-line arguments
2. Environment variables
3. Configuration file
4. Default values

## Configuration File Structure

CloudViz uses YAML configuration files with a hierarchical structure. The default locations are:

1. `config/config.yaml` (in application directory)
2. `~/.cloudviz/config.yaml` (user home directory)
3. `/etc/cloudviz/config.yaml` (system-wide)

### Basic Configuration Template

```yaml
# config/config.yaml
# CloudViz Configuration File

# Application metadata
app:
  name: "CloudViz"
  version: "1.0.0"
  environment: "production"  # development, staging, production
  
# API server configuration
api:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  reload: false
  log_level: "info"
  timeout: 300
  max_request_size: 10485760  # 10MB
  
  # CORS settings
  cors_enabled: true
  cors_origins: ["*"]
  cors_methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
  cors_headers: ["*"]
  
  # Rate limiting
  rate_limit_requests: 100
  rate_limit_window: 60
  rate_limit_burst: 200
  
  # Security
  enable_https: false
  ssl_cert_file: null
  ssl_key_file: null
  
  # Authentication
  jwt_secret: "${CLOUDVIZ_JWT_SECRET}"
  jwt_algorithm: "HS256"
  jwt_expiration: 3600
  
# Database configuration
database:
  url: "${DATABASE_URL}"
  driver: "postgresql"
  pool_size: 10
  max_overflow: 20
  pool_timeout: 30
  pool_recycle: 3600
  echo: false
  
# Cache configuration
cache:
  enabled: true
  backend: "redis"
  url: "${REDIS_URL}"
  default_ttl: 3600
  max_size: 1000
  
# Logging configuration
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  json_format: false
  correlation_id: true
  
# Visualization settings
visualization:
  default_theme: "professional"
  default_format: "mermaid"
  default_layout: "hierarchical"
  output_directory: "/app/output"
  
# Cloud provider configurations
providers:
  azure:
    enabled: true
    authentication_method: "service_principal"
    tenant_id: "${AZURE_TENANT_ID}"
    client_id: "${AZURE_CLIENT_ID}"
    client_secret: "${AZURE_CLIENT_SECRET}"
    
  aws:
    enabled: false
    authentication_method: "access_key"
    access_key_id: "${AWS_ACCESS_KEY_ID}"
    secret_access_key: "${AWS_SECRET_ACCESS_KEY}"
    region: "us-east-1"
    
  gcp:
    enabled: false
    authentication_method: "service_account"
    project_id: "${GCP_PROJECT_ID}"
    credentials_path: "/app/config/gcp-credentials.json"
```

## Environment Variables

### Core Application Variables

```bash
# Application
CLOUDVIZ_ENV=production
CLOUDVIZ_CONFIG_FILE=/app/config/production.yml
CLOUDVIZ_SECRET_KEY=your-secret-key-here
CLOUDVIZ_DEBUG=false

# API Server
CLOUDVIZ_API_HOST=0.0.0.0
CLOUDVIZ_API_PORT=8000
CLOUDVIZ_API_WORKERS=4
CLOUDVIZ_API_RELOAD=false
CLOUDVIZ_LOG_LEVEL=INFO

# Authentication
CLOUDVIZ_JWT_SECRET=your-jwt-secret-here
CLOUDVIZ_JWT_ALGORITHM=HS256
CLOUDVIZ_JWT_EXPIRATION=3600

# Database
DATABASE_URL=postgresql://user:pass@host:5432/cloudviz
CLOUDVIZ_DB_POOL_SIZE=10
CLOUDVIZ_DB_MAX_OVERFLOW=20

# Cache
REDIS_URL=redis://host:6379/0
CLOUDVIZ_CACHE_ENABLED=true
CLOUDVIZ_CACHE_TTL=3600

# Security
CLOUDVIZ_ENABLE_HTTPS=false
CLOUDVIZ_SSL_CERT_FILE=/app/ssl/cert.pem
CLOUDVIZ_SSL_KEY_FILE=/app/ssl/key.pem
```

### Cloud Provider Variables

```bash
# Azure
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_SUBSCRIPTION_ID=your-subscription-id

# AWS
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=us-east-1
AWS_SESSION_TOKEN=your-session-token  # For temporary credentials

# GCP
GCP_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
CLOUDSDK_CORE_PROJECT=your-project-id
```

### Optional Variables

```bash
# Monitoring
CLOUDVIZ_METRICS_ENABLED=true
PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus

# Logging
CLOUDVIZ_LOG_FILE=/var/log/cloudviz/app.log
CLOUDVIZ_LOG_MAX_SIZE=10485760
CLOUDVIZ_LOG_BACKUP_COUNT=5

# Performance
CLOUDVIZ_MAX_CONCURRENT_JOBS=10
CLOUDVIZ_JOB_TIMEOUT=3600
CLOUDVIZ_CACHE_MAX_SIZE=1000

# Development
CLOUDVIZ_PROFILE=false
CLOUDVIZ_DEBUG_SQL=false
```

## API Server Configuration

### Basic API Configuration

```yaml
api:
  # Server binding
  host: "0.0.0.0"          # Bind to all interfaces
  port: 8000               # Default port
  workers: 4               # Number of worker processes
  reload: false            # Auto-reload on code changes (dev only)
  
  # Request handling
  timeout: 300             # Request timeout in seconds
  max_request_size: 10485760  # Maximum request size (10MB)
  keepalive_timeout: 2     # Keep-alive timeout
  
  # Logging
  log_level: "info"        # debug, info, warning, error, critical
  access_log: true         # Enable access logging
```

### Advanced API Configuration

```yaml
api:
  # Performance settings
  workers: 4
  worker_class: "uvicorn.workers.UvicornWorker"
  worker_connections: 1000
  max_requests: 1000
  max_requests_jitter: 50
  preload_app: true
  
  # Security settings
  enable_https: true
  ssl_cert_file: "/app/ssl/cert.pem"
  ssl_key_file: "/app/ssl/key.pem"
  ssl_ciphers: "ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS"
  
  # Headers
  server_header: false     # Hide server header
  forwarded_allow_ips: "*" # Trusted proxy IPs
  proxy_headers: true      # Trust proxy headers
  
  # Timeouts
  timeout: 300
  keepalive_timeout: 2
  graceful_timeout: 30
```

### CORS Configuration

```yaml
api:
  cors_enabled: true
  cors_origins:
    - "https://app.example.com"
    - "https://dashboard.example.com"
    - "http://localhost:3000"  # Development
  cors_methods:
    - "GET"
    - "POST"
    - "PUT"
    - "DELETE"
    - "OPTIONS"
  cors_headers:
    - "Authorization"
    - "Content-Type"
    - "X-Requested-With"
  cors_credentials: true
  cors_max_age: 3600
```

### Rate Limiting Configuration

```yaml
api:
  rate_limiting:
    enabled: true
    storage: "redis"  # memory, redis
    storage_url: "${REDIS_URL}"
    
    # Global limits
    default_rate: "100/minute"
    burst_rate: "200/minute"
    
    # Per-endpoint limits
    endpoints:
      "/api/v1/extract": "5/minute"
      "/api/v1/render": "20/minute"
      "/auth/login": "10/minute"
    
    # Per-user limits
    per_user:
      basic: "50/minute"
      premium: "200/minute"
      admin: "1000/minute"
```

## Database Configuration

### PostgreSQL Configuration

```yaml
database:
  # Connection string (recommended)
  url: "postgresql://cloudviz:password@localhost:5432/cloudviz"
  
  # Or individual components
  driver: "postgresql"
  host: "localhost"
  port: 5432
  database: "cloudviz"
  username: "cloudviz"
  password: "password"
  
  # Connection pool settings
  pool_size: 10            # Number of connections to pool
  max_overflow: 20         # Additional connections beyond pool_size
  pool_timeout: 30         # Timeout to get connection from pool
  pool_recycle: 3600       # Recycle connections after seconds
  pool_pre_ping: true      # Validate connections before use
  
  # SQLAlchemy settings
  echo: false              # Log SQL statements
  echo_pool: false         # Log connection pool events
  future: true             # Use SQLAlchemy 2.0 style
  
  # SSL settings
  ssl_mode: "prefer"       # disable, allow, prefer, require
  ssl_cert: "/path/to/client-cert.pem"
  ssl_key: "/path/to/client-key.pem"
  ssl_ca: "/path/to/ca-cert.pem"
```

### Database Performance Tuning

```yaml
database:
  # Connection optimization
  pool_size: 20
  max_overflow: 50
  pool_timeout: 60
  pool_recycle: 7200
  
  # Query optimization
  query_timeout: 30
  statement_timeout: 60
  
  # Performance settings
  isolation_level: "READ_COMMITTED"
  autocommit: false
  autoflush: true
  
  # Monitoring
  echo: false
  echo_pool: false
  enable_query_stats: true
```

### Multiple Database Support

```yaml
databases:
  primary:
    url: "postgresql://user:pass@primary-db:5432/cloudviz"
    role: "read_write"
  
  replica:
    url: "postgresql://user:pass@replica-db:5432/cloudviz"
    role: "read_only"
  
  analytics:
    url: "postgresql://user:pass@analytics-db:5432/cloudviz_analytics"
    role: "read_write"
```

## Cache Configuration

### Redis Configuration

```yaml
cache:
  enabled: true
  backend: "redis"
  
  # Connection
  url: "redis://localhost:6379/0"
  # Or individual components
  host: "localhost"
  port: 6379
  db: 0
  password: null
  username: null  # Redis 6.0+
  
  # Connection pool
  max_connections: 20
  retry_on_timeout: true
  socket_timeout: 5
  socket_connect_timeout: 5
  
  # Behavior
  default_ttl: 3600        # Default expiration in seconds
  key_prefix: "cloudviz:"  # Prefix for all keys
  
  # Serialization
  serializer: "json"       # json, pickle, msgpack
  compression: "gzip"      # none, gzip, lz4
```

### Cache Strategies

```yaml
cache:
  strategies:
    # Resource inventories
    inventories:
      ttl: 3600
      max_size: 100
      strategy: "lru"
    
    # Rendered diagrams
    diagrams:
      ttl: 7200
      max_size: 50
      strategy: "lfu"
    
    # API responses
    api_responses:
      ttl: 300
      max_size: 1000
      strategy: "ttl"
```

### Multi-tier Caching

```yaml
cache:
  tiers:
    - name: "memory"
      backend: "memory"
      max_size: 100
      ttl: 300
    
    - name: "redis"
      backend: "redis"
      url: "${REDIS_URL}"
      ttl: 3600
    
    - name: "disk"
      backend: "disk"
      path: "/app/cache"
      ttl: 86400
```

## Logging Configuration

### Basic Logging

```yaml
logging:
  # Log level
  level: "INFO"            # DEBUG, INFO, WARNING, ERROR, CRITICAL
  
  # Format
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  json_format: false
  
  # Output
  console: true
  file: "/var/log/cloudviz/app.log"
  
  # Rotation
  max_file_size: 10485760  # 10MB
  backup_count: 5
  
  # Features
  correlation_id: true
  request_id: true
```

### Advanced Logging

```yaml
logging:
  # Structured logging
  json_format: true
  fields:
    service: "cloudviz"
    version: "1.0.0"
    environment: "${CLOUDVIZ_ENV}"
  
  # Multiple handlers
  handlers:
    console:
      class: "StreamHandler"
      level: "INFO"
      stream: "ext://sys.stdout"
    
    file:
      class: "RotatingFileHandler"
      level: "DEBUG"
      filename: "/var/log/cloudviz/app.log"
      max_bytes: 10485760
      backup_count: 5
    
    syslog:
      class: "SysLogHandler"
      level: "WARNING"
      address: ["localhost", 514]
      facility: "local0"
  
  # Logger configuration
  loggers:
    cloudviz:
      level: "DEBUG"
      handlers: ["console", "file"]
      propagate: false
    
    sqlalchemy:
      level: "WARNING"
      handlers: ["file"]
      propagate: false
    
    uvicorn:
      level: "INFO"
      handlers: ["console"]
      propagate: false
```

### Monitoring Integration

```yaml
logging:
  # External integrations
  integrations:
    # Elastic Stack
    elasticsearch:
      enabled: true
      hosts: ["http://elasticsearch:9200"]
      index: "cloudviz-logs"
    
    # Grafana Loki
    loki:
      enabled: true
      url: "http://loki:3100"
      labels:
        service: "cloudviz"
        environment: "${CLOUDVIZ_ENV}"
    
    # Sentry
    sentry:
      enabled: true
      dsn: "${SENTRY_DSN}"
      environment: "${CLOUDVIZ_ENV}"
      traces_sample_rate: 0.1
```

## Visualization Configuration

### Default Settings

```yaml
visualization:
  # Defaults
  default_theme: "professional"
  default_format: "mermaid"
  default_layout: "hierarchical"
  
  # Output
  output_directory: "/app/output"
  temp_directory: "/tmp/cloudviz"
  
  # Supported formats
  supported_formats:
    - "mermaid"
    - "graphviz"
    - "png"
    - "svg"
    - "pdf"
    - "jpg"
  
  # Available themes
  themes:
    - "professional"
    - "dark"
    - "light"
    - "minimal"
    - "colorful"
  
  # Layout algorithms
  layouts:
    - "hierarchical"
    - "force"
    - "circular"
    - "grid"
    - "mindmap"
    - "timeline"
```

### Rendering Configuration

```yaml
visualization:
  # Image settings
  image:
    default_width: 1920
    default_height: 1080
    default_dpi: 300
    max_width: 4096
    max_height: 4096
    background_color: "white"
    
  # Mermaid settings
  mermaid:
    theme: "professional"
    width: 1920
    height: 1080
    background_color: "white"
    config:
      theme: "base"
      themeVariables:
        primaryColor: "#ff0000"
  
  # Graphviz settings
  graphviz:
    engine: "dot"           # dot, neato, circo, twopi, fdp
    format: "svg"
    dpi: 300
    rankdir: "TB"           # TB, BT, LR, RL
    
  # Performance limits
  limits:
    max_nodes: 10000
    max_edges: 50000
    timeout: 300
    memory_limit: "2GB"
```

### Theme Configuration

```yaml
visualization:
  custom_themes:
    corporate:
      name: "Corporate Theme"
      colors:
        primary: "#0066cc"
        secondary: "#6699ff"
        accent: "#ff6600"
        background: "#ffffff"
        text: "#333333"
      fonts:
        primary: "Arial, sans-serif"
        secondary: "Georgia, serif"
      styles:
        node_border: 2
        edge_width: 1
        border_radius: 4
```

## Cloud Provider Configuration

### Azure Configuration

```yaml
providers:
  azure:
    enabled: true
    
    # Authentication
    authentication_method: "service_principal"  # service_principal, managed_identity, interactive, device_code
    tenant_id: "${AZURE_TENANT_ID}"
    client_id: "${AZURE_CLIENT_ID}"
    client_secret: "${AZURE_CLIENT_SECRET}"
    subscription_id: "${AZURE_SUBSCRIPTION_ID}"
    
    # Alternative: Managed Identity
    # authentication_method: "managed_identity"
    # client_id: "${AZURE_CLIENT_ID}"  # For user-assigned managed identity
    
    # Rate limiting
    rate_limits:
      requests_per_minute: 100
      burst_requests: 200
      backoff_factor: 2
      max_retries: 3
    
    # Timeout settings
    timeout: 300
    connection_timeout: 30
    read_timeout: 60
    
    # Resource filtering
    default_filters:
      include_resource_types:
        - "Microsoft.Compute/virtualMachines"
        - "Microsoft.Storage/storageAccounts"
        - "Microsoft.Sql/servers"
        - "Microsoft.Network/virtualNetworks"
      exclude_resource_groups:
        - "NetworkWatcherRG"
        - "AzureBackupRG"
    
    # Advanced settings
    extraction_settings:
      include_properties: true
      include_tags: true
      include_relationships: true
      max_concurrent_requests: 5
      chunk_size: 100
```

### AWS Configuration

```yaml
providers:
  aws:
    enabled: true
    
    # Authentication
    authentication_method: "access_key"  # access_key, iam_role, sso, instance_metadata
    access_key_id: "${AWS_ACCESS_KEY_ID}"
    secret_access_key: "${AWS_SECRET_ACCESS_KEY}"
    session_token: "${AWS_SESSION_TOKEN}"  # For temporary credentials
    region: "us-east-1"
    
    # Alternative: IAM Role
    # authentication_method: "iam_role"
    # role_arn: "arn:aws:iam::123456789012:role/CloudVizRole"
    # external_id: "unique-external-id"
    
    # Alternative: SSO
    # authentication_method: "sso"
    # sso_start_url: "https://example.awsapps.com/start"
    # sso_region: "us-east-1"
    # sso_account_id: "123456789012"
    # sso_role_name: "CloudVizRole"
    
    # Multi-region support
    regions:
      - "us-east-1"
      - "us-west-2"
      - "eu-west-1"
    
    # Rate limiting
    rate_limits:
      requests_per_minute: 200
      burst_requests: 400
      backoff_factor: 2
      max_retries: 3
    
    # Resource filtering
    default_filters:
      include_resource_types:
        - "ec2_instance"
        - "s3_bucket"
        - "rds_instance"
        - "vpc"
        - "load_balancer"
      exclude_regions:
        - "ap-south-1"  # Exclude specific regions
    
    # Service-specific settings
    services:
      ec2:
        include_terminated: false
        max_results_per_page: 100
      s3:
        include_bucket_policies: true
        include_encryption: true
      rds:
        include_snapshots: false
```

### GCP Configuration

```yaml
providers:
  gcp:
    enabled: true
    
    # Authentication
    authentication_method: "service_account"  # service_account, oauth, adc
    project_id: "${GCP_PROJECT_ID}"
    credentials_path: "/app/config/gcp-service-account.json"
    
    # Alternative: ADC (Application Default Credentials)
    # authentication_method: "adc"
    
    # Alternative: OAuth
    # authentication_method: "oauth"
    # client_id: "${GCP_CLIENT_ID}"
    # client_secret: "${GCP_CLIENT_SECRET}"
    # refresh_token: "${GCP_REFRESH_TOKEN}"
    
    # Multi-project support
    projects:
      - "${GCP_PROJECT_ID}"
      - "another-project-id"
    
    # Rate limiting
    rate_limits:
      requests_per_minute: 150
      quotas:
        compute: 100
        storage: 50
        sql: 20
    
    # Resource filtering
    default_filters:
      include_resource_types:
        - "compute_instance"
        - "cloud_storage"
        - "cloud_sql"
        - "vpc_network"
      exclude_zones:
        - "us-central1-c"
    
    # Service-specific settings
    services:
      compute:
        include_instance_templates: true
        include_instance_groups: true
      storage:
        include_bucket_iam: true
        include_lifecycle_policies: true
```

## Security Configuration

### Authentication Configuration

```yaml
security:
  # JWT settings
  jwt:
    secret_key: "${CLOUDVIZ_JWT_SECRET}"
    algorithm: "HS256"
    expiration: 3600
    issuer: "cloudviz"
    audience: "cloudviz-api"
    
  # Password requirements
  password_policy:
    min_length: 8
    require_uppercase: true
    require_lowercase: true
    require_numbers: true
    require_special_chars: true
    blacklist:
      - "password"
      - "123456"
      - "cloudviz"
  
  # Session management
  session:
    timeout: 3600
    max_concurrent_sessions: 5
    remember_me_duration: 2592000  # 30 days
  
  # Two-factor authentication
  totp:
    enabled: false
    issuer: "CloudViz"
    window: 1
    backup_codes: 10
```

### Authorization Configuration

```yaml
security:
  # Role-based access control
  rbac:
    enabled: true
    default_role: "user"
    
    roles:
      admin:
        permissions:
          - "admin"
          - "extract"
          - "visualize"
          - "view"
          - "manage_users"
      
      user:
        permissions:
          - "extract"
          - "visualize"
          - "view"
      
      viewer:
        permissions:
          - "view"
  
  # API key authentication
  api_keys:
    enabled: true
    default_permissions:
      - "extract"
      - "visualize"
    rate_limits:
      requests_per_minute: 1000
```

### Data Protection

```yaml
security:
  # Encryption
  encryption:
    # Data at rest
    database_encryption: true
    file_encryption: true
    
    # Data in transit
    tls_version: "1.2"
    cipher_suites:
      - "ECDHE-RSA-AES128-GCM-SHA256"
      - "ECDHE-RSA-AES256-GCM-SHA384"
  
  # Data retention
  data_retention:
    job_results: 30  # days
    logs: 90        # days
    user_data: 365  # days
  
  # Privacy
  privacy:
    anonymize_logs: true
    data_minimization: true
    consent_required: false
```

## Performance Tuning

### Application Performance

```yaml
performance:
  # Worker configuration
  workers:
    count: 4
    max_requests: 1000
    max_requests_jitter: 50
    timeout: 300
    keep_alive: 2
  
  # Request handling
  request_queue_size: 1000
  max_concurrent_requests: 100
  
  # Background jobs
  job_queue:
    max_concurrent_jobs: 10
    job_timeout: 3600
    result_retention: 86400  # 24 hours
  
  # Memory management
  memory:
    max_memory_per_worker: "2GB"
    gc_threshold: 0.8
    cache_memory_limit: "1GB"
```

### Database Performance

```yaml
performance:
  database:
    # Connection pooling
    pool_size: 20
    max_overflow: 50
    pool_timeout: 60
    
    # Query optimization
    query_timeout: 30
    statement_timeout: 60
    slow_query_log: true
    slow_query_threshold: 1.0
    
    # Indexing
    auto_index_creation: true
    index_statistics: true
```

### Caching Performance

```yaml
performance:
  cache:
    # Memory allocation
    max_memory: "1GB"
    eviction_policy: "lru"
    
    # Connection pooling
    connection_pool_size: 20
    connection_timeout: 5
    
    # Compression
    compression_enabled: true
    compression_algorithm: "gzip"
    compression_level: 6
```

## Monitoring Configuration

### Metrics Configuration

```yaml
monitoring:
  # Prometheus metrics
  prometheus:
    enabled: true
    port: 9090
    path: "/metrics"
    
    # Custom metrics
    custom_metrics:
      - name: "extraction_duration"
        type: "histogram"
        description: "Time taken for resource extraction"
      
      - name: "active_jobs"
        type: "gauge"
        description: "Number of active jobs"
  
  # Health checks
  health_checks:
    enabled: true
    interval: 30
    timeout: 10
    
    checks:
      - name: "database"
        type: "database"
        critical: true
      
      - name: "cache"
        type: "cache"
        critical: false
      
      - name: "providers"
        type: "external"
        critical: false
```

### Alerting Configuration

```yaml
monitoring:
  alerting:
    # Alertmanager integration
    alertmanager:
      enabled: true
      url: "http://alertmanager:9093"
    
    # Alert rules
    rules:
      - name: "high_error_rate"
        condition: "error_rate > 0.05"
        severity: "warning"
        duration: "5m"
      
      - name: "database_down"
        condition: "database_health == 0"
        severity: "critical"
        duration: "1m"
  
  # Tracing
  tracing:
    enabled: true
    backend: "jaeger"
    endpoint: "http://jaeger:14268/api/traces"
    sample_rate: 0.1
```

## Deployment-Specific Configurations

### Development Configuration

```yaml
# config/dev.yml
app:
  environment: "development"

api:
  host: "127.0.0.1"
  port: 8000
  workers: 1
  reload: true
  log_level: "debug"
  cors_origins: ["*"]

database:
  url: "postgresql://cloudviz:cloudviz@localhost:5432/cloudviz_dev"
  echo: true

cache:
  backend: "memory"

logging:
  level: "DEBUG"
  json_format: false
  console: true
  file: null

visualization:
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

### Production Configuration

```yaml
# config/prod.yml
app:
  environment: "production"

api:
  host: "0.0.0.0"
  port: 8000
  workers: 8
  reload: false
  log_level: "info"
  enable_https: true
  ssl_cert_file: "/app/ssl/cert.pem"
  ssl_key_file: "/app/ssl/key.pem"

database:
  url: "${DATABASE_URL}"
  pool_size: 20
  max_overflow: 50
  echo: false

cache:
  backend: "redis"
  url: "${REDIS_URL}"
  default_ttl: 3600

logging:
  level: "INFO"
  json_format: true
  file: "/var/log/cloudviz/app.log"
  max_file_size: 104857600  # 100MB
  backup_count: 10

security:
  jwt:
    secret_key: "${CLOUDVIZ_JWT_SECRET}"
    expiration: 1800  # 30 minutes
  
monitoring:
  prometheus:
    enabled: true
  
  alerting:
    enabled: true
```

### Docker Configuration

```yaml
# docker-compose.yml environment configuration
version: '3.8'

services:
  cloudviz:
    environment:
      - CLOUDVIZ_ENV=production
      - CLOUDVIZ_CONFIG_FILE=/app/config/docker.yml
      - DATABASE_URL=postgresql://cloudviz:${DB_PASSWORD}@db:5432/cloudviz
      - REDIS_URL=redis://redis:6379/0
      - CLOUDVIZ_JWT_SECRET=${JWT_SECRET}
      - AZURE_TENANT_ID=${AZURE_TENANT_ID}
      - AZURE_CLIENT_ID=${AZURE_CLIENT_ID}
      - AZURE_CLIENT_SECRET=${AZURE_CLIENT_SECRET}
```

### Kubernetes Configuration

```yaml
# k8s-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cloudviz-config
data:
  config.yml: |
    app:
      environment: "production"
    
    api:
      host: "0.0.0.0"
      port: 8000
      workers: 4
    
    database:
      url: "postgresql://cloudviz:$(DB_PASSWORD)@postgres-service:5432/cloudviz"
    
    cache:
      url: "redis://redis-service:6379/0"
```

## Configuration Validation

### Schema Validation

CloudViz automatically validates configuration using JSON Schema:

```python
# Example validation errors
{
  "error": "Configuration validation failed",
  "details": [
    {
      "field": "api.port",
      "message": "Port must be between 1 and 65535",
      "value": 70000
    },
    {
      "field": "providers.azure.authentication_method",
      "message": "Must be one of: service_principal, managed_identity, interactive",
      "value": "invalid_method"
    }
  ]
}
```

### Configuration Testing

```bash
# Test configuration file
cloudviz config validate --config config/production.yml

# Test environment variables
cloudviz config test --env

# Generate configuration template
cloudviz config template --output config/template.yml

# Show effective configuration
cloudviz config show --merged
```

## Troubleshooting

### Common Configuration Issues

#### 1. Database Connection Issues

**Problem**: Unable to connect to database
```yaml
database:
  url: "postgresql://wrong-user:wrong-pass@localhost:5432/cloudviz"
```

**Solution**: Verify connection parameters
```bash
# Test database connection
psql "postgresql://cloudviz:password@localhost:5432/cloudviz" -c "SELECT 1;"

# Check connection in configuration
cloudviz config test --database
```

#### 2. Redis Connection Issues

**Problem**: Cache not working
```yaml
cache:
  url: "redis://wrong-host:6379/0"
```

**Solution**: Verify Redis connection
```bash
# Test Redis connection
redis-cli -h localhost -p 6379 ping

# Check cache configuration
cloudviz config test --cache
```

#### 3. Provider Authentication Issues

**Problem**: Azure authentication failing
```yaml
providers:
  azure:
    authentication_method: "service_principal"
    tenant_id: "wrong-tenant"
    client_id: "wrong-client"
    client_secret: "wrong-secret"
```

**Solution**: Verify credentials
```bash
# Test Azure authentication
az login --service-principal -u $AZURE_CLIENT_ID -p $AZURE_CLIENT_SECRET --tenant $AZURE_TENANT_ID

# Test provider configuration
cloudviz config test --provider azure
```

### Configuration Debugging

```bash
# Enable debug logging
export CLOUDVIZ_LOG_LEVEL=DEBUG

# Show effective configuration
cloudviz config show --effective

# Validate all settings
cloudviz config validate --strict

# Test specific components
cloudviz config test --component database
cloudviz config test --component cache
cloudviz config test --component providers
```

### Environment-Specific Issues

#### Development Environment
- Use `reload: true` for auto-restart
- Enable SQL echoing: `echo: true`
- Use memory cache for simplicity
- Enable CORS for frontend development

#### Production Environment
- Disable debug logging
- Use connection pooling
- Enable HTTPS
- Configure proper rate limiting
- Set up monitoring and alerting

#### Container Environment
- Use environment variables
- Mount configuration files as volumes
- Configure proper health checks
- Set resource limits

For additional configuration examples and advanced scenarios, see the [Examples Directory](../examples/configurations/) in the repository.
