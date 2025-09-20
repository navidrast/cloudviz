# CloudViz Quick Start and Verification Script
# This script sets up CloudViz and verifies all components are working

param(
    [Parameter()]
    [ValidateSet("docker", "python")]
    [string]$Method = "python",
    
    [Parameter()]
    [switch]$SkipInstall,
    
    [Parameter()]
    [switch]$TestOnly
)

$ErrorActionPreference = "Stop"

# Colors for output
$Red = "`e[31m"
$Green = "`e[32m"
$Yellow = "`e[33m"
$Blue = "`e[34m"
$Reset = "`e[0m"

function Write-ColorOutput {
    param([string]$Message, [string]$Color = $Reset)
    Write-Host "$Color$Message$Reset"
}

function Test-ComponentHealth {
    param([string]$ComponentName, [string]$TestCommand, [string]$ExpectedOutput = "")
    
    Write-ColorOutput "Testing $ComponentName..." $Blue
    
    try {
        $result = Invoke-Expression $TestCommand
        if ($ExpectedOutput -and $result -notmatch $ExpectedOutput) {
            Write-ColorOutput "✗ $ComponentName test failed" $Red
            return $false
        }
        Write-ColorOutput "✓ $ComponentName is working" $Green
        return $true
    }
    catch {
        Write-ColorOutput "✗ $ComponentName test failed: $($_.Exception.Message)" $Red
        return $false
    }
}

function Test-NetworkConnectivity {
    param([string]$Url, [string]$Description)
    
    Write-ColorOutput "Testing $Description..." $Blue
    
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-ColorOutput "✓ $Description is accessible" $Green
            return $true
        } else {
            Write-ColorOutput "✗ $Description returned status code: $($response.StatusCode)" $Red
            return $false
        }
    }
    catch {
        Write-ColorOutput "✗ $Description is not accessible: $($_.Exception.Message)" $Red
        return $false
    }
}

function Test-CloudProviderCredentials {
    Write-ColorOutput "Testing cloud provider credentials..." $Blue
    
    $credentialsValid = $true
    
    # Check if .env file exists
    if (!(Test-Path ".env")) {
        Write-ColorOutput "✗ .env file not found. Please copy .env.example to .env and configure it." $Red
        return $false
    }
    
    # Load environment variables from .env file
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^([^#][^=]*?)=(.*)$') {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
    
    # Test Azure credentials
    $azureTenantId = [Environment]::GetEnvironmentVariable("AZURE_TENANT_ID")
    $azureClientId = [Environment]::GetEnvironmentVariable("AZURE_CLIENT_ID")
    if ($azureTenantId -and $azureClientId) {
        if ($azureTenantId -eq "your-azure-tenant-id" -or $azureClientId -eq "your-azure-client-id") {
            Write-ColorOutput "⚠ Azure credentials not configured (using example values)" $Yellow
        } else {
            Write-ColorOutput "✓ Azure credentials configured" $Green
        }
    } else {
        Write-ColorOutput "⚠ Azure credentials not found in .env file" $Yellow
    }
    
    # Test AWS credentials
    $awsAccessKey = [Environment]::GetEnvironmentVariable("AWS_ACCESS_KEY_ID")
    $awsSecretKey = [Environment]::GetEnvironmentVariable("AWS_SECRET_ACCESS_KEY")
    if ($awsAccessKey -and $awsSecretKey) {
        if ($awsAccessKey -eq "your-aws-access-key" -or $awsSecretKey -eq "your-aws-secret-key") {
            Write-ColorOutput "⚠ AWS credentials not configured (using example values)" $Yellow
        } else {
            Write-ColorOutput "✓ AWS credentials configured" $Green
        }
    } else {
        Write-ColorOutput "⚠ AWS credentials not found in .env file" $Yellow
    }
    
    # Test GCP credentials
    $gcpProjectId = [Environment]::GetEnvironmentVariable("GCP_PROJECT_ID")
    $gcpCredentials = [Environment]::GetEnvironmentVariable("GOOGLE_APPLICATION_CREDENTIALS")
    if ($gcpProjectId -and $gcpCredentials) {
        if ($gcpProjectId -eq "your-gcp-project-id") {
            Write-ColorOutput "⚠ GCP credentials not configured (using example values)" $Yellow
        } else {
            Write-ColorOutput "✓ GCP credentials configured" $Green
        }
    } else {
        Write-ColorOutput "⚠ GCP credentials not found in .env file" $Yellow
    }
    
    return $credentialsValid
}

function Start-CloudVizServices {
    param([string]$InstallMethod)
    
    Write-ColorOutput "Starting CloudViz services ($InstallMethod)..." $Blue
    
    switch ($InstallMethod) {
        "docker" {
            # Check if Docker is available
            try {
                docker --version | Out-Null
            }
            catch {
                Write-ColorOutput "✗ Docker is not available. Please install Docker Desktop." $Red
                return $false
            }
            
            # Start services with Docker Compose
            Write-ColorOutput "Starting services with Docker Compose..." $Blue
            docker compose up -d
            
            # Wait for services to start
            Start-Sleep -Seconds 30
        }
        "python" {
            # Check if virtual environment exists
            if (!(Test-Path "venv")) {
                Write-ColorOutput "✗ Virtual environment not found. Please run installation first." $Red
                return $false
            }
            
            # Activate virtual environment and start server
            Write-ColorOutput "Starting CloudViz server..." $Blue
            & "venv\Scripts\Activate.ps1"
            
            # Start server in background
            Start-Process -FilePath "venv\Scripts\python.exe" -ArgumentList "-m", "uvicorn", "cloudviz.api.main:app", "--host", "0.0.0.0", "--port", "8000" -WindowStyle Hidden
            
            # Wait for server to start
            Start-Sleep -Seconds 15
        }
    }
    
    return $true
}

function Test-CloudVizAPI {
    Write-ColorOutput "Testing CloudViz API endpoints..." $Blue
    
    $allTests = $true
    
    # Test health endpoint
    if (!(Test-NetworkConnectivity "http://localhost:8000/health" "Health endpoint")) {
        $allTests = $false
    }
    
    # Test API documentation
    if (!(Test-NetworkConnectivity "http://localhost:8000/docs" "API documentation")) {
        $allTests = $false
    }
    
    # Test OpenAPI schema
    if (!(Test-NetworkConnectivity "http://localhost:8000/openapi.json" "OpenAPI schema")) {
        $allTests = $false
    }
    
    return $allTests
}

function Run-BasicFunctionalTests {
    Write-ColorOutput "Running basic functional tests..." $Blue
    
    $allTests = $true
    
    # Activate virtual environment if using Python method
    if ($Method -eq "python") {
        & "venv\Scripts\Activate.ps1"
    }
    
    # Test CLI help
    try {
        if ($Method -eq "python") {
            $result = & "venv\Scripts\python.exe" -m cloudviz --help
        } else {
            $result = docker compose exec cloudviz cloudviz --help
        }
        Write-ColorOutput "✓ CLI help command works" $Green
    }
    catch {
        Write-ColorOutput "✗ CLI help command failed: $($_.Exception.Message)" $Red
        $allTests = $false
    }
    
    # Test configuration validation
    try {
        if ($Method -eq "python") {
            $result = & "venv\Scripts\python.exe" -m cloudviz config validate
        } else {
            $result = docker compose exec cloudviz cloudviz config validate
        }
        Write-ColorOutput "✓ Configuration validation works" $Green
    }
    catch {
        Write-ColorOutput "✗ Configuration validation failed: $($_.Exception.Message)" $Red
        $allTests = $false
    }
    
    return $allTests
}

function Show-PostStartupInstructions {
    Write-ColorOutput "`nCloudViz Quick Start Complete!" $Green
    Write-ColorOutput "===============================" $Green
    
    Write-ColorOutput "CloudViz is now running and accessible at:" $Blue
    Write-ColorOutput "• Main API: http://localhost:8000" $Blue
    Write-ColorOutput "• API Documentation: http://localhost:8000/docs" $Blue
    Write-ColorOutput "• Health Check: http://localhost:8000/health" $Blue
    
    Write-ColorOutput "`nNext Steps:" $Yellow
    Write-ColorOutput "1. Configure cloud provider credentials in .env file" $Yellow
    Write-ColorOutput "2. Test cloud connectivity:" $Yellow
    if ($Method -eq "python") {
        Write-ColorOutput "   venv\Scripts\Activate.ps1" $Yellow
        Write-ColorOutput "   cloudviz provider test azure" $Yellow
    } else {
        Write-ColorOutput "   docker compose exec cloudviz cloudviz provider test azure" $Yellow
    }
    Write-ColorOutput "3. Extract your first inventory:" $Yellow
    if ($Method -eq "python") {
        Write-ColorOutput "   cloudviz extract azure --output my-inventory.json" $Yellow
    } else {
        Write-ColorOutput "   docker compose exec cloudviz cloudviz extract azure --output my-inventory.json" $Yellow
    }
    Write-ColorOutput "4. Generate a diagram:" $Yellow
    if ($Method -eq "python") {
        Write-ColorOutput "   cloudviz render my-inventory.json --format mermaid --output diagram.md" $Yellow
    } else {
        Write-ColorOutput "   docker compose exec cloudviz cloudviz render my-inventory.json --format mermaid --output diagram.md" $Yellow
    }
    
    Write-ColorOutput "`nUseful Commands:" $Blue
    if ($Method -eq "docker") {
        Write-ColorOutput "• View logs: docker compose logs -f" $Blue
        Write-ColorOutput "• Stop services: docker compose down" $Blue
        Write-ColorOutput "• Restart services: docker compose restart" $Blue
    } else {
        Write-ColorOutput "• Activate environment: venv\Scripts\Activate.ps1" $Blue
        Write-ColorOutput "• Check status: cloudviz status" $Blue
        Write-ColorOutput "• View help: cloudviz --help" $Blue
    }
}

# Main execution
try {
    Write-ColorOutput "CloudViz Quick Start and Verification" $Blue
    Write-ColorOutput "====================================" $Blue
    Write-ColorOutput "Method: $Method" $Blue
    
    if (!$SkipInstall -and !$TestOnly) {
        Write-ColorOutput "`nRunning installation..." $Blue
        if ($Method -eq "docker") {
            & ".\scripts\install-windows.ps1" -InstallMethod docker
        } else {
            & ".\scripts\install-windows.ps1" -InstallMethod python
        }
    }
    
    if (!$TestOnly) {
        # Start services
        if (!(Start-CloudVizServices $Method)) {
            Write-ColorOutput "Failed to start CloudViz services" $Red
            exit 1
        }
    }
    
    # Run verification tests
    Write-ColorOutput "`nRunning verification tests..." $Blue
    $allTestsPassed = $true
    
    # Test system components
    Write-ColorOutput "`nTesting system components..." $Blue
    
    if ($Method -eq "python") {
        $allTestsPassed = $allTestsPassed -and (Test-ComponentHealth "Python" "python --version" "Python")
        $allTestsPassed = $allTestsPassed -and (Test-ComponentHealth "Pip" "pip --version" "pip")
    } else {
        $allTestsPassed = $allTestsPassed -and (Test-ComponentHealth "Docker" "docker --version" "Docker")
        $allTestsPassed = $allTestsPassed -and (Test-ComponentHealth "Docker Compose" "docker compose version" "Docker Compose")
    }
    
    # Test CloudViz API
    Write-ColorOutput "`nTesting CloudViz API..." $Blue
    $allTestsPassed = $allTestsPassed -and (Test-CloudVizAPI)
    
    # Test cloud provider credentials
    Write-ColorOutput "`nTesting configuration..." $Blue
    Test-CloudProviderCredentials | Out-Null
    
    # Run basic functional tests
    Write-ColorOutput "`nRunning functional tests..." $Blue
    $allTestsPassed = $allTestsPassed -and (Run-BasicFunctionalTests)
    
    # Show results
    Write-ColorOutput "`nVerification Results:" $Blue
    Write-ColorOutput "===================" $Blue
    
    if ($allTestsPassed) {
        Write-ColorOutput "✓ All tests passed! CloudViz is ready to use." $Green
        Show-PostStartupInstructions
    } else {
        Write-ColorOutput "✗ Some tests failed. Please check the output above for details." $Red
        Write-ColorOutput "For troubleshooting help, see: wiki/Troubleshooting.md" $Yellow
    }
    
} catch {
    Write-ColorOutput "`nQuick start failed: $($_.Exception.Message)" $Red
    Write-ColorOutput "Please check the error above and try again." $Red
    Write-ColorOutput "For help, see: wiki/Troubleshooting.md" $Yellow
    exit 1
}
