from fastapi import HTTPException
from typing import Any, Dict, Optional


class BaseAPIException(HTTPException):
    """Base exception for API errors"""

    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        pass


class AuthenticationError(BaseAPIException):
    """Authentication related errors"""

    def __init__(self, detail: str = "Authentication failed"):
        pass


class AuthorizationError(BaseAPIException):
    """Authorization related errors"""

    def __init__(self, detail: str = "Not enough permissions"):
        pass


class ValidationError(BaseAPIException):
    """Validation related errors"""

    def __init__(self, detail: str = "Validation failed"):
        pass


class NotFoundError(BaseAPIException):
    """Resource not found errors"""

    def __init__(self, detail: str = "Resource not found"):
        pass


class ConflictError(BaseAPIException):
    """Resource conflict errors"""

    def __init__(self, detail: str = "Resource conflict"):
        pass


class DatabaseError(BaseAPIException):
    """Database related errors"""

    def __init__(self, detail: str = "Database error"):
        pass
