#!/usr/bin/env python3
"""
Database migration script for CloudViz.
Handles database schema migrations across environments.
"""

import argparse
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from alembic import command
from alembic.config import Config
from cloudviz.core.config import CloudVizConfig


def run_migrations(env: str = "dev"):
    """Run database migrations for the specified environment."""
    print(f"Running migrations for environment: {env}")
    
    # Load configuration for the environment
    config = CloudVizConfig.from_env(env)
    
    # Set database URL for Alembic
    database_url = config.database.url
    if database_url.startswith("${") and database_url.endswith("}"):
        # Environment variable reference
        env_var = database_url[2:-1]
        database_url = os.getenv(env_var)
        if not database_url:
            raise ValueError(f"Environment variable {env_var} not set")
    
    # Configure Alembic
    alembic_cfg = Config(str(project_root / "alembic.ini"))
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    
    # Run migrations
    try:
        command.upgrade(alembic_cfg, "head")
        print("✅ Migrations completed successfully")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)


def create_migration(message: str, env: str = "dev"):
    """Create a new migration."""
    print(f"Creating migration: {message}")
    
    # Load configuration
    config = CloudVizConfig.from_env(env)
    database_url = config.database.url
    
    if database_url.startswith("${") and database_url.endswith("}"):
        env_var = database_url[2:-1]
        database_url = os.getenv(env_var)
        if not database_url:
            raise ValueError(f"Environment variable {env_var} not set")
    
    # Configure Alembic
    alembic_cfg = Config(str(project_root / "alembic.ini"))
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    
    # Create migration
    try:
        command.revision(alembic_cfg, message=message, autogenerate=True)
        print("✅ Migration created successfully")
    except Exception as e:
        print(f"❌ Migration creation failed: {e}")
        sys.exit(1)


def check_migration_status(env: str = "dev"):
    """Check current migration status."""
    print(f"Checking migration status for environment: {env}")
    
    # Load configuration
    config = CloudVizConfig.from_env(env)
    database_url = config.database.url
    
    if database_url.startswith("${") and database_url.endswith("}"):
        env_var = database_url[2:-1]
        database_url = os.getenv(env_var)
        if not database_url:
            raise ValueError(f"Environment variable {env_var} not set")
    
    # Configure Alembic
    alembic_cfg = Config(str(project_root / "alembic.ini"))
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    
    # Check status
    try:
        command.current(alembic_cfg, verbose=True)
        command.history(alembic_cfg, verbose=True)
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="CloudViz Database Migration Tool")
    parser.add_argument(
        "--env",
        choices=["dev", "ppt", "prod"],
        default="dev",
        help="Environment to run migrations for"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Migrate command
    migrate_parser = subparsers.add_parser("migrate", help="Run migrations")
    
    # Create migration command
    create_parser = subparsers.add_parser("create", help="Create new migration")
    create_parser.add_argument("message", help="Migration message")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check migration status")
    
    args = parser.parse_args()
    
    if args.command == "migrate" or not args.command:
        run_migrations(args.env)
    elif args.command == "create":
        create_migration(args.message, args.env)
    elif args.command == "status":
        check_migration_status(args.env)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
