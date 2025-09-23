#!/bin/bash
# CloudViz Linux/macOS Installation Script
# This script installs CloudViz and all its dependencies on Linux and macOS

set -e

# Configuration
INSTALL_METHOD="${1:-python}"
SKIP_DEPENDENCIES="${2:-false}"
PYTHON_VERSION="${3:-3.11}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &> /dev/null; then
            OS="ubuntu"
        elif command -v yum &> /dev/null; then
            OS="centos"
        elif command -v pacman &> /dev/null; then
            OS="arch"
        else
            OS="linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    else
        log_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    
    log_info "Detected OS: $OS"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_warning "Running as root. Some operations may not work as expected."
    fi
}

# Install system dependencies
install_system_dependencies() {
    log_info "Installing system dependencies..."
    
    case $OS in
        "ubuntu")
            sudo apt-get update
            sudo apt-get install -y \
                curl \
                wget \
                git \
                build-essential \
                libssl-dev \
                libffi-dev \
                python3-dev \
                python3-pip \
                python3-venv \
                graphviz \
                libgraphviz-dev \
                pkg-config \
                postgresql-client \
                redis-tools
            ;;
        "centos")
            sudo yum update -y
            sudo yum groupinstall -y "Development Tools"
            sudo yum install -y \
                curl \
                wget \
                git \
                openssl-devel \
                libffi-devel \
                python3-devel \
                python3-pip \
                graphviz \
                graphviz-devel \
                postgresql \
                redis
            ;;
        "macos")
            # Check if Homebrew is installed
            if ! command -v brew &> /dev/null; then
                log_info "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            
            brew install \
                python@${PYTHON_VERSION} \
                node \
                graphviz \
                postgresql@15 \
                redis \
                git
            ;;
        *)
            log_warning "Manual dependency installation required for $OS"
            ;;
    esac
    
    log_success "System dependencies installed"
}

# Install Python
install_python() {
    log_info "Setting up Python environment..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed. Please install Python 3.8+ and try again."
        exit 1
    fi
    
    # Check Python version
    PYTHON_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    log_info "Python version: $PYTHON_VER"
    
    if [[ "$(echo "$PYTHON_VER < 3.8" | bc -l)" -eq 1 ]]; then
        log_error "Python 3.8+ is required. Current version: $PYTHON_VER"
        exit 1
    fi
    
    log_success "Python setup complete"
}

# Install Node.js and Mermaid CLI
install_nodejs() {
    log_info "Installing Node.js and Mermaid CLI..."
    
    if ! command -v node &> /dev/null; then
        case $OS in
            "ubuntu")
                curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
                sudo apt-get install -y nodejs
                ;;
            "centos")
                curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
                sudo yum install -y nodejs
                ;;
            "macos")
                brew install node
                ;;
        esac
    fi
    
    # Install Mermaid CLI
    sudo npm install -g @mermaid-js/mermaid-cli
    
    log_success "Node.js and Mermaid CLI installed"
}

# Install Docker
install_docker() {
    log_info "Installing Docker..."
    
    if command -v docker &> /dev/null; then
        log_success "Docker already installed"
        return
    fi
    
    case $OS in
        "ubuntu")
            # Install Docker using the official script
            curl -fsSL https://get.docker.com -o get-docker.sh
            sudo sh get-docker.sh
            sudo usermod -aG docker $USER
            
            # Install Docker Compose
            sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            sudo chmod +x /usr/local/bin/docker-compose
            ;;
        "centos")
            sudo yum install -y yum-utils
            sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            sudo yum install -y docker-ce docker-ce-cli containerd.io
            sudo systemctl start docker
            sudo systemctl enable docker
            sudo usermod -aG docker $USER
            
            # Install Docker Compose
            sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            sudo chmod +x /usr/local/bin/docker-compose
            ;;
        "macos")
            log_info "Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
            log_warning "After installation, start Docker Desktop and try again"
            exit 1
            ;;
    esac
    
    log_success "Docker installed"
    log_warning "Please log out and log back in for Docker group membership to take effect"
}

# Install PostgreSQL
install_postgresql() {
    log_info "Installing PostgreSQL..."
    
    case $OS in
        "ubuntu")
            sudo apt-get install -y postgresql postgresql-contrib
            sudo systemctl start postgresql
            sudo systemctl enable postgresql
            
            # Create database and user
            sudo -u postgres psql -c "CREATE USER cloudviz WITH PASSWORD 'cloudviz';"
            sudo -u postgres psql -c "CREATE DATABASE cloudviz OWNER cloudviz;"
            sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE cloudviz TO cloudviz;"
            ;;
        "centos")
            sudo yum install -y postgresql-server postgresql-contrib
            sudo postgresql-setup initdb
            sudo systemctl start postgresql
            sudo systemctl enable postgresql
            
            # Create database and user
            sudo -u postgres psql -c "CREATE USER cloudviz WITH PASSWORD 'cloudviz';"
            sudo -u postgres psql -c "CREATE DATABASE cloudviz OWNER cloudviz;"
            sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE cloudviz TO cloudviz;"
            ;;
        "macos")
            brew services start postgresql@15
            
            # Create database and user
            createuser cloudviz
            createdb cloudviz -O cloudviz
            psql -d postgres -c "ALTER USER cloudviz WITH PASSWORD 'cloudviz';"
            ;;
    esac
    
    log_success "PostgreSQL installed and configured"
}

# Install Redis
install_redis() {
    log_info "Installing Redis..."
    
    case $OS in
        "ubuntu")
            sudo apt-get install -y redis-server
            sudo systemctl start redis-server
            sudo systemctl enable redis-server
            ;;
        "centos")
            sudo yum install -y redis
            sudo systemctl start redis
            sudo systemctl enable redis
            ;;
        "macos")
            brew services start redis
            ;;
    esac
    
    log_success "Redis installed and started"
}

# Install CloudViz with Python
install_cloudviz_python() {
    log_info "Installing CloudViz via Python..."
    
    # Create virtual environment
    if [[ ! -d "venv" ]]; then
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install CloudViz in development mode
    pip install -e .
    
    # Copy example configuration
    if [[ ! -f ".env" ]]; then
        cp examples/configurations/.env.example .env
        log_success "Configuration file created: .env"
        log_warning "Please edit .env with your cloud provider credentials"
    fi
    
    log_success "CloudViz installed successfully!"
    log_info "To start CloudViz:"
    log_info "  1. Activate virtual environment: source venv/bin/activate"
    log_info "  2. Configure .env file with your credentials"
    log_info "  3. Start server: cloudviz server start"
}

# Install CloudViz with Docker
install_cloudviz_docker() {
    log_info "Setting up CloudViz with Docker..."
    
    # Check if Docker is running
    if ! docker ps &> /dev/null; then
        log_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Copy example configuration
    if [[ ! -f ".env" ]]; then
        cp examples/configurations/.env.example .env
        log_success "Configuration file created: .env"
        log_warning "Please edit .env with your cloud provider credentials"
    fi
    
    # Create required directories
    mkdir -p logs output config
    
    # Start services
    log_info "Starting CloudViz services with Docker Compose..."
    docker compose up -d
    
    # Wait for services to be ready
    log_info "Waiting for services to start..."
    sleep 30
    
    # Check health
    max_attempts=10
    attempt=0
    while [[ $attempt -lt $max_attempts ]]; do
        if curl -f http://localhost:8000/health &> /dev/null; then
            log_success "CloudViz is running successfully!"
            break
        else
            ((attempt++))
            log_info "Waiting for CloudViz to start... (attempt $attempt/$max_attempts)"
            sleep 10
        fi
    done
    
    if [[ $attempt -eq $max_attempts ]]; then
        log_error "CloudViz failed to start. Check logs with: docker compose logs"
        exit 1
    fi
    
    log_success "CloudViz is available at: http://localhost:8000"
    log_success "API documentation: http://localhost:8000/docs"
}

# Show post-install instructions
show_post_install_instructions() {
    echo
    log_success "CloudViz Installation Complete!"
    echo "================================="
    
    case $INSTALL_METHOD in
        "docker")
            log_info "Docker installation completed."
            log_info "Access CloudViz at: http://localhost:8000"
            log_info "API docs at: http://localhost:8000/docs"
            echo
            log_info "Useful commands:"
            log_info "  View logs: docker compose logs -f"
            log_info "  Stop services: docker compose down"
            log_info "  Restart services: docker compose restart"
            ;;
        "python"|"dev")
            log_info "Python installation completed."
            echo
            log_info "To start CloudViz:"
            log_info "  1. source venv/bin/activate"
            log_info "  2. Edit .env file with your cloud credentials"
            log_info "  3. cloudviz server start"
            ;;
    esac
    
    echo
    log_warning "Next steps:"
    log_warning "  1. Configure cloud provider credentials in .env"
    log_warning "  2. Test cloud connectivity: cloudviz provider test azure"
    log_warning "  3. Extract your first inventory: cloudviz extract azure"
    log_warning "  4. Generate a diagram: cloudviz render inventory.json"
}

# Main installation flow
main() {
    log_info "CloudViz Installation Script"
    log_info "==========================="
    log_info "Installation method: $INSTALL_METHOD"
    
    detect_os
    check_root
    
    # Install dependencies
    if [[ "$SKIP_DEPENDENCIES" != "true" ]]; then
        log_info "Installing dependencies..."
        install_system_dependencies
        
        if [[ "$INSTALL_METHOD" != "docker" ]]; then
            install_python
            install_nodejs
            install_postgresql
            install_redis
        fi
        
        if [[ "$INSTALL_METHOD" == "docker" ]]; then
            install_docker
        fi
    fi
    
    # Install CloudViz
    log_info "Installing CloudViz..."
    
    case $INSTALL_METHOD in
        "docker")
            install_cloudviz_docker
            ;;
        "python"|"dev")
            install_cloudviz_python
            ;;
        *)
            log_error "Unknown installation method: $INSTALL_METHOD"
            log_error "Supported methods: docker, python, dev"
            exit 1
            ;;
    esac
    
    show_post_install_instructions
}

# Run main function
main "$@"
