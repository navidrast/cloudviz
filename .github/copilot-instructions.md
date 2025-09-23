# CloudViz - Multi-Cloud Infrastructure Visualization Platform

**ALWAYS follow these instructions first. Only fallback to additional search and context gathering if the information in these instructions is incomplete or found to be in error.**

CloudViz is a Python-based FastAPI application that provides multi-cloud infrastructure visualization with REST API endpoints and Mermaid diagram generation. It integrates with Azure, AWS, and GCP to extract and visualize cloud resources.

## Working Effectively

### Bootstrap, Build, and Test the Repository

1. **Prerequisites Setup:**
   ```bash
   # Install system dependencies (Ubuntu/Debian)
   sudo apt update
   sudo apt install -y python3.11 python3.11-dev python3.11-venv \
     postgresql postgresql-contrib redis-server nodejs npm \
     graphviz libgraphviz-dev pkg-config build-essential \
     libssl-dev libffi-dev curl git docker.io docker-compose
   
   # Install Mermaid CLI globally
   sudo npm install -g @mermaid-js/mermaid-cli
   ```

2. **Python Environment Setup:**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   
   # Upgrade pip
   pip install --upgrade pip
   
   # Install development dependencies (may fail in restricted networks)
   pip install -r requirements/dev.txt
   
   # Alternative for network-restricted environments:
   pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements/dev.txt
   
   # Install CloudViz in development mode
   pip install -e .
   ```
   **NEVER CANCEL:** Dependency installation takes 10-15 minutes. Set timeout to 30+ minutes.
   **NETWORK WARNING:** May fail with SSL certificate issues. Use trusted-host flags as shown above.

3. **Database Setup:**
   ```bash
   # Start PostgreSQL and Redis
   sudo systemctl start postgresql redis-server
   
   # Create database and user
   sudo -u postgres createuser cloudviz
   sudo -u postgres createdb cloudviz -O cloudviz
   sudo -u postgres psql -c "ALTER USER cloudviz WITH PASSWORD 'cloudviz';"
   ```

4. **Environment Configuration:**
   ```bash
   # Copy environment template and configure
   cp .env.example .env
   # Edit .env file with your cloud provider credentials and database settings
   ```

5. **Build and Test:**
   ```bash
   # Run linting (ALWAYS run before committing)
   black cloudviz/
   isort cloudviz/
   flake8 cloudviz/
   mypy cloudviz/
   
   # Run tests
   pytest tests/unit/ -v --cov=cloudviz --cov-report=html
   pytest tests/integration/ -v
   ```
   **NEVER CANCEL:** Test suite takes 5-10 minutes. Set timeout to 20+ minutes.

6. **Run the Application:**
   ```bash
   # Development server with auto-reload
   uvicorn cloudviz.api.main:app --reload --host 0.0.0.0 --port 8000
   
   # Production server
   uvicorn cloudviz.api.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

### Docker Alternative

**NETWORK LIMITATION WARNING:** Docker builds may fail due to network restrictions. Use pre-built images when possible.

1. **Docker Development (if network allows):**
   ```bash
   # Build and run with Docker Compose
   docker compose up --build
   ```
   **NEVER CANCEL:** Docker build takes 15-20 minutes. Set timeout to 45+ minutes.
   **KNOWN ISSUE:** May fail with SSL certificate errors in restricted environments.

2. **Docker Production (alternative approach):**
   ```bash
   # If build fails, try using existing base images
   docker pull python:3.11-slim
   
   # Or use the scripts that handle network issues
   ./scripts/install-linux.sh docker
   ```

## Validation and Testing

### ALWAYS validate changes with these scenarios:

1. **Basic Structure Validation (always works):**
   ```bash
   # Verify repository structure
   ls -la pyproject.toml docker-compose.yml .env.example
   
   # Check critical directories
   ls -la cloudviz/api/ cloudviz/providers/ cloudviz/visualization/
   
   # Verify scripts are executable
   ls -la scripts/*.sh scripts/*.ps1
   chmod +x scripts/*.sh  # Make executable if needed
   ```

2. **Configuration Validation:**
   ```bash
   # Test Docker Compose configuration
   docker compose config --quiet
   
   # Verify environment template
   head -20 .env.example
   
   # Check Python syntax in main files
   python3 -m py_compile cloudviz/api/main.py
   python3 -m py_compile cloudviz/core/config.py
   ```

3. **Health Check Validation (requires dependencies):**
   ```bash
   # Test API health endpoint (after starting application)
   curl http://localhost:8000/health
   
   # Expected response:
   # {"status":"healthy","version":"1.0.0","database":"connected","cache":"connected"}
   ```

4. **Core Functionality Test (requires cloud credentials):**
   ```bash
   # Test extraction endpoint
   curl -X POST http://localhost:8000/api/v1/extract \
     -H "Content-Type: application/json" \
     -d '{
       "provider": "azure",
       "scope": "subscription", 
       "scope_identifier": "your-subscription-id"
     }'
   ```

5. **Comprehensive Health Check (requires dependencies):**
   ```bash
   # Use built-in health check script
   python scripts/health_check.py --url http://localhost:8000 --wait
   ```

6. **Installation Verification:**
   ```bash
   # Linux/macOS
   ./scripts/verify-installation.sh python
   
   # Windows PowerShell
   .\scripts\verify-installation.ps1 -Method python
   ```

### Manual Validation Requirements

**CRITICAL:** After any changes to the API or visualization components:

1. Start the application (`uvicorn cloudviz.api.main:app --reload`)
2. Access the health endpoint and verify successful response
3. Test at least one extraction workflow (if credentials available)
4. Verify Mermaid diagram generation works
5. Check logs for any errors or warnings

## CI/CD and Code Quality

### Pre-commit Requirements (ALWAYS run before committing):

```bash
# Code formatting and quality checks
black cloudviz/
isort cloudviz/
flake8 cloudviz/ --count --max-complexity=10 --max-line-length=127 --statistics
mypy cloudviz/

# Security scanning
bandit -r cloudviz/ -f json -o bandit-report.json

# Run relevant tests
pytest tests/unit/ -v
```

**NEVER CANCEL:** Linting and type checking takes 2-3 minutes. Set timeout to 10+ minutes.

### Build Times and Expectations:

- **Dependency Installation:** 10-15 minutes (requires network access)
- **Docker Build:** 15-20 minutes (full build with dependencies)
- **Test Suite:** 5-10 minutes (unit + integration tests)
- **Linting and Type Checking:** 2-3 minutes
- **Production Build:** 20-25 minutes (includes optimizations)

## Common Issues and Limitations

### Network Connectivity Issues:

**CRITICAL LIMITATION:** This environment has network restrictions that prevent:
- Installing Python packages via pip (SSL certificate issues)
- Docker builds requiring external resources (Node.js installation fails)
- Downloading cloud provider SDKs

```bash
# If pip install fails due to network timeouts/SSL issues:
pip install --timeout=300 --retries=3 --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements/dev.txt

# Alternative: Install core packages individually with trusted hosts
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org fastapi uvicorn pytest black isort flake8 mypy

# Or use pre-installed system packages where available
```

**WORKAROUND:** In environments with network restrictions:
1. Use the provided installation scripts which handle these issues
2. Copy the `.env.example` to `.env` and configure manually
3. Use Docker images from a registry rather than building locally
4. Test with mock/offline mode if available

### Database Connection Issues:
```bash
# Reset database if needed
sudo -u postgres dropdb cloudviz
sudo -u postgres createdb cloudviz -O cloudviz

# Check service status
sudo systemctl status postgresql redis-server
```

### Import Errors:
```bash
# Ensure virtual environment is activated and dependencies installed
source venv/bin/activate
pip install -e .
```

## Repository Structure and Key Files

### Critical Files:
- **`pyproject.toml`**: Project configuration, dependencies, and tool settings
- **`docker-compose.yml`**: Multi-service Docker deployment configuration
- **`.env.example`**: Environment configuration template (copy to `.env`)
- **`cloudviz/api/main.py`**: FastAPI application entry point
- **`cloudviz/core/config.py`**: Configuration management
- **`requirements/dev.txt`**: Development dependencies
- **`.github/workflows/ci.yml`**: CI/CD pipeline configuration

### Key Directories:
- **`cloudviz/api/`**: FastAPI application and REST endpoints
- **`cloudviz/providers/`**: Cloud provider integrations (Azure, AWS, GCP)
- **`cloudviz/visualization/`**: Diagram generation engines
- **`scripts/`**: Automation and utility scripts
- **`docs/`**: Comprehensive documentation
- **`examples/`**: Configuration examples and workflows

### Testing:
- **Unit Tests**: Run with `pytest tests/unit/`
- **Integration Tests**: Run with `pytest tests/integration/`
- **API Tests**: Run with `pytest tests/api/` (if exists)
- **Coverage Reports**: `pytest --cov=cloudviz --cov-report=html`

## Quick Reference Commands

```bash
# ALWAYS validate basic structure first (no dependencies required)
ls -la pyproject.toml docker-compose.yml .env.example
python3 -m py_compile cloudviz/api/main.py cloudviz/core/config.py

# Development workflow (requires dependencies)
source venv/bin/activate
pip install -e .
uvicorn cloudviz.api.main:app --reload

# Production workflow (requires Docker)
docker compose up --build
python scripts/health_check.py --url http://localhost:8000

# Testing workflow (requires dependencies)
pytest tests/unit/ -v --cov=cloudviz
black cloudviz/ && isort cloudviz/ && flake8 cloudviz/

# Network-restricted environment workflow
python3 -m venv venv && source venv/bin/activate
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org fastapi uvicorn
cp .env.example .env  # Edit manually
# Use mock/offline mode for testing

# Deployment workflow
docker build -t cloudviz:prod --target production .
python scripts/deploy.py production
```

## Troubleshooting

### Known Environment Limitations:
1. **Network restrictions**: SSL certificate issues prevent pip and Docker builds
2. **Dependency installation**: Use `--trusted-host` flags for pip
3. **Docker builds**: May fail due to Node.js installation issues
4. **Cloud provider APIs**: Require valid credentials in `.env` file

### Common Solutions:
1. **Application won't start**: Check `.env` file configuration and database connectivity
2. **Import errors**: Ensure virtual environment is activated and `pip install -e .` was run
3. **Test failures**: Verify database is running and test database is configured
4. **Docker build fails**: Use installation scripts or pre-built images
5. **Network timeouts**: Use `--trusted-host` flags or installation scripts in `scripts/` directory

### Quick Diagnostic Commands:
```bash
# Test basic structure (always works)
ls -la pyproject.toml .env.example && python3 --version

# Test Python syntax (no dependencies)
python3 -m py_compile cloudviz/api/main.py

# Test Docker configuration
docker compose config --quiet

# Test environment template
head -10 .env.example

# Test virtual environment
python3 -m venv test_venv && source test_venv/bin/activate && python --version
```

**Remember:** Always verify your changes work by running the application and testing core functionality before committing.