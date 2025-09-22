# CloudViz Scripts

This directory contains automation scripts for CloudViz installation, deployment, and maintenance.

## 📁 Script Categories

### Installation Scripts
- **`install-windows.ps1`** - Automated Windows installation script
- **`install-linux.sh`** - Automated Linux/macOS installation script

### Verification & Testing
- **`verify-installation.ps1`** - Windows installation verification
- **`verify-installation.sh`** - Linux/macOS installation verification
- **`quick-start*.ps1`** - Various quick-start verification scripts
- **`health_check.py`** - Application health monitoring

### Deployment & Maintenance
- **`deploy.py`** - Production deployment automation
- **`migrate.py`** - Database migration utilities
- **`deploy_wiki.py`** - Documentation deployment
- **`wiki_setup_helper.py`** - Wiki configuration helper

## Quick Usage

### Windows Installation
```powershell
# Full automated installation
.\scripts\install-windows.ps1 -InstallMethod docker

# Verify installation
.\scripts\verify-installation.ps1 -Method docker
```

### Linux/macOS Installation
```bash
# Full automated installation
./scripts/install-linux.sh docker

# Verify installation  
./scripts/verify-installation.sh docker
```

### Health Monitoring
```bash
# Check application health
python scripts/health_check.py

# Run comprehensive verification
python scripts/deploy.py --verify-only
```

## 📋 Prerequisites

- **Windows**: PowerShell 5.1+ (scripts ending in .ps1)
- **Linux/macOS**: Bash 4.0+ (scripts ending in .sh)  
- **Python**: 3.8+ (for .py scripts)
- **Admin/Sudo**: Required for system-level installations
