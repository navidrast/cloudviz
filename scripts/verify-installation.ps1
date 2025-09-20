# CloudViz Quick Start Verification Script
param(
    [string]$Method = "python",
    [switch]$TestOnly
)

# Simple verification script for CloudViz installation

function Write-Status {
    param([string]$Message, [string]$Status = "INFO")
    switch ($Status) {
        "SUCCESS" { Write-Host "[OK] $Message" -ForegroundColor Green }
        "ERROR" { Write-Host "[ERROR] $Message" -ForegroundColor Red }
        "WARNING" { Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
        default { Write-Host "[INFO] $Message" -ForegroundColor Blue }
    }
}

function Test-DockerAPI {
    Write-Status "Testing Docker API endpoints..."
    
    $allTests = $true
    
    # Wait for services to be ready
    Write-Status "Waiting for services to start..." "INFO"
    Start-Sleep -Seconds 5
    
    # Test health endpoint
    try {
        $healthResponse = Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing -TimeoutSec 30
        if ($healthResponse.StatusCode -eq 200) {
            Write-Status "Health endpoint is accessible" "SUCCESS"
            
            # Parse and show health details
            $healthData = $healthResponse.Content | ConvertFrom-Json
            Write-Status "API Status: $($healthData.status), Version: $($healthData.version)" "INFO"
        } else {
            Write-Status "Health endpoint returned status code: $($healthResponse.StatusCode)" "ERROR"
            $allTests = $false
        }
    } catch {
        Write-Status "Health endpoint is not accessible: $($_.Exception.Message)" "ERROR"
        $allTests = $false
    }
    
    # Test API documentation
    try {
        $docsResponse = Invoke-WebRequest -Uri http://localhost:8000/docs -UseBasicParsing -TimeoutSec 10
        if ($docsResponse.StatusCode -eq 200) {
            Write-Status "API documentation is accessible" "SUCCESS"
        } else {
            Write-Status "API documentation returned status code: $($docsResponse.StatusCode)" "ERROR"
            $allTests = $false
        }
    } catch {
        Write-Status "API documentation is not accessible: $($_.Exception.Message)" "ERROR"
        $allTests = $false
    }
    
    # Test OpenAPI schema
    try {
        $schemaResponse = Invoke-WebRequest -Uri http://localhost:8000/openapi.json -UseBasicParsing -TimeoutSec 10
        if ($schemaResponse.StatusCode -eq 200) {
            Write-Status "OpenAPI schema is accessible" "SUCCESS"
        } else {
            Write-Status "OpenAPI schema returned status code: $($schemaResponse.StatusCode)" "ERROR"
            $allTests = $false
        }
    } catch {
        Write-Status "OpenAPI schema is not accessible: $($_.Exception.Message)" "ERROR"
        $allTests = $false
    }
    
    return $allTests
}

Write-Host "CloudViz Quick Start Verification" -ForegroundColor Blue
Write-Host "=================================" -ForegroundColor Blue
Write-Host "Method: $Method" -ForegroundColor Blue

$allTests = $true

# Test Python installation
if ($Method -eq "python") {
    Write-Status "Testing Python installation..."
    
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Python is available: $pythonVersion" "SUCCESS"
        } else {
            Write-Status "Python test failed" "ERROR"
            $allTests = $false
        }
    } catch {
        Write-Status "Python not found" "ERROR"
        $allTests = $false
    }
    
    # Test pip
    try {
        pip --version | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Pip is available" "SUCCESS"
        } else {
            Write-Status "Pip test failed" "ERROR"
            $allTests = $false
        }
    } catch {
        Write-Status "Pip not found" "ERROR"
        $allTests = $false
    }
    
    # Test virtual environment
    if (Test-Path "venv") {
        Write-Status "Virtual environment found" "SUCCESS"
        
        # Test CloudViz import
        try {
            & "venv\Scripts\python.exe" -c "import cloudviz; print('SUCCESS')" 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Status "CloudViz module imports successfully" "SUCCESS"
            } else {
                Write-Status "CloudViz module import failed" "ERROR"
                $allTests = $false
            }
        } catch {
            Write-Status "Failed to test CloudViz import" "ERROR"
            $allTests = $false
        }
    } else {
        Write-Status "Virtual environment not found" "ERROR"
        $allTests = $false
    }
}

# Test Docker installation
if ($Method -eq "docker") {
    Write-Status "Testing Docker installation..."
    
    # Add Docker to PATH if needed
    if (!(Get-Command "docker" -ErrorAction SilentlyContinue)) {
        $dockerPath = "C:\Program Files\Docker\Docker\resources\bin"
        if (Test-Path $dockerPath) {
            $env:PATH += ";$dockerPath"
            Write-Status "Added Docker to PATH" "INFO"
        }
    }
    
    try {
        $dockerVersion = docker --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Docker is available: $dockerVersion" "SUCCESS"
        } else {
            Write-Status "Docker test failed" "ERROR"
            $allTests = $false
        }
    } catch {
        Write-Status "Docker not found" "ERROR"
        $allTests = $false
    }
    
    try {
        $composeVersion = docker compose version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Docker Compose is available" "SUCCESS"
        } else {
            Write-Status "Docker Compose test failed" "ERROR"
            $allTests = $false
        }
    } catch {
        Write-Status "Docker Compose not available" "ERROR"
        $allTests = $false
    }
    
    if (Test-Path "docker-compose.yml") {
        Write-Status "Docker Compose configuration found" "SUCCESS"
        
        # Test if services are running
        try {
            $services = docker compose ps --format json 2>&1 | ConvertFrom-Json
            $runningServices = $services | Where-Object { $_.State -eq "running" }
            
            if ($runningServices.Count -gt 0) {
                Write-Status "Found $($runningServices.Count) running Docker services" "SUCCESS"
                
                # Test API if CloudViz is running
                $cloudvizService = $runningServices | Where-Object { $_.Service -eq "cloudviz" }
                if ($cloudvizService) {
                    Write-Status "CloudViz container is running" "SUCCESS"
                    $allTests = $allTests -and (Test-DockerAPI)
                } else {
                    Write-Status "CloudViz container is not running. Start with: docker compose up -d" "WARNING"
                }
            } else {
                Write-Status "No Docker services are running. Start with: docker compose up -d" "WARNING"
            }
        } catch {
            Write-Status "Could not check Docker service status: $($_.Exception.Message)" "WARNING"
        }
    } else {
        Write-Status "Docker Compose configuration not found" "ERROR"
        $allTests = $false
    }
}

# Test configuration
Write-Status "Testing configuration..."
if (Test-Path ".env") {
    Write-Status "Environment configuration file found" "SUCCESS"
} elseif (Test-Path ".env.example") {
    Write-Status ".env file not found, but .env.example exists" "WARNING"
    Write-Status "Please copy .env.example to .env and configure it" "INFO"
} else {
    Write-Status "No environment configuration files found" "ERROR"
    $allTests = $false
}

# Show results
Write-Host ""
Write-Host "Verification Results:" -ForegroundColor Blue
Write-Host "====================" -ForegroundColor Blue

if ($allTests) {
    Write-Status "All tests passed! CloudViz environment is ready." "SUCCESS"
    
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Configure cloud provider credentials in .env file"
    Write-Host "2. Start the CloudViz service:"
    
    if ($Method -eq "python") {
        Write-Host "   venv\Scripts\Activate.ps1"
        Write-Host "   uvicorn cloudviz.api.main:app --reload"
    } else {
        Write-Host "   docker compose up -d"
    }
    
    Write-Host "3. Access CloudViz at http://localhost:8000"
    Write-Host "4. View API documentation at http://localhost:8000/docs"
    
    exit 0
} else {
    Write-Status "Some tests failed. Please check the output above for details." "ERROR"
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "* For installation help, run: .\scripts\install-windows.ps1"
    Write-Host "* Check the Installation Guide in wiki/Installation-Guide.md"
    Write-Host "* Verify all prerequisites are installed"
    
    exit 1
}
