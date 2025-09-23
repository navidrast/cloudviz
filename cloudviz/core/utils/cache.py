"""
Cache utilities for CloudViz platform.
Provides cache key generation and management utilities.
"""

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from cloudviz.core.models import CloudProvider, ExtractionScope


@dataclass
class CacheKey:
    """Structured cache key for consistent caching."""

    prefix: str
    provider: Optional[CloudProvider] = None
    scope: Optional[ExtractionScope] = None
    scope_identifier: Optional[str] = None
    resource_types: Optional[List[str]] = None
    tags: Optional[Dict[str, str]] = None
    format: Optional[str] = None
    theme: Optional[str] = None
    layout: Optional[str] = None
    additional_params: Optional[Dict[str, Any]] = None

    def generate(self) -> str:
        """
        Generate cache key string.

        Returns:
            str: Cache key
        """
        key_parts = [self.prefix]

        if self.provider:
            key_parts.append(f"provider:{self.provider.value}")

        if self.scope:
            key_parts.append(f"scope:{self.scope.value}")

        if self.scope_identifier:
            key_parts.append(f"id:{self.scope_identifier}")

        if self.resource_types:
            types_str = ",".join(sorted(self.resource_types))
            key_parts.append(f"types:{types_str}")

        if self.tags:
            tags_str = ",".join(f"{k}:{v}" for k, v in sorted(self.tags.items()))
            key_parts.append(f"tags:{tags_str}")

        if self.format:
            key_parts.append(f"format:{self.format}")

        if self.theme:
            key_parts.append(f"theme:{self.theme}")

        if self.layout:
            key_parts.append(f"layout:{self.layout}")

        if self.additional_params:
            params_str = json.dumps(
                self.additional_params, sort_keys=True, separators=(",", ":")
            )
            params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
            key_parts.append(f"params:{params_hash}")

        return ":".join(key_parts)


def generate_cache_key(
    prefix: str,
    provider: Optional[CloudProvider] = None,
    scope: Optional[ExtractionScope] = None,
    scope_identifier: Optional[str] = None,
    **kwargs,
) -> str:
    """
    Generate a cache key for resource extraction.

    Args:
        prefix: Cache key prefix
        provider: Cloud provider
        scope: Extraction scope
        scope_identifier: Scope identifier
        **kwargs: Additional parameters

    Returns:
        str: Generated cache key
    """
    cache_key = CacheKey(
        prefix=prefix,
        provider=provider,
        scope=scope,
        scope_identifier=scope_identifier,
        **kwargs,
    )
    return cache_key.generate()


def generate_visualization_cache_key(
    inventory_hash: str,
    output_format: str,
    theme: Optional[str] = None,
    layout: Optional[str] = None,
    **kwargs,
) -> str:
    """
    Generate a cache key for visualization.

    Args:
        inventory_hash: Hash of the resource inventory
        output_format: Output format
        theme: Visualization theme
        layout: Layout algorithm
        **kwargs: Additional parameters

    Returns:
        str: Generated cache key
    """
    cache_key = CacheKey(
        prefix="visualization",
        format=output_format,
        theme=theme,
        layout=layout,
        additional_params={"inventory_hash": inventory_hash, **kwargs},
    )
    return cache_key.generate()


def hash_inventory(inventory_data: Dict[str, Any]) -> str:
    """
    Generate hash for resource inventory data.

    Args:
        inventory_data: Inventory data dictionary

    Returns:
        str: SHA256 hash of the inventory
    """
    # Create deterministic JSON string
    json_str = json.dumps(inventory_data, sort_keys=True, separators=(",", ":"))

    # Generate hash
    return hashlib.sha256(json_str.encode()).hexdigest()


def extract_cache_pattern(
    prefix: str,
    provider: Optional[CloudProvider] = None,
    scope: Optional[ExtractionScope] = None,
) -> str:
    """
    Generate cache pattern for invalidation.

    Args:
        prefix: Cache key prefix
        provider: Optional provider filter
        scope: Optional scope filter

    Returns:
        str: Cache key pattern
    """
    pattern_parts = [prefix]

    if provider:
        pattern_parts.append(f"provider:{provider.value}")
    else:
        pattern_parts.append("provider:*")

    if scope:
        pattern_parts.append(f"scope:{scope.value}")
    else:
        pattern_parts.append("scope:*")

    pattern_parts.append("*")

    return ":".join(pattern_parts)


class CacheKeyBuilder:
    """Builder class for constructing cache keys."""

    def __init__(self, prefix: str):
        self.cache_key = CacheKey(prefix=prefix)

    def provider(self, provider: CloudProvider) -> "CacheKeyBuilder":
        """Set provider."""
        self.cache_key.provider = provider
        return self

    def scope(self, scope: ExtractionScope, identifier: str) -> "CacheKeyBuilder":
        """Set scope and identifier."""
        self.cache_key.scope = scope
        self.cache_key.scope_identifier = identifier
        return self

    def resource_types(self, types: List[str]) -> "CacheKeyBuilder":
        """Set resource types."""
        self.cache_key.resource_types = types
        return self

    def tags(self, tags: Dict[str, str]) -> "CacheKeyBuilder":
        """Set tags."""
        self.cache_key.tags = tags
        return self

    def visualization_options(
        self, format: str, theme: Optional[str] = None, layout: Optional[str] = None
    ) -> "CacheKeyBuilder":
        """Set visualization options."""
        self.cache_key.format = format
        self.cache_key.theme = theme
        self.cache_key.layout = layout
        return self

    def additional_params(self, params: Dict[str, Any]) -> "CacheKeyBuilder":
        """Set additional parameters."""
        self.cache_key.additional_params = params
        return self

    def build(self) -> str:
        """Build the cache key."""
        return self.cache_key.generate()


def cache_key_builder(prefix: str) -> CacheKeyBuilder:
    """
    Create a new cache key builder.

    Args:
        prefix: Cache key prefix

    Returns:
        CacheKeyBuilder: New builder instance
    """
    return CacheKeyBuilder(prefix)
