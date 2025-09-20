Write-Host "=== CloudViz API Demo ===" -ForegroundColor Cyan

# Test API Health
Write-Host "`n1. Testing API Health..." -ForegroundColor Green
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
    Write-Host "✓ API Status: $($health.status)" -ForegroundColor Green
    Write-Host "  Version: $($health.version)" -ForegroundColor White
    Write-Host "  Uptime: $([math]::Round($health.uptime_seconds, 2)) seconds" -ForegroundColor White
} catch {
    Write-Host "✗ API Health check failed" -ForegroundColor Red
}

# Test API Info
Write-Host "`n2. Getting API Information..." -ForegroundColor Green
try {
    $apiInfo = Invoke-RestMethod -Uri "http://localhost:8000/" -Method GET
    Write-Host "✓ API Name: $($apiInfo.name)" -ForegroundColor Green
    Write-Host "  Description: $($apiInfo.description)" -ForegroundColor White
} catch {
    Write-Host "✗ API Info failed" -ForegroundColor Red
}

# Test AWS Resource Types
Write-Host "`n3. Getting AWS Resource Types..." -ForegroundColor Green
try {
    $awsTypes = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/aws/resource-types" -Method GET
    Write-Host "✓ Supported AWS Resource Types:" -ForegroundColor Green
    foreach ($type in $awsTypes) {
        Write-Host "  - $type" -ForegroundColor White
    }
} catch {
    Write-Host "✗ AWS Resource Types failed" -ForegroundColor Red
}

# Show Documentation URLs
Write-Host "`n4. API Documentation:" -ForegroundColor Green
Write-Host "  Interactive Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  ReDoc: http://localhost:8000/redoc" -ForegroundColor Cyan

Write-Host "`n=== CloudViz API is Ready for Cloud Analysis! ===" -ForegroundColor Cyan
