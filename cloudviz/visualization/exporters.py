"""
Diagram export and conversion utilities for CloudViz.
Handles exporting diagrams to various formats and storage systems.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from cloudviz.core.models import ResourceInventory
from cloudviz.core.utils import LoggerMixin, get_logger


class DiagramExporter(LoggerMixin):
    """
    Export diagrams to various formats and destinations.
    Supports file system, cloud storage, and other export targets.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize diagram exporter."""
        self.config = config or {}
        self.default_output_dir = self.config.get("output_directory", "./output")
        self.include_metadata = self.config.get("include_metadata", True)
        self.timestamp_files = self.config.get("timestamp_files", True)

        # Ensure output directory exists
        Path(self.default_output_dir).mkdir(parents=True, exist_ok=True)

    async def export_diagram(
        self,
        diagram_content: bytes,
        format_type: str,
        inventory: ResourceInventory,
        output_path: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Export diagram to file.

        Args:
            diagram_content: Diagram content as bytes
            format_type: Format type (mermaid, dot, png, svg, etc.)
            inventory: Resource inventory for metadata
            output_path: Optional custom output path
            **kwargs: Additional export options

        Returns:
            str: Path to exported file
        """
        # Generate output filename
        if not output_path:
            output_path = self._generate_output_path(format_type, inventory, **kwargs)

        # Ensure output directory exists
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # Write diagram content
        Path(output_path).write_bytes(diagram_content)

        self.log_info(
            "Diagram exported successfully",
            format=format_type,
            path=output_path,
            size=len(diagram_content),
        )

        # Export metadata if enabled
        if self.include_metadata:
            metadata_path = self._export_metadata(inventory, output_path, **kwargs)
            self.log_debug("Metadata exported", path=metadata_path)

        return output_path

    def _generate_output_path(
        self, format_type: str, inventory: ResourceInventory, **kwargs
    ) -> str:
        """Generate output file path."""
        # Base filename components
        components = []

        # Add provider
        if inventory.provider:
            components.append(inventory.provider.value.lower())

        # Add scope
        if inventory.extraction_scope:
            components.append(inventory.extraction_scope.value.lower())

        # Add scope identifier if available
        if inventory.scope_identifier:
            # Sanitize scope identifier
            safe_scope = self._sanitize_filename(inventory.scope_identifier)
            components.append(safe_scope)

        # Add timestamp if enabled
        if self.timestamp_files:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            components.append(timestamp)

        # Join components
        if components:
            filename = "_".join(components)
        else:
            filename = "cloudviz_diagram"

        # Add extension
        filename += f".{format_type}"

        # Return full path
        return str(Path(self.default_output_dir) / filename)

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for file system compatibility."""
        # Replace problematic characters
        safe_chars = []
        for char in filename:
            if char.isalnum() or char in "-_":
                safe_chars.append(char)
            elif char in " /\\":
                safe_chars.append("_")

        return "".join(safe_chars)[:50]  # Limit length

    def _export_metadata(
        self, inventory: ResourceInventory, diagram_path: str, **kwargs
    ) -> str:
        """Export metadata alongside diagram."""
        # Generate metadata
        metadata = {
            "diagram_info": {
                "path": diagram_path,
                "format": Path(diagram_path).suffix[1:],
                "generated_at": datetime.now().isoformat(),
                "generator": "CloudViz",
            },
            "inventory_info": {
                "provider": inventory.provider.value if inventory.provider else None,
                "scope": (
                    inventory.extraction_scope.value
                    if inventory.extraction_scope
                    else None
                ),
                "scope_identifier": inventory.scope_identifier,
                "extraction_time": inventory.extraction_time.isoformat(),
                "resource_count": len(inventory.resources),
                "relationship_count": len(inventory.relationships),
            },
            "resource_summary": self._generate_resource_summary(inventory),
            "export_options": kwargs,
        }

        # Generate metadata path
        metadata_path = str(Path(diagram_path).with_suffix(".metadata.json"))

        # Write metadata
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        return metadata_path

    def _generate_resource_summary(
        self, inventory: ResourceInventory
    ) -> Dict[str, Any]:
        """Generate summary of resources."""
        summary = {"by_type": {}, "by_resource_group": {}, "by_region": {}}

        # Count by type
        for resource in inventory.resources:
            res_type = resource.get_category()
            summary["by_type"][res_type] = summary["by_type"].get(res_type, 0) + 1

        # Count by resource group
        for resource in inventory.resources:
            rg = resource.resource_group or "None"
            summary["by_resource_group"][rg] = (
                summary["by_resource_group"].get(rg, 0) + 1
            )

        # Count by region
        for resource in inventory.resources:
            region = resource.region or "None"
            summary["by_region"][region] = summary["by_region"].get(region, 0) + 1

        return summary

    async def export_multiple_formats(
        self,
        inventory: ResourceInventory,
        formats: List[str],
        base_output_path: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, str]:
        """
        Export diagram in multiple formats.

        Args:
            inventory: Resource inventory to visualize
            formats: List of formats to export
            base_output_path: Base path for outputs
            **kwargs: Additional export options

        Returns:
            Dict mapping format to output path
        """
        from cloudviz.visualization.engines import (
            GraphvizEngine,
            ImageEngine,
            MermaidEngine,
        )

        exported_files = {}

        # Initialize engines as needed
        engines = {}

        for format_type in formats:
            self.log_info("Exporting format", format=format_type)

            try:
                # Get or create appropriate engine
                if format_type in ["mermaid", "md"]:
                    if "mermaid" not in engines:
                        engines["mermaid"] = MermaidEngine(self.config)
                    engine = engines["mermaid"]
                elif format_type in ["dot", "gv"]:
                    if "graphviz" not in engines:
                        engines["graphviz"] = GraphvizEngine(self.config)
                    engine = engines["graphviz"]
                elif format_type in ["png", "svg", "pdf", "jpg", "jpeg"]:
                    if "image" not in engines:
                        engines["image"] = ImageEngine(self.config)
                    engine = engines["image"]
                else:
                    self.log_warning("Unsupported format", format=format_type)
                    continue

                # Render diagram
                diagram_content = await engine.render(inventory, format_type, **kwargs)

                # Generate output path
                if base_output_path:
                    output_path = f"{base_output_path}.{format_type}"
                else:
                    output_path = self._generate_output_path(
                        format_type, inventory, **kwargs
                    )

                # Export diagram
                exported_path = await self.export_diagram(
                    diagram_content, format_type, inventory, output_path, **kwargs
                )

                exported_files[format_type] = exported_path

            except Exception as e:
                self.log_error(
                    "Failed to export format",
                    format=format_type,
                    error=str(e),
                    exc_info=True,
                )

        self.log_info(
            "Multi-format export completed",
            formats=list(exported_files.keys()),
            count=len(exported_files),
        )

        return exported_files

    async def export_to_cloud_storage(
        self,
        diagram_content: bytes,
        format_type: str,
        inventory: ResourceInventory,
        storage_config: Dict[str, Any],
        **kwargs,
    ) -> str:
        """
        Export diagram to cloud storage.

        Args:
            diagram_content: Diagram content
            format_type: Format type
            inventory: Resource inventory
            storage_config: Cloud storage configuration
            **kwargs: Additional options

        Returns:
            str: Cloud storage URL or path
        """
        storage_type = storage_config.get("type", "").lower()

        if storage_type == "azure_blob":
            return await self._export_to_azure_blob(
                diagram_content, format_type, inventory, storage_config, **kwargs
            )
        elif storage_type == "aws_s3":
            return await self._export_to_aws_s3(
                diagram_content, format_type, inventory, storage_config, **kwargs
            )
        elif storage_type == "gcp_storage":
            return await self._export_to_gcp_storage(
                diagram_content, format_type, inventory, storage_config, **kwargs
            )
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")

    async def _export_to_azure_blob(
        self,
        content: bytes,
        format_type: str,
        inventory: ResourceInventory,
        config: Dict[str, Any],
        **kwargs,
    ) -> str:
        """Export to Azure Blob Storage."""
        try:
            from azure.storage.blob import BlobServiceClient

            # Extract configuration
            connection_string = config.get("connection_string")
            account_url = config.get("account_url")
            container_name = config.get("container_name", "cloudviz")

            # Create blob service client
            if connection_string:
                blob_service = BlobServiceClient.from_connection_string(
                    connection_string
                )
            elif account_url:
                blob_service = BlobServiceClient(account_url=account_url)
            else:
                raise ValueError(
                    "Azure storage requires connection_string or account_url"
                )

            # Generate blob name
            blob_name = self._generate_cloud_path(format_type, inventory, **kwargs)

            # Upload blob
            blob_client = blob_service.get_blob_client(
                container=container_name, blob=blob_name
            )

            blob_client.upload_blob(content, overwrite=True)

            # Return blob URL
            blob_url = blob_client.url
            self.log_info("Exported to Azure Blob Storage", url=blob_url)
            return blob_url

        except ImportError:
            raise RuntimeError("Azure storage requires azure-storage-blob package")
        except Exception as e:
            self.log_error("Failed to export to Azure Blob Storage", error=str(e))
            raise

    async def _export_to_aws_s3(
        self,
        content: bytes,
        format_type: str,
        inventory: ResourceInventory,
        config: Dict[str, Any],
        **kwargs,
    ) -> str:
        """Export to AWS S3."""
        try:
            import boto3

            # Extract configuration
            bucket_name = config.get("bucket_name")
            region = config.get("region", "us-east-1")

            if not bucket_name:
                raise ValueError("AWS S3 export requires bucket_name")

            # Create S3 client
            s3_client = boto3.client("s3", region_name=region)

            # Generate object key
            object_key = self._generate_cloud_path(format_type, inventory, **kwargs)

            # Upload object
            s3_client.put_object(
                Bucket=bucket_name,
                Key=object_key,
                Body=content,
                ContentType=self._get_content_type(format_type),
            )

            # Generate URL
            s3_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{object_key}"
            self.log_info("Exported to AWS S3", url=s3_url)
            return s3_url

        except ImportError:
            raise RuntimeError("AWS S3 export requires boto3 package")
        except Exception as e:
            self.log_error("Failed to export to AWS S3", error=str(e))
            raise

    async def _export_to_gcp_storage(
        self,
        content: bytes,
        format_type: str,
        inventory: ResourceInventory,
        config: Dict[str, Any],
        **kwargs,
    ) -> str:
        """Export to Google Cloud Storage."""
        try:
            from google.cloud import storage

            # Extract configuration
            bucket_name = config.get("bucket_name")
            project_id = config.get("project_id")

            if not bucket_name:
                raise ValueError("GCP Storage export requires bucket_name")

            # Create storage client
            client = storage.Client(project=project_id)
            bucket = client.bucket(bucket_name)

            # Generate blob name
            blob_name = self._generate_cloud_path(format_type, inventory, **kwargs)

            # Upload blob
            blob = bucket.blob(blob_name)
            blob.upload_from_string(
                content, content_type=self._get_content_type(format_type)
            )

            # Generate URL
            gcs_url = f"gs://{bucket_name}/{blob_name}"
            self.log_info("Exported to Google Cloud Storage", url=gcs_url)
            return gcs_url

        except ImportError:
            raise RuntimeError(
                "GCP Storage export requires google-cloud-storage package"
            )
        except Exception as e:
            self.log_error("Failed to export to Google Cloud Storage", error=str(e))
            raise

    def _generate_cloud_path(
        self, format_type: str, inventory: ResourceInventory, **kwargs
    ) -> str:
        """Generate cloud storage path."""
        # Use similar logic to file path but with forward slashes
        path_components = ["cloudviz"]

        # Add date folder
        date_folder = datetime.now().strftime("%Y/%m/%d")
        path_components.append(date_folder)

        # Add provider
        if inventory.provider:
            path_components.append(inventory.provider.value.lower())

        # Generate filename
        filename_parts = []

        if inventory.extraction_scope:
            filename_parts.append(inventory.extraction_scope.value.lower())

        if inventory.scope_identifier:
            safe_scope = self._sanitize_filename(inventory.scope_identifier)
            filename_parts.append(safe_scope)

        if self.timestamp_files:
            timestamp = datetime.now().strftime("%H%M%S")
            filename_parts.append(timestamp)

        filename = "_".join(filename_parts) if filename_parts else "diagram"
        filename += f".{format_type}"

        path_components.append(filename)

        return "/".join(path_components)

    def _get_content_type(self, format_type: str) -> str:
        """Get MIME content type for format."""
        content_types = {
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "svg": "image/svg+xml",
            "pdf": "application/pdf",
            "dot": "text/vnd.graphviz",
            "gv": "text/vnd.graphviz",
            "mermaid": "text/plain",
            "md": "text/markdown",
        }

        return content_types.get(format_type, "application/octet-stream")

    def list_exported_files(self, pattern: Optional[str] = None) -> List[str]:
        """List previously exported files."""
        output_dir = Path(self.default_output_dir)

        if not output_dir.exists():
            return []

        if pattern:
            files = list(output_dir.glob(pattern))
        else:
            files = [f for f in output_dir.iterdir() if f.is_file()]

        return [str(f) for f in files]

    def cleanup_old_exports(self, max_age_days: int = 30) -> int:
        """Clean up old exported files."""
        output_dir = Path(self.default_output_dir)

        if not output_dir.exists():
            return 0

        cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
        deleted_count = 0

        for file_path in output_dir.iterdir():
            if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                try:
                    file_path.unlink()
                    deleted_count += 1
                    self.log_debug("Deleted old export", path=str(file_path))
                except Exception as e:
                    self.log_warning(
                        "Failed to delete old export", path=str(file_path), error=str(e)
                    )

        self.log_info("Cleanup completed", deleted_files=deleted_count)
        return deleted_count
