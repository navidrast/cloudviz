# Security Guide

This comprehensive security guide covers all aspects of securing CloudViz in production environments.

## 🔒 Security Overview

CloudViz handles sensitive infrastructure data and cloud credentials, making security a critical concern. This guide covers:

- **Authentication & Authorization**: Secure access control
- **Data Protection**: Encryption and data handling
- **Network Security**: Secure communications
- **Cloud Provider Security**: Credential management
- **Audit & Compliance**: Logging and monitoring
- **Incident Response**: Security incident handling

## 🔐 Authentication & Authorization

### 1. Authentication Methods

CloudViz supports multiple authentication methods:

#### API Key Authentication
```python
# Generate secure API keys
import secrets
import hashlib

def generate_api_key():
    """Generate cryptographically secure API key."""
    key = secrets.token_urlsafe(32)
    return key

def hash_api_key(api_key: str, salt: str) -> str:
    """Hash API key for secure storage."""
    return hashlib.pbkdf2_hmac('sha256', 
                               api_key.encode('utf-8'), 
                               salt.encode('utf-8'), 
                               100000)
```

#### JWT Token Authentication
```python
from jose import JWTError, jwt
from datetime import datetime, timedelta

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """Verify JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

#### OAuth 2.0 Integration
```python
from authlib.integrations.fastapi_oauth2 import OAuth2AuthorizationCodeBearer

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://provider.com/oauth/authorize",
    tokenUrl="https://provider.com/oauth/token",
)

@app.dependency
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current authenticated user from OAuth token."""
    # Verify token with OAuth provider
    user_info = await verify_oauth_token(token)
    return user_info
```

### 2. Role-Based Access Control (RBAC)

```python
from enum import Enum
from typing import List, Dict

class Permission(Enum):
    READ_RESOURCES = "read:resources"
    WRITE_RESOURCES = "write:resources"
    GENERATE_DIAGRAMS = "generate:diagrams"
    ADMIN_ACCESS = "admin:access"
    CLOUD_CONNECT = "cloud:connect"

class Role(BaseModel):
    name: str
    permissions: List[Permission]

# Predefined roles
ROLES = {
    "viewer": Role(
        name="viewer",
        permissions=[Permission.READ_RESOURCES, Permission.GENERATE_DIAGRAMS]
    ),
    "operator": Role(
        name="operator", 
        permissions=[
            Permission.READ_RESOURCES,
            Permission.WRITE_RESOURCES,
            Permission.GENERATE_DIAGRAMS,
            Permission.CLOUD_CONNECT
        ]
    ),
    "admin": Role(
        name="admin",
        permissions=[
            Permission.READ_RESOURCES,
            Permission.WRITE_RESOURCES,
            Permission.GENERATE_DIAGRAMS,
            Permission.CLOUD_CONNECT,
            Permission.ADMIN_ACCESS
        ]
    )
}

class RBACManager:
    """Role-Based Access Control manager."""
    
    def __init__(self):
        self.user_roles: Dict[str, List[str]] = {}
    
    def assign_role(self, user_id: str, role_name: str):
        """Assign role to user."""
        if user_id not in self.user_roles:
            self.user_roles[user_id] = []
        if role_name not in self.user_roles[user_id]:
            self.user_roles[user_id].append(role_name)
    
    def check_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has specific permission."""
        user_roles = self.user_roles.get(user_id, [])
        
        for role_name in user_roles:
            role = ROLES.get(role_name)
            if role and permission in role.permissions:
                return True
        
        return False
    
    def require_permission(self, permission: Permission):
        """Decorator to require specific permission."""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # Get current user from request context
                current_user = get_current_user()
                if not self.check_permission(current_user.id, permission):
                    raise HTTPException(
                        status_code=403,
                        detail="Insufficient permissions"
                    )
                return await func(*args, **kwargs)
            return wrapper
        return decorator

# Usage example
rbac = RBACManager()

@app.get("/api/v1/resources")
@rbac.require_permission(Permission.READ_RESOURCES)
async def get_resources():
    """Get resources - requires READ_RESOURCES permission."""
    pass
```

### 3. Multi-Factor Authentication (MFA)

```python
import pyotp
import qrcode
from io import BytesIO

class MFAManager:
    """Multi-Factor Authentication manager."""
    
    def generate_secret(self, user_email: str) -> str:
        """Generate TOTP secret for user."""
        secret = pyotp.random_base32()
        return secret
    
    def generate_qr_code(self, user_email: str, secret: str) -> bytes:
        """Generate QR code for TOTP setup."""
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_email,
            issuer_name="CloudViz"
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def verify_totp(self, secret: str, token: str) -> bool:
        """Verify TOTP token."""
        totp = pyotp.TOTP(secret)
        return totp.verify(token)

@app.post("/auth/mfa/setup")
async def setup_mfa(current_user: User = Depends(get_current_user)):
    """Setup MFA for user."""
    mfa_manager = MFAManager()
    secret = mfa_manager.generate_secret(current_user.email)
    
    # Store secret securely (encrypted)
    await store_user_mfa_secret(current_user.id, secret)
    
    # Generate QR code
    qr_code = mfa_manager.generate_qr_code(current_user.email, secret)
    
    return {
        "secret": secret,
        "qr_code": base64.b64encode(qr_code).decode()
    }

@app.post("/auth/mfa/verify")
async def verify_mfa(
    token: str,
    current_user: User = Depends(get_current_user)
):
    """Verify MFA token."""
    mfa_manager = MFAManager()
    secret = await get_user_mfa_secret(current_user.id)
    
    if not mfa_manager.verify_totp(secret, token):
        raise HTTPException(status_code=401, detail="Invalid MFA token")
    
    return {"message": "MFA verification successful"}
```

## 🔒 Data Protection

### 1. Encryption at Rest

```python
from cryptography.fernet import Fernet
import os
import base64

class EncryptionManager:
    """Handles encryption and decryption of sensitive data."""
    
    def __init__(self):
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _get_or_create_key(self) -> bytes:
        """Get encryption key from environment or generate new one."""
        key_b64 = os.getenv('ENCRYPTION_KEY')
        if key_b64:
            return base64.b64decode(key_b64)
        else:
            # Generate new key (save this securely!)
            key = Fernet.generate_key()
            print(f"Generated new encryption key: {base64.b64encode(key).decode()}")
            return key
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data."""
        if not data:
            return data
        
        encrypted_data = self.cipher.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data."""
        if not encrypted_data:
            return encrypted_data
        
        try:
            encrypted_bytes = base64.b64decode(encrypted_data)
            decrypted_data = self.cipher.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise ValueError("Failed to decrypt data")

# Usage for storing cloud credentials
encryption_manager = EncryptionManager()

class CloudCredential(BaseModel):
    provider: str
    credential_type: str
    encrypted_value: str
    
    @classmethod
    def create(cls, provider: str, credential_type: str, value: str):
        """Create encrypted credential."""
        encrypted_value = encryption_manager.encrypt(value)
        return cls(
            provider=provider,
            credential_type=credential_type,
            encrypted_value=encrypted_value
        )
    
    def get_value(self) -> str:
        """Get decrypted credential value."""
        return encryption_manager.decrypt(self.encrypted_value)
```

### 2. Encryption in Transit

```python
import ssl
from fastapi import FastAPI
import uvicorn

def create_ssl_context():
    """Create SSL context for HTTPS."""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(
        certfile="/path/to/cert.pem",
        keyfile="/path/to/key.pem"
    )
    
    # Security settings
    context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
    context.options |= ssl.OP_NO_SSLv2
    context.options |= ssl.OP_NO_SSLv3
    context.options |= ssl.OP_NO_TLSv1
    context.options |= ssl.OP_NO_TLSv1_1
    
    return context

# Run with HTTPS
if __name__ == "__main__":
    ssl_context = create_ssl_context()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=443,
        ssl=ssl_context
    )
```

### 3. Data Sanitization

```python
import re
from typing import Any, Dict

class DataSanitizer:
    """Sanitizes sensitive data in logs and responses."""
    
    SENSITIVE_PATTERNS = [
        (r'password["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', 'password'),
        (r'secret["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', 'secret'),
        (r'key["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', 'key'),
        (r'token["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)', 'token'),
        (r'Bearer\s+([A-Za-z0-9\-._~+/]+=*)', 'bearer_token'),
        (r'[A-Za-z0-9]{20,}', 'potential_secret')  # Long alphanumeric strings
    ]
    
    def sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize dictionary data."""
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, dict):
                sanitized[key] = self.sanitize_dict(value)
            elif isinstance(value, str):
                sanitized[key] = self.sanitize_string(value)
            else:
                # Check key names for sensitive data
                if any(sensitive in key.lower() for sensitive in ['password', 'secret', 'key', 'token']):
                    sanitized[key] = '***REDACTED***'
                else:
                    sanitized[key] = value
        
        return sanitized
    
    def sanitize_string(self, text: str) -> str:
        """Sanitize string data."""
        sanitized = text
        
        for pattern, name in self.SENSITIVE_PATTERNS:
            sanitized = re.sub(pattern, f'{name}=***REDACTED***', sanitized, flags=re.IGNORECASE)
        
        return sanitized

# Usage in logging
sanitizer = DataSanitizer()

def safe_log(level: str, message: str, data: Dict = None):
    """Log message with sanitized data."""
    if data:
        sanitized_data = sanitizer.sanitize_dict(data)
        logger.log(level, f"{message}: {sanitized_data}")
    else:
        logger.log(level, message)
```

## 🔗 Network Security

### 1. Network Policies (Kubernetes)

```yaml
# k8s/network-policies.yml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: cloudviz-network-policy
  namespace: cloudviz
spec:
  podSelector:
    matchLabels:
      app: cloudviz
  policyTypes:
  - Ingress
  - Egress
  
  ingress:
  # Allow traffic from ingress controller
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  
  # Allow internal communication
  - from:
    - podSelector:
        matchLabels:
          app: cloudviz
    ports:
    - protocol: TCP
      port: 8000
  
  egress:
  # Allow communication to database
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
  
  # Allow communication to Redis
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
  
  # Allow external HTTPS for cloud APIs
  - to: []
    ports:
    - protocol: TCP
      port: 443
  
  # Allow DNS
  - to: []
    ports:
    - protocol: UDP
      port: 53
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-default
  namespace: cloudviz
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
```

### 2. Firewall Rules (Docker)

```bash
#!/bin/bash
# firewall-setup.sh

# Reset iptables
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X

# Default policies
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Allow loopback
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# Allow established connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow SSH (change port as needed)
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Allow HTTP/HTTPS
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Allow CloudViz API (only from specific sources)
iptables -A INPUT -p tcp --dport 8000 -s 10.0.0.0/8 -j ACCEPT
iptables -A INPUT -p tcp --dport 8000 -s 172.16.0.0/12 -j ACCEPT
iptables -A INPUT -p tcp --dport 8000 -s 192.168.0.0/16 -j ACCEPT

# Allow database access (only from CloudViz containers)
iptables -A INPUT -p tcp --dport 5432 -s 172.18.0.0/16 -j ACCEPT

# Allow Redis access (only from CloudViz containers)
iptables -A INPUT -p tcp --dport 6379 -s 172.18.0.0/16 -j ACCEPT

# Log dropped packets
iptables -A INPUT -j LOG --log-prefix "DROPPED: "
iptables -A INPUT -j DROP

# Save rules
iptables-save > /etc/iptables/rules.v4
```

### 3. TLS Configuration

```python
import ssl
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI()

# Force HTTPS in production
if os.getenv("CLOUDVIZ_ENV") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# Trusted hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["cloudviz.company.com", "*.company.com"]
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    # Remove server header
    response.headers.pop("server", None)
    
    return response
```

## ☁️ Cloud Provider Security

### 1. Credential Management

```python
import boto3
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from google.cloud import secretmanager

class SecureCredentialManager:
    """Manages cloud credentials securely."""
    
    def __init__(self):
        self.azure_kv_client = None
        self.aws_sm_client = None
        self.gcp_sm_client = None
        
    def _get_azure_client(self):
        """Get Azure Key Vault client."""
        if not self.azure_kv_client:
            credential = DefaultAzureCredential()
            vault_url = os.getenv("AZURE_KEY_VAULT_URL")
            self.azure_kv_client = SecretClient(vault_url=vault_url, credential=credential)
        return self.azure_kv_client
    
    def _get_aws_client(self):
        """Get AWS Secrets Manager client."""
        if not self.aws_sm_client:
            self.aws_sm_client = boto3.client('secretsmanager')
        return self.aws_sm_client
    
    def _get_gcp_client(self):
        """Get GCP Secret Manager client."""
        if not self.gcp_sm_client:
            self.gcp_sm_client = secretmanager.SecretManagerServiceClient()
        return self.gcp_sm_client
    
    async def get_azure_secret(self, secret_name: str) -> str:
        """Get secret from Azure Key Vault."""
        try:
            client = self._get_azure_client()
            secret = client.get_secret(secret_name)
            return secret.value
        except Exception as e:
            logger.error(f"Failed to retrieve Azure secret {secret_name}: {e}")
            raise
    
    async def get_aws_secret(self, secret_name: str) -> str:
        """Get secret from AWS Secrets Manager."""
        try:
            client = self._get_aws_client()
            response = client.get_secret_value(SecretId=secret_name)
            return response['SecretString']
        except Exception as e:
            logger.error(f"Failed to retrieve AWS secret {secret_name}: {e}")
            raise
    
    async def get_gcp_secret(self, project_id: str, secret_id: str) -> str:
        """Get secret from GCP Secret Manager."""
        try:
            client = self._get_gcp_client()
            name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
            response = client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
        except Exception as e:
            logger.error(f"Failed to retrieve GCP secret {secret_id}: {e}")
            raise

# Usage
credential_manager = SecureCredentialManager()

async def get_azure_credentials():
    """Get Azure credentials securely."""
    client_id = await credential_manager.get_azure_secret("azure-client-id")
    client_secret = await credential_manager.get_azure_secret("azure-client-secret")
    tenant_id = await credential_manager.get_azure_secret("azure-tenant-id")
    
    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "tenant_id": tenant_id
    }
```

### 2. Least Privilege Access

#### Azure IAM Policies
```json
{
  "properties": {
    "roleName": "CloudViz Reader",
    "description": "Custom role for CloudViz with minimal required permissions",
    "assignableScopes": [
      "/subscriptions/{subscription-id}"
    ],
    "permissions": [
      {
        "actions": [
          "*/read",
          "Microsoft.Resources/subscriptions/resourceGroups/read",
          "Microsoft.Compute/virtualMachines/read",
          "Microsoft.Network/*/read",
          "Microsoft.Storage/storageAccounts/read",
          "Microsoft.Sql/servers/databases/read",
          "Microsoft.CostManagement/*/read"
        ],
        "notActions": [
          "Microsoft.Authorization/*/write",
          "Microsoft.Authorization/*/delete"
        ],
        "dataActions": [],
        "notDataActions": []
      }
    ]
  }
}
```

#### AWS IAM Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:Describe*",
        "rds:Describe*",
        "s3:ListBucket",
        "s3:GetBucketLocation",
        "lambda:List*",
        "lambda:Get*",
        "ecs:Describe*",
        "eks:Describe*",
        "elasticloadbalancing:Describe*",
        "cloudformation:Describe*",
        "cloudformation:List*",
        "cost-explorer:Get*",
        "budgets:View*"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Deny",
      "Action": [
        "*:Create*",
        "*:Delete*",
        "*:Update*",
        "*:Put*",
        "*:Modify*"
      ],
      "Resource": "*"
    }
  ]
}
```

#### GCP IAM Roles
```yaml
# Custom role for CloudViz
title: "CloudViz Viewer"
description: "Custom role for CloudViz with read-only access"
stage: "GA"
includedPermissions:
- compute.instances.list
- compute.instances.get
- storage.buckets.list
- storage.buckets.get
- sql.instances.list
- sql.instances.get
- container.clusters.list
- container.clusters.get
- cloudfunctions.functions.list
- billing.accounts.get
- monitoring.metricDescriptors.list
- logging.logs.list
```

### 3. Credential Rotation

```python
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any

class CredentialRotationManager:
    """Manages automatic credential rotation."""
    
    def __init__(self):
        self.rotation_intervals = {
            'azure': timedelta(days=90),
            'aws': timedelta(days=90),
            'gcp': timedelta(days=90)
        }
        self.last_rotation = {}
    
    async def check_rotation_needed(self, provider: str) -> bool:
        """Check if credential rotation is needed."""
        last_rotation = self.last_rotation.get(provider)
        if not last_rotation:
            return True
        
        interval = self.rotation_intervals.get(provider, timedelta(days=90))
        return datetime.utcnow() - last_rotation > interval
    
    async def rotate_azure_credentials(self) -> Dict[str, str]:
        """Rotate Azure service principal credentials."""
        try:
            # Create new service principal secret
            credential = DefaultAzureCredential()
            graph_client = GraphServiceClient(credentials=credential)
            
            app_id = os.getenv("AZURE_CLIENT_ID")
            
            # Add new password credential
            password_credential = PasswordCredential(
                display_name="CloudViz-Auto-Rotated",
                end_date_time=datetime.utcnow() + timedelta(days=90)
            )
            
            result = await graph_client.applications[app_id].add_password.post(
                password_credential
            )
            
            # Update stored credentials
            new_secret = result.secret_text
            await self.update_stored_secret("azure-client-secret", new_secret)
            
            # Schedule old credential deletion
            asyncio.create_task(
                self.schedule_old_credential_deletion("azure", result.key_id, timedelta(days=7))
            )
            
            self.last_rotation['azure'] = datetime.utcnow()
            
            return {
                "provider": "azure",
                "new_secret_id": result.key_id,
                "rotation_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Azure credential rotation failed: {e}")
            raise
    
    async def rotate_aws_credentials(self) -> Dict[str, str]:
        """Rotate AWS access keys."""
        try:
            iam_client = boto3.client('iam')
            username = os.getenv("AWS_USERNAME", "cloudviz-user")
            
            # Create new access key
            response = iam_client.create_access_key(UserName=username)
            new_access_key = response['AccessKey']
            
            # Update stored credentials
            await self.update_stored_secret("aws-access-key-id", new_access_key['AccessKeyId'])
            await self.update_stored_secret("aws-secret-access-key", new_access_key['SecretAccessKey'])
            
            # Schedule old key deletion
            old_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
            if old_access_key_id:
                asyncio.create_task(
                    self.schedule_old_credential_deletion("aws", old_access_key_id, timedelta(days=7))
                )
            
            self.last_rotation['aws'] = datetime.utcnow()
            
            return {
                "provider": "aws",
                "new_access_key_id": new_access_key['AccessKeyId'],
                "rotation_time": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"AWS credential rotation failed: {e}")
            raise
    
    async def schedule_old_credential_deletion(self, provider: str, credential_id: str, delay: timedelta):
        """Schedule deletion of old credentials after delay."""
        await asyncio.sleep(delay.total_seconds())
        
        try:
            if provider == "azure":
                await self.delete_azure_credential(credential_id)
            elif provider == "aws":
                await self.delete_aws_credential(credential_id)
            
            logger.info(f"Successfully deleted old {provider} credential: {credential_id}")
            
        except Exception as e:
            logger.error(f"Failed to delete old {provider} credential {credential_id}: {e}")
    
    async def auto_rotation_worker(self):
        """Background worker for automatic credential rotation."""
        while True:
            try:
                for provider in ['azure', 'aws', 'gcp']:
                    if await self.check_rotation_needed(provider):
                        logger.info(f"Starting credential rotation for {provider}")
                        
                        if provider == 'azure':
                            result = await self.rotate_azure_credentials()
                        elif provider == 'aws':
                            result = await self.rotate_aws_credentials()
                        
                        # Send notification
                        await self.send_rotation_notification(result)
                
                # Check every 24 hours
                await asyncio.sleep(86400)
                
            except Exception as e:
                logger.error(f"Credential rotation worker error: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour
```

## 🔍 Audit & Compliance

### 1. Audit Logging

```python
import json
from datetime import datetime
from typing import Any, Dict, Optional
from fastapi import Request
import structlog

class AuditLogger:
    """Comprehensive audit logging for security events."""
    
    def __init__(self):
        self.logger = structlog.get_logger("audit")
    
    def log_authentication_event(
        self,
        user_id: str,
        event_type: str,  # login, logout, failed_login, etc.
        source_ip: str,
        user_agent: str,
        success: bool,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log authentication events."""
        self.logger.info(
            "authentication_event",
            event_type=event_type,
            user_id=user_id,
            source_ip=source_ip,
            user_agent=user_agent,
            success=success,
            timestamp=datetime.utcnow().isoformat(),
            details=details or {}
        )
    
    def log_authorization_event(
        self,
        user_id: str,
        action: str,
        resource: str,
        granted: bool,
        source_ip: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log authorization events."""
        self.logger.info(
            "authorization_event",
            user_id=user_id,
            action=action,
            resource=resource,
            granted=granted,
            source_ip=source_ip,
            timestamp=datetime.utcnow().isoformat(),
            details=details or {}
        )
    
    def log_data_access(
        self,
        user_id: str,
        data_type: str,
        operation: str,  # read, write, delete
        resource_count: int,
        source_ip: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log data access events."""
        self.logger.info(
            "data_access_event",
            user_id=user_id,
            data_type=data_type,
            operation=operation,
            resource_count=resource_count,
            source_ip=source_ip,
            timestamp=datetime.utcnow().isoformat(),
            details=details or {}
        )
    
    def log_security_event(
        self,
        event_type: str,  # suspicious_activity, policy_violation, etc.
        severity: str,    # low, medium, high, critical
        description: str,
        source_ip: str,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log security events."""
        self.logger.warning(
            "security_event",
            event_type=event_type,
            severity=severity,
            description=description,
            source_ip=source_ip,
            user_id=user_id,
            timestamp=datetime.utcnow().isoformat(),
            details=details or {}
        )

# Audit middleware
audit_logger = AuditLogger()

@app.middleware("http")
async def audit_middleware(request: Request, call_next):
    """Middleware to audit API requests."""
    start_time = datetime.utcnow()
    
    # Extract request details
    source_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    method = request.method
    path = request.url.path
    
    # Get current user (if authenticated)
    user_id = None
    try:
        user = await get_current_user_from_request(request)
        user_id = user.id if user else None
    except:
        pass
    
    response = await call_next(request)
    
    # Log the request
    duration = (datetime.utcnow() - start_time).total_seconds()
    
    audit_logger.logger.info(
        "api_request",
        method=method,
        path=path,
        status_code=response.status_code,
        user_id=user_id,
        source_ip=source_ip,
        user_agent=user_agent,
        duration_seconds=duration,
        timestamp=start_time.isoformat()
    )
    
    # Log suspicious activity
    if response.status_code == 401:
        audit_logger.log_security_event(
            event_type="unauthorized_access_attempt",
            severity="medium",
            description=f"Unauthorized access attempt to {path}",
            source_ip=source_ip,
            user_id=user_id
        )
    elif response.status_code == 403:
        audit_logger.log_security_event(
            event_type="forbidden_access_attempt", 
            severity="medium",
            description=f"Forbidden access attempt to {path}",
            source_ip=source_ip,
            user_id=user_id
        )
    
    return response
```

### 2. Compliance Framework

```python
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any

class ComplianceFramework(Enum):
    SOC2 = "SOC2"
    ISO27001 = "ISO27001"
    GDPR = "GDPR"
    HIPAA = "HIPAA"
    PCI_DSS = "PCI_DSS"

@dataclass
class ComplianceRequirement:
    framework: ComplianceFramework
    control_id: str
    description: str
    implemented: bool
    evidence: List[str]
    notes: str

class ComplianceManager:
    """Manages compliance requirements and reporting."""
    
    def __init__(self):
        self.requirements = self._initialize_requirements()
    
    def _initialize_requirements(self) -> List[ComplianceRequirement]:
        """Initialize compliance requirements."""
        return [
            # SOC2 Type II requirements
            ComplianceRequirement(
                framework=ComplianceFramework.SOC2,
                control_id="CC6.1",
                description="Logical and physical access controls",
                implemented=True,
                evidence=[
                    "RBAC implementation",
                    "MFA enforcement",
                    "Network security policies"
                ],
                notes="Implemented with RBAC and MFA"
            ),
            ComplianceRequirement(
                framework=ComplianceFramework.SOC2,
                control_id="CC6.7",
                description="Data transmission and disposal",
                implemented=True,
                evidence=[
                    "TLS encryption",
                    "Data sanitization procedures",
                    "Secure credential storage"
                ],
                notes="All data encrypted in transit and at rest"
            ),
            
            # GDPR requirements
            ComplianceRequirement(
                framework=ComplianceFramework.GDPR,
                control_id="Art.32",
                description="Security of processing",
                implemented=True,
                evidence=[
                    "Encryption implementation",
                    "Access logging",
                    "Regular security assessments"
                ],
                notes="Technical and organizational measures implemented"
            ),
            ComplianceRequirement(
                framework=ComplianceFramework.GDPR,
                control_id="Art.17",
                description="Right to erasure",
                implemented=True,
                evidence=[
                    "Data deletion procedures",
                    "Audit logs of deletions"
                ],
                notes="User data can be completely removed on request"
            ),
            
            # ISO 27001 requirements
            ComplianceRequirement(
                framework=ComplianceFramework.ISO27001,
                control_id="A.9.1.2",
                description="Access to networks and network services",
                implemented=True,
                evidence=[
                    "Network policies",
                    "Firewall rules",
                    "VPN access controls"
                ],
                notes="Network access properly controlled and monitored"
            )
        ]
    
    def get_compliance_status(self, framework: ComplianceFramework) -> Dict[str, Any]:
        """Get compliance status for a framework."""
        framework_requirements = [
            req for req in self.requirements 
            if req.framework == framework
        ]
        
        implemented_count = sum(1 for req in framework_requirements if req.implemented)
        total_count = len(framework_requirements)
        
        return {
            "framework": framework.value,
            "total_requirements": total_count,
            "implemented_requirements": implemented_count,
            "compliance_percentage": (implemented_count / total_count) * 100 if total_count > 0 else 0,
            "requirements": [
                {
                    "control_id": req.control_id,
                    "description": req.description,
                    "implemented": req.implemented,
                    "evidence": req.evidence,
                    "notes": req.notes
                }
                for req in framework_requirements
            ]
        }
    
    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate comprehensive compliance report."""
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "frameworks": {}
        }
        
        for framework in ComplianceFramework:
            report["frameworks"][framework.value] = self.get_compliance_status(framework)
        
        return report

@app.get("/api/v1/compliance/report")
async def get_compliance_report(
    framework: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get compliance report."""
    # Check admin permissions
    if not rbac.check_permission(current_user.id, Permission.ADMIN_ACCESS):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    compliance_manager = ComplianceManager()
    
    if framework:
        try:
            framework_enum = ComplianceFramework(framework.upper())
            return compliance_manager.get_compliance_status(framework_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid framework")
    else:
        return compliance_manager.generate_compliance_report()
```

### 3. Security Monitoring

```python
import asyncio
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List

class SecurityMonitor:
    """Real-time security monitoring and threat detection."""
    
    def __init__(self):
        self.failed_login_attempts = defaultdict(deque)
        self.api_request_rates = defaultdict(deque)
        self.suspicious_ips = set()
        self.alert_thresholds = {
            'failed_logins_per_minute': 5,
            'api_requests_per_minute': 100,
            'suspicious_patterns': 3
        }
    
    def track_failed_login(self, ip_address: str, user_id: str):
        """Track failed login attempts."""
        now = datetime.utcnow()
        
        # Add to tracking
        self.failed_login_attempts[ip_address].append(now)
        
        # Clean old entries (older than 1 minute)
        cutoff = now - timedelta(minutes=1)
        while (self.failed_login_attempts[ip_address] and 
               self.failed_login_attempts[ip_address][0] < cutoff):
            self.failed_login_attempts[ip_address].popleft()
        
        # Check for threshold breach
        if len(self.failed_login_attempts[ip_address]) >= self.alert_thresholds['failed_logins_per_minute']:
            asyncio.create_task(self.send_security_alert(
                "multiple_failed_logins",
                f"Multiple failed logins from IP {ip_address}",
                "high",
                {"ip_address": ip_address, "user_id": user_id, "attempt_count": len(self.failed_login_attempts[ip_address])}
            ))
            
            # Add to suspicious IPs
            self.suspicious_ips.add(ip_address)
    
    def track_api_request(self, ip_address: str, endpoint: str):
        """Track API request rates."""
        now = datetime.utcnow()
        
        # Add to tracking
        key = f"{ip_address}:{endpoint}"
        self.api_request_rates[key].append(now)
        
        # Clean old entries (older than 1 minute)
        cutoff = now - timedelta(minutes=1)
        while (self.api_request_rates[key] and 
               self.api_request_rates[key][0] < cutoff):
            self.api_request_rates[key].popleft()
        
        # Check for rate limiting threshold
        if len(self.api_request_rates[key]) >= self.alert_thresholds['api_requests_per_minute']:
            asyncio.create_task(self.send_security_alert(
                "api_rate_limit_exceeded",
                f"API rate limit exceeded from IP {ip_address} for endpoint {endpoint}",
                "medium",
                {"ip_address": ip_address, "endpoint": endpoint, "request_count": len(self.api_request_rates[key])}
            ))
    
    def detect_suspicious_patterns(self, request_data: Dict):
        """Detect suspicious request patterns."""
        suspicious_indicators = []
        
        # Check for SQL injection patterns
        if any(pattern in str(request_data).lower() for pattern in [
            'union select', 'drop table', 'delete from', '; --', '1=1'
        ]):
            suspicious_indicators.append("sql_injection_attempt")
        
        # Check for XSS patterns
        if any(pattern in str(request_data).lower() for pattern in [
            '<script', 'javascript:', 'onerror=', 'onload='
        ]):
            suspicious_indicators.append("xss_attempt")
        
        # Check for path traversal
        if any(pattern in str(request_data) for pattern in [
            '../', '..\\', '/etc/passwd', '/proc/self'
        ]):
            suspicious_indicators.append("path_traversal_attempt")
        
        # Check for command injection
        if any(pattern in str(request_data) for pattern in [
            '|', '&&', '||', ';', '$(', '`'
        ]):
            suspicious_indicators.append("command_injection_attempt")
        
        if suspicious_indicators:
            asyncio.create_task(self.send_security_alert(
                "suspicious_request_pattern",
                f"Suspicious patterns detected: {', '.join(suspicious_indicators)}",
                "high",
                {"patterns": suspicious_indicators, "request_data": str(request_data)[:500]}
            ))
    
    async def send_security_alert(self, alert_type: str, message: str, severity: str, details: Dict):
        """Send security alert."""
        alert = {
            "alert_type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details
        }
        
        # Log the alert
        audit_logger.log_security_event(
            event_type=alert_type,
            severity=severity,
            description=message,
            source_ip=details.get("ip_address", "unknown"),
            details=details
        )
        
        # Send to monitoring systems (Slack, email, SIEM, etc.)
        await self.notify_security_team(alert)
    
    async def notify_security_team(self, alert: Dict):
        """Notify security team of alerts."""
        # Send to Slack
        if os.getenv("SLACK_WEBHOOK_URL"):
            await self.send_slack_alert(alert)
        
        # Send email for high severity
        if alert["severity"] in ["high", "critical"] and os.getenv("SECURITY_EMAIL"):
            await self.send_email_alert(alert)
        
        # Send to SIEM system
        if os.getenv("SIEM_ENDPOINT"):
            await self.send_siem_alert(alert)

# Initialize security monitor
security_monitor = SecurityMonitor()

# Integration with authentication
@app.post("/auth/login")
async def login(credentials: LoginCredentials, request: Request):
    try:
        user = await authenticate_user(credentials.username, credentials.password)
        if not user:
            security_monitor.track_failed_login(request.client.host, credentials.username)
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Successful login
        audit_logger.log_authentication_event(
            user_id=user.id,
            event_type="login",
            source_ip=request.client.host,
            user_agent=request.headers.get("user-agent", ""),
            success=True
        )
        
        return {"access_token": create_access_token({"sub": user.username})}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        security_monitor.track_failed_login(request.client.host, credentials.username)
        raise HTTPException(status_code=500, detail="Login failed")

# Request monitoring middleware
@app.middleware("http")
async def security_monitoring_middleware(request: Request, call_next):
    """Security monitoring middleware."""
    
    # Track API requests
    security_monitor.track_api_request(request.client.host, request.url.path)
    
    # Check for suspicious patterns in request
    request_data = {}
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.body()
            if body:
                request_data = json.loads(body.decode())
        except:
            pass
    
    # Add query parameters
    request_data.update(dict(request.query_params))
    
    if request_data:
        security_monitor.detect_suspicious_patterns(request_data)
    
    response = await call_next(request)
    return response
```

## 🚨 Incident Response

### 1. Incident Response Plan

```python
from enum import Enum
from datetime import datetime
from typing import List, Dict, Any

class IncidentSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentStatus(Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    MITIGATING = "mitigating"
    RESOLVED = "resolved"
    CLOSED = "closed"

@dataclass
class SecurityIncident:
    id: str
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus
    detected_at: datetime
    affected_systems: List[str]
    indicators: Dict[str, Any]
    response_actions: List[str]
    assigned_to: str
    resolved_at: Optional[datetime] = None

class IncidentResponseManager:
    """Manages security incident response."""
    
    def __init__(self):
        self.incidents = {}
        self.response_procedures = {
            IncidentSeverity.CRITICAL: {
                "response_time": timedelta(minutes=15),
                "notification_channels": ["slack", "email", "sms", "pagerduty"],
                "escalation_levels": ["security_team", "engineering_manager", "ciso"]
            },
            IncidentSeverity.HIGH: {
                "response_time": timedelta(hours=1),
                "notification_channels": ["slack", "email"],
                "escalation_levels": ["security_team", "engineering_manager"]
            },
            IncidentSeverity.MEDIUM: {
                "response_time": timedelta(hours=4),
                "notification_channels": ["slack"],
                "escalation_levels": ["security_team"]
            },
            IncidentSeverity.LOW: {
                "response_time": timedelta(hours=24),
                "notification_channels": ["slack"],
                "escalation_levels": ["security_team"]
            }
        }
    
    async def create_incident(
        self,
        title: str,
        description: str,
        severity: IncidentSeverity,
        affected_systems: List[str],
        indicators: Dict[str, Any]
    ) -> SecurityIncident:
        """Create new security incident."""
        
        incident_id = f"INC-{datetime.utcnow().strftime('%Y%m%d')}-{secrets.token_hex(4)}"
        
        incident = SecurityIncident(
            id=incident_id,
            title=title,
            description=description,
            severity=severity,
            status=IncidentStatus.OPEN,
            detected_at=datetime.utcnow(),
            affected_systems=affected_systems,
            indicators=indicators,
            response_actions=[],
            assigned_to=""
        )
        
        self.incidents[incident_id] = incident
        
        # Start incident response
        await self.initiate_response(incident)
        
        return incident
    
    async def initiate_response(self, incident: SecurityIncident):
        """Initiate incident response procedures."""
        
        # Log incident creation
        audit_logger.log_security_event(
            event_type="security_incident_created",
            severity=incident.severity.value,
            description=f"Security incident created: {incident.title}",
            source_ip="system",
            details={
                "incident_id": incident.id,
                "affected_systems": incident.affected_systems,
                "indicators": incident.indicators
            }
        )
        
        # Send notifications
        await self.send_incident_notifications(incident)
        
        # Auto-assign based on severity
        if incident.severity in [IncidentSeverity.CRITICAL, IncidentSeverity.HIGH]:
            incident.assigned_to = "security-team-lead"
        
        # Start automated response actions
        await self.execute_automated_response(incident)
    
    async def execute_automated_response(self, incident: SecurityIncident):
        """Execute automated response actions."""
        
        if incident.severity == IncidentSeverity.CRITICAL:
            # Critical incidents: Immediate lockdown
            await self.enable_security_lockdown()
            incident.response_actions.append("Security lockdown enabled")
        
        # Block suspicious IPs
        if "suspicious_ips" in incident.indicators:
            for ip in incident.indicators["suspicious_ips"]:
                await self.block_ip_address(ip)
                incident.response_actions.append(f"Blocked IP address: {ip}")
        
        # Disable compromised accounts
        if "compromised_accounts" in incident.indicators:
            for account in incident.indicators["compromised_accounts"]:
                await self.disable_user_account(account)
                incident.response_actions.append(f"Disabled account: {account}")
        
        # Rotate credentials if needed
        if "credential_compromise" in incident.indicators:
            await self.initiate_credential_rotation()
            incident.response_actions.append("Initiated credential rotation")
    
    async def enable_security_lockdown(self):
        """Enable emergency security lockdown."""
        
        # Increase rate limiting
        await self.update_rate_limits(factor=0.1)
        
        # Enable additional security checks
        await self.enable_enhanced_monitoring()
        
        # Notify operations team
        await self.notify_operations_team("Security lockdown enabled")
    
    async def block_ip_address(self, ip_address: str):
        """Block IP address at firewall level."""
        
        # Add to blocked IPs list
        blocked_ips = await self.get_blocked_ips()
        blocked_ips.add(ip_address)
        await self.save_blocked_ips(blocked_ips)
        
        # Update firewall rules (implementation depends on infrastructure)
        await self.update_firewall_rules()
    
    async def generate_incident_report(self, incident_id: str) -> Dict[str, Any]:
        """Generate comprehensive incident report."""
        
        incident = self.incidents.get(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")
        
        # Calculate response time
        if incident.resolved_at:
            response_time = incident.resolved_at - incident.detected_at
        else:
            response_time = datetime.utcnow() - incident.detected_at
        
        return {
            "incident": {
                "id": incident.id,
                "title": incident.title,
                "description": incident.description,
                "severity": incident.severity.value,
                "status": incident.status.value,
                "detected_at": incident.detected_at.isoformat(),
                "resolved_at": incident.resolved_at.isoformat() if incident.resolved_at else None,
                "response_time_minutes": response_time.total_seconds() / 60
            },
            "affected_systems": incident.affected_systems,
            "indicators": incident.indicators,
            "response_actions": incident.response_actions,
            "timeline": await self.get_incident_timeline(incident_id),
            "lessons_learned": await self.get_lessons_learned(incident_id)
        }

# Automated incident detection
async def detect_security_incidents():
    """Automated security incident detection."""
    
    incident_manager = IncidentResponseManager()
    
    # Check for multiple failed logins
    if len(security_monitor.failed_login_attempts) > 10:
        await incident_manager.create_incident(
            title="Multiple Failed Login Attempts Detected",
            description="Unusual number of failed login attempts across multiple IPs",
            severity=IncidentSeverity.MEDIUM,
            affected_systems=["authentication_system"],
            indicators={
                "failed_login_count": len(security_monitor.failed_login_attempts),
                "suspicious_ips": list(security_monitor.suspicious_ips)
            }
        )
    
    # Check for unusual API usage patterns
    high_usage_ips = [
        ip for ip, requests in security_monitor.api_request_rates.items()
        if len(requests) > 500  # More than 500 requests per minute
    ]
    
    if high_usage_ips:
        await incident_manager.create_incident(
            title="Unusual API Usage Patterns Detected",
            description="High volume API requests detected from multiple sources",
            severity=IncidentSeverity.HIGH,
            affected_systems=["api_gateway"],
            indicators={
                "high_usage_ips": high_usage_ips,
                "request_patterns": "high_volume"
            }
        )
```

## 📋 Security Checklist

### Pre-Deployment Security Checklist

```markdown
## 🔒 CloudViz Security Deployment Checklist

### Authentication & Authorization
- [ ] Strong passwords enforced (12+ characters, complexity requirements)
- [ ] Multi-factor authentication enabled for all admin accounts
- [ ] Role-based access control (RBAC) implemented
- [ ] JWT tokens properly configured with secure secrets
- [ ] API keys generated with sufficient entropy
- [ ] Default credentials changed/removed

### Data Protection
- [ ] Encryption at rest enabled for all sensitive data
- [ ] Encryption in transit (TLS 1.2+) enforced
- [ ] Database credentials encrypted and rotated
- [ ] Cloud provider credentials stored securely
- [ ] Data sanitization implemented in logs
- [ ] Backup encryption enabled

### Network Security
- [ ] Firewall rules configured with least privilege
- [ ] Network segmentation implemented
- [ ] VPN/private network access for admin functions
- [ ] Rate limiting configured
- [ ] DDoS protection enabled
- [ ] Security headers implemented

### Monitoring & Logging
- [ ] Comprehensive audit logging enabled
- [ ] Security event monitoring configured
- [ ] Failed login attempt tracking
- [ ] Suspicious activity detection
- [ ] Log retention policy defined
- [ ] SIEM integration completed

### Compliance & Governance
- [ ] Compliance requirements documented
- [ ] Data retention policies defined
- [ ] Privacy policy updated
- [ ] Security policies documented
- [ ] Incident response plan tested
- [ ] Vulnerability assessment completed

### Infrastructure Security
- [ ] Container images scanned for vulnerabilities
- [ ] Kubernetes security policies applied
- [ ] Secrets management implemented
- [ ] Resource limits configured
- [ ] Security contexts defined
- [ ] Network policies applied

### Application Security
- [ ] Input validation implemented
- [ ] SQL injection prevention
- [ ] XSS protection enabled
- [ ] CSRF protection implemented
- [ ] Security headers configured
- [ ] Error handling secured

### Operational Security
- [ ] Credential rotation scheduled
- [ ] Security patches up to date
- [ ] Backup and recovery tested
- [ ] Security training completed
- [ ] Access reviews scheduled
- [ ] Penetration testing completed
```

---

This security guide provides comprehensive coverage of all security aspects for CloudViz deployment and operation. Regular review and updates of these security measures are essential for maintaining a strong security posture.