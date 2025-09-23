"""
Helper utilities for CloudViz platform.
General-purpose utility functions used across the platform.
"""

import asyncio
import functools
import hashlib
import random
import re
import uuid
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Union


def generate_id() -> str:
    """
    Generate a unique identifier.

    Returns:
        str: Unique identifier
    """
    return str(uuid.uuid4())


def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Safely get a value from a dictionary with dot notation support.

    Args:
        data: Dictionary to search
        key: Key to retrieve (supports dot notation like 'a.b.c')
        default: Default value if key not found

    Returns:
        Any: Value if found, default otherwise
    """
    if "." not in key:
        return data.get(key, default)

    keys = key.split(".")
    current = data

    for k in keys:
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return default

    return current


def flatten_dict(
    data: Dict[str, Any], parent_key: str = "", sep: str = "."
) -> Dict[str, Any]:
    """
    Flatten a nested dictionary.

    Args:
        data: Dictionary to flatten
        parent_key: Parent key prefix
        sep: Separator for nested keys

    Returns:
        Dict[str, Any]: Flattened dictionary
    """
    items = []

    for key, value in data.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key

        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, sep).items())
        else:
            items.append((new_key, value))

    return dict(items)


def unflatten_dict(data: Dict[str, Any], sep: str = ".") -> Dict[str, Any]:
    """
    Unflatten a dictionary with dot notation keys.

    Args:
        data: Flattened dictionary
        sep: Separator used in keys

    Returns:
        Dict[str, Any]: Nested dictionary
    """
    result = {}

    for key, value in data.items():
        parts = key.split(sep)
        current = result

        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        current[parts[-1]] = value

    return result


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
):
    """
    Decorator for retrying functions with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        jitter: Whether to add random jitter

    Returns:
        Decorator function
    """

    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    if attempt == max_retries:
                        break

                    # Calculate delay
                    delay = min(base_delay * (exponential_base**attempt), max_delay)

                    if jitter:
                        delay *= 0.5 + random.random() * 0.5

                    await asyncio.sleep(delay)

            raise last_exception

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    if attempt == max_retries:
                        break

                    # Calculate delay
                    delay = min(base_delay * (exponential_base**attempt), max_delay)

                    if jitter:
                        delay *= 0.5 + random.random() * 0.5

                    import time

                    time.sleep(delay)

            raise last_exception

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def validate_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        bool: True if valid email format
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe filesystem usage.

    Args:
        filename: Original filename

    Returns:
        str: Sanitized filename
    """
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)

    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(" .")

    # Limit length
    if len(sanitized) > 255:
        name, ext = sanitized.rsplit(".", 1) if "." in sanitized else (sanitized, "")
        max_name_len = 255 - len(ext) - 1 if ext else 255
        sanitized = name[:max_name_len] + ("." + ext if ext else "")

    return sanitized or "unnamed"


def format_bytes(bytes_value: int) -> str:
    """
    Format bytes value in human readable format.

    Args:
        bytes_value: Number of bytes

    Returns:
        str: Formatted string (e.g., "1.5 MB")
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def format_duration(seconds: float) -> str:
    """
    Format duration in human readable format.

    Args:
        seconds: Duration in seconds

    Returns:
        str: Formatted duration
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f}h"
    else:
        days = seconds / 86400
        return f"{days:.1f}d"


def parse_duration(duration_str: str) -> float:
    """
    Parse duration string to seconds.

    Args:
        duration_str: Duration string (e.g., "1h30m", "90s")

    Returns:
        float: Duration in seconds
    """
    pattern = r"(\d+(?:\.\d+)?)\s*([smhd]?)"
    matches = re.findall(pattern, duration_str.lower())

    total_seconds = 0.0
    for value, unit in matches:
        value = float(value)

        if unit == "s" or unit == "":
            total_seconds += value
        elif unit == "m":
            total_seconds += value * 60
        elif unit == "h":
            total_seconds += value * 3600
        elif unit == "d":
            total_seconds += value * 86400

    return total_seconds


def chunk_list(data: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size.

    Args:
        data: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List[List[Any]]: List of chunks
    """
    return [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple dictionaries with deep merging.

    Args:
        *dicts: Dictionaries to merge

    Returns:
        Dict[str, Any]: Merged dictionary
    """
    result = {}

    for d in dicts:
        for key, value in d.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = merge_dicts(result[key], value)
            else:
                result[key] = value

    return result


def calculate_hash(data: str, algorithm: str = "sha256") -> str:
    """
    Calculate hash of string data.

    Args:
        data: Data to hash
        algorithm: Hash algorithm to use

    Returns:
        str: Hexadecimal hash string
    """
    hasher = hashlib.new(algorithm)
    hasher.update(data.encode("utf-8"))
    return hasher.hexdigest()


def is_valid_url(url: str) -> bool:
    """
    Validate URL format.

    Args:
        url: URL to validate

    Returns:
        bool: True if valid URL
    """
    pattern = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    return pattern.match(url) is not None


def normalize_name(name: str) -> str:
    """
    Normalize a name for consistent usage.

    Args:
        name: Name to normalize

    Returns:
        str: Normalized name
    """
    # Convert to lowercase
    normalized = name.lower()

    # Replace spaces and special characters with underscores
    normalized = re.sub(r"[^a-z0-9_]", "_", normalized)

    # Remove multiple consecutive underscores
    normalized = re.sub(r"_+", "_", normalized)

    # Remove leading/trailing underscores
    normalized = normalized.strip("_")

    return normalized or "unnamed"


def get_nested_value(data: Dict[str, Any], path: List[str], default: Any = None) -> Any:
    """
    Get nested value from dictionary using path list.

    Args:
        data: Dictionary to search
        path: List of keys representing the path
        default: Default value if path not found

    Returns:
        Any: Value at path or default
    """
    current = data

    for key in path:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default

    return current


def set_nested_value(data: Dict[str, Any], path: List[str], value: Any):
    """
    Set nested value in dictionary using path list.

    Args:
        data: Dictionary to modify
        path: List of keys representing the path
        value: Value to set
    """
    current = data

    for key in path[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]

    current[path[-1]] = value


class Timer:
    """Context manager for timing operations."""

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.duration = None

    def __enter__(self):
        self.start_time = datetime.now()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()

    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self.start_time is None:
            return 0.0

        end_time = self.end_time or datetime.now()
        return (end_time - self.start_time).total_seconds()


def rate_limit(calls: int, period: float):
    """
    Decorator for rate limiting function calls.

    Args:
        calls: Number of calls allowed
        period: Time period in seconds

    Returns:
        Decorator function
    """

    def decorator(func):
        call_times = []

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = datetime.now()

            # Remove old calls outside the period
            cutoff = now - timedelta(seconds=period)
            call_times[:] = [t for t in call_times if t > cutoff]

            # Check if we're at the limit
            if len(call_times) >= calls:
                sleep_time = (
                    call_times[0] + timedelta(seconds=period) - now
                ).total_seconds()
                if sleep_time > 0:
                    import time

                    time.sleep(sleep_time)

            call_times.append(now)
            return func(*args, **kwargs)

        return wrapper

    return decorator
