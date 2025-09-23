"""
GCP provider for CloudViz platform.
Handles Google Cloud Platform resource discovery and extraction.
"""

from .extractor import GCPResourceExtractor
from .factory import GCPResourceFactory
from .models import GCPProject, GCPResource

__all__ = ["GCPResourceExtractor", "GCPResourceFactory", "GCPResource", "GCPProject"]
