#!/usr/bin/env python3
"""
Deployment script for CloudViz.
Handles deployment to different environments.
"""

import argparse
import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, Any

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from cloudviz.core.config import CloudVizConfig
except ImportError:
    print("⚠️  CloudViz not installed. Running basic deployment.")
    CloudVizConfig = None


class Deployer:
    """CloudViz deployment manager."""
    
    def __init__(self, env: str):
        self.env = env
        self.config = None
        
        if CloudVizConfig:
            try:
                self.config = CloudVizConfig.from_env(env)
            except Exception as e:
                print(f"⚠️  Could not load config: {e}")
    
    def deploy(self):
        """Execute deployment for the environment."""
        print(f"🚀 Starting deployment to {self.env} environment")
        
        if self.env == "dev":
            self._deploy_dev()
        elif self.env == "ppt":
            self._deploy_ppt()
        elif self.env == "prod":
            self._deploy_prod()
        else:
            raise ValueError(f"Unknown environment: {self.env}")
        
        print(f"✅ Deployment to {self.env} completed successfully")
    
    def _deploy_dev(self):
        """Deploy to development environment."""
        print("📝 Deploying to development...")
        
        # Install dependencies
        self._run_command([
            sys.executable, "-m", "pip", "install", "-r", "requirements/dev.txt"
        ])
        
        # Run migrations
        self._run_command([
            sys.executable, "scripts/migrate.py", "--env", "dev", "migrate"
        ])
        
        # Start development server
        print("🔄 Development server ready. Run: uvicorn cloudviz.api.main:app --reload")
    
    def _deploy_ppt(self):
        """Deploy to pre-production environment."""
        print("🔧 Deploying to pre-production...")
        
        # Install production dependencies
        self._run_command([
            sys.executable, "-m", "pip", "install", "-r", "requirements/prod.txt"
        ])
        
        # Run migrations
        self._run_command([
            sys.executable, "scripts/migrate.py", "--env", "ppt", "migrate"
        ])
        
        # Deploy using supervisor or systemd
        self._deploy_with_supervisor("ppt")
    
    def _deploy_prod(self):
        """Deploy to production environment."""
        print("🏭 Deploying to production...")
        
        # Backup current deployment
        self._create_backup()
        
        # Install production dependencies
        self._run_command([
            sys.executable, "-m", "pip", "install", "-r", "requirements/prod.txt"
        ])
        
        # Run migrations
        self._run_command([
            sys.executable, "scripts/migrate.py", "--env", "prod", "migrate"
        ])
        
        # Deploy using production method
        deployment_method = os.getenv("DEPLOYMENT_METHOD", "docker")
        
        if deployment_method == "docker":
            self._deploy_with_docker()
        elif deployment_method == "kubernetes":
            self._deploy_with_kubernetes()
        else:
            self._deploy_with_supervisor("prod")
    
    def _deploy_with_supervisor(self, env: str):
        """Deploy using Supervisor process manager."""
        print(f"📦 Deploying with Supervisor for {env}...")
        
        # Create supervisor configuration
        supervisor_config = f"""
[program:cloudviz-{env}]
command={sys.executable} -m uvicorn cloudviz.api.main:app --host 0.0.0.0 --port 8000
directory={project_root}
environment=CLOUDVIZ_ENV="{env}"
user=cloudviz
autostart=true
autorestart=true
stdout_logfile=/var/log/cloudviz/access.log
stderr_logfile=/var/log/cloudviz/error.log
stdout_logfile_maxbytes=100MB
stdout_logfile_backups=5
stderr_logfile_maxbytes=100MB
stderr_logfile_backups=5
"""
        
        config_path = f"/etc/supervisor/conf.d/cloudviz-{env}.conf"
        
        try:
            with open(config_path, 'w') as f:
                f.write(supervisor_config)
            
            # Reload supervisor
            self._run_command(["sudo", "supervisorctl", "reread"])
            self._run_command(["sudo", "supervisorctl", "update"])
            self._run_command(["sudo", "supervisorctl", "restart", f"cloudviz-{env}"])
            
        except PermissionError:
            print(f"⚠️  Could not write supervisor config. Manual setup required:")
            print(f"Config path: {config_path}")
            print(supervisor_config)
    
    def _deploy_with_docker(self):
        """Deploy using Docker."""
        print("🐳 Deploying with Docker...")
        
        # Build Docker image
        tag = f"cloudviz:prod-{int(time.time())}"
        self._run_command(["docker", "build", "-t", tag, "."])
        
        # Stop existing container
        self._run_command(["docker", "stop", "cloudviz-prod"], check=False)
        self._run_command(["docker", "rm", "cloudviz-prod"], check=False)
        
        # Start new container
        self._run_command([
            "docker", "run", "-d",
            "--name", "cloudviz-prod",
            "--restart", "unless-stopped",
            "-p", "8000:8000",
            "-e", "CLOUDVIZ_ENV=prod",
            "-v", "/var/log/cloudviz:/app/logs",
            "-v", "/etc/cloudviz:/app/config",
            tag
        ])
        
        print(f"✅ Docker container started with image: {tag}")
    
    def _deploy_with_kubernetes(self):
        """Deploy using Kubernetes."""
        print("☸️  Deploying with Kubernetes...")
        
        # Apply Kubernetes manifests
        k8s_dir = project_root / "k8s"
        
        if k8s_dir.exists():
            self._run_command(["kubectl", "apply", "-f", str(k8s_dir)])
            
            # Wait for rollout
            self._run_command([
                "kubectl", "rollout", "status", "deployment/cloudviz"
            ])
        else:
            print("⚠️  Kubernetes manifests not found in k8s/ directory")
    
    def _create_backup(self):
        """Create backup of current deployment."""
        print("💾 Creating backup...")
        
        backup_dir = f"/opt/cloudviz/backups/{int(time.time())}"
        
        try:
            self._run_command(["mkdir", "-p", backup_dir])
            
            # Backup application files
            self._run_command([
                "cp", "-r", str(project_root), f"{backup_dir}/app"
            ])
            
            # Backup database if SQLite
            if self.config and "sqlite" in getattr(self.config.database, 'url', ''):
                db_path = self.config.database.url.replace("sqlite:///", "")
                if os.path.exists(db_path):
                    self._run_command([
                        "cp", db_path, f"{backup_dir}/database.db"
                    ])
            
            print(f"✅ Backup created at: {backup_dir}")
            
        except Exception as e:
            print(f"⚠️  Backup failed: {e}")
    
    def _run_command(self, cmd: list, check: bool = True):
        """Run a shell command."""
        print(f"🔧 Running: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                check=check,
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            if result.stdout:
                print(result.stdout)
            
            if result.stderr and result.returncode != 0:
                print(f"⚠️  Error: {result.stderr}")
                
        except subprocess.CalledProcessError as e:
            if check:
                print(f"❌ Command failed: {e}")
                sys.exit(1)
        except FileNotFoundError:
            if check:
                print(f"❌ Command not found: {cmd[0]}")
                sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="CloudViz Deployment Tool")
    parser.add_argument(
        "--env",
        choices=["dev", "ppt", "prod"],
        required=True,
        help="Environment to deploy to"
    )
    parser.add_argument(
        "--skip-backup",
        action="store_true",
        help="Skip backup creation (prod only)"
    )
    
    args = parser.parse_args()
    
    try:
        deployer = Deployer(args.env)
        deployer.deploy()
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
