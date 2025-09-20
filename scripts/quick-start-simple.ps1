# CloudViz Quick Start Verification Script
param(
    [string]$Method = "python",
    [switch]$TestOnly
)

# Simple verification script for CloudViz installation

function Write-Status {
    param([string]$Message, [string]$Status = "INFO")
    switch ($Status) {
        "SUCCESS" { Write-Host "✓ $Message" -ForegroundColor Green }
        "ERROR" { Write-Host "✗ $Message" -ForegroundColor Red }
        "WARNING" { Write-Host "⚠ $Message" -ForegroundColor Yellow }
        default { Write-Host "• $Message" -ForegroundColor Blue }
    }
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
    
    try {
        docker --version | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Docker is available" "SUCCESS"
        } else {
            Write-Status "Docker test failed" "ERROR"
            $allTests = $false
        }
    } catch {
        Write-Status "Docker not found" "ERROR"
        $allTests = $false
    }
    
    try {
        docker compose version | Out-Null
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
Write-Host "`nVerification Results:" -ForegroundColor Blue
Write-Host "====================" -ForegroundColor Blue

if ($allTests) {
    Write-Status "All tests passed! CloudViz environment is ready." "SUCCESS"
    
    Write-Host "`nNext Steps:" -ForegroundColor Yellow
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
    Write-Host "`nTroubleshooting:" -ForegroundColor Yellow
    Write-Host "• For installation help, run: .\scripts\install-windows.ps1"
    Write-Host "• Check the Installation Guide in wiki/Installation-Guide.md"
    Write-Host "• Verify all prerequisites are installed"
    
    exit 1
}
