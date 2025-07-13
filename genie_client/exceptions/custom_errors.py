class GenieBaseError(Exception):
    """Base exception for all Genie client errors"""
    def __init__(self, message, context=None):
        super().__init__(message)
        self.context = context or {}
        self.message = message
        
    def __str__(self):
        return f"{self.__class__.__name__}: {self.message} | Context: {self.context}"

class ConfigurationError(GenieBaseError):
    """Invalid configuration provided"""

class AuthenticationError(GenieBaseError):
    """Authentication failure"""

class APIRequestError(GenieBaseError):
    """API request failure"""
    
    def __init__(self, message, status_code, response_body, context=None):
        super().__init__(message, context)
        self.status_code = status_code
        self.response_body = response_body

class RateLimitError(APIRequestError):
    """Rate limit exceeded"""

class TimeoutError(GenieBaseError):
    """Polling timeout reached"""

class InvalidInputError(GenieBaseError):
    """Invalid input parameters"""

class TokenRefreshError(AuthenticationError):
    """Failed to refresh access token"""

class ResultRetrievalError(APIRequestError):
    """Failed to fetch query results"""

class OperationAbortedError(GenieBaseError):
    """Operation aborted by client or server"""