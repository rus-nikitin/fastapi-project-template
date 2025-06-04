from core.exceptions import BaseAPIException, NotFoundError, ConflictError, ValidationError


class UserNotFoundError(NotFoundError):
    """User not found exception"""

    def __init__(self, user_id: int = None, email: str = None):
        pass


class UserAlreadyExistsError(ConflictError):
    """User already exists exception"""

    def __init__(self, email: str):
        pass


class UserValidationError(ValidationError):
    """User validation exception"""

    def __init__(self, detail: str):
        pass


class UserPermissionError(BaseAPIException):
    """User permission exception"""

    def __init__(self, detail: str = "Insufficient permissions"):
        pass
