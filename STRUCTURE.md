# CloudViz Project Structure

This document describes the organization of the CloudViz repository.

## 📁 Root Directory Structure

```
cloudviz/
├── cloudviz/                   # Main Python package
│   ├── api/                    # FastAPI application
│   ├── core/                   # Core utilities and configuration
│   ├── providers/              # Cloud provider integrations
│   └── visualization/          # Diagram generation engine
├── docs/                       # All documentation
│   ├── wiki/                   # User guides and references
│   ├── PRODUCTION-DEPLOYMENT.md
│   ├── TROUBLESHOOTING.md
│   └── README.md
├── scripts/                    # Automation scripts
│   ├── install-windows.ps1    # Windows installation
│   ├── install-linux.sh       # Linux/macOS installation
│   └── verify-installation.*  # Verification scripts
├── examples/                   # Configuration examples and workflows
│   ├── configurations/        # Sample configurations
│   └── n8n-workflows/         # n8n automation workflows
├── requirements/               # Dependency management
│   ├── base.txt               # Core dependencies
│   ├── dev.txt                # Development dependencies
│   └── prod.txt               # Production dependencies
├── config/                     # Configuration templates
├── .env.example               # Environment configuration template
├── docker-compose.yml         # Docker deployment configuration
├── Dockerfile                 # Container definition
├── nginx.conf                 # Reverse proxy configuration
└── pyproject.toml            # Python project configuration
```

## Architecture Overview

### Core Package (`cloudviz/`)
- **`api/`**: FastAPI REST API implementation
- **`core/`**: Shared utilities, configuration, and base classes
- **`providers/`**: Cloud provider-specific resource extractors
- **`visualization/`**: Diagram generation and export engines

### Documentation (`docs/`)
- Comprehensive user and developer documentation
- Production deployment guides
- Troubleshooting and support resources

### Automation (`scripts/`)
- Installation scripts for multiple platforms
- Verification and testing utilities
- Deployment automation

### Configuration
- **`requirements/`**: Structured dependency management
- **`config/`**: Environment-specific configuration templates
- **`.env.example`**: Environment variables template

## Getting Started

1. **Clone the repository**
2. **Follow the installation guide**: [docs/wiki/Installation-Guide.md](docs/wiki/Installation-Guide.md)
3. **Configure environment**: Copy `.env.example` to `.env` and configure
4. **Deploy**: Use Docker (`docker compose up`) or Python (`pip install -e .`)

## Key Files

- **`README.md`**: Project overview and quick start
- **`pyproject.toml`**: Python packaging and tool configuration
- **`docker-compose.yml`**: Multi-service Docker deployment
- **`nginx.conf`**: Production reverse proxy configuration
- **`.env.example`**: Environment configuration template

## Development

For development setup and contribution guidelines, see:
- [docs/wiki/Installation-Guide.md](docs/wiki/Installation-Guide.md) - Development setup
- [scripts/README.md](scripts/README.md) - Automation scripts
- [requirements/dev.txt](requirements/dev.txt) - Development dependencies
