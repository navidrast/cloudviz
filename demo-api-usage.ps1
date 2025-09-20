# CloudViz API Demo Script
# Demonstrates end-to-end cloud provider analysis using CloudViz API

param(
    [string]$BaseUrl = "http://localhost:8000",
    [switch]$SkipAuth,
    [string]$AWSProfile = "default"
)

Write-Host "=== CloudViz API Demo ===" -ForegroundColor Cyan
Write-Host "Base URL: $BaseUrl" -ForegroundColor Yellow

# Function to make API calls with error handling
function Invoke-CloudVizAPI {
    param(
        [string]$Endpoint,
        [string]$Method = "GET",
        [hashtable]$Headers = @{},
        [object]$Body = $null
    )
    
    try {
        $uri = "$BaseUrl$Endpoint"
        $params = @{
            Uri = $uri
            Method = $Method
            Headers = $Headers
        }
        
        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json)
            $params.ContentType = "application/json"
        }
        
        Write-Host "→ $Method $Endpoint" -ForegroundColor Gray
        $response = Invoke-RestMethod @params
        return $response
    }
    catch {
        Write-Host "✗ Error calling $Endpoint`: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# 1. Check API Health
Write-Host "`n1. Checking API Health..." -ForegroundColor Green
$health = Invoke-CloudVizAPI -Endpoint "/health"
if ($health) {
    Write-Host "✓ API Status: $($health.status)" -ForegroundColor Green
    Write-Host "  Version: $($health.version)" -ForegroundColor White
    Write-Host "  Uptime: $([math]::Round($health.uptime_seconds, 2)) seconds" -ForegroundColor White
    Write-Host "  Checks: $($health.checks | ConvertTo-Json -Compress)" -ForegroundColor White
}

# 2. Get API Information
Write-Host "`n2. Getting API Information..." -ForegroundColor Green
$apiInfo = Invoke-CloudVizAPI -Endpoint "/"
if ($apiInfo) {
    Write-Host "✓ API Name: $($apiInfo.name)" -ForegroundColor Green
    Write-Host "  Description: $($apiInfo.description)" -ForegroundColor White
    Write-Host "  Documentation: $BaseUrl$($apiInfo.docs_url)" -ForegroundColor White
}

# 3. Get Supported AWS Resource Types
Write-Host "`n3. Getting Supported AWS Resource Types..." -ForegroundColor Green
$awsTypes = Invoke-CloudVizAPI -Endpoint "/api/v1/aws/resource-types"
if ($awsTypes) {
    Write-Host "✓ Supported AWS Resource Types:" -ForegroundColor Green
    foreach ($type in $awsTypes) {
        Write-Host "  - $type" -ForegroundColor White
    }
}
}

# 4. Test AWS Account Information (if credentials available)
Write-Host "`n4. Testing AWS Account Access..." -ForegroundColor Green
Write-Host "Note: This requires AWS credentials to be configured" -ForegroundColor Yellow

# Check if AWS CLI is available and configured
try {
    $awsIdentity = aws sts get-caller-identity 2>$null | ConvertFrom-Json
    if ($awsIdentity) {
        Write-Host "✓ AWS Credentials Found:" -ForegroundColor Green
        Write-Host "  Account: $($awsIdentity.Account)" -ForegroundColor White
        Write-Host "  User: $($awsIdentity.Arn)" -ForegroundColor White
        
        # Try to get account info through API
        $accountInfo = Invoke-CloudVizAPI -Endpoint "/api/v1/aws/account-info?profile_name=$AWSProfile"
        if ($accountInfo) {
            Write-Host "✓ AWS Account Info Retrieved:" -ForegroundColor Green
            Write-Host "  Account ID: $($accountInfo.account_id)" -ForegroundColor White
            Write-Host "  Total Regions: $($accountInfo.total_regions)" -ForegroundColor White
        }
    }
}
catch {
    Write-Host "⚠ AWS CLI not available or not configured" -ForegroundColor Yellow
    Write-Host "  To test AWS functionality, run: aws configure" -ForegroundColor Gray
}

# 5. Get GCP Resource Types (if available)
Write-Host "`n5. Getting Supported GCP Resource Types..." -ForegroundColor Green
$gcpTypes = Invoke-CloudVizAPI -Endpoint "/api/v1/gcp/resource-types"
if ($gcpTypes) {
    Write-Host "✓ Supported GCP Resource Types:" -ForegroundColor Green
    foreach ($type in $gcpTypes) {
        Write-Host "  - $type" -ForegroundColor White
    }
} else {
    Write-Host "⚠ GCP endpoints may not be fully implemented" -ForegroundColor Yellow
}

# 6. Demonstrate Extraction Job (simulation)
Write-Host "`n6. Demonstrating Resource Extraction..." -ForegroundColor Green
Write-Host "Note: This would require valid cloud credentials for real extraction" -ForegroundColor Yellow

$extractionRequest = @{
    account_id = "123456789012"
    regions = @("us-east-1", "us-west-2")
    resource_types = @("ec2_instance", "s3_bucket", "vpc")
    include_global_resources = $true
}

Write-Host "Sample Extraction Request:" -ForegroundColor White
Write-Host ($extractionRequest | ConvertTo-Json -Depth 3) -ForegroundColor Gray

# 7. API Documentation
Write-Host "`n7. API Documentation Available At:" -ForegroundColor Green
Write-Host "  Interactive Docs: $BaseUrl/docs" -ForegroundColor Cyan
Write-Host "  ReDoc: $BaseUrl/redoc" -ForegroundColor Cyan
Write-Host "  OpenAPI Schema: $BaseUrl/openapi.json" -ForegroundColor Cyan

# 8. Usage Examples
Write-Host "`n8. Common Usage Patterns:" -ForegroundColor Green

Write-Host "`nA. Extract all AWS resources:" -ForegroundColor Yellow
Write-Host @"
POST $BaseUrl/api/v1/aws/extract
{
  "regions": ["us-east-1", "us-west-2"],
  "include_global_resources": true,
  "profile_name": "default"
}
"@ -ForegroundColor Gray

Write-Host "`nB. Get specific resource types:" -ForegroundColor Yellow
Write-Host @"
POST $BaseUrl/api/v1/aws/extract
{
  "regions": ["us-east-1"],
  "resource_types": ["ec2_instance", "rds_instance"],
  "tags_filter": {"Environment": "Production"}
}
"@ -ForegroundColor Gray

Write-Host "`nC. Check extraction job status:" -ForegroundColor Yellow
Write-Host "GET $BaseUrl/api/v1/jobs/{job_id}/status" -ForegroundColor Gray

# 9. Next Steps
Write-Host "`n9. Next Steps for End-to-End Usage:" -ForegroundColor Green
Write-Host "  1. Configure cloud provider credentials (AWS CLI, GCP SDK, Azure CLI)" -ForegroundColor White
Write-Host "  2. Set up environment variables in .env file" -ForegroundColor White
Write-Host "  3. Use POST /api/v1/aws/extract to start resource discovery" -ForegroundColor White
Write-Host "  4. Monitor job progress with job status endpoints" -ForegroundColor White
Write-Host "  5. Retrieve and visualize extracted infrastructure data" -ForegroundColor White

Write-Host "`n=== Demo Complete ===" -ForegroundColor Cyan
Write-Host "CloudViz API is ready for cloud infrastructure analysis!" -ForegroundColor Green
