"""
Authentication endpoints for CloudViz API.
Handles JWT-based authentication and user management.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr

from cloudviz.core.config import CloudVizConfig
from cloudviz.core.utils import get_logger
from cloudviz.core.utils.security import generate_token, validate_token, hash_string
from cloudviz.api.dependencies import get_current_config


logger = get_logger(__name__)
router = APIRouter()
security = HTTPBearer()


class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response model."""
    access_token: str
    token_type: str
    expires_in: int
    user_info: Dict[str, Any]


class RefreshRequest(BaseModel):
    """Token refresh request model."""
    refresh_token: str


class UserInfo(BaseModel):
    """User information model."""
    username: str
    email: Optional[EmailStr] = None
    roles: list[str] = []
    permissions: list[str] = []
    last_login: Optional[datetime] = None


class TokenValidationResponse(BaseModel):
    """Token validation response model."""
    valid: bool
    user_info: Optional[UserInfo] = None
    expires_at: Optional[datetime] = None


# Mock user database - In production, this would be a real database
MOCK_USERS = {
    "admin": {
        "username": "admin",
        "password_hash": hash_string("admin123"),  # In production, use proper hashing
        "email": "admin@cloudviz.com",
        "roles": ["admin", "operator", "viewer"],
        "permissions": ["extract", "render", "admin", "view"]
    },
    "operator": {
        "username": "operator", 
        "password_hash": hash_string("operator123"),
        "email": "operator@cloudviz.com",
        "roles": ["operator", "viewer"],
        "permissions": ["extract", "render", "view"]
    },
    "viewer": {
        "username": "viewer",
        "password_hash": hash_string("viewer123"),
        "email": "viewer@cloudviz.com", 
        "roles": ["viewer"],
        "permissions": ["view"]
    }
}


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate user credentials."""
    user = MOCK_USERS.get(username)
    if not user:
        return None
    
    if user["password_hash"] != hash_string(password):
        return None
        
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    config: CloudVizConfig = Depends(get_current_config)
) -> Dict[str, Any]:
    """Get current authenticated user from JWT token."""
    try:
        token = credentials.credentials
        payload = validate_token(token, config.api.jwt_secret or "default-secret")
        
        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user = MOCK_USERS.get(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
        
    except Exception as e:
        logger.warning("Token validation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    config: CloudVizConfig = Depends(get_current_config)
):
    """
    Authenticate user and return JWT token.
    """
    try:
        # Authenticate user
        user = authenticate_user(request.username, request.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Generate JWT token
        token_data = {
            "sub": user["username"],
            "roles": user["roles"],
            "permissions": user["permissions"],
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=config.api.jwt_expiration // 3600)
        }
        
        access_token = generate_token(token_data, config.api.jwt_secret or "default-secret")
        
        # Update last login
        user["last_login"] = datetime.now()
        
        response = LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=config.api.jwt_expiration,
            user_info={
                "username": user["username"],
                "email": user["email"],
                "roles": user["roles"],
                "permissions": user["permissions"]
            }
        )
        
        logger.info("User authenticated successfully", username=user["username"])
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login failed", exc_info=True, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(
    request: RefreshRequest,
    config: CloudVizConfig = Depends(get_current_config)
):
    """
    Refresh JWT token.
    """
    # In a real implementation, you'd validate the refresh token
    # For simplicity, this endpoint is not fully implemented
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token refresh not implemented"
    )


@router.get("/validate", response_model=TokenValidationResponse)
async def validate_token_endpoint(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Validate current JWT token and return user info.
    """
    try:
        user_info = UserInfo(
            username=current_user["username"],
            email=current_user["email"],
            roles=current_user["roles"],
            permissions=current_user["permissions"],
            last_login=current_user.get("last_login")
        )
        
        return TokenValidationResponse(
            valid=True,
            user_info=user_info,
            expires_at=datetime.now() + timedelta(hours=1)  # Simplified
        )
        
    except Exception as e:
        logger.error("Token validation failed", exc_info=True, error=str(e))
        return TokenValidationResponse(valid=False)


@router.post("/logout")
async def logout(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Logout user (in a real implementation, this would invalidate the token).
    """
    logger.info("User logged out", username=current_user["username"])
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserInfo)
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get current user information.
    """
    return UserInfo(
        username=current_user["username"],
        email=current_user["email"],
        roles=current_user["roles"],
        permissions=current_user["permissions"],
        last_login=current_user.get("last_login")
    )
