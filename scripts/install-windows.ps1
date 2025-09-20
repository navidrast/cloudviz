# CloudViz Windows Installation Script
# This script installs CloudViz and all its dependencies on Windows

param(
    [Parameter()]
    [ValidateSet("docker", "python", "dev")]
    [string]$InstallMethod = "python",
    
    [Parameter()]
    [switch]$SkipDependencies,
    
    [Parameter()]
    [switch]$InstallDocker,
    
    [Parameter()]
    [string]$PythonVersion = "3.11"
)

# Set error action preference
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

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Install-Chocolatey {
    Write-ColorOutput "Installing Chocolatey package manager..." $Blue
    
    if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
        Set-ExecutionPolicy Bypass -Scope Process -Force
        [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        refreshenv
    } else {
        Write-ColorOutput "Chocolatey already installed" $Green
    }
}

function Install-Python {
    Write-ColorOutput "Installing Python $PythonVersion..." $Blue
    
    if (!(Get-Command python -ErrorAction SilentlyContinue)) {
        choco install python --version=$PythonVersion -y
        refreshenv
    } else {
        $currentVersion = python --version
        Write-ColorOutput "Python already installed: $currentVersion" $Green
    }
}

function Install-NodeJS {
    Write-ColorOutput "Installing Node.js..." $Blue
    
    if (!(Get-Command node -ErrorAction SilentlyContinue)) {
        choco install nodejs -y
        refreshenv
    } else {
        $currentVersion = node --version
        Write-ColorOutput "Node.js already installed: $currentVersion" $Green
    }
    
    # Install Mermaid CLI
    Write-ColorOutput "Installing Mermaid CLI..." $Blue
    npm install -g @mermaid-js/mermaid-cli
}

function Install-Docker {
    Write-ColorOutput "Installing Docker Desktop..." $Blue
    
    if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
        choco install docker-desktop -y
        Write-ColorOutput "Docker Desktop installed. Please restart your computer and enable WSL 2." $Yellow
        Write-ColorOutput "After restart, run: wsl --set-default-version 2" $Yellow
    } else {
        $currentVersion = docker --version
        Write-ColorOutput "Docker already installed: $currentVersion" $Green
    }
}

function Install-Git {
    Write-ColorOutput "Installing Git..." $Blue
    
    if (!(Get-Command git -ErrorAction SilentlyContinue)) {
        choco install git -y
        refreshenv
    } else {
        $currentVersion = git --version
        Write-ColorOutput "Git already installed: $currentVersion" $Green
    }
}

function Install-PostgreSQL {
    Write-ColorOutput "Installing PostgreSQL..." $Blue
    
    if (!(Get-Command psql -ErrorAction SilentlyContinue)) {
        choco install postgresql15 --params '/Password:cloudviz' -y
        refreshenv
        
        # Start PostgreSQL service
        Start-Service postgresql-x64-15
        Set-Service postgresql-x64-15 -StartupType Automatic
        
        # Create database and user
        $env:PGPASSWORD = "cloudviz"
        & "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "CREATE USER cloudviz WITH PASSWORD 'cloudviz';"
        & "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "CREATE DATABASE cloudviz OWNER cloudviz;"
        & "C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE cloudviz TO cloudviz;"
    } else {
        Write-ColorOutput "PostgreSQL already installed" $Green
    }
}

function Install-Redis {
    Write-ColorOutput "Installing Redis..." $Blue
    
    # Redis for Windows (using Memurai as alternative)
    if (!(Get-Process memurai -ErrorAction SilentlyContinue)) {
        Write-ColorOutput "Installing Memurai (Redis alternative for Windows)..." $Blue
        choco install memurai-developer -y
        refreshenv
    } else {
        Write-ColorOutput "Redis/Memurai already installed" $Green
    }
}

function Install-CloudVizPython {
    Write-ColorOutput "Installing CloudViz via Python..." $Blue
    
    # Create virtual environment
    if (!(Test-Path "venv")) {
        python -m venv venv
    }
    
    # Activate virtual environment
    & "venv\Scripts\Activate.ps1"
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    # Install CloudViz in development mode
    pip install -e .
    
    # Copy example configuration
    if (!(Test-Path ".env")) {
        Copy-Item "examples\configurations\.env.example" ".env"
        Write-ColorOutput "Configuration file created: .env" $Green
        Write-ColorOutput "Please edit .env with your cloud provider credentials" $Yellow
    }
    
    Write-ColorOutput "CloudViz installed successfully!" $Green
    Write-ColorOutput "To start CloudViz:" $Blue
    Write-ColorOutput "  1. Activate virtual environment: venv\Scripts\Activate.ps1" $Blue
    Write-ColorOutput "  2. Configure .env file with your credentials" $Blue
    Write-ColorOutput "  3. Start server: cloudviz server start" $Blue
}

function Install-CloudVizDocker {
    Write-ColorOutput "Setting up CloudViz with Docker..." $Blue
    
    # Check if Docker is running
    try {
        docker ps | Out-Null
    }
    catch {
        Write-ColorOutput "Docker is not running. Please start Docker Desktop first." $Red
        exit 1
    }
    
    # Copy example configuration
    if (!(Test-Path ".env")) {
        Copy-Item "examples\configurations\.env.example" ".env"
        Write-ColorOutput "Configuration file created: .env" $Green
        Write-ColorOutput "Please edit .env with your cloud provider credentials" $Yellow
    }
    
    # Create required directories
    New-Item -ItemType Directory -Force -Path "logs", "output", "config"
    
    # Start services
    Write-ColorOutput "Starting CloudViz services with Docker Compose..." $Blue
    docker compose up -d
    
    # Wait for services to be ready
    Write-ColorOutput "Waiting for services to start..." $Blue
    Start-Sleep -Seconds 30
    
    # Check health
    $maxAttempts = 10
    $attempt = 0
    do {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-ColorOutput "CloudViz is running successfully!" $Green
                break
            }
        }
        catch {
            $attempt++
            Write-ColorOutput "Waiting for CloudViz to start... (attempt $attempt/$maxAttempts)" $Yellow
            Start-Sleep -Seconds 10
        }
    } while ($attempt -lt $maxAttempts)
    
    if ($attempt -eq $maxAttempts) {
        Write-ColorOutput "CloudViz failed to start. Check logs with: docker compose logs" $Red
        exit 1
    }
    
    Write-ColorOutput "CloudViz is available at: http://localhost:8000" $Green
    Write-ColorOutput "API documentation: http://localhost:8000/docs" $Green
}

function Show-PostInstallInstructions {
    Write-ColorOutput "`nCloudViz Installation Complete!" $Green
    Write-ColorOutput "=================================" $Green
    
    switch ($InstallMethod) {
        "docker" {
            Write-ColorOutput "Docker installation completed." $Blue
            Write-ColorOutput "Access CloudViz at: http://localhost:8000" $Blue
            Write-ColorOutput "API docs at: http://localhost:8000/docs" $Blue
            Write-ColorOutput "" 
            Write-ColorOutput "Useful commands:" $Blue
            Write-ColorOutput "  View logs: docker compose logs -f" $Blue
            Write-ColorOutput "  Stop services: docker compose down" $Blue
            Write-ColorOutput "  Restart services: docker compose restart" $Blue
        }
        "python" {
            Write-ColorOutput "Python installation completed." $Blue
            Write-ColorOutput "" 
            Write-ColorOutput "To start CloudViz:" $Blue
            Write-ColorOutput "  1. venv\Scripts\Activate.ps1" $Blue
            Write-ColorOutput "  2. Edit .env file with your cloud credentials" $Blue
            Write-ColorOutput "  3. cloudviz server start" $Blue
        }
        "dev" {
            Write-ColorOutput "Development environment setup completed." $Blue
            Write-ColorOutput "" 
            Write-ColorOutput "To start development:" $Blue
            Write-ColorOutput "  1. venv\Scripts\Activate.ps1" $Blue
            Write-ColorOutput "  2. Edit .env file with your cloud credentials" $Blue
            Write-ColorOutput "  3. cloudviz server start --reload" $Blue
        }
    }
    
    Write-ColorOutput "" 
    Write-ColorOutput "Next steps:" $Yellow
    Write-ColorOutput "  1. Configure cloud provider credentials in .env" $Yellow
    Write-ColorOutput "  2. Test cloud connectivity: cloudviz provider test azure" $Yellow
    Write-ColorOutput "  3. Extract your first inventory: cloudviz extract azure" $Yellow
    Write-ColorOutput "  4. Generate a diagram: cloudviz render inventory.json" $Yellow
}

# Main installation flow
try {
    Write-ColorOutput "CloudViz Windows Installer" $Blue
    Write-ColorOutput "=========================" $Blue
    Write-ColorOutput "Installation method: $InstallMethod" $Blue
    
    # Check if running as administrator for system-wide installs
    if ($InstallMethod -eq "docker" -or $InstallDocker) {
        if (!(Test-Administrator)) {
            Write-ColorOutput "This installation requires administrator privileges." $Red
            Write-ColorOutput "Please run PowerShell as Administrator and try again." $Red
            exit 1
        }
    }
    
    # Install dependencies
    if (!$SkipDependencies) {
        Write-ColorOutput "`nInstalling dependencies..." $Blue
        Install-Chocolatey
        Install-Git
        
        if ($InstallMethod -ne "docker") {
            Install-Python
            Install-NodeJS
            Install-PostgreSQL
            Install-Redis
        }
        
        if ($InstallMethod -eq "docker" -or $InstallDocker) {
            Install-Docker
        }
    }
    
    # Install CloudViz
    Write-ColorOutput "`nInstalling CloudViz..." $Blue
    
    switch ($InstallMethod) {
        "docker" {
            Install-CloudVizDocker
        }
        "python" {
            Install-CloudVizPython
        }
        "dev" {
            Install-CloudVizPython
            # Additional dev setup
            & "venv\Scripts\Activate.ps1"
            pip install -r requirements/dev.txt
        }
    }
    
    Show-PostInstallInstructions
    
} catch {
    Write-ColorOutput "`nInstallation failed: $($_.Exception.Message)" $Red
    Write-ColorOutput "Please check the error above and try again." $Red
    exit 1
}
