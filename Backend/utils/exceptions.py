class APIException(Exception):
    """Base exception for API errors"""
    def __init__(self, message, status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(APIException):
    """Raised when input validation fails"""
    def __init__(self, message):
        super().__init__(message, status_code=400)


class NotFoundError(APIException):
    """Raised when a resource is not found"""
    def __init__(self, message):
        super().__init__(message, status_code=404)


class UnauthorizedError(APIException):
    """Raised when authentication fails"""
    def __init__(self, message):
        super().__init__(message, status_code=401)


class ForbiddenError(APIException):
    """Raised when authorization fails"""
    def __init__(self, message):
        super().__init__(message, status_code=403)


class ConflictError(APIException):
    """Raised when there's a conflict (duplicate, etc)"""
    def __init__(self, message):
        super().__init__(message, status_code=409)


class DatabaseError(APIException):
    """Raised when database operations fail"""
    def __init__(self, message):
        super().__init__(message, status_code=500)