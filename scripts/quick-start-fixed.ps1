# CloudViz Quick Start and Verification Script (Fixed)
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
        $result = Invoke-Expression $TestCommand 2>&1
        if ($LASTEXITCODE -eq 0) {
            if ($ExpectedOutput -and $result -notmatch $ExpectedOutput) {
                Write-ColorOutput "✗ $ComponentName test failed - unexpected output" $Red
                return $false
            }
            Write-ColorOutput "✓ $ComponentName is working" $Green
            return $true
        } else {
            Write-ColorOutput "✗ $ComponentName test failed" $Red
            return $false
        }
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
    
    # Check if .env file exists
    if (!(Test-Path ".env")) {
        Write-ColorOutput "⚠ .env file not found. Please copy .env.example to .env and configure it." $Yellow
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
    
    # Test CLI help
    try {
        if ($Method -eq "python") {
            if (Test-Path "venv\Scripts\python.exe") {
                $result = & "venv\Scripts\python.exe" -m cloudviz --help 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-ColorOutput "✓ CLI help command works" $Green
                } else {
                    Write-ColorOutput "✗ CLI help command failed" $Red
                    $allTests = $false
                }
            } else {
                Write-ColorOutput "✗ Virtual environment not found" $Red
                $allTests = $false
            }
        } else {
            # Docker method - skip for now
            Write-ColorOutput "⚠ Skipping CLI tests for Docker method" $Yellow
        }
    }
    catch {
        Write-ColorOutput "✗ CLI test failed: $($_.Exception.Message)" $Red
        $allTests = $false
    }
    
    return $allTests
}

function Show-PostStartupInstructions {
    Write-ColorOutput "`nCloudViz Quick Start Complete!" $Green
    Write-ColorOutput "===============================" $Green
    
    Write-ColorOutput "CloudViz is accessible at:" $Blue
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
}

# Main execution
try {
    Write-ColorOutput "CloudViz Quick Start and Verification" $Blue
    Write-ColorOutput "====================================" $Blue
    Write-ColorOutput "Method: $Method" $Blue
    
    if (!$TestOnly) {
        Write-ColorOutput "`nNote: This is a verification script. For full installation, use:" $Yellow
        Write-ColorOutput ".\scripts\install-windows.ps1 -InstallMethod $Method" $Yellow
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
        if (Get-Command "docker" -ErrorAction SilentlyContinue) {
            try {
                $composeVersion = docker compose version 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-ColorOutput "✓ Docker Compose is working" $Green
                } else {
                    Write-ColorOutput "✗ Docker Compose test failed" $Red
                    $allTestsPassed = $false
                }
            } catch {
                Write-ColorOutput "✗ Docker Compose not available" $Red
                $allTestsPassed = $false
            }
        }
    }
    
    # Test CloudViz API (only if not TestOnly or if service should be running)
    if (!$TestOnly) {
        Write-ColorOutput "`nTesting CloudViz API..." $Blue
        $allTestsPassed = $allTestsPassed -and (Test-CloudVizAPI)
    }
    
    # Test cloud provider credentials
    Write-ColorOutput "`nTesting configuration..." $Blue
    Test-CloudProviderCredentials | Out-Null
    
    # Run basic functional tests
    if (!$TestOnly) {
        Write-ColorOutput "`nRunning functional tests..." $Blue
        $allTestsPassed = $allTestsPassed -and (Run-BasicFunctionalTests)
    }
    
    # Show results
    Write-ColorOutput "`nVerification Results:" $Blue
    Write-ColorOutput "===================" $Blue
    
    if ($allTestsPassed) {
        Write-ColorOutput "✓ All tests passed! CloudViz environment is ready." $Green
        if (!$TestOnly) {
            Show-PostStartupInstructions
        }
    } else {
        Write-ColorOutput "✗ Some tests failed. Please check the output above for details." $Red
        Write-ColorOutput "For troubleshooting help, see: wiki/Troubleshooting.md" $Yellow
    }
    
} catch {
    Write-ColorOutput "`nQuick start verification failed: $($_.Exception.Message)" $Red
    Write-ColorOutput "Please check the error above and try again." $Red
    Write-ColorOutput "For help, see: wiki/Troubleshooting.md" $Yellow
    exit 1
}
