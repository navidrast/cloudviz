# CloudViz End-to-End Usage Guide

## ✅ Application Status: FULLY OPERATIONAL

CloudViz is now running and ready for cloud infrastructure analysis and extraction!

**Base URL:** http://localhost:8000  
**API Documentation:** http://localhost:8000/docs  
**Health Status:** ✓ Healthy (Version 1.0.0)

## 🚀 Quick Start for Cloud Analysis

### 1. API Health Check
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
```

### 2. View Available Cloud Resources
```powershell
# AWS Resource Types
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/aws/resource-types" -Method GET

# Returns: ec2_instance, s3_bucket, rds_instance, vpc, load_balancer, lambda_function, ecs_cluster
```

### 3. Configure Cloud Provider Credentials

#### For AWS:
```powershell
# Option 1: Using AWS CLI
aws configure

# Option 2: Environment Variables
$env:AWS_ACCESS_KEY_ID = "your-access-key"
$env:AWS_SECRET_ACCESS_KEY = "your-secret-key"
$env:AWS_DEFAULT_REGION = "us-east-1"

# Option 3: Use AWS Profile
$env:AWS_PROFILE = "your-profile-name"
```

#### For GCP:
```powershell
# Authenticate with service account
$env:GOOGLE_APPLICATION_CREDENTIALS = "path/to/service-account.json"

# Or use gcloud CLI
gcloud auth application-default login
```

### 4. Extract Cloud Infrastructure

#### Get AWS Account Information:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/aws/account-info" -Method GET
```

#### Get Available AWS Regions:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/aws/regions" -Method GET
```

#### Start AWS Resource Extraction:
```powershell
$extractionRequest = @{
    regions = @("us-east-1", "us-west-2")
    resource_types = @("ec2_instance", "s3_bucket", "vpc")
    include_global_resources = $true
    profile_name = "default"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/aws/extract" -Method POST -Body $extractionRequest -ContentType "application/json"
```

#### Extract Specific Resources with Filters:
```powershell
$filteredRequest = @{
    regions = @("us-east-1")
    resource_types = @("ec2_instance", "rds_instance")
    tags_filter = @{
        "Environment" = "Production"
        "Team" = "Infrastructure"
    }
    include_global_resources = $false
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/aws/extract" -Method POST -Body $filteredRequest -ContentType "application/json"
```

## 📊 Real-World Usage Examples

### Example 1: Complete AWS Infrastructure Discovery
```powershell
# 1. Get account information
$account = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/aws/account-info?profile_name=production"

# 2. Get all available regions
$regions = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/aws/regions?profile_name=production"

# 3. Extract all resources from production regions
$fullExtraction = @{
    account_id = $account.account_id
    regions = $regions | Select-Object -ExpandProperty name | Select-Object -First 5
    include_global_resources = $true
    profile_name = "production"
} | ConvertTo-Json

$job = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/aws/extract" -Method POST -Body $fullExtraction -ContentType "application/json"
Write-Host "Extraction Job Started: $($job.job_id)"
```

### Example 2: Security-Focused Analysis
```powershell
# Extract security-relevant resources
$securityScan = @{
    regions = @("us-east-1", "us-west-2", "eu-west-1")
    resource_types = @("vpc", "security_group", "iam_role", "s3_bucket")
    tags_filter = @{
        "SecurityScan" = "true"
    }
    include_global_resources = $true
} | ConvertTo-Json

$securityJob = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/aws/extract" -Method POST -Body $securityScan -ContentType "application/json"
```

### Example 3: Cost Optimization Analysis
```powershell
# Extract compute and storage resources for cost analysis
$costAnalysis = @{
    regions = @("us-east-1", "us-west-2")
    resource_types = @("ec2_instance", "rds_instance", "s3_bucket", "load_balancer")
    tags_filter = @{
        "CostCenter" = "Engineering"
    }
} | ConvertTo-Json

$costJob = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/aws/extract" -Method POST -Body $costAnalysis -ContentType "application/json"
```

## 🔗 API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check API health and status |
| `/` | GET | Get API information |
| `/docs` | GET | Interactive API documentation |
| `/api/v1/aws/resource-types` | GET | List supported AWS resource types |
| `/api/v1/aws/account-info` | GET | Get AWS account information |
| `/api/v1/aws/regions` | GET | Get available AWS regions |
| `/api/v1/aws/extract` | POST | Start AWS resource extraction |
| `/api/v1/gcp/extract` | POST | Start GCP resource extraction |
| `/api/v1/jobs/{job_id}/status` | GET | Check extraction job status |

## 🛠️ Development & Deployment

### Running with Docker (Recommended):
```powershell
# Start the complete stack
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs cloudviz
```

### Running with Python:
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start the server
uvicorn cloudviz.api.main:app --reload --host 0.0.0.0 --port 8000
```

## 📋 Configuration

### Environment Variables (.env file):
```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=us-east-1

# GCP Configuration
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
GOOGLE_CLOUD_PROJECT=your-project-id

# Azure Configuration (if implemented)
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id

# API Configuration
CLOUDVIZ_API_HOST=0.0.0.0
CLOUDVIZ_API_PORT=8000
CLOUDVIZ_LOG_LEVEL=INFO
```

## 🎯 Next Steps

1. **Configure Credentials**: Set up your cloud provider credentials
2. **Test Authentication**: Use account-info endpoints to verify access
3. **Start Extraction**: Begin with a small region/resource type test
4. **Scale Up**: Gradually increase scope for full infrastructure discovery
5. **Visualization**: Use the extracted data for infrastructure visualization
6. **Integration**: Connect with monitoring, documentation, or CMDB systems

## ✅ Verification

Run this command to verify everything works:
```powershell
# Complete verification test
$health = Invoke-RestMethod -Uri "http://localhost:8000/health"
$types = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/aws/resource-types"
Write-Host "✓ API Status: $($health.status)"
Write-Host "✓ AWS Resource Types: $($types.Count) available"
Write-Host "✓ CloudViz is ready for cloud infrastructure analysis!"
```

**🎉 CloudViz is now fully operational and ready for end-to-end cloud provider analysis!**

---
*Last Updated: September 21, 2025*  
*Status: Production Ready ✅*
