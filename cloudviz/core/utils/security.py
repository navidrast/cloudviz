"""
Security utilities for CloudViz platform.
Provides encryption, hashing, token generation and validation utilities.
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from cryptography.fernet import Fernet
from jose import jwt

from cloudviz.core.config import get_config


def hash_string(data: str, algorithm: str = "sha256") -> str:
    """
    Hash a string using specified algorithm.

    Args:
        data: String to hash
        algorithm: Hash algorithm (sha256, sha512, md5)

    Returns:
        str: Hexadecimal hash
    """
    hasher = hashlib.new(algorithm)
    hasher.update(data.encode("utf-8"))
    return hasher.hexdigest()


def generate_random_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token.

    Args:
        length: Token length in bytes

    Returns:
        str: Random token (hex encoded)
    """
    return secrets.token_hex(length)


def generate_jwt_token(
    payload: Dict[str, Any],
    secret: Optional[str] = None,
    algorithm: str = "HS256",
    expires_in: Optional[int] = None,
) -> str:
    """
    Generate a JWT token.

    Args:
        payload: Token payload
        secret: Secret key (uses config if None)
        algorithm: JWT algorithm
        expires_in: Expiration time in seconds

    Returns:
        str: JWT token
    """
    if secret is None:
        config = get_config()
        secret = config.api.jwt_secret

        if not secret:
            raise ValueError("JWT secret not configured")

    # Add standard claims
    now = datetime.utcnow()
    payload = payload.copy()
    payload["iat"] = now

    if expires_in is not None:
        payload["exp"] = now + timedelta(seconds=expires_in)
    elif hasattr(get_config(), "api") and get_config().api.jwt_expiration:
        payload["exp"] = now + timedelta(seconds=get_config().api.jwt_expiration)

    return jwt.encode(payload, secret, algorithm=algorithm)


def validate_jwt_token(
    token: str, secret: Optional[str] = None, algorithm: str = "HS256"
) -> Optional[Dict[str, Any]]:
    """
    Validate and decode a JWT token.

    Args:
        token: JWT token to validate
        secret: Secret key (uses config if None)
        algorithm: JWT algorithm

    Returns:
        Optional[Dict[str, Any]]: Decoded payload if valid, None otherwise
    """
    try:
        if secret is None:
            config = get_config()
            secret = config.api.jwt_secret

            if not secret:
                return None

        payload = jwt.decode(token, secret, algorithms=[algorithm])
        return payload

    except jwt.InvalidTokenError:
        return None


def generate_api_key() -> str:
    """
    Generate an API key.

    Returns:
        str: API key
    """
    return f"cv_{secrets.token_urlsafe(32)}"


def validate_api_key_format(api_key: str) -> bool:
    """
    Validate API key format.

    Args:
        api_key: API key to validate

    Returns:
        bool: True if format is valid
    """
    return api_key.startswith("cv_") and len(api_key) > 10


def generate_encryption_key() -> bytes:
    """
    Generate an encryption key for Fernet.

    Returns:
        bytes: Encryption key
    """
    return Fernet.generate_key()


def encrypt_string(data: str, key: bytes) -> str:
    """
    Encrypt a string using Fernet encryption.

    Args:
        data: String to encrypt
        key: Encryption key

    Returns:
        str: Encrypted data (base64 encoded)
    """
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data.encode("utf-8"))
    return encrypted.decode("utf-8")


def decrypt_string(encrypted_data: str, key: bytes) -> str:
    """
    Decrypt a string using Fernet encryption.

    Args:
        encrypted_data: Encrypted data (base64 encoded)
        key: Encryption key

    Returns:
        str: Decrypted string
    """
    fernet = Fernet(key)
    decrypted = fernet.decrypt(encrypted_data.encode("utf-8"))
    return decrypted.decode("utf-8")


def hash_password(password: str) -> str:
    """
    Hash a password using a secure method.

    Args:
        password: Password to hash

    Returns:
        str: Hashed password
    """
    import bcrypt

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        password: Plain text password
        hashed_password: Hashed password

    Returns:
        bool: True if password matches
    """
    import bcrypt

    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def generate_token(
    length: int = 32, prefix: str = "", include_timestamp: bool = False
) -> str:
    """
    Generate a secure token with optional prefix and timestamp.

    Args:
        length: Token length
        prefix: Optional prefix
        include_timestamp: Whether to include timestamp

    Returns:
        str: Generated token
    """
    token = secrets.token_urlsafe(length)

    if include_timestamp:
        timestamp = int(datetime.now().timestamp())
        token = f"{timestamp}_{token}"

    if prefix:
        token = f"{prefix}_{token}"

    return token


def validate_token(token: str, expected_prefix: str = "") -> bool:
    """
    Validate token format.

    Args:
        token: Token to validate
        expected_prefix: Expected prefix

    Returns:
        bool: True if token format is valid
    """
    if expected_prefix and not token.startswith(f"{expected_prefix}_"):
        return False

    # Remove prefix if present
    if expected_prefix:
        token = token[len(expected_prefix) + 1 :]

    # Check if token contains timestamp
    if "_" in token:
        parts = token.split("_", 1)
        if len(parts) == 2:
            try:
                timestamp = int(parts[0])
                # Validate timestamp is reasonable (not too old or in future)
                now = int(datetime.now().timestamp())
                if abs(now - timestamp) > 86400 * 365:  # 1 year
                    return False
                token = parts[1]
            except ValueError:
                pass

    # Validate token length and characters
    return len(token) >= 16 and token.replace("-", "").replace("_", "").isalnum()


class TokenManager:
    """Manager for token generation and validation."""

    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or generate_random_token()

    def create_access_token(
        self, user_id: str, scopes: list = None, expires_in: int = 3600
    ) -> str:
        """
        Create an access token.

        Args:
            user_id: User identifier
            scopes: Token scopes
            expires_in: Expiration time in seconds

        Returns:
            str: Access token
        """
        payload = {"sub": user_id, "type": "access", "scopes": scopes or []}
        return generate_jwt_token(payload, self.secret_key, expires_in=expires_in)

    def create_refresh_token(self, user_id: str) -> str:
        """
        Create a refresh token.

        Args:
            user_id: User identifier

        Returns:
            str: Refresh token
        """
        payload = {"sub": user_id, "type": "refresh"}
        return generate_jwt_token(
            payload, self.secret_key, expires_in=30 * 24 * 3600
        )  # 30 days

    def validate_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate an access token.

        Args:
            token: Token to validate

        Returns:
            Optional[Dict[str, Any]]: Token payload if valid
        """
        payload = validate_jwt_token(token, self.secret_key)
        if payload and payload.get("type") == "access":
            return payload
        return None

    def validate_refresh_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate a refresh token.

        Args:
            token: Token to validate

        Returns:
            Optional[Dict[str, Any]]: Token payload if valid
        """
        payload = validate_jwt_token(token, self.secret_key)
        if payload and payload.get("type") == "refresh":
            return payload
        return None


def secure_compare(a: str, b: str) -> bool:
    """
    Perform a timing-safe string comparison.

    Args:
        a: First string
        b: Second string

    Returns:
        bool: True if strings are equal
    """
    return secrets.compare_digest(a.encode("utf-8"), b.encode("utf-8"))
