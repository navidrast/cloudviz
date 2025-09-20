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

function Test-SystemComponents {
    Write-ColorOutput "`nTesting system components..." $Blue
    $allTests = $true
    
    if ($Method -eq "python") {
        # Test Python
        try {
            $pythonResult = python --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-ColorOutput "✓ Python is available: $pythonResult" $Green
            } else {
                Write-ColorOutput "✗ Python test failed" $Red
                $allTests = $false
            }
        } catch {
            Write-ColorOutput "✗ Python not found" $Red
            $allTests = $false
        }
        
        # Test Pip
        try {
            $pipResult = pip --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-ColorOutput "✓ Pip is available" $Green
            } else {
                Write-ColorOutput "✗ Pip test failed" $Red
                $allTests = $false
            }
        } catch {
            Write-ColorOutput "✗ Pip not found" $Red
            $allTests = $false
        }
        
    } else {
        # Test Docker
        try {
            $dockerResult = docker --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-ColorOutput "✓ Docker is available: $dockerResult" $Green
            } else {
                Write-ColorOutput "✗ Docker test failed" $Red
                $allTests = $false
            }
        } catch {
            Write-ColorOutput "✗ Docker not found" $Red
            $allTests = $false
        }
        
        # Test Docker Compose
        try {
            $composeResult = docker compose version 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-ColorOutput "✓ Docker Compose is available" $Green
            } else {
                Write-ColorOutput "✗ Docker Compose test failed" $Red
                $allTests = $false
            }
        } catch {
            Write-ColorOutput "✗ Docker Compose not available" $Red
            $allTests = $false
        }
    }
    
    return $allTests
}

function Test-CloudVizInstallation {
    Write-ColorOutput "`nTesting CloudViz installation..." $Blue
    $allTests = $true
    
    if ($Method -eq "python") {
        # Check if virtual environment exists
        if (Test-Path "venv") {
            Write-ColorOutput "✓ Virtual environment found" $Green
            
            # Test CloudViz import
            try {
                $importResult = & "venv\Scripts\python.exe" -c "import cloudviz; print('CloudViz module imported successfully')" 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-ColorOutput "✓ CloudViz module imports successfully" $Green
                } else {
                    Write-ColorOutput "✗ CloudViz module import failed" $Red
                    $allTests = $false
                }
            } catch {
                Write-ColorOutput "✗ Failed to test CloudViz import: $($_.Exception.Message)" $Red
                $allTests = $false
            }
            
        } else {
            Write-ColorOutput "✗ Virtual environment not found" $Red
            $allTests = $false
        }
    } else {
        # Docker method - check if containers are defined
        if (Test-Path "docker-compose.yml") {
            Write-ColorOutput "✓ Docker Compose configuration found" $Green
        } else {
            Write-ColorOutput "✗ Docker Compose configuration not found" $Red
            $allTests = $false
        }
    }
    
    return $allTests
}

function Test-Configuration {
    Write-ColorOutput "`nTesting configuration..." $Blue
    
    # Check if .env file exists
    if (Test-Path ".env") {
        Write-ColorOutput "✓ Environment configuration file found" $Green
        return $true
    } elseif (Test-Path ".env.example") {
        Write-ColorOutput "⚠ .env file not found, but .env.example exists" $Yellow
        Write-ColorOutput "  Please copy .env.example to .env and configure it" $Yellow
        return $false
    } else {
        Write-ColorOutput "✗ No environment configuration files found" $Red
        return $false
    }
}

function Show-Summary {
    param([bool]$AllTestsPassed)
    
    Write-ColorOutput "`nCloudViz Verification Results:" $Blue
    Write-ColorOutput "==============================" $Blue
    
    if ($AllTestsPassed) {
        Write-ColorOutput "✓ All tests passed! CloudViz environment is ready." $Green
        
        Write-ColorOutput "`nNext Steps:" $Yellow
        Write-ColorOutput "1. Configure cloud provider credentials in .env file" $Yellow
        Write-ColorOutput "2. Start the CloudViz service:" $Yellow
        
        if ($Method -eq "python") {
            Write-ColorOutput "   venv\Scripts\Activate.ps1" $Yellow
            Write-ColorOutput "   uvicorn cloudviz.api.main:app --reload" $Yellow
        } else {
            Write-ColorOutput "   docker compose up -d" $Yellow
        }
        
        Write-ColorOutput "3. Access CloudViz at http://localhost:8000" $Yellow
        Write-ColorOutput "4. View API documentation at http://localhost:8000/docs" $Yellow
        
    } else {
        Write-ColorOutput "✗ Some tests failed. Please check the output above for details." $Red
        Write-ColorOutput "`nTroubleshooting:" $Yellow
        Write-ColorOutput "• For installation help, run: .\scripts\install-windows.ps1" $Yellow
        Write-ColorOutput "• Check the Installation Guide in wiki/Installation-Guide.md" $Yellow
        Write-ColorOutput "• Verify all prerequisites are installed" $Yellow
    }
}

# Main execution
Write-ColorOutput "CloudViz Quick Start and Verification" $Blue
Write-ColorOutput "====================================" $Blue
Write-ColorOutput "Method: $Method" $Blue

if ($TestOnly) {
    Write-ColorOutput "Mode: Test Only" $Blue
} else {
    Write-ColorOutput "Mode: Full Verification" $Blue
}

# Initialize test results
$systemTests = $false
$installTests = $false
$configTests = $false

try {
    # Run system component tests
    $systemTests = Test-SystemComponents
    
    # Run installation tests
    $installTests = Test-CloudVizInstallation
    
    # Run configuration tests
    $configTests = Test-Configuration
    
    # Calculate overall result
    $allTestsPassed = $systemTests -and $installTests -and $configTests
    
    # Show summary
    Show-Summary -AllTestsPassed $allTestsPassed
    
    # Exit with appropriate code
    if ($allTestsPassed) {
        exit 0
    } else {
        exit 1
    }
    
} catch {
    Write-ColorOutput "`nUnexpected error during verification: $($_.Exception.Message)" $Red
    Write-ColorOutput "Please check the error above and try again." $Red
    exit 1
}
