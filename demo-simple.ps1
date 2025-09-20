# CloudViz API Demo Script
# Demonstrates end-to-end cloud provider analysis using CloudViz API

param(
    [string]$BaseUrl = "http://localhost:8000",
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
        Write-Host "✗ Error calling $Endpoint : $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

Write-Host "`n1. Checking API Health..." -ForegroundColor Green
$health = Invoke-CloudVizAPI -Endpoint "/health"
if ($health) {
    Write-Host "✓ API Status: $($health.status)" -ForegroundColor Green
    Write-Host "  Version: $($health.version)" -ForegroundColor White
    Write-Host "  Uptime: $([math]::Round($health.uptime_seconds, 2)) seconds" -ForegroundColor White
}

Write-Host "`n2. Getting API Information..." -ForegroundColor Green
$apiInfo = Invoke-CloudVizAPI -Endpoint "/"
if ($apiInfo) {
    Write-Host "✓ API Name: $($apiInfo.name)" -ForegroundColor Green
    Write-Host "  Description: $($apiInfo.description)" -ForegroundColor White
}

Write-Host "`n3. Getting Supported AWS Resource Types..." -ForegroundColor Green
$awsTypes = Invoke-CloudVizAPI -Endpoint "/api/v1/aws/resource-types"
if ($awsTypes) {
    Write-Host "✓ Supported AWS Resource Types:" -ForegroundColor Green
    foreach ($type in $awsTypes) {
        Write-Host "  - $type" -ForegroundColor White
    }
}

Write-Host "`n4. API Documentation Available At:" -ForegroundColor Green
Write-Host "  Interactive Docs: $BaseUrl/docs" -ForegroundColor Cyan
Write-Host "  ReDoc: $BaseUrl/redoc" -ForegroundColor Cyan
Write-Host "  OpenAPI Schema: $BaseUrl/openapi.json" -ForegroundColor Cyan

Write-Host "`n5. Example Usage for Cloud Analysis:" -ForegroundColor Green
Write-Host "A. Extract AWS Resources:" -ForegroundColor Yellow
Write-Host "   POST $BaseUrl/api/v1/aws/extract" -ForegroundColor Gray
Write-Host "   Body: { regions: ['us-east-1'], resource_types: ['ec2_instance'] }" -ForegroundColor Gray

Write-Host "`nB. Get Account Info:" -ForegroundColor Yellow  
Write-Host "   GET $BaseUrl/api/v1/aws/account-info" -ForegroundColor Gray

Write-Host "`nC. Get AWS Regions:" -ForegroundColor Yellow
Write-Host "   GET $BaseUrl/api/v1/aws/regions" -ForegroundColor Gray

Write-Host "`n=== End-to-End Ready ===" -ForegroundColor Cyan
Write-Host "CloudViz API is operational for cloud infrastructure analysis!" -ForegroundColor Green
