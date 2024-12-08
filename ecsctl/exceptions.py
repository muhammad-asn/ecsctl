"""Custom exceptions for the ecsctl package."""

class ECSCommandError(Exception):
    """Custom exception for ECS command errors."""
    pass

class AuthenticationError(Exception):
    """Custom exception for AWS authentication failures.
    
    This exception is raised when AWS authentication or role assumption fails.
    
    Attributes:
        message (str): Explanation of the authentication error
        original_error (Optional[Exception]): The original exception that caused this error
    """
    def __init__(self, message: str, original_error: Exception = None) -> None:
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)