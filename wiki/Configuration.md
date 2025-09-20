# Configuration

CloudViz supports multiple configuration methods to suit different deployment scenarios and environments. This guide covers all configuration options, from environment variables to YAML files.

## 🔧 Configuration Methods

CloudViz supports configuration through multiple methods, in order of precedence:

1. **Command Line Arguments** (highest priority)
2. **Environment Variables**
3. **YAML Configuration Files**
4. **Default Values** (lowest priority)

## 📁 Configuration Files

### Configuration Directory Structure

```
config/
├── default.yml          # Default configuration
├── development.yml      # Development environment
├── staging.yml         # Staging environment
├── production.yml      # Production environment
├── local.yml           # Local overrides (git-ignored)
└── secrets/
    ├── azure.yml       # Azure credentials
    ├── aws.yml         # AWS credentials
    └── gcp.yml         # GCP credentials
```

### Environment-Specific Configuration

CloudViz automatically loads configuration based on the `CLOUDVIZ_ENV` environment variable:

```bash
export CLOUDVIZ_ENV=production  # Loads config/production.yml
export CLOUDVIZ_ENV=staging     # Loads config/staging.yml
export CLOUDVIZ_ENV=development # Loads config/development.yml
```

### Default Configuration (`config/default.yml`)

```yaml
# API Server Configuration
api:
  host: "0.0.0.0"
  port: 8000
  workers: 1
  reload: false
  debug: false
  log_level: "INFO"
  
# Database Configuration
database:
  url: "sqlite:///data/cloudviz.db"
  pool_size: 5
  max_overflow: 10
  pool_timeout: 30
  echo: false

# Cache Configuration
cache:
  backend: "redis"
  redis_url: "redis://localhost:6379/0"
  default_ttl: 3600
  key_prefix: "cloudviz:"

# Security Configuration
security:
  jwt:
    secret_key: "your-secret-key-here"
    algorithm: "HS256"
    expiration: 3600
  
  cors:
    allow_origins: ["*"]
    allow_methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers: ["*"]
    allow_credentials: true

# Cloud Provider Configuration
cloud_providers:
  azure:
    enabled: false
    timeout: 300
    retry_attempts: 3
    
  aws:
    enabled: false
    timeout: 300
    retry_attempts: 3
    
  gcp:
    enabled: false
    timeout: 300
    retry_attempts: 3

# Visualization Configuration
visualization:
  default_theme: "enterprise"
  default_layout: "hierarchical"
  default_format: "mermaid"
  include_costs: true
  include_dependencies: true
  
  themes:
    enterprise:
      colors:
        compute: "#9b59b6"
        network: "#3498db"
        storage: "#e67e22"
        security: "#e74c3c"
        management: "#27ae60"

# Background Jobs Configuration
jobs:
  backend: "redis"
  broker_url: "redis://localhost:6379/1"
  result_backend: "redis://localhost:6379/1"
  task_serializer: "json"
  accept_content: ["json"]
  timezone: "UTC"

# Logging Configuration
logging:
  level: "INFO"
  format: "standard"
  file: null
  max_size: "100MB"
  backup_count: 5
  
# Rate Limiting Configuration
rate_limiting:
  enabled: true
  discovery: "10/minute"
  diagrams: "20/minute"
  api: "100/minute"
```

### Production Configuration (`config/production.yml`)

```yaml
# Production-specific overrides
api:
  workers: 4
  debug: false
  log_level: "INFO"

database:
  url: "${DATABASE_URL}"
  pool_size: 20
  max_overflow: 30
  pool_timeout: 30

security:
  jwt:
    secret_key: "${JWT_SECRET_KEY}"
  
  cors:
    allow_origins:
      - "https://your-domain.com"
      - "https://app.your-domain.com"
    allow_credentials: false

cloud_providers:
  azure:
    enabled: true
    client_id: "${AZURE_CLIENT_ID}"
    client_secret: "${AZURE_CLIENT_SECRET}"
    tenant_id: "${AZURE_TENANT_ID}"
    subscription_ids:
      - "${AZURE_SUBSCRIPTION_ID}"
    
    # Advanced Azure configuration
    regions:
      - "australiaeast"
      - "australiasoutheast"
    
    resource_groups:
      - "production"
      - "staging"
    
    discovery:
      parallel_regions: true
      batch_size: 100
      include_costs: true
      include_dependencies: true
      timeout: 300

logging:
  level: "INFO"
  format: "json"
  file: "/app/logs/cloudviz.log"

rate_limiting:
  discovery: "5/minute"
  diagrams: "10/minute"
  api: "50/minute"
```

### Development Configuration (`config/development.yml`)

```yaml
# Development-specific settings
api:
  reload: true
  debug: true
  log_level: "DEBUG"

database:
  url: "sqlite:///data/cloudviz_dev.db"
  echo: true

security:
  cors:
    allow_origins: ["*"]
    allow_credentials: true

cloud_providers:
  azure:
    enabled: true
    # Use environment variables for credentials
    timeout: 60  # Shorter timeout for development

logging:
  level: "DEBUG"
  format: "standard"

rate_limiting:
  enabled: false  # Disable for development
```

## 🌍 Environment Variables

### Core Environment Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `CLOUDVIZ_ENV` | Environment name | `development` | `production` |
| `API_HOST` | API server host | `0.0.0.0` | `0.0.0.0` |
| `API_PORT` | API server port | `8000` | `8000` |
| `DEBUG` | Enable debug mode | `false` | `true` |
| `LOG_LEVEL` | Logging level | `INFO` | `DEBUG` |

### Database Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection URL | `postgresql://user:pass@host:5432/db` |
| `DB_POOL_SIZE` | Connection pool size | `20` |
| `DB_MAX_OVERFLOW` | Max pool overflow | `30` |

### Cache Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `CACHE_TTL` | Default cache TTL | `3600` |
| `CACHE_KEY_PREFIX` | Cache key prefix | `cloudviz:` |

### Security Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `JWT_SECRET_KEY` | JWT signing key | `your-super-secret-key` |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `JWT_EXPIRATION` | JWT expiration (seconds) | `3600` |
| `ENCRYPTION_KEY` | Data encryption key | `32-char-encryption-key` |

### Azure Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `AZURE_CLIENT_ID` | Service principal client ID | `12345678-1234-...` |
| `AZURE_CLIENT_SECRET` | Service principal secret | `your-secret-value` |
| `AZURE_TENANT_ID` | Azure tenant ID | `87654321-4321-...` |
| `AZURE_SUBSCRIPTION_ID` | Default subscription ID | `subscription-id` |
| `AZURE_USE_CLI` | Use Azure CLI auth | `true` |
| `AZURE_USE_MANAGED_IDENTITY` | Use managed identity | `true` |

### AWS Environment Variables (Planned)

| Variable | Description | Example |
|----------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | AWS access key | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | `wJalrXUtnFEMI/K7MDENG/...` |
| `AWS_DEFAULT_REGION` | Default AWS region | `ap-southeast-2` |
| `AWS_PROFILE` | AWS CLI profile | `cloudviz` |

### GCP Environment Variables (Planned)

| Variable | Description | Example |
|----------|-------------|---------|
| `GOOGLE_APPLICATION_CREDENTIALS` | Service account file path | `/app/config/gcp-sa.json` |
| `GCP_PROJECT_ID` | Default GCP project | `my-gcp-project` |
| `GOOGLE_CLOUD_PROJECT` | Alternative project variable | `my-gcp-project` |

## 📄 YAML Configuration Reference

### Complete Configuration Example

```yaml
# Complete configuration example
app:
  name: "CloudViz"
  version: "1.0.0"
  description: "Multi-cloud infrastructure visualization"

api:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  reload: false
  debug: false
  log_level: "INFO"
  
  # Request/Response configuration
  request_timeout: 60
  max_request_size: "10MB"
  
  # CORS configuration
  cors:
    allow_origins:
      - "https://your-domain.com"
      - "https://app.your-domain.com"
    allow_methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers: ["Authorization", "Content-Type"]
    allow_credentials: false

database:
  url: "${DATABASE_URL}"
  pool_size: 20
  max_overflow: 30
  pool_timeout: 30
  pool_recycle: 3600
  echo: false
  
  # Migration settings
  migrations:
    auto_upgrade: false
    backup_before_upgrade: true

cache:
  backend: "redis"
  redis_url: "${REDIS_URL}"
  default_ttl: 3600
  max_connections: 50
  key_prefix: "cloudviz:"
  
  # Cache strategy configuration
  strategies:
    resources: 3600      # 1 hour
    diagrams: 7200       # 2 hours
    auth: 86400          # 24 hours
    rate_limit: 60       # 1 minute

security:
  jwt:
    secret_key: "${JWT_SECRET_KEY}"
    algorithm: "HS256"
    expiration: 3600
    
  # Rate limiting
  rate_limiting:
    enabled: true
    storage: "redis"
    storage_url: "${REDIS_URL}"
    
    limits:
      discovery: "10/minute"
      diagrams: "20/minute"
      api: "100/minute"
      auth: "5/minute"
  
  # Encryption for stored credentials
  encryption:
    key: "${ENCRYPTION_KEY}"
    algorithm: "AES-256-GCM"

cloud_providers:
  azure:
    enabled: true
    
    # Authentication
    client_id: "${AZURE_CLIENT_ID}"
    client_secret: "${AZURE_CLIENT_SECRET}"
    tenant_id: "${AZURE_TENANT_ID}"
    
    # Alternative authentication methods
    use_cli: false
    use_managed_identity: false
    
    # Scope configuration
    subscription_ids:
      - "${AZURE_SUBSCRIPTION_ID}"
    
    regions:
      - "australiaeast"
      - "australiasoutheast"
      - "eastus"
      - "westeurope"
    
    resource_groups:
      - "production"
      - "staging"
      - "development"
    
    # Resource type filtering
    resource_types:
      - "Microsoft.Compute/virtualMachines"
      - "Microsoft.Network/virtualNetworks"
      - "Microsoft.Storage/storageAccounts"
      - "Microsoft.Sql/servers"
      - "Microsoft.Web/sites"
    
    # Discovery configuration
    discovery:
      parallel_regions: true
      batch_size: 100
      include_costs: true
      include_dependencies: true
      include_security_analysis: true
      timeout: 300
      retry_attempts: 3
      retry_delay: 5
    
    # Cost analysis
    cost_analysis:
      enabled: true
      currency: "USD"
      billing_period: "monthly"
      include_estimates: true
      cost_threshold_alerts: true
      thresholds:
        warning: 1000
        critical: 5000

  aws:
    enabled: false
    
    # Authentication (planned)
    access_key_id: "${AWS_ACCESS_KEY_ID}"
    secret_access_key: "${AWS_SECRET_ACCESS_KEY}"
    region: "ap-southeast-2"
    
    # Multi-account support
    accounts:
      - account_id: "123456789012"
        role_arn: "arn:aws:iam::123456789012:role/CloudVizRole"
        regions: ["ap-southeast-2", "us-east-1"]
    
    discovery:
      parallel_regions: true
      include_costs: true

  gcp:
    enabled: false
    
    # Authentication (planned)
    service_account_path: "${GOOGLE_APPLICATION_CREDENTIALS}"
    project_id: "${GCP_PROJECT_ID}"
    
    # Multi-project support
    projects:
      - project_id: "production-project"
        regions: ["australia-southeast1", "us-central1"]
      - project_id: "staging-project"
        regions: ["australia-southeast1"]
    
    discovery:
      include_costs: true
      include_iam: true

visualization:
  default_theme: "enterprise"
  default_layout: "hierarchical"
  default_format: "mermaid"
  include_costs: true
  include_dependencies: true
  
  # Theme definitions
  themes:
    enterprise:
      name: "Enterprise"
      description: "Professional corporate theme"
      colors:
        compute: "#9b59b6"
        network: "#3498db"
        storage: "#e67e22"
        security: "#e74c3c"
        management: "#27ae60"
        database: "#8e44ad"
      styles:
        node_shape: "rounded"
        edge_style: "solid"
        font_family: "Arial, sans-serif"
        font_size: "12px"
    
    security:
      name: "Security Focus"
      description: "Security-oriented visualization"
      colors:
        secure: "#27ae60"
        warning: "#f39c12"
        critical: "#e74c3c"
        unknown: "#95a5a6"
    
    cost:
      name: "Cost Analysis"
      description: "Cost-focused visualization"
      colors:
        low: "#27ae60"
        medium: "#f1c40f"
        high: "#e67e22"
        very_high: "#e74c3c"
  
  # Layout configurations
  layouts:
    hierarchical:
      direction: "TD"
      spacing: 50
      grouping:
        by_provider: true
        by_region: true
        by_resource_group: true
        by_tier: true
    
    network:
      direction: "LR"
      show_subnets: true
      show_connections: true
      emphasize_security: true
    
    flat:
      direction: "TD"
      group_similar: true
      show_all_dependencies: false
  
  # Export settings
  export:
    default_width: 1920
    default_height: 1080
    default_background: "white"
    max_file_size: "50MB"
    supported_formats: ["png", "svg", "pdf", "mermaid"]

jobs:
  backend: "redis"
  broker_url: "${REDIS_URL}/1"
  result_backend: "${REDIS_URL}/1"
  task_serializer: "json"
  accept_content: ["json"]
  result_serializer: "json"
  timezone: "UTC"
  enable_utc: true
  
  # Worker configuration
  worker:
    concurrency: 4
    prefetch_multiplier: 1
    max_tasks_per_child: 1000
    task_time_limit: 3600
    task_soft_time_limit: 3000
  
  # Task routing
  routes:
    "cloudviz.tasks.discovery.*": "discovery"
    "cloudviz.tasks.diagram.*": "diagram"
    "cloudviz.tasks.export.*": "export"

webhooks:
  enabled: true
  timeout: 30
  retry_attempts: 3
  retry_delay: 5
  
  # Webhook security
  require_signature: true
  signature_header: "X-CloudViz-Signature"
  signature_algorithm: "sha256"

logging:
  level: "INFO"
  format: "json"
  file: "/app/logs/cloudviz.log"
  max_size: "100MB"
  backup_count: 5
  
  # Log rotation
  rotation:
    when: "midnight"
    interval: 1
    
  # Structured logging
  structured: true
  correlation_id: true
  
  # Logger configuration
  loggers:
    cloudviz:
      level: "INFO"
    uvicorn:
      level: "INFO"
    sqlalchemy:
      level: "WARNING"

monitoring:
  enabled: true
  
  # Metrics collection
  metrics:
    enabled: true
    endpoint: "/api/v1/system/metrics"
    
  # Health checks
  health_checks:
    interval: 30
    timeout: 10
    
  # Alerting (if integrated with external systems)
  alerts:
    enabled: false
    webhook_url: null
    
    thresholds:
      api_response_time: 1000  # milliseconds
      error_rate: 0.05         # 5%
      memory_usage: 0.85       # 85%
      cpu_usage: 0.80          # 80%

feature_flags:
  # Enable/disable features
  multi_cloud_discovery: true
  cost_analysis: true
  security_analysis: true
  background_jobs: true
  webhooks: true
  rate_limiting: true
  
  # Experimental features
  experimental:
    ai_recommendations: false
    real_time_updates: false
    advanced_analytics: false
```

## 🔒 Secrets Management

### Environment-based Secrets

For production deployments, use environment variables for sensitive data:

```bash
# .env file (DO NOT commit to version control)
AZURE_CLIENT_ID=12345678-1234-1234-1234-123456789012
AZURE_CLIENT_SECRET=your-very-secret-value
AZURE_TENANT_ID=87654321-4321-4321-4321-210987654321
JWT_SECRET_KEY=your-super-secret-jwt-signing-key-at-least-32-chars
ENCRYPTION_KEY=your-32-char-encryption-key-here
DATABASE_URL=postgresql://cloudviz:password@localhost:5432/cloudviz
```

### External Secrets Management

#### Azure Key Vault Integration

```yaml
# config/production.yml
secrets:
  backend: "azure_key_vault"
  azure_key_vault:
    vault_url: "https://your-vault.vault.azure.net/"
    
    # Credential mappings
    mappings:
      AZURE_CLIENT_SECRET: "azure-client-secret"
      JWT_SECRET_KEY: "jwt-secret-key"
      DATABASE_PASSWORD: "database-password"
```

#### AWS Secrets Manager Integration

```yaml
# config/production.yml (planned)
secrets:
  backend: "aws_secrets_manager"
  aws_secrets_manager:
    region: "ap-southeast-2"
    
    mappings:
      AZURE_CLIENT_SECRET: "cloudviz/azure/client-secret"
      JWT_SECRET_KEY: "cloudviz/jwt/secret-key"
```

#### HashiCorp Vault Integration

```yaml
# config/production.yml (planned)
secrets:
  backend: "hashicorp_vault"
  vault:
    url: "https://vault.your-company.com"
    token: "${VAULT_TOKEN}"
    mount_point: "cloudviz"
    
    mappings:
      AZURE_CLIENT_SECRET: "azure/client-secret"
      JWT_SECRET_KEY: "jwt/secret-key"
```

### Kubernetes Secrets

```yaml
# kubernetes-secret.yaml
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
  JWT_SECRET_KEY: "your-jwt-secret"
  DATABASE_URL: "postgresql://user:pass@host:5432/db"
```

## 🎯 Configuration Validation

### Validation Rules

CloudViz validates configuration on startup:

```python
# Configuration validation
from pydantic import BaseModel, validator
from typing import Optional

class CloudVizConfig(BaseModel):
    # API configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    @validator('api_port')
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError('Port must be between 1 and 65535')
        return v
    
    # JWT configuration
    jwt_secret_key: str
    
    @validator('jwt_secret_key')
    def validate_jwt_secret(cls, v):
        if len(v) < 32:
            raise ValueError('JWT secret key must be at least 32 characters')
        return v
    
    # Azure configuration
    azure_enabled: bool = False
    azure_client_id: Optional[str] = None
    azure_client_secret: Optional[str] = None
    azure_tenant_id: Optional[str] = None
    
    @validator('azure_client_secret')
    def validate_azure_secret(cls, v, values):
        if values.get('azure_enabled') and not v:
            raise ValueError('Azure client secret required when Azure is enabled')
        return v
```

### Configuration Testing

```bash
# Test configuration
python -m cloudviz.cli config validate

# Test with specific environment
CLOUDVIZ_ENV=production python -m cloudviz.cli config validate

# Show current configuration
python -m cloudviz.cli config show

# Show configuration differences
python -m cloudviz.cli config diff production staging
```

## 🔄 Dynamic Configuration

### Runtime Configuration Updates

Some configuration can be updated at runtime through the API:

```bash
# Update visualization settings
curl -X PUT "http://localhost:8000/api/v1/config/visualization" \
     -H "Content-Type: application/json" \
     -d '{
       "default_theme": "security",
       "include_costs": false
     }'

# Update rate limiting
curl -X PUT "http://localhost:8000/api/v1/config/rate_limiting" \
     -H "Content-Type: application/json" \
     -d '{
       "discovery": "5/minute",
       "diagrams": "15/minute"
     }'

# Update cloud provider settings
curl -X PUT "http://localhost:8000/api/v1/config/providers/azure" \
     -H "Content-Type: application/json" \
     -d '{
       "discovery": {
         "batch_size": 50,
         "parallel_regions": false
       }
     }'
```

### Configuration Reloading

```bash
# Reload configuration (graceful restart)
curl -X POST "http://localhost:8000/api/v1/system/reload-config"

# Or send SIGHUP signal
kill -HUP $(pgrep -f cloudviz)
```

## 🔧 Configuration Best Practices

### 1. Environment Separation

```yaml
# Use different configurations for each environment
config/
├── development.yml    # Local development
├── testing.yml       # CI/CD testing
├── staging.yml       # Pre-production
└── production.yml    # Production
```

### 2. Secret Management

```bash
# Never commit secrets to version control
echo "config/secrets/" >> .gitignore
echo ".env" >> .gitignore

# Use environment variables for production
export AZURE_CLIENT_SECRET="$(cat /run/secrets/azure_secret)"
```

### 3. Configuration Validation

```yaml
# Include validation in CI/CD pipeline
stages:
  - name: validate-config
    script:
      - python -m cloudviz.cli config validate
```

### 4. Documentation

```yaml
# Document configuration options
cloud_providers:
  azure:
    # Enable Azure resource discovery
    enabled: true
    
    # Azure service principal credentials
    # See: https://docs.microsoft.com/en-us/azure/active-directory/develop/app-objects-and-service-principals
    client_id: "${AZURE_CLIENT_ID}"
    client_secret: "${AZURE_CLIENT_SECRET}"
    tenant_id: "${AZURE_TENANT_ID}"
```

### 5. Configuration Templates

```bash
# Provide configuration templates
cp config/production.yml.template config/production.yml
# Edit config/production.yml with your values
```

## 📊 Configuration Monitoring

### Configuration Drift Detection

```python
# Monitor configuration changes
import hashlib
import yaml

def config_checksum(config_path):
    with open(config_path, 'r') as f:
        content = yaml.safe_load(f)
    return hashlib.sha256(str(content).encode()).hexdigest()

# Alert on configuration changes
current_checksum = config_checksum('config/production.yml')
if current_checksum != expected_checksum:
    send_alert("Configuration drift detected")
```

### Configuration Backup

```bash
#!/bin/bash
# backup-config.sh
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf "/backups/config_backup_$DATE.tar.gz" config/
```

---

For more configuration examples and environment-specific setups, see our **[Deployment](Deployment)** guide or check the **[Examples](Examples)** page for real-world configuration scenarios.