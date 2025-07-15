"""
Custom exception classes for different platform errors.
"""

from typing import Optional, Dict, Any


class JobBotError(Exception):
    """Base exception for job bot errors."""
    
    def __init__(self, message: str, platform: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.platform = platform
        self.details = details or {}
        self.timestamp = None
        
        # Set timestamp
        import datetime
        self.timestamp = datetime.datetime.now().isoformat()


class PlatformError(JobBotError):
    """Base exception for platform-specific errors."""
    pass


class AuthenticationError(PlatformError):
    """Authentication failed on platform."""
    pass


class LoginError(AuthenticationError):
    """Login process failed."""
    pass


class CaptchaError(PlatformError):
    """Captcha encountered."""
    pass


class ElementNotFoundError(PlatformError):
    """Required element not found on page."""
    pass


class FormSubmissionError(PlatformError):
    """Form submission failed."""
    pass


class NetworkError(PlatformError):
    """Network-related error."""
    pass


class TimeoutError(PlatformError):
    """Operation timed out."""
    pass


class RateLimitError(PlatformError):
    """Rate limit exceeded."""
    pass


class ApplicationError(PlatformError):
    """Job application failed."""
    pass


class SearchError(PlatformError):
    """Job search failed."""
    pass


class DataExtractionError(PlatformError):
    """Failed to extract data from page."""
    pass


# Platform-specific exceptions
class LinkedInError(PlatformError):
    """LinkedIn-specific error."""
    pass


class IndeedError(PlatformError):
    """Indeed-specific error."""
    pass


class DiceError(PlatformError):
    """Dice-specific error."""
    pass


class RemoteOKError(PlatformError):
    """RemoteOK-specific error."""
    pass


class FlexJobsError(PlatformError):
    """FlexJobs-specific error."""
    pass


class TwitterError(PlatformError):
    """Twitter/X-specific error."""
    pass


class TuringError(PlatformError):
    """Turing-specific error."""
    pass


# Error type mapping for platforms
PLATFORM_ERROR_MAP = {
    'linkedin': LinkedInError,
    'indeed': IndeedError,
    'dice': DiceError,
    'remoteok': RemoteOKError,
    'flexjobs': FlexJobsError,
    'twitter': TwitterError,
    'turing': TuringError,
}


def get_platform_error(platform: str) -> type:
    """
    Get platform-specific error class.
    
    Args:
        platform: Platform name
        
    Returns:
        Platform-specific error class
    """
    return PLATFORM_ERROR_MAP.get(platform.lower(), PlatformError)


def create_platform_error(platform: str, message: str, error_type: str = None, details: Dict[str, Any] = None) -> PlatformError:
    """
    Create a platform-specific error.
    
    Args:
        platform: Platform name
        message: Error message
        error_type: Specific error type
        details: Additional error details
        
    Returns:
        Platform-specific error instance
    """
    error_class = get_platform_error(platform)
    
    # Map error types to specific exceptions
    if error_type:
        error_type_map = {
            'authentication': AuthenticationError,
            'login': LoginError,
            'captcha': CaptchaError,
            'element_not_found': ElementNotFoundError,
            'form_submission': FormSubmissionError,
            'network': NetworkError,
            'timeout': TimeoutError,
            'rate_limit': RateLimitError,
            'application': ApplicationError,
            'search': SearchError,
            'data_extraction': DataExtractionError,
        }
        
        specific_error_class = error_type_map.get(error_type, error_class)
        return specific_error_class(message, platform, details)
    
    return error_class(message, platform, details)