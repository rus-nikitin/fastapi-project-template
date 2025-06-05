from typing import List, Annotated
import logging
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel

from core.config.settings import settings

logger = logging.getLogger(__name__)

oauth2_scheme = HTTPBearer(auto_error=False)


class JwtClient(BaseModel):
    """Client data extracted from JWT token"""
    sub: str  # Subject (client identifier)
    roles: List[str] = []
    exp: int  # Expiration timestamp

    @property
    def client_id(self) -> str:
        """Alias for sub field"""
        return self.sub

    def has_role(self, role: str) -> bool:
        """Check if client has specific role"""
        return role in self.roles

    def has_any_role(self, roles: List[str]) -> bool:
        """Check if client has any of specified roles"""
        return any(role in self.roles for role in roles)


def validate_jwt_token(token: str) -> JwtClient:
    """Validate JWT token and extract client data"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )

        # Extract required fields
        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception

        # Check expiration
        exp = payload.get("exp")
        if exp is None:
            raise credentials_exception

        if datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Extract roles (optional)
        roles = payload.get("roles", [])
        if not isinstance(roles, list):
            roles = []

        return JwtClient(sub=sub, roles=roles, exp=exp)

    except JWTError as e:
        logger.warning(f"JWT validation failed: {e}")
        raise credentials_exception


def get_jwt_client(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)
) -> JwtClient:
    """Extract and validate client from JWT token"""

    # Development mode: skip authentication completely
    if settings.jwt_dev_mode:
        logger.info("JWT dev mode: bypassing authentication, using admin client")
        return JwtClient(
            sub="dev-client",
            roles=["admin", "base"],
            exp=9999999999
        )

    # Production mode: require token
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Production mode: full validation
    return validate_jwt_token(credentials.credentials)


def require_roles(required_roles: List[str]):
    """Dependency factory for role-based authorization"""
    def role_checker(jwt_client: JwtClient = Depends(get_jwt_client)) -> JwtClient:
        if not jwt_client.has_any_role(required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {required_roles}"
            )
        return jwt_client
    return role_checker


def require_role(required_role: str):
    """Dependency factory for single role authorization"""
    return require_roles([required_role])


# Convenient type aliases
JwtClientDep = Annotated[JwtClient, Depends(get_jwt_client)]
AdminJwtClientDep = Annotated[JwtClient, Depends(require_role("admin"))]
