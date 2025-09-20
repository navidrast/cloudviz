#!/usr/bin/env python3
"""
CloudViz Installation Verification Script
Validates that CloudViz is properly installed and functional

This script tests both the Python direct installation method 
and verifies core API functionality.
"""

import os
import sys
import subprocess
import importlib
import requests
import json
from pathlib import Path


def check_python_environment():
    """Check Python environment and CloudViz installation."""
    print("🐍 Checking Python Environment...")
    print("-" * 40)
    
    # Check Python version
    python_version = sys.version
    print(f"✅ Python Version: {python_version.split()[0]}")
    
    # Check if CloudViz can be imported
    try:
        import cloudviz
        print(f"✅ CloudViz module: Importable")
        if hasattr(cloudviz, '__version__'):
            print(f"   Version: {cloudviz.__version__}")
    except ImportError as e:
        print(f"❌ CloudViz import failed: {e}")
        return False
    
    # Check key dependencies
    dependencies = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'email_validator',
        'azure.identity',
        'boto3',
        'google.cloud.compute',
    ]
    
    print("\n📦 Checking Dependencies:")
    for dep in dependencies:
        try:
            importlib.import_module(dep)
            print(f"✅ {dep}: Available")
        except ImportError:
            print(f"❌ {dep}: Missing")
    
    return True


def check_api_functionality():
    """Check if the API server is functional."""
    print("\n🌐 Checking API Functionality...")
    print("-" * 40)
    
    base_url = "http://localhost:8000"
    
    # Test basic endpoints
    endpoints = [
        ("/health/", "Health Check"),
        ("/", "API Root"),
        ("/openapi.json", "OpenAPI Schema"),
        ("/docs", "API Documentation"),
    ]
    
    for endpoint, description in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {description}: {url}")
                
                # Parse JSON for health endpoint
                if endpoint == "/health/":
                    try:
                        health_data = response.json()
                        print(f"   Status: {health_data.get('status', 'unknown')}")
                        print(f"   Version: {health_data.get('version', 'unknown')}")
                        print(f"   Uptime: {health_data.get('uptime_seconds', 0):.1f}s")
                    except:
                        pass
                        
            else:
                print(f"❌ {description}: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {description}: Connection failed - {e}")
            return False
    
    return True


def check_docker_environment():
    """Check Docker environment (optional)."""
    print("\n🐳 Checking Docker Environment (Optional)...")
    print("-" * 40)
    
    try:
        # Check if Docker is available
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Docker: {result.stdout.strip()}")
            
            # Check if Docker Compose is available
            result = subprocess.run(['docker', 'compose', 'version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ Docker Compose: {result.stdout.strip()}")
                return True
            else:
                print("❌ Docker Compose: Not available")
                return False
        else:
            print("❌ Docker: Not available")
            return False
            
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Docker: Not available or not in PATH")
        return False


def main():
    """Main verification function."""
    print("🚀 CloudViz Installation Verification")
    print("=" * 60)
    print()
    
    # Check current directory
    cwd = Path.cwd()
    print(f"📁 Current Directory: {cwd}")
    
    # Check if we're in the CloudViz directory
    if not (cwd / "cloudviz").exists():
        print("⚠️  Warning: Not in CloudViz root directory")
        print("   Make sure you're in the cloudviz repository root")
    
    print()
    
    # Run checks
    python_ok = check_python_environment()
    
    # Only check API if Python environment is OK
    api_ok = False
    if python_ok:
        api_ok = check_api_functionality()
    
    # Check Docker (optional)
    docker_ok = check_docker_environment()
    
    # Summary
    print("\n📊 Verification Summary")
    print("=" * 60)
    
    status_python = "✅ PASS" if python_ok else "❌ FAIL"
    status_api = "✅ PASS" if api_ok else "❌ FAIL"
    status_docker = "✅ PASS" if docker_ok else "⚠️  Optional"
    
    print(f"Python Environment:  {status_python}")
    print(f"API Functionality:   {status_api}")
    print(f"Docker Environment:  {status_docker}")
    
    if python_ok and api_ok:
        print("\n🎉 CloudViz is successfully installed and functional!")
        print("\n📋 Next Steps:")
        print("1. Configure cloud provider credentials in .env file")
        print("2. Access the API documentation at http://localhost:8000/docs")
        print("3. Test cloud resource discovery with your credentials")
        print("\n📖 Documentation:")
        print("- Installation Guide: docs/Installation-Guide-Tested.md")
        print("- Troubleshooting: docs/TROUBLESHOOTING.md")
        print("- API Reference: wiki/API-Reference.md")
        
        return 0
    else:
        print("\n❌ CloudViz installation has issues")
        print("\n🔧 Troubleshooting:")
        if not python_ok:
            print("- Install CloudViz with: pip install -e .")
            print("- Install dependencies: pip install -r requirements.txt")
        if not api_ok:
            print("- Start API server: uvicorn cloudviz.api.main:app --host 0.0.0.0 --port 8000")
            print("- Check the troubleshooting guide: docs/TROUBLESHOOTING.md")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())